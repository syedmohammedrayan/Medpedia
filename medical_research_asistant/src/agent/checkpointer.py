"""checkpointer.py
───────────────
Persistent, thread-safe checkpoint saver for LangGraph.
Extends LangGraph's MemorySaver by automatically syncing checkpoints and thread
states to disk using atomic file replacements.

Key Capabilities:
1. Multi-User Isolation: Each user / clinical inquiry maintains its own unique thread_id namespace.
2. Resilience across Process Restarts: When containers restart, server workers recycle,
   or redeployments occur, paused interrupts and completed research states are seamlessly
   reloaded from disk.
3. Zero External Dependencies: Built entirely on Python standard library (pickle + os.replace).
"""

import os
import pickle
import threading
from typing import Any, Sequence
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import ChannelVersions, Checkpoint, CheckpointMetadata
from langgraph.checkpoint.memory import MemorySaver


class PersistentMemorySaver(MemorySaver):
    """A durable checkpointer that persists LangGraph state to disk.
    Guarantees thread-safe atomic writes and full state restoration on server startup.
    """

    def __init__(self, file_path: str | None = None, serde=None):
        super().__init__(serde=serde)
        if file_path:
            self.file_path = file_path
        else:
            env_path = os.getenv("MEDPEDIA_CHECKPOINTS_FILE")
            if env_path:
                self.file_path = env_path
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                self.file_path = os.path.join(base_dir, "medpedia_checkpoints.pkl")

        self._lock = threading.Lock()
        self._load()

    def _load(self) -> None:
        """Loads all stored thread checkpoints from disk into memory."""
        if os.path.exists(self.file_path):
            with self._lock:
                try:
                    with open(self.file_path, "rb") as f:
                        s, w, b = pickle.load(f)
                    for thread_id, namespaces in s.items():
                        for ns, checkpoints in namespaces.items():
                            self.storage[thread_id][ns].update(checkpoints)
                    self.writes.update(w)
                    self.blobs.update(b)
                except Exception as exc:
                    print(f"[PersistentMemorySaver] Warning: could not restore checkpoints from {self.file_path}: {exc}")

    def _sync(self) -> None:
        """Atomically persists in-memory dictionaries to disk."""
        with self._lock:
            try:
                # Convert lambdas from defaultdict to standard dicts for pickling
                s = {tid: {ns: dict(ckpts) for ns, ckpts in ns_dict.items()} for tid, ns_dict in self.storage.items()}
                w = dict(self.writes)
                b = dict(self.blobs)

                tmp_path = f"{self.file_path}.tmp"
                os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)
                with open(tmp_path, "wb") as f:
                    pickle.dump((s, w, b), f)
                os.replace(tmp_path, self.file_path)
            except Exception as exc:
                print(f"[PersistentMemorySaver] Warning: checkpoint sync failed: {exc}")

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        res = super().put(config, checkpoint, metadata, new_versions)
        self._sync()
        return res

    def put_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        super().put_writes(config, writes, task_id, task_path)
        self._sync()

    def delete_thread(self, thread_id: str) -> None:
        super().delete_thread(thread_id)
        self._sync()
