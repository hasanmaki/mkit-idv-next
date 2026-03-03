import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";

import { ACCOUNT_STATUSES, type AccountBulkForm, type AccountEditForm, type AccountSingleForm } from "../types";

type SingleAccountFormFieldsProps = {
  form: AccountSingleForm;
  onChange: React.Dispatch<React.SetStateAction<AccountSingleForm>>;
  orders: { id: number; name: string }[];
  isLoadingOrders: boolean;
};

export function SingleAccountFormFields({ form, onChange, orders, isLoadingOrders }: SingleAccountFormFieldsProps) {
  return (
    <div className="grid gap-4 py-2">
      <div className="space-y-2">
        <Label htmlFor="single-order">Order</Label>
        <Select
          value={form.order_id.toString()}
          onValueChange={(value) => onChange((prev) => ({ ...prev, order_id: Number(value) }))}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select order" />
          </SelectTrigger>
          <SelectContent>
            {orders.map((order) => (
              <SelectItem key={order.id} value={order.id.toString()}>
                {order.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="grid gap-4 py-2 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="single-msisdn">MSISDN</Label>
          <Input
            id="single-msisdn"
            value={form.msisdn}
            onChange={(event) => onChange((prev) => ({ ...prev, msisdn: event.target.value }))}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="single-pin">PIN</Label>
          <Input
            id="single-pin"
            value={form.pin}
            onChange={(event) => onChange((prev) => ({ ...prev, pin: event.target.value }))}
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="single-email">Email</Label>
        <Input
          id="single-email"
          value={form.email}
          onChange={(event) => onChange((prev) => ({ ...prev, email: event.target.value }))}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="single-notes">Notes</Label>
        <Textarea
          id="single-notes"
          rows={3}
          value={form.notes}
          onChange={(event) => onChange((prev) => ({ ...prev, notes: event.target.value }))}
        />
      </div>
    </div>
  );
}

type BulkAccountFormFieldsProps = {
  form: AccountBulkForm;
  onChange: React.Dispatch<React.SetStateAction<AccountBulkForm>>;
  orders: { id: number; name: string }[];
  isLoadingOrders: boolean;
};

export function BulkAccountFormFields({ form, onChange, orders, isLoadingOrders }: BulkAccountFormFieldsProps) {
  return (
    <div className="grid gap-4 py-2">
      <div className="space-y-2">
        <Label htmlFor="bulk-order">Order</Label>
        <Select
          value={form.order_id.toString()}
          onValueChange={(value) => onChange((prev) => ({ ...prev, order_id: Number(value) }))}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select order" />
          </SelectTrigger>
          <SelectContent>
            {orders.map((order) => (
              <SelectItem key={order.id} value={order.id.toString()}>
                {order.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label htmlFor="bulk-msisdns">MSISDN List</Label>
        <Textarea
          id="bulk-msisdns"
          rows={6}
          placeholder="0857..., 0815...\nSatu nomor per baris atau pisah koma"
          value={form.msisdns_text}
          onChange={(event) =>
            onChange((prev) => ({ ...prev, msisdns_text: event.target.value }))
          }
        />
      </div>
      <div className="grid gap-4 py-2 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="bulk-pin">Default PIN</Label>
          <Input
            id="bulk-pin"
            value={form.pin}
            onChange={(event) => onChange((prev) => ({ ...prev, pin: event.target.value }))}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="bulk-email">Email</Label>
          <Input
            id="bulk-email"
            value={form.email}
            onChange={(event) => onChange((prev) => ({ ...prev, email: event.target.value }))}
          />
        </div>
      </div>
    </div>
  );
}

type EditAccountFormFieldsProps = {
  form: AccountEditForm;
  onChange: React.Dispatch<React.SetStateAction<AccountEditForm | null>>;
};

export function EditAccountFormFields({ form, onChange }: EditAccountFormFieldsProps) {
  return (
    <div className="grid gap-4 py-2 md:grid-cols-2">
      <div className="space-y-2 md:col-span-2">
        <Label htmlFor="edit-email">Email</Label>
        <Input
          id="edit-email"
          value={form.email}
          onChange={(event) => onChange((prev) => (prev ? { ...prev, email: event.target.value } : prev))}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="edit-pin">PIN</Label>
        <Input
          id="edit-pin"
          value={form.pin}
          onChange={(event) => onChange((prev) => (prev ? { ...prev, pin: event.target.value } : prev))}
        />
      </div>
      <div className="space-y-2">
        <Label>Status</Label>
        <Select
          value={form.status}
          onValueChange={(value) =>
            onChange((prev) => (prev ? { ...prev, status: value as AccountEditForm["status"] } : prev))
          }
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {ACCOUNT_STATUSES.map((status) => (
              <SelectItem key={status} value={status}>
                {status}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2 md:col-span-2">
        <Label htmlFor="edit-last-device-id">Last Device ID</Label>
        <Input
          id="edit-last-device-id"
          value={form.last_device_id}
          onChange={(event) =>
            onChange((prev) => (prev ? { ...prev, last_device_id: event.target.value } : prev))
          }
        />
      </div>
      <div className="space-y-2 md:col-span-2">
        <Label htmlFor="edit-notes">Notes</Label>
        <Textarea
          id="edit-notes"
          rows={3}
          value={form.notes}
          onChange={(event) => onChange((prev) => (prev ? { ...prev, notes: event.target.value } : prev))}
        />
      </div>
      <Separator className="md:col-span-2" />
      <div className="flex items-center justify-between rounded-md border p-3 md:col-span-2">
        <div>
          <p className="text-sm font-medium">Is Reseller</p>
          <p className="text-xs text-muted-foreground">Set reseller flag account.</p>
        </div>
        <Switch
          checked={form.is_reseller}
          onCheckedChange={(checked) => onChange((prev) => (prev ? { ...prev, is_reseller: checked } : prev))}
        />
      </div>
    </div>
  );
}
