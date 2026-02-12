import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";

import {
  BINDING_STEPS,
  type AccountOption,
  type AccountStatus,
  type BindingFilters,
  type ServerOption,
} from "../types";

type BindingCreateForm = {
  server_id: string;
  account_id: string;
  balance_start: string;
};

type VerifyForm = {
  otp: string;
};

type RequestLoginForm = {
  pin: string;
};

type LogoutForm = {
  account_status: AccountStatus;
  last_error_code: string;
  last_error_message: string;
};

export function BindingCreateFields({
  form,
  onChange,
  serverOptions,
  accountOptions,
}: {
  form: BindingCreateForm;
  onChange: (next: BindingCreateForm) => void;
  serverOptions: ServerOption[];
  accountOptions: AccountOption[];
}) {
  return (
    <div className="grid gap-4 sm:grid-cols-3">
      <div className="space-y-1.5">
        <Label>Server ID</Label>
        <Select
          value={form.server_id || "none"}
          onValueChange={(value) =>
            onChange({ ...form, server_id: value === "none" ? "" : value })
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="Pilih server" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">Pilih server</SelectItem>
            {serverOptions.map((server) => (
              <SelectItem key={server.id} value={String(server.id)}>
                {server.id} | {server.base_url}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-1.5">
        <Label>Account ID</Label>
        <Select
          value={form.account_id || "none"}
          onValueChange={(value) =>
            onChange({ ...form, account_id: value === "none" ? "" : value })
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="Pilih account" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">Pilih account</SelectItem>
            {accountOptions.map((account) => (
              <SelectItem key={account.id} value={String(account.id)}>
                {account.id} | {account.msisdn} | {account.batch_id}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-1.5">
        <Label>Balance Start (optional)</Label>
        <Input
          type="number"
          value={form.balance_start}
          onChange={(event) => onChange({ ...form, balance_start: event.target.value })}
        />
      </div>
    </div>
  );
}

export function BindingFilterFields({
  filters,
  onChange,
}: {
  filters: BindingFilters;
  onChange: (next: BindingFilters) => void;
}) {
  return (
    <div className="grid gap-3 md:grid-cols-5">
      <Input
        placeholder="Server ID"
        value={filters.server_id}
        onChange={(event) => onChange({ ...filters, server_id: event.target.value })}
      />
      <Input
        placeholder="Account ID"
        value={filters.account_id}
        onChange={(event) => onChange({ ...filters, account_id: event.target.value })}
      />
      <Input
        placeholder="Batch ID"
        value={filters.batch_id}
        onChange={(event) => onChange({ ...filters, batch_id: event.target.value })}
      />
      <Select
        value={filters.step || "all"}
        onValueChange={(value) =>
          onChange({ ...filters, step: value === "all" ? "" : (value as BindingFilters["step"]) })
        }
      >
        <SelectTrigger>
          <SelectValue placeholder="Step" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Steps</SelectItem>
          {BINDING_STEPS.map((step) => (
            <SelectItem key={step} value={step}>
              {step}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <div className="flex items-center gap-2 rounded-md border px-3">
        <Switch
          checked={filters.active_only}
          onCheckedChange={(value) => onChange({ ...filters, active_only: value })}
        />
        <span className="text-sm">Active only</span>
      </div>
    </div>
  );
}

export function BindingVerifyFields({
  form,
  onChange,
}: {
  form: VerifyForm;
  onChange: (next: VerifyForm) => void;
}) {
  return (
    <div className="grid gap-4 sm:grid-cols-1">
      <div className="space-y-1.5">
        <Label>OTP</Label>
        <Input value={form.otp} onChange={(event) => onChange({ ...form, otp: event.target.value })} />
      </div>
    </div>
  );
}

export function BindingRequestLoginFields({
  form,
  onChange,
}: {
  form: RequestLoginForm;
  onChange: (next: RequestLoginForm) => void;
}) {
  return (
    <div className="grid gap-4 sm:grid-cols-1">
      <div className="space-y-1.5">
        <Label>PIN override (optional)</Label>
        <Input value={form.pin} onChange={(event) => onChange({ ...form, pin: event.target.value })} />
      </div>
    </div>
  );
}

export function BindingLogoutFields({
  form,
  onChange,
}: {
  form: LogoutForm;
  onChange: (next: LogoutForm) => void;
}) {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <div className="space-y-1.5 sm:col-span-2">
        <Label>Account Status</Label>
        <Select
          value={form.account_status}
          onValueChange={(value) =>
            onChange({ ...form, account_status: value as AccountStatus })
          }
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="new">new</SelectItem>
            <SelectItem value="active">active</SelectItem>
            <SelectItem value="exhausted">exhausted</SelectItem>
            <SelectItem value="disabled">disabled</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-1.5">
        <Label>Error code (optional)</Label>
        <Input
          value={form.last_error_code}
          onChange={(event) =>
            onChange({ ...form, last_error_code: event.target.value })
          }
        />
      </div>
      <div className="space-y-1.5">
        <Label>Error message (optional)</Label>
        <Input
          value={form.last_error_message}
          onChange={(event) =>
            onChange({ ...form, last_error_message: event.target.value })
          }
        />
      </div>
    </div>
  );
}

export type { BindingCreateForm, LogoutForm, RequestLoginForm, VerifyForm };
