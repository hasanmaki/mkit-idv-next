import { Plus, RefreshCw, Users, Link2 } from "lucide-react";
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
import { ErrorDialog } from "@/components/error/ErrorDialog";

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
        <div className="flex items-center gap-2">
          <Link2 className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold tracking-tight">Binding Management</h1>
        </div>
        <p className="text-sm text-muted-foreground">
          Hubungkan akun MSISDN ke instance server untuk menjalankan transaksi IDV.
        </p>
      </header>

      <section className="grid gap-3 sm:grid-cols-3">
        <StatCard title="Total Bindings" value={vm.bindings.length.toString()} />
        <StatCard
          title="Sesi Aktif"
          value={vm.bindings.filter((b) => b.is_active).length.toString()}
        />
        <StatCard
          title="Terverifikasi"
          value={vm.bindings.filter((b) => b.step === "VERIFIED" || b.step === "COMPLETED").length.toString()}
        />
      </section>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Daftar Bindings</CardTitle>
              <CardDescription>
                Kelola status alur kerja OTP, pengecekan saldo, dan sesi server.
              </CardDescription>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button variant="secondary" onClick={() => void vm.loadBindings()}>
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
                    <DialogTitle>Bulk Bind Akun</DialogTitle>
                    <DialogDescription>
                      Hubungkan banyak akun ke satu server sekaligus.
                    </DialogDescription>
                  </DialogHeader>
                  <BulkBindFormFields
                    form={vm.bulkBindForm}
                    onChange={vm.setBulkBindForm}
                  />
                  <DialogFooter>
                    <Button onClick={() => void vm.bulkBindAccounts()} disabled={vm.isSubmitting}>
                      Jalankan Bulk Bind
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>

              <Dialog open={vm.isBindDialogOpen} onOpenChange={vm.setIsBindDialogOpen}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="mr-2 h-4 w-4" /> New Binding
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-lg">
                  <DialogHeader>
                    <DialogTitle>Tambah Binding Baru</DialogTitle>
                    <DialogDescription>
                      Pilih session, akun, dan server untuk dihubungkan.
                    </DialogDescription>
                  </DialogHeader>
                  <BindAccountFormFields
                    form={vm.bindForm}
                    onChange={vm.setBindForm}
                    orders={vm.orders}
                    servers={vm.servers}
                    accounts={vm.accounts}
                    isLoadingOptions={vm.isLoadingOptions}
                    onOrderChange={vm.handleOrderChange}
                  />
                  <DialogFooter>
                    <Button onClick={() => void vm.bindAccount()} disabled={vm.isSubmitting}>
                      Simpan Binding
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
              {otpMode === "request" ? "Minta Kode OTP" : "Verifikasi OTP"}
            </DialogTitle>
            <DialogDescription>
              {otpMode === "request"
                ? "Masukkan PIN untuk memicu pengiriman SMS OTP dari provider."
                : "Masukkan kode OTP yang diterima melalui SMS."}
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
              Batal
            </Button>
            <Button
              onClick={() => {
                if (otpMode === "request" && activeBinding) {
                  void vm.requestOTP(activeBinding.id, pin);
                } else if (activeBinding) {
                  void vm.verifyOTP(activeBinding.id, otp);
                }
              }}
              disabled={vm.isSubmitting || (otpMode === "request" && !pin) || (otpMode === "verify" && !otp)}
            >
              {otpMode === "request" ? "Kirim Request" : "Verifikasi Sekarang"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Balance Dialog */}
      <Dialog open={vm.isBalanceDialogOpen} onOpenChange={vm.setIsBalanceDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Update Saldo Awal</DialogTitle>
            <DialogDescription>
              Tentukan saldo awal untuk binding ini secara manual.
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
              Batal
            </Button>
            <Button
              onClick={() => {
                if (activeBinding) {
                  void vm.setBalanceStart(activeBinding.id, balance, balanceSource);
                }
              }}
              disabled={vm.isSubmitting}
            >
              Simpan Saldo
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Release Confirm Dialog */}
      <AlertDialog open={vm.isReleaseConfirmOpen} onOpenChange={vm.setIsReleaseConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Release Sesi Binding?</AlertDialogTitle>
            <AlertDialogDescription>
              Aksi ini akan mengeluarkan akun dari sesi aktif server. Akun akan tersedia kembali untuk sesi lain.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={vm.isSubmitting}>Batal</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (vm.pendingReleaseBindingId) {
                  void vm.releaseBinding(vm.pendingReleaseBindingId);
                }
              }}
              disabled={vm.isSubmitting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Release Sesi
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <ErrorDialog
        error={vm.error}
        open={vm.isDialogOpen}
        onOpenChange={vm.closeDialog}
        title="Gagal Memproses Binding"
      />
    </section>
  );
}
