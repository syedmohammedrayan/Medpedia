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
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Mail, Check } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface EmailModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const EmailModal = ({ open, onOpenChange }: EmailModalProps) => {
  const [email, setEmail] = useState("");
  const [includeExcel, setIncludeExcel] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [sent, setSent] = useState(false);
  const { toast } = useToast();

  const handleSend = async () => {
    if (!email || !email.includes("@")) {
      toast({
        title: "Invalid address",
        description: "Please specify a valid institutional or personal email address.",
        variant: "destructive",
      });
      return;
    }

    setIsSending(true);
    
    // Simulate dispatch
    setTimeout(() => {
      setIsSending(false);
      setSent(true);
      
      setTimeout(() => {
        toast({
          title: "Report Dispatched",
          description: `Comprehensive evidence report delivered to ${email}`,
        });
        setTimeout(() => {
          onOpenChange(false);
          setSent(false);
          setEmail("");
        }, 1500);
      }, 1000);
    }, 1500);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
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
                Receive a formatted PDF evidence synthesis and extraction matrix.
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
                  Recipient Address
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="clinician@hospital.edu"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isSending}
                  className="bg-white border-[#DDE3E8] text-[#211B20] text-sm focus-visible:ring-[#3A0F34] focus-visible:border-[#3A0F34]"
                />
              </div>

              <div className="flex items-start space-x-2.5 pt-1">
                <Checkbox
                  id="excel"
                  checked={includeExcel}
                  onCheckedChange={(checked) => setIncludeExcel(checked as boolean)}
                  disabled={isSending}
                  className="border-[#DDE3E8] data-[state=checked]:bg-[#3A0F34] data-[state=checked]:border-[#3A0F34]"
                />
                <Label
                  htmlFor="excel"
                  className="text-xs text-[#6B5F69] font-normal leading-tight cursor-pointer"
                >
                  Attach complete PICO evidence extraction matrix as spreadsheet (.xlsx)
                </Label>
              </div>

              <div className="pt-2">
                <button
                  onClick={handleSend}
                  disabled={isSending}
                  className="btn-editorial-primary w-full py-2.5 rounded-xl text-xs font-heading font-semibold uppercase tracking-wider flex items-center justify-center gap-2"
                >
                  {isSending ? (
                    <span>Compiling Report…</span>
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
              <div className="w-12 h-12 bg-[#3A0F34] rounded-full flex items-center justify-center">
                <Check className="w-6 h-6 text-[#EAAA00]" />
              </div>
              <p className="text-sm font-bold text-[#211B20] font-heading">
                Dossier Dispatched Successfully
              </p>
              <p className="text-xs text-[#6B5F69] text-center max-w-xs">
                Check your inbox for the compiled literature synthesis and evidence table.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </DialogContent>
    </Dialog>
  );
};

export default EmailModal;
