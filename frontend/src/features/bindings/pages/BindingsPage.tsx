import { Plus, RefreshCw, Search, Upload } from "lucide-react";
import { useMemo, useState } from "react";

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
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";

import {
  BindingCreateFields,
  BindingFilterFields,
  BindingLogoutFields,
  BindingRequestLoginFields,
  BindingVerifyFields,
  type BindingCreateForm,
  type LogoutForm,
  type RequestLoginForm,
  type VerifyForm,
} from "../components/BindingForms";
import { BindingsTable } from "../components/BindingsTable";
import { useBindings } from "../hooks/useBindings";
import type { Binding, BindingBulkItemInput } from "../types";

const defaultCreateForm: BindingCreateForm = {
  server_id: "",
  account_id: "",
  balance_start: "",
};

const defaultVerifyForm: VerifyForm = {
  otp: "",
};

const defaultRequestLoginForm: RequestLoginForm = {
  pin: "",
};

const defaultLogoutForm: LogoutForm = {
  account_status: "exhausted",
  last_error_code: "",
  last_error_message: "",
};

export function BindingsPage() {
  const vm = useBindings();
  const totalBalanceLast = useMemo(
    () =>
      vm.bindings.reduce(
        (acc, item) => acc + (typeof item.balance_last === "number" ? item.balance_last : 0),
        0,
      ),
    [vm.bindings],
  );
  const totalBalanceStart = useMemo(
    () =>
      vm.bindings.reduce(
        (acc, item) => acc + (typeof item.balance_start === "number" ? item.balance_start : 0),
        0,
      ),
    [vm.bindings],
  );

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [createForm, setCreateForm] = useState(defaultCreateForm);

  const [isVerifyOpen, setIsVerifyOpen] = useState(false);
  const [verifyForm, setVerifyForm] = useState(defaultVerifyForm);
  const [verifyTarget, setVerifyTarget] = useState<Binding | null>(null);

  const [isRequestLoginOpen, setIsRequestLoginOpen] = useState(false);
  const [requestLoginForm, setRequestLoginForm] = useState(defaultRequestLoginForm);
  const [requestLoginTarget, setRequestLoginTarget] = useState<Binding | null>(null);

  const [isLogoutOpen, setIsLogoutOpen] = useState(false);
  const [logoutForm, setLogoutForm] = useState(defaultLogoutForm);
  const [logoutTarget, setLogoutTarget] = useState<Binding | null>(null);
  const [isBulkOpen, setIsBulkOpen] = useState(false);
  const [bulkMode, setBulkMode] = useState<"port_msisdn" | "server_account">(
    "port_msisdn",
  );
  const [bulkRawText, setBulkRawText] = useState("");
  const [bulkStopOnFirstError, setBulkStopOnFirstError] = useState(false);
  const [bulkPin, setBulkPin] = useState("");
  const [otpQueue, setOtpQueue] = useState<Record<number, string>>({});

  async function onCreateBinding(): Promise<void> {
    if (!createForm.server_id || !createForm.account_id) {
      return;
    }
    await vm.createBinding({
      server_id: Number(createForm.server_id),
      account_id: Number(createForm.account_id),
      balance_start: createForm.balance_start.trim()
        ? Number(createForm.balance_start)
        : null,
    });
    setCreateForm(defaultCreateForm);
    setIsCreateOpen(false);
  }

  function openVerify(binding: Binding): void {
    setVerifyTarget(binding);
    setVerifyForm(defaultVerifyForm);
    setIsVerifyOpen(true);
  }

  function openRequestLogin(binding: Binding): void {
    setRequestLoginTarget(binding);
    setRequestLoginForm(defaultRequestLoginForm);
    setIsRequestLoginOpen(true);
  }

  async function onRequestLogin(): Promise<void> {
    if (!requestLoginTarget) {
      return;
    }
    await vm.requestBindingLogin(requestLoginTarget.id, {
      pin: requestLoginForm.pin.trim() || null,
    });
    setIsRequestLoginOpen(false);
    setRequestLoginTarget(null);
  }

  async function onVerifyBinding(): Promise<void> {
    if (!verifyTarget) {
      return;
    }
    await vm.verifyBinding(verifyTarget.id, {
      otp: verifyForm.otp,
    });
    setIsVerifyOpen(false);
    setVerifyTarget(null);
  }

  function openLogout(binding: Binding): void {
    setLogoutTarget(binding);
    setLogoutForm(defaultLogoutForm);
    setIsLogoutOpen(true);
  }

  async function onLogoutBinding(): Promise<void> {
    if (!logoutTarget) {
      return;
    }
    await vm.logoutBinding(logoutTarget.id, {
      account_status: logoutForm.account_status,
      last_error_code: logoutForm.last_error_code.trim() || null,
      last_error_message: logoutForm.last_error_message.trim() || null,
    });
    setIsLogoutOpen(false);
    setLogoutTarget(null);
  }

  function parseBulkLines(): BindingBulkItemInput[] {
    const lines = bulkRawText
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter((line) => line.length > 0);
    const items: BindingBulkItemInput[] = [];
    for (const line of lines) {
      const parts = line
        .split(/[,\t;]/)
        .map((part) => part.trim())
        .filter((part) => part.length > 0);
      if (bulkMode === "port_msisdn") {
        items.push({
          port: Number(parts[0]),
          msisdn: parts[1],
          batch_id: parts[2] || undefined,
        });
      } else {
        items.push({
          server_id: Number(parts[0]),
          account_id: Number(parts[1]),
        });
      }
    }
    return items;
  }

  async function onBulkDryRun(): Promise<void> {
    await vm.dryRunBulkBindings({
      items: parseBulkLines(),
      stop_on_first_error: bulkStopOnFirstError,
    });
  }

  async function onBulkCreate(): Promise<void> {
    await vm.createBulkBindings({
      items: parseBulkLines(),
      stop_on_first_error: bulkStopOnFirstError,
    });
  }

  async function onBulkRequestLogin(): Promise<void> {
    await vm.bulkRequestLogin(bulkPin.trim() || null);
  }

  async function onBulkCheckBalance(): Promise<void> {
    await vm.bulkCheckBalance();
  }

  async function onBulkRefreshToken(): Promise<void> {
    await vm.bulkRefreshTokenLocation();
  }

  async function onBulkLogout(): Promise<void> {
    await vm.bulkLogout({
      account_status: "exhausted",
      last_error_code: "bulk_logout",
      last_error_message: "Bulk logout",
    });
  }

  async function onBulkDelete(): Promise<void> {
    await vm.bulkDelete();
  }

  async function onBulkVerifyReseller(): Promise<void> {
    await vm.bulkVerifyReseller();
  }

  function buildOtpQueueBindings(): Binding[] {
    return vm.bindings.filter(
      (binding) =>
        vm.selectedBindingIds.includes(binding.id) && binding.step === "otp_requested",
    );
  }

  async function submitOtpQueue(): Promise<void> {
    const queue = buildOtpQueueBindings();
    for (const binding of queue) {
      const otp = (otpQueue[binding.id] ?? "").trim();
      if (!otp) {
        continue;
      }
      await vm.verifyBinding(binding.id, { otp });
    }
    setOtpQueue({});
  }

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Bindings</h1>
        <p className="text-sm text-muted-foreground">
          Unit kerja account + server, termasuk verify login dan logout.
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
          <CardContent><p className="text-3xl font-semibold tracking-tight">{vm.bindings.length}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardDescription>Active</CardDescription></CardHeader>
          <CardContent><p className="text-3xl font-semibold tracking-tight">{vm.activeCount}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Balance (Last)</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold tracking-tight">
              {totalBalanceLast.toLocaleString("id-ID")}
            </p>
            <p className="text-xs text-muted-foreground">
              Start: {totalBalanceStart.toLocaleString("id-ID")}
            </p>
          </CardContent>
        </Card>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Filter</CardTitle>
          <CardDescription>Filter list binding sebelum eksekusi action.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <BindingFilterFields filters={vm.filters} onChange={vm.setFilters} />
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
              <CardTitle>Binding List</CardTitle>
              <CardDescription>Manage verify, logout, dan delete binding.</CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="secondary" onClick={() => void vm.loadBindings()}>
                <RefreshCw className="mr-2 h-4 w-4" /> Refresh
              </Button>
              <Button variant="outline" onClick={() => setIsBulkOpen(true)}>
                <Upload className="mr-2 h-4 w-4" /> Bulk Builder
              </Button>
              <Button onClick={() => setIsCreateOpen(true)}>
                <Plus className="mr-2 h-4 w-4" /> Create Binding
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="mb-3 flex flex-wrap items-center gap-2 rounded-md border p-3">
            <span className="text-sm font-medium">
              Selected: {vm.selectedCount}
            </span>
            <Button
              size="sm"
              variant="secondary"
              disabled={vm.selectedCount === 0 || vm.isSubmitting}
              onClick={() => void onBulkCheckBalance()}
            >
              Bulk Check Balance
            </Button>
            <Button
              size="sm"
              variant="secondary"
              disabled={vm.selectedCount === 0 || vm.isSubmitting}
              onClick={() => void onBulkRefreshToken()}
            >
              Bulk Refresh token_loc
            </Button>
            <Button
              size="sm"
              variant="secondary"
              disabled={vm.selectedCount === 0 || vm.isSubmitting}
              onClick={() => void onBulkVerifyReseller()}
            >
              Bulk Verify Reseller
            </Button>
            <div className="flex items-center gap-2">
              <Label htmlFor="bulk-pin">PIN (opsional)</Label>
              <input
                id="bulk-pin"
                className="h-8 w-36 rounded-md border bg-background px-2 text-sm"
                value={bulkPin}
                onChange={(event) => setBulkPin(event.target.value)}
              />
              <Button
                size="sm"
                variant="secondary"
                disabled={vm.selectedCount === 0 || vm.isSubmitting}
                onClick={() => void onBulkRequestLogin()}
              >
                Bulk Request Login
              </Button>
            </div>
            <Button
              size="sm"
              variant="outline"
              disabled={vm.selectedCount === 0 || vm.isSubmitting}
              onClick={() => void onBulkLogout()}
            >
              Bulk Logout
            </Button>
            <Button
              size="sm"
              variant="destructive"
              disabled={vm.selectedCount === 0 || vm.isSubmitting}
              onClick={() => void onBulkDelete()}
            >
              Bulk Delete
            </Button>
          </div>
          <BindingsTable
            bindings={vm.bindings}
            selectedBindingIds={vm.selectedBindingIds}
            allSelected={vm.allSelected}
            isLoading={vm.isLoading}
            pendingRowActions={vm.pendingRowActions}
            onToggleSelectAll={vm.toggleSelectAll}
            onToggleSelectBinding={vm.toggleSelectBinding}
            onCheckBalance={(bindingId) => void vm.checkBalanceBinding(bindingId)}
            onRefreshTokenLocation={(bindingId) =>
              void vm.refreshTokenLocationBinding(bindingId)
            }
            onVerifyReseller={(bindingId) => void vm.verifyResellerBinding(bindingId)}
            onOpenRequestLogin={openRequestLogin}
            onOpenVerify={openVerify}
            onOpenLogout={openLogout}
            onDelete={(bindingId) => void vm.deleteBinding(bindingId)}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>OTP Queue</CardTitle>
          <CardDescription>
            Khusus selected bindings dengan step <code>otp_requested</code>.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {buildOtpQueueBindings().length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Tidak ada selected binding di step otp_requested.
            </p>
          ) : (
            <div className="space-y-2">
              {buildOtpQueueBindings().map((binding) => (
                <div key={binding.id} className="flex items-center gap-2">
                  <span className="w-14 text-sm">#{binding.id}</span>
                  <span className="w-64 truncate font-mono text-xs">
                    {binding.account_msisdn ?? binding.account_id}
                  </span>
                  <input
                    className="h-8 w-40 rounded-md border bg-background px-2 text-sm"
                    placeholder="OTP"
                    value={otpQueue[binding.id] ?? ""}
                    onChange={(event) =>
                      setOtpQueue((prev) => ({ ...prev, [binding.id]: event.target.value }))
                    }
                  />
                </div>
              ))}
            </div>
          )}
          <Button
            disabled={buildOtpQueueBindings().length === 0 || vm.isSubmitting}
            onClick={() => void submitOtpQueue()}
          >
            Submit OTP Queue
          </Button>
        </CardContent>
      </Card>

      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Binding</DialogTitle>
            <DialogDescription>Masukkan pair server_id dan account_id.</DialogDescription>
          </DialogHeader>
          <BindingCreateFields
            form={createForm}
            onChange={setCreateForm}
            serverOptions={vm.serverOptions}
            accountOptions={vm.accountOptions}
          />
          <DialogFooter>
            <Button variant="secondary" onClick={() => setIsCreateOpen(false)}>Cancel</Button>
            <Button
              onClick={() => void onCreateBinding()}
              disabled={vm.isSubmitting || !createForm.server_id || !createForm.account_id}
            >
              Create
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={isVerifyOpen} onOpenChange={setIsVerifyOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Verify Login</DialogTitle>
            <DialogDescription>
              Binding #{verifyTarget?.id} - submit OTP setelah request login.
            </DialogDescription>
          </DialogHeader>
          <BindingVerifyFields form={verifyForm} onChange={setVerifyForm} />
          <DialogFooter>
            <Button variant="secondary" onClick={() => setIsVerifyOpen(false)}>Cancel</Button>
            <Button onClick={() => void onVerifyBinding()}>Submit OTP</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={isBulkOpen} onOpenChange={setIsBulkOpen}>
        <DialogContent className="sm:max-w-3xl">
          <DialogHeader>
            <DialogTitle>Bulk Bindings</DialogTitle>
            <DialogDescription>
              Input multiline CSV: `port,msisdn[,batch_id]` atau `server_id,account_id`.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-3">
            <div className="flex flex-wrap items-center gap-3 text-sm">
              <Button
                type="button"
                variant={bulkMode === "port_msisdn" ? "default" : "secondary"}
                onClick={() => setBulkMode("port_msisdn")}
              >
                Port + MSISDN
              </Button>
              <Button
                type="button"
                variant={bulkMode === "server_account" ? "default" : "secondary"}
                onClick={() => setBulkMode("server_account")}
              >
                Server ID + Account ID
              </Button>
              <div className="ml-auto flex items-center gap-2">
                <Label htmlFor="bulk-stop-first">Stop on first error</Label>
                <Switch
                  id="bulk-stop-first"
                  checked={bulkStopOnFirstError}
                  onCheckedChange={setBulkStopOnFirstError}
                />
              </div>
            </div>
            <Textarea
              rows={10}
              value={bulkRawText}
              onChange={(event) => setBulkRawText(event.target.value)}
              placeholder={
                bulkMode === "port_msisdn"
                  ? "9900,08577096575,batch-a\n9901,08577096576,batch-a"
                  : "1,100\n2,101"
              }
            />
          </div>
          <DialogFooter>
            <Button variant="secondary" onClick={() => void onBulkDryRun()}>
              Dry Run
            </Button>
            <Button onClick={() => void onBulkCreate()} disabled={vm.isSubmitting}>
              Save Bulk
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {vm.bulkResult ? (
        <Card>
          <CardHeader>
            <CardTitle>Bulk Result</CardTitle>
            <CardDescription>
              Requested: {vm.bulkResult.total_requested} | Created:{" "}
              {vm.bulkResult.total_created} | Failed: {vm.bulkResult.total_failed} | Mode:{" "}
              {vm.bulkResult.dry_run ? "DRY RUN" : "CREATE"}
            </CardDescription>
          </CardHeader>
          <CardContent className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>#</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Server</TableHead>
                  <TableHead>Account</TableHead>
                  <TableHead>Reason</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {vm.bulkResult.items.map((item) => (
                  <TableRow key={`${item.index}-${item.server_id ?? "na"}-${item.account_id ?? "na"}`}>
                    <TableCell>{item.index + 1}</TableCell>
                    <TableCell>{item.status}</TableCell>
                    <TableCell>{item.server_id ?? item.port ?? "-"}</TableCell>
                    <TableCell>{item.account_id ?? item.msisdn ?? "-"}</TableCell>
                    <TableCell className="max-w-[420px] truncate">{item.reason ?? "-"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ) : null}

      <Dialog open={isRequestLoginOpen} onOpenChange={setIsRequestLoginOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Request Login</DialogTitle>
            <DialogDescription>
              Binding #{requestLoginTarget?.id} - request OTP (PIN optional).
            </DialogDescription>
          </DialogHeader>
          <BindingRequestLoginFields form={requestLoginForm} onChange={setRequestLoginForm} />
          <DialogFooter>
            <Button variant="secondary" onClick={() => setIsRequestLoginOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => void onRequestLogin()}>Request OTP</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={isLogoutOpen} onOpenChange={setIsLogoutOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Logout Binding</DialogTitle>
            <DialogDescription>
              Binding #{logoutTarget?.id} akan di-set ke step logged_out.
            </DialogDescription>
          </DialogHeader>
          <BindingLogoutFields form={logoutForm} onChange={setLogoutForm} />
          <DialogFooter>
            <Button variant="secondary" onClick={() => setIsLogoutOpen(false)}>Cancel</Button>
            <Button onClick={() => void onLogoutBinding()}>Logout</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </section>
  );
}
