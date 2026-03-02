import { Plus, RefreshCw, Users } from "lucide-react";
import { useState } from "react";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
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
  DialogTrigger,
} from "@/components/ui/dialog";

import {
  BalanceDialogFields,
  BindAccountFormFields,
  BulkBindFormFields,
  OTPDialogFields,
} from "../components/BindingForms";
import { BindingsTable } from "../components/BindingsTable";
import { useBindings } from "../hooks/useBindings";

function StatCard({ title, value }: { title: string; value: string }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{title}</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-3xl font-semibold tracking-tight">{value}</p>
      </CardContent>
    </Card>
  );
}

export function BindingsPage() {
  const vm = useBindings();

  const activeBinding = vm.activeBindingId
    ? vm.bindings.find((b) => b.id === vm.activeBindingId) || null
    : null;

  const [pin, setPin] = useState("");
  const [otp, setOtp] = useState("");
  const [balance, setBalance] = useState(0);
  const [balanceSource, setBalanceSource] = useState<"MANUAL" | "AUTO_CHECK">("MANUAL");
  const [otpMode, setOtpMode] = useState<"request" | "verify">("request");

  function handleOpenOTP(bindingId: number, mode: "request" | "verify") {
    setOtpMode(mode);
    setPin("");
    setOtp("");
    vm.openOTPDialog(bindingId);
  }

  function handleOpenBalance(bindingId: number) {
    const binding = vm.bindings.find((b) => b.id === bindingId);
    setBalance(binding?.balance_start ?? 0);
    setBalanceSource((binding?.balance_source as "MANUAL" | "AUTO_CHECK") ?? "MANUAL");
    vm.openBalanceDialog(bindingId);
  }

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Bindings Management</h1>
        <p className="text-sm text-muted-foreground">
          Bind accounts to servers for sessions. Manage OTP workflow and balance tracking.
        </p>
      </header>

      {vm.errorMessage ? (
        <Card className="border-destructive/40 bg-destructive/10">
          <CardContent className="py-3 text-sm text-destructive">{vm.errorMessage}</CardContent>
        </Card>
      ) : null}

      <section className="grid gap-3 sm:grid-cols-3">
        <StatCard title="Total Bindings" value={vm.bindings.length.toString()} />
        <StatCard
          title="Active"
          value={vm.bindings.filter((b) => b.is_active).length.toString()}
        />
        <StatCard
          title="Verified"
          value={vm.bindings.filter((b) => b.step === "VERIFIED").length.toString()}
        />
      </section>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Bindings</CardTitle>
              <CardDescription>
                Manage account bindings with workflow tracking.
              </CardDescription>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button variant="secondary" onClick={() => vm.loadBindings()}>
                <RefreshCw className="mr-2 h-4 w-4" /> Refresh
              </Button>

              <Dialog open={vm.isBulkBindDialogOpen} onOpenChange={vm.setIsBulkBindDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline">
                    <Users className="mr-2 h-4 w-4" /> Bulk Bind
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-lg">
                  <DialogHeader>
                    <DialogTitle>Bulk Bind Accounts</DialogTitle>
                    <DialogDescription>
                      Bind multiple accounts to a server at once.
                    </DialogDescription>
                  </DialogHeader>
                  <BulkBindFormFields
                    form={vm.bulkBindForm}
                    onChange={vm.setBulkBindForm}
                  />
                  <DialogFooter>
                    <Button onClick={() => vm.bulkBindAccounts()} disabled={vm.isSubmitting}>
                      Bind All
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>

              <Dialog open={vm.isBindDialogOpen} onOpenChange={vm.setIsBindDialogOpen}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="mr-2 h-4 w-4" /> Bind Account
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-lg">
                  <DialogHeader>
                    <DialogTitle>Bind Account to Server</DialogTitle>
                    <DialogDescription>
                      Create a new binding between session, account, and server.
                    </DialogDescription>
                  </DialogHeader>
                  <BindAccountFormFields
                    form={vm.bindForm}
                    onChange={vm.setBindForm}
                  />
                  <DialogFooter>
                    <Button onClick={() => vm.bindAccount()} disabled={vm.isSubmitting}>
                      Bind
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <BindingsTable
            bindings={vm.bindings}
            isLoadingBindings={vm.isLoadingBindings}
            pendingRowActions={vm.pendingRowActions}
            onRequestOTP={(id) => handleOpenOTP(id, "request")}
            onVerifyOTP={(id) => handleOpenOTP(id, "verify")}
            onMarkVerified={vm.markVerified}
            onSetBalance={(id) => handleOpenBalance(id)}
            onRelease={vm.openReleaseConfirm}
          />
        </CardContent>
      </Card>

      {/* OTP Dialog */}
      <Dialog open={vm.isOTPDialogOpen} onOpenChange={vm.setIsOTPDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>
              {otpMode === "request" ? "Request OTP" : "Verify OTP"}
            </DialogTitle>
            <DialogDescription>
              {otpMode === "request"
                ? "Request OTP for the binding."
                : "Enter the OTP code to verify."}
            </DialogDescription>
          </DialogHeader>
          <OTPDialogFields
            binding={activeBinding}
            mode={otpMode}
            pin={pin}
            otp={otp}
            onPinChange={setPin}
            onOTPChange={setOtp}
          />
          <DialogFooter>
            <Button variant="secondary" onClick={() => vm.setIsOTPDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={() => {
                if (otpMode === "request" && activeBinding) {
                  vm.requestOTP(activeBinding.id, pin);
                } else if (activeBinding) {
                  vm.verifyOTP(activeBinding.id, otp);
                }
              }}
              disabled={vm.isSubmitting || (otpMode === "request" && !pin) || (otpMode === "verify" && !otp)}
            >
              {otpMode === "request" ? "Request OTP" : "Verify OTP"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Balance Dialog */}
      <Dialog open={vm.isBalanceDialogOpen} onOpenChange={vm.setIsBalanceDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Set Balance Start</DialogTitle>
            <DialogDescription>
              Set the starting balance for this binding.
            </DialogDescription>
          </DialogHeader>
          <BalanceDialogFields
            binding={activeBinding}
            balance={balance}
            source={balanceSource}
            onBalanceChange={setBalance}
            onSourceChange={setBalanceSource}
          />
          <DialogFooter>
            <Button variant="secondary" onClick={() => vm.setIsBalanceDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={() => {
                if (activeBinding) {
                  vm.setBalanceStart(activeBinding.id, balance, balanceSource);
                }
              }}
              disabled={vm.isSubmitting}
            >
              Save Balance
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Release Confirm Dialog */}
      <AlertDialog open={vm.isReleaseConfirmOpen} onOpenChange={vm.setIsReleaseConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Release binding?</AlertDialogTitle>
            <AlertDialogDescription>
              This will logout the binding and free the account for other sessions.
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={vm.isSubmitting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (vm.pendingReleaseBindingId) {
                  vm.releaseBinding(vm.pendingReleaseBindingId);
                }
              }}
              disabled={vm.isSubmitting}
            >
              Release
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </section>
  );
}
