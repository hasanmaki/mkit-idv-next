import { Plus, RefreshCw, Search } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import {
  OtpField,
  ReasonField,
  TransactionFilterFields,
  TransactionStartFields,
  type OtpForm,
  type ReasonForm,
  type TransactionStartForm,
} from "../components/TransactionForms";
import { TransactionsTable } from "../components/TransactionsTable";
import { useTransactions } from "../hooks/useTransactions";
import type { Transaction } from "../types";

const defaultStartForm: TransactionStartForm = {
  binding_id: "",
  product_id: "650",
  email: "",
  limit_harga: "100000",
  otp_required: false,
};

const defaultOtpForm: OtpForm = { otp: "" };
const defaultReasonForm: ReasonForm = { reason: "" };

export function TransactionsPage() {
  const vm = useTransactions();

  const [isStartOpen, setIsStartOpen] = useState(false);
  const [startForm, setStartForm] = useState(defaultStartForm);

  const [otpTarget, setOtpTarget] = useState<Transaction | null>(null);
  const [otpForm, setOtpForm] = useState(defaultOtpForm);

  const [pauseTarget, setPauseTarget] = useState<Transaction | null>(null);
  const [pauseForm, setPauseForm] = useState(defaultReasonForm);

  const [stopTarget, setStopTarget] = useState<Transaction | null>(null);
  const [stopForm, setStopForm] = useState(defaultReasonForm);

  async function onStart(): Promise<void> {
    await vm.startTransaction({
      binding_id: Number(startForm.binding_id),
      product_id: startForm.product_id,
      email: startForm.email,
      limit_harga: Number(startForm.limit_harga),
      otp_required: startForm.otp_required,
    });
    setStartForm(defaultStartForm);
    setIsStartOpen(false);
  }

  function openOtp(transaction: Transaction): void {
    setOtpTarget(transaction);
    setOtpForm(defaultOtpForm);
  }

  async function submitOtp(): Promise<void> {
    if (!otpTarget) {
      return;
    }
    await vm.submitOtp(otpTarget.id, otpForm.otp);
    setOtpTarget(null);
  }

  function openPause(transaction: Transaction): void {
    setPauseTarget(transaction);
    setPauseForm(defaultReasonForm);
  }

  async function submitPause(): Promise<void> {
    if (!pauseTarget) {
      return;
    }
    await vm.pauseTransaction(pauseTarget.id, pauseForm.reason || "manual_pause");
    setPauseTarget(null);
  }

  function openStop(transaction: Transaction): void {
    setStopTarget(transaction);
    setStopForm(defaultReasonForm);
  }

  async function submitStop(): Promise<void> {
    if (!stopTarget) {
      return;
    }
    await vm.stopTransaction(stopTarget.id, stopForm.reason || "manual_stop");
    setStopTarget(null);
  }

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Transactions</h1>
        <p className="text-sm text-muted-foreground">
          Start dan kontrol transaksi (continue/otp/pause/resume/stop/check).
        </p>
      </header>

      {vm.errorMessage ? (
        <Card className="border-destructive/40 bg-destructive/10">
          <CardContent className="py-3 text-sm text-destructive">{vm.errorMessage}</CardContent>
        </Card>
      ) : null}

      <section className="grid gap-3 sm:grid-cols-3">
        <Card>
          <CardHeader className="pb-2"><CardDescription>Total</CardDescription></CardHeader>
          <CardContent><p className="text-3xl font-semibold tracking-tight">{vm.transactions.length}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardDescription>Processing</CardDescription></CardHeader>
          <CardContent><p className="text-3xl font-semibold tracking-tight">{vm.processingCount}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardDescription>Sukses</CardDescription></CardHeader>
          <CardContent><p className="text-3xl font-semibold tracking-tight">{vm.successCount}</p></CardContent>
        </Card>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Filter</CardTitle>
          <CardDescription>Filter list transaksi sesuai binding/server/status.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <TransactionFilterFields filters={vm.filters} onChange={vm.setFilters} />
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={() => void vm.applyFilters()}>
              <Search className="mr-2 h-4 w-4" /> Apply
            </Button>
            <Button variant="outline" onClick={() => void vm.resetFilters()}>
              Reset
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <CardTitle>Transaction List</CardTitle>
              <CardDescription>Action ada di menu dropdown tiap row.</CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="secondary" onClick={() => void vm.loadTransactions()}>
                <RefreshCw className="mr-2 h-4 w-4" /> Refresh
              </Button>
              <Button onClick={() => setIsStartOpen(true)}>
                <Plus className="mr-2 h-4 w-4" /> Start
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <TransactionsTable
            transactions={vm.transactions}
            isLoading={vm.isLoading}
            pendingRowActions={vm.pendingRowActions}
            onOpenOtp={openOtp}
            onOpenPause={openPause}
            onOpenStop={openStop}
            onContinue={(id) => void vm.continueTransaction(id)}
            onResume={(id) => void vm.resumeTransaction(id)}
            onCheck={(id) => void vm.checkTransaction(id)}
            onDelete={(id) => void vm.deleteTransaction(id)}
          />
        </CardContent>
      </Card>

      <Dialog open={isStartOpen} onOpenChange={setIsStartOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Start Transaction</DialogTitle>
            <DialogDescription>
              Trigger orchestration start untuk 1 binding.
            </DialogDescription>
          </DialogHeader>
          <TransactionStartFields form={startForm} onChange={setStartForm} />
          <DialogFooter>
            <Button variant="secondary" onClick={() => setIsStartOpen(false)}>Cancel</Button>
            <Button onClick={() => void onStart()} disabled={vm.isSubmitting}>Start</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={Boolean(otpTarget)} onOpenChange={(open) => !open && setOtpTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Submit OTP</DialogTitle>
            <DialogDescription>Transaction #{otpTarget?.id}</DialogDescription>
          </DialogHeader>
          <OtpField form={otpForm} onChange={setOtpForm} />
          <DialogFooter>
            <Button variant="secondary" onClick={() => setOtpTarget(null)}>Cancel</Button>
            <Button onClick={() => void submitOtp()}>Submit</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog
        open={Boolean(pauseTarget)}
        onOpenChange={(open) => !open && setPauseTarget(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Pause Transaction</DialogTitle>
            <DialogDescription>Transaction #{pauseTarget?.id}</DialogDescription>
          </DialogHeader>
          <ReasonField form={pauseForm} onChange={setPauseForm} label="Reason" />
          <DialogFooter>
            <Button variant="secondary" onClick={() => setPauseTarget(null)}>Cancel</Button>
            <Button onClick={() => void submitPause()}>Pause</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog
        open={Boolean(stopTarget)}
        onOpenChange={(open) => !open && setStopTarget(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Stop Transaction</DialogTitle>
            <DialogDescription>Transaction #{stopTarget?.id}</DialogDescription>
          </DialogHeader>
          <ReasonField form={stopForm} onChange={setStopForm} label="Reason" />
          <DialogFooter>
            <Button variant="secondary" onClick={() => setStopTarget(null)}>Cancel</Button>
            <Button onClick={() => void submitStop()}>Stop</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </section>
  );
}
