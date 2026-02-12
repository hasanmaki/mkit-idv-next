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
import type { Binding } from "../types";

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
              <Button onClick={() => setIsCreateOpen(true)}>
                <Plus className="mr-2 h-4 w-4" /> Create Binding
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <BindingsTable
            bindings={vm.bindings}
            isLoading={vm.isLoading}
            pendingRowActions={vm.pendingRowActions}
            onOpenRequestLogin={openRequestLogin}
            onOpenVerify={openVerify}
            onOpenLogout={openLogout}
            onDelete={(bindingId) => void vm.deleteBinding(bindingId)}
          />
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
