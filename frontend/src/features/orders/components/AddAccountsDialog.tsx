import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { apiRequest } from "@/lib/api";

type AddAccountsDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  orderId: number | null;
  onSuccess: () => void;
};

// Shared utility to parse MSISDNs (comma or newline separated)
function parseMsisdns(input: string): string[] {
  return input
    .split(/[\n,]+/)  // Split by newline OR comma
    .map(s => s.trim())
    .filter(s => s.length > 0);
}

export function AddAccountsDialog({
  open,
  onOpenChange,
  orderId,
  onSuccess,
}: AddAccountsDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [form, setForm] = useState({
    msisdns: "",
    email: "",
    pin: "",
  });

  const handleSubmit = async () => {
    if (!orderId) return;

    const msisdnList = parseMsisdns(form.msisdns);
    
    if (msisdnList.length === 0) {
      toast.error("Please enter at least one MSISDN");
      return;
    }

    try {
      setIsSubmitting(true);

      // Create accounts in parallel
      const promises = msisdnList.map((msisdn) =>
        apiRequest("/v1/accounts", "POST", {
          order_id: orderId,
          msisdn: msisdn.trim(),
          email: form.email.trim(),
          pin: form.pin || undefined,
        })
      );

      const results = await Promise.allSettled(promises);
      const successCount = results.filter(r => r.status === 'fulfilled').length;
      const failCount = results.filter(r => r.status === 'rejected').length;

      setForm({ msisdns: "", email: "", pin: "" });
      onOpenChange(false);
      onSuccess();

      if (failCount === 0) {
        toast.success(`${successCount} account(s) berhasil ditambahkan.`);
      } else {
        toast.success(`${successCount} account(s) added, ${failCount} failed`);
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Gagal menambahkan accounts.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Add Accounts to Order</DialogTitle>
          <DialogDescription>
            Add one or more phone numbers (MSISDNs) to this order.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="msisdns">MSISDNs (Phone Numbers)</Label>
            <Textarea
              id="msisdns"
              value={form.msisdns}
              onChange={(e) => setForm((prev) => ({ ...prev, msisdns: e.target.value }))}
              placeholder="081234567890, 081234567891&#10;081234567892&#10;081234567893"
              rows={6}
            />
            <p className="text-xs text-muted-foreground">
              Separate with commas or newlines. Example: "081234567890, 081234567891"
            </p>
          </div>

          <div className="grid gap-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={form.email}
              onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))}
              placeholder="customer@example.com"
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="pin">PIN (optional)</Label>
            <Input
              id="pin"
              type="text"
              value={form.pin}
              onChange={(e) => setForm((prev) => ({ ...prev, pin: e.target.value }))}
              placeholder="1234"
              maxLength={10}
            />
            <p className="text-xs text-muted-foreground">Leave empty to use order's default PIN</p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting}>
            Add {parseMsisdns(form.msisdns).length > 0 ? `(${parseMsisdns(form.msisdns).length})` : ''} Accounts
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
