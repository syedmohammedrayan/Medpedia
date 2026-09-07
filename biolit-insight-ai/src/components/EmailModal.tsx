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
import { Button } from "@/components/ui/button";
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
        title: "Invalid email",
        description: "Please enter a valid email address",
        variant: "destructive",
      });
      return;
    }

    setIsSending(true);
    
    // Simulate sending
    setTimeout(() => {
      setIsSending(false);
      setSent(true);
      
      setTimeout(() => {
        toast({
          title: "Report sent! 🎉",
          description: `Evidence report delivered to ${email}`,
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
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Mail className="w-5 h-5 text-primary" />
            Email Report
          </DialogTitle>
          <DialogDescription>
            Receive a professionally formatted PDF report with the complete evidence synthesis
          </DialogDescription>
        </DialogHeader>

        <AnimatePresence mode="wait">
          {!sent ? (
            <motion.div
              key="form"
              initial={{ opacity: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="space-y-4 py-4"
            >
              <div className="space-y-2">
                <Label htmlFor="email">Email address</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="researcher@university.edu"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isSending}
                />
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="excel"
                  checked={includeExcel}
                  onCheckedChange={(checked) => setIncludeExcel(checked as boolean)}
                  disabled={isSending}
                />
                <Label
                  htmlFor="excel"
                  className="text-sm font-normal cursor-pointer"
                >
                  Include full evidence matrix as Excel attachment
                </Label>
              </div>

              <Button
                onClick={handleSend}
                disabled={isSending}
                className="w-full"
              >
                {isSending ? "Sending..." : "Send Report"}
              </Button>
            </motion.div>
          ) : (
            <motion.div
              key="success"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center justify-center py-8"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", duration: 0.6 }}
                className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center mb-4"
              >
                <Check className="w-8 h-8 text-white" />
              </motion.div>
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="text-lg font-semibold text-center"
              >
                Report sent successfully!
              </motion.p>
            </motion.div>
          )}
        </AnimatePresence>
      </DialogContent>
    </Dialog>
  );
};

export default EmailModal;

