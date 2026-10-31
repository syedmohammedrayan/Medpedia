import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Mail, Check, AlertCircle, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface EmailModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  threadId?: string;
  evidenceReport?: string;
  query?: string;
}

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");

const EmailModal = ({ open, onOpenChange, threadId, evidenceReport, query }: EmailModalProps) => {
  const [email, setEmail] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);
  const { toast } = useToast();

  const handleSend = async () => {
    setError(null);
    const cleanedEmail = email.trim();
    const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9]+([.-][a-zA-Z0-9]+)*\.[a-zA-Z]{2,}$/;

    if (!cleanedEmail || !emailRegex.test(cleanedEmail)) {
      toast({
        title: "Invalid address",
        description: "Please specify a valid clinician or institutional email address.",
        variant: "destructive",
      });
      return;
    }

    setIsSending(true);
    setStatusMessage("Compiling research synthesis & PDF dossier…");

    try {
      // 1. Progress to dispatch phase
      setTimeout(() => {
        setStatusMessage("Dispatching binary PDF attachment via HTTPS…");
      }, 900);

      const activeThreadId = threadId || "default-user";
      const response = await fetch(`${API_BASE}/research/dispatch-email`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: cleanedEmail,
          thread_id: activeThreadId,
          evidence_report: evidenceReport || "",
          query: query || "",
        }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok || !data.success) {
        const errorMsg = data.error || data.detail || `Server error (${response.status}): Failed to dispatch email.`;
        setError(errorMsg);
        setIsSending(false);
        setStatusMessage("");
        toast({
          title: "Dispatch Failed",
          description: errorMsg,
          variant: "destructive",
        });
        return;
      }

      // Real success confirmed by backend
      setIsSending(false);
      setSent(true);
      toast({
        title: "Report Dispatched",
        description: `Comprehensive evidence dossier successfully delivered to ${cleanedEmail}`,
      });

      setTimeout(() => {
        onOpenChange(false);
        setSent(false);
        setEmail("");
        setError(null);
        setStatusMessage("");
      }, 2500);

    } catch (err: any) {
      setIsSending(false);
      setStatusMessage("");
      const networkError = err.message || "Failed to connect to the Medpedia research dispatch server.";
      setError(networkError);
      toast({
        title: "Connection Error",
        description: networkError,
        variant: "destructive",
      });
    }
  };

  const handleDialogChange = (isOpen: boolean) => {
    if (!isSending) {
      setError(null);
      setStatusMessage("");
      onOpenChange(isOpen);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleDialogChange}>
      <DialogContent className="sm:max-w-md bg-[#FAF8F5] border border-[#DDE3E8] p-6 rounded-2xl shadow-xl">
        <DialogHeader className="space-y-2 border-b border-[#DDE3E8] pb-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#3A0F34] flex items-center justify-center">
              <Mail className="w-4 h-4 text-[#EAAA00]" />
            </div>
            <div>
              <DialogTitle className="text-base font-bold text-[#211B20] font-heading">
                Dispatch Evidence Dossier
              </DialogTitle>
              <DialogDescription className="text-xs text-[#6B5F69]">
                Receive the formatted PDF evidence synthesis and complete literature citations.
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <AnimatePresence mode="wait">
          {!sent ? (
            <motion.div
              key="form"
              initial={{ opacity: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="space-y-4 py-3"
            >
              <div className="space-y-2">
                <Label htmlFor="email" className="text-xs font-mono uppercase tracking-wider text-[#3A0F34] font-bold">
                  Recipient Institutional Address
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="clinician@hospital.edu"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (error) setError(null);
                  }}
                  disabled={isSending}
                  className="bg-white border-[#DDE3E8] text-[#211B20] text-sm focus-visible:ring-[#3A0F34] focus-visible:border-[#3A0F34]"
                />
              </div>

              {/* Real Status Progression */}
              {isSending && (
                <div className="flex items-center gap-2.5 p-3 rounded-xl bg-white border border-[#DDE3E8] text-xs text-[#3A0F34]">
                  <Loader2 className="w-4 h-4 animate-spin text-[#EAAA00] flex-shrink-0" />
                  <span className="font-medium">{statusMessage}</span>
                </div>
              )}

              {/* Real Error Feedback */}
              {error && (
                <div className="flex items-start gap-2.5 p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-800">
                  <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <strong className="block font-semibold">Delivery Unsuccessful</strong>
                    <span>{error}</span>
                  </div>
                </div>
              )}

              <div className="p-3 rounded-xl bg-[#FAF8F5] border border-[#DDE3E8] text-[11px] text-[#6B5F69] space-y-1">
                <div className="font-semibold text-[#3A0F34]">Included in Attachment:</div>
                <div>&bull; Systematic Evidence Summary & PICO Analysis</div>
                <div>&bull; Complete Source Records with Verified PubMed / PMC URLs</div>
                <div>&bull; Publication Document: <code>Medpedia_Comprehensive_Evidence_Report.pdf</code></div>
              </div>

              <div className="pt-2">
                <button
                  onClick={handleSend}
                  disabled={isSending || !email.trim()}
                  className="btn-editorial-primary w-full py-2.5 rounded-xl text-xs font-heading font-semibold uppercase tracking-wider flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                >
                  {isSending ? (
                    <span>Processing Transmit…</span>
                  ) : (
                    <>
                      <span>Transmit Dossier</span>
                      <Mail className="w-3.5 h-3.5 text-[#EAAA00]" />
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="success"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center justify-center py-6 space-y-3"
            >
              <div className="w-12 h-12 bg-[#3A0F34] rounded-full flex items-center justify-center shadow-md">
                <Check className="w-6 h-6 text-[#EAAA00]" />
              </div>
              <p className="text-sm font-bold text-[#211B20] font-heading">
                Evidence Dossier Dispatched
              </p>
              <p className="text-xs text-[#6B5F69] text-center max-w-xs leading-relaxed">
                The complete research report PDF has been delivered to <strong>{email}</strong>.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </DialogContent>
    </Dialog>
  );
};

export default EmailModal;
