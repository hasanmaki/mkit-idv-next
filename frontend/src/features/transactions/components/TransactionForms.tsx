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
  TRANSACTION_STATUSES,
  type TransactionFilters,
} from "../types";

type TransactionStartForm = {
  binding_id: string;
  product_id: string;
  email: string;
  limit_harga: string;
  otp_required: boolean;
};

type OtpForm = {
  otp: string;
};

type ReasonForm = {
  reason: string;
};

export function TransactionFilterFields({
  filters,
  onChange,
}: {
  filters: TransactionFilters;
  onChange: (next: TransactionFilters) => void;
}) {
  return (
    <div className="grid gap-3 md:grid-cols-5">
      <Select
        value={filters.status_filter || "all"}
        onValueChange={(value) =>
          onChange({
            ...filters,
            status_filter: value === "all" ? "" : (value as TransactionFilters["status_filter"]),
          })
        }
      >
        <SelectTrigger>
          <SelectValue placeholder="Status" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Status</SelectItem>
          {TRANSACTION_STATUSES.map((status) => (
            <SelectItem key={status} value={status}>
              {status}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Input
        placeholder="Binding ID"
        value={filters.binding_id}
        onChange={(event) => onChange({ ...filters, binding_id: event.target.value })}
      />
      <Input
        placeholder="Account ID"
        value={filters.account_id}
        onChange={(event) => onChange({ ...filters, account_id: event.target.value })}
      />
      <Input
        placeholder="Server ID"
        value={filters.server_id}
        onChange={(event) => onChange({ ...filters, server_id: event.target.value })}
      />
      <Input
        placeholder="Batch ID"
        value={filters.batch_id}
        onChange={(event) => onChange({ ...filters, batch_id: event.target.value })}
      />
    </div>
  );
}

export function TransactionStartFields({
  form,
  onChange,
}: {
  form: TransactionStartForm;
  onChange: (next: TransactionStartForm) => void;
}) {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <div className="space-y-1.5">
        <Label>Binding ID</Label>
        <Input
          type="number"
          value={form.binding_id}
          onChange={(event) => onChange({ ...form, binding_id: event.target.value })}
        />
      </div>
      <div className="space-y-1.5">
        <Label>Product ID</Label>
        <Input
          value={form.product_id}
          onChange={(event) => onChange({ ...form, product_id: event.target.value })}
        />
      </div>
      <div className="space-y-1.5">
        <Label>Email</Label>
        <Input
          value={form.email}
          onChange={(event) => onChange({ ...form, email: event.target.value })}
        />
      </div>
      <div className="space-y-1.5">
        <Label>Limit Harga</Label>
        <Input
          type="number"
          value={form.limit_harga}
          onChange={(event) => onChange({ ...form, limit_harga: event.target.value })}
        />
      </div>
      <div className="sm:col-span-2 flex items-center gap-2 rounded-md border px-3 py-2">
        <Switch
          checked={form.otp_required}
          onCheckedChange={(value) => onChange({ ...form, otp_required: value })}
        />
        <span className="text-sm">Force OTP required</span>
      </div>
    </div>
  );
}

export function OtpField({
  form,
  onChange,
}: {
  form: OtpForm;
  onChange: (next: OtpForm) => void;
}) {
  return (
    <div className="space-y-1.5">
      <Label>OTP</Label>
      <Input value={form.otp} onChange={(event) => onChange({ otp: event.target.value })} />
    </div>
  );
}

export function ReasonField({
  form,
  onChange,
  label,
}: {
  form: ReasonForm;
  onChange: (next: ReasonForm) => void;
  label: string;
}) {
  return (
    <div className="space-y-1.5">
      <Label>{label}</Label>
      <Input
        value={form.reason}
        onChange={(event) => onChange({ reason: event.target.value })}
      />
    </div>
  );
}

export type { OtpForm, ReasonForm, TransactionStartForm };
