import os
import time
import json
import io
import csv
import requests
import xml.etree.ElementTree as ET
from typing import Any, Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain_core.tools import tool


def _get_api_key() -> str | None:
    """Safely retrieve the NCBI API key from environment."""
    return os.getenv("NCBI_API_KEY") or None


def _build_params(base: dict, api_key: str | None) -> dict:
    """Attach api_key to params dict if available."""
    if api_key:
        base["api_key"] = api_key
    return base


def _get_pmc_ids(pmids: List[str], api_key: str | None) -> Dict[str, str]:
    """
    Convert PubMed IDs to PMC IDs using elink.
    Returns a dict: {pmid -> pmcid} for articles available in PMC.
    """
    params = _build_params({
        "dbfrom": "pubmed",
        "db": "pmc",
        "id": ",".join(pmids),
        "retmode": "json",
    }, api_key)

    try:
        resp = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi",
            params=params,
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()

        pmid_to_pmc = {}
        linksets = data.get("linksets", [])
        for linkset in linksets:
            pmid = linkset.get("ids", [None])[0]
            links = linkset.get("linksetdbs", [])
            for link in links:
                if link.get("linkname") == "pubmed_pmc":
                    pmc_ids = link.get("links", [])
                    if pmc_ids and pmid:
                        pmid_to_pmc[str(pmid)] = str(pmc_ids[0])
        return pmid_to_pmc
    except Exception:
        return {}


def _fetch_pmc_full_text(pmc_id: str, api_key: str | None) -> str:
    """
    Fetch the full text of a PMC article using efetch.
    Parses all body sections (intro, methods, results, discussion, conclusion).
    Returns concatenated plain text of the full article body.
    """
    params = _build_params({
        "db": "pmc",
        "id": pmc_id,
        "rettype": "full",
        "retmode": "xml",
    }, api_key)

    try:
        resp = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            params=params,
            timeout=30,
        )
        resp.raise_for_status()

        root = ET.fromstring(resp.text)
        sections = []

        # Extract all section titles + paragraphs from article body
        for sec in root.findall(".//sec"):
            title_elem = sec.find("title")
            sec_title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
            paragraphs = []
            for p in sec.findall(".//p"):
                text = "".join(p.itertext()).strip()
                if text:
                    paragraphs.append(text)
            if paragraphs:
                if sec_title:
                    sections.append(f"\n## {sec_title}\n" + "\n".join(paragraphs))
                else:
                    sections.append("\n".join(paragraphs))

        # Fallback: if no sections found, get all paragraph text
        if not sections:
            all_p = root.findall(".//p")
            sections = ["".join(p.itertext()).strip() for p in all_p if "".join(p.itertext()).strip()]

        return "\n\n".join(sections) if sections else "Full text not available."
    except Exception as e:
        return f"Full text fetch failed: {e}"


@tool
def pubmed_to_pmc_full_text_search(query: str, max_results: int = 10) -> str:
    """
    Search PubMed and return FULL article text via PMC.

    Args:
        query (str): Search term for PubMed.
        max_results (int): Maximum articles.
    """
    api_key = _get_api_key()
    t_total = time.time()
    print(f"\n[TIMING] pubmed_tool → started | query: {query[:80]}")

    # ── Step 1: Search PubMed for IDs ──────────────────────────────────────
    search_params = _build_params({
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "sort": "date",  # Most recent first
    }, api_key)

    try:
        t = time.time()
        search_resp = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params=search_params,
            timeout=30,
        )
        search_resp.raise_for_status()
        pmids = search_resp.json().get("esearchresult", {}).get("idlist", [])
        print(f"[TIMING] pubmed_tool step1 esearch → {time.time()-t:.2f}s | {len(pmids)} PMIDs")

        if not pmids:
            return json.dumps({
                "status": "no_results",
                "message": f"No results found for: '{query}'. Try MeSH terms like 'diabetes mellitus[mesh]'.",
                "articles": [],
            })

        # ── Step 2: Fetch article summaries (metadata) ─────────────────────
        summary_params = _build_params({
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "json",
        }, api_key)

        t = time.time()
        summary_resp = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
            params=summary_params,
            timeout=20,
        )
        summary_resp.raise_for_status()
        articles_data = summary_resp.json().get("result", {})
        print(f"[TIMING] pubmed_tool step2 esummary → {time.time()-t:.2f}s")

        # ── Step 3: Fetch abstracts via efetch XML ─────────────────────────
        fetch_params = _build_params({
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
        }, api_key)

        t = time.time()
        fetch_resp = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            params=fetch_params,
            timeout=20,
        )
        fetch_resp.raise_for_status()

        root = ET.fromstring(fetch_resp.text)
        abstracts = {}
        for article in root.findall(".//PubmedArticle"):
            pmid_elem = article.find(".//PMID")
            # Collect all abstract text parts (some abstracts have multiple labeled sections)
            abstract_parts = article.findall(".//Abstract/AbstractText")
            if pmid_elem is not None and abstract_parts:
                full_abstract = " ".join(
                    f"[{p.get('Label', '')}] {p.text or ''}" if p.get("Label") else (p.text or "")
                    for p in abstract_parts
                ).strip()
                abstracts[pmid_elem.text] = full_abstract
        print(f"[TIMING] pubmed_tool step3 efetch abstracts → {time.time()-t:.2f}s")

        # ── Step 4: Assemble results (abstracts only — PMC full text skipped) ──
        results = []
        for pmid in pmids:
            if pmid not in articles_data:
                continue
            meta = articles_data[pmid]
            abstract = abstracts.get(pmid, "No abstract available.")

            results.append({
                "title": meta.get("title", "").rstrip("."),
                "authors": [a.get("name", "") for a in meta.get("authors", [])[:5]],
                "journal": meta.get("source", ""),
                "published_date": meta.get("pubdate", ""),
                "summary": abstract,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            })

        output = json.dumps(results, ensure_ascii=False)
        print(f"[TIMING] pubmed_tool → TOTAL {time.time()-t_total:.2f}s | output size: {len(output)} chars")
        return output

    except requests.exceptions.RequestException as e:
        return json.dumps({"status": "error", "message": f"Network error: {e}", "articles": []})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Processing error: {e}", "articles": []})


# ── CSV Helpers ────────────────────────────────────────────────────────────────

def articles_to_csv(articles: List[Dict[str, Any]]) -> str:
    """Convert a list of article dicts to a CSV string."""
    if not articles:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["title", "authors", "journal", "published_date", "summary", "url"],
        extrasaction="ignore",
    )
    writer.writeheader()
    for article in articles:
        row = article.copy()
        row["authors"] = ", ".join(row.get("authors", []))
        writer.writerow(row)
    return output.getvalue()


def save_csv_file(articles: List[Dict[str, Any]], filename: str = "search_results.csv") -> str:
    """Save articles as a CSV file and return the absolute file path."""
    csv_content = articles_to_csv(articles)
    with open(filename, "w", encoding="utf-8", newline="") as f:
        f.write(csv_content)
    return os.path.abspath(filename)
