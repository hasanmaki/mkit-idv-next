import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Users } from "lucide-react";

type CreateOrderFormFieldsProps = {
  form: {
    name: string;
    email: string;
    default_pin: string;
    msisdns: string;
    description: string;
    is_active: boolean;
    notes: string;
  };
  onChange: React.Dispatch<
    React.SetStateAction<{
      name: string;
      email: string;
      default_pin: string;
      msisdns: string;
      description: string;
      is_active: boolean;
      notes: string;
    }>
  >;
};

// Shared utility to parse MSISDNs (comma or newline separated)
function parseMsisdns(input: string): string[] {
  return input
    .split(/[\n,]+/)  // Split by newline OR comma
    .map(s => s.trim())
    .filter(s => s.length > 0);
}

export function CreateOrderFormFields({ form, onChange }: CreateOrderFormFieldsProps) {
  const msisdnCount = parseMsisdns(form.msisdns).length;

  return (
    <div className="grid gap-4 py-2">
      <div className="grid gap-2">
        <Label htmlFor="order-name">Name</Label>
        <Input
          id="order-name"
          value={form.name}
          onChange={(event) => onChange((prev) => ({ ...prev, name: event.target.value }))}
          placeholder="Operator 1"
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="order-email">Email</Label>
        <Input
          id="order-email"
          type="email"
          value={form.email}
          onChange={(event) => onChange((prev) => ({ ...prev, email: event.target.value }))}
          placeholder="operator@example.com"
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="order-default-pin">Default PIN</Label>
        <Input
          id="order-default-pin"
          type="text"
          value={form.default_pin}
          onChange={(event) => onChange((prev) => ({ ...prev, default_pin: event.target.value }))}
          placeholder="1234"
          maxLength={10}
        />
        <p className="text-xs text-muted-foreground">Default PIN for all accounts (4-10 digits)</p>
      </div>
      <div className="grid gap-2">
        <Label htmlFor="order-msisdns">MSISDN List (optional)</Label>
        <Textarea
          id="order-msisdns"
          value={form.msisdns}
          onChange={(event) => onChange((prev) => ({ ...prev, msisdns: event.target.value }))}
          placeholder="081234567890, 081234567891&#10;081234567892&#10;081234567893"
          rows={6}
        />
        <div className="flex items-center justify-between">
          <p className="text-xs text-muted-foreground">
            Separate with commas or newlines
          </p>
          {msisdnCount > 0 && (
            <Badge variant="outline" className="gap-1">
              <Users className="h-3 w-3" />
              {msisdnCount} {msisdnCount === 1 ? 'account' : 'accounts'}
            </Badge>
          )}
        </div>
      </div>
      <div className="grid gap-2">
        <Label htmlFor="order-description">Description</Label>
        <Input
          id="order-description"
          value={form.description}
          onChange={(event) => onChange((prev) => ({ ...prev, description: event.target.value }))}
          placeholder="Main customer order"
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="order-notes">Notes</Label>
        <Textarea
          id="order-notes"
          value={form.notes}
          onChange={(event) => onChange((prev) => ({ ...prev, notes: event.target.value }))}
          rows={3}
          placeholder="Additional notes..."
        />
      </div>
      <div className="flex items-center justify-between rounded-md border p-3">
        <div>
          <p className="text-sm font-medium">Active Status</p>
          <p className="text-xs text-muted-foreground">Set order active status on creation.</p>
        </div>
        <Switch
          checked={form.is_active}
          onCheckedChange={(checked) => onChange((prev) => ({ ...prev, is_active: checked }))}
        />
      </div>
    </div>
  );
}

type EditOrderFormFieldsProps = {
  form: {
    name: string;
    email: string;
    description: string | null;
    is_active: boolean;
    notes: string | null;
  } | null;
  onChange: React.Dispatch<
    React.SetStateAction<{
      name: string;
      email: string;
      description: string | null;
      is_active: boolean;
      notes: string | null;
    } | null>
  >;
};

export function EditOrderFormFields({ form, onChange }: EditOrderFormFieldsProps) {
  if (!form) return null;

  return (
    <div className="grid gap-4 py-2">
      <div className="grid gap-2">
        <Label htmlFor="edit-order-name">Name</Label>
        <Input
          id="edit-order-name"
          value={form.name}
          onChange={(event) =>
            onChange((prev) => (prev ? { ...prev, name: event.target.value } : prev))
          }
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="edit-order-email">Email</Label>
        <Input
          id="edit-order-email"
          type="email"
          value={form.email}
          onChange={(event) =>
            onChange((prev) => (prev ? { ...prev, email: event.target.value } : prev))
          }
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="edit-order-description">Description</Label>
        <Input
          id="edit-order-description"
          value={form.description ?? ""}
          onChange={(event) =>
            onChange((prev) => (prev ? { ...prev, description: event.target.value } : prev))
          }
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="edit-order-notes">Notes</Label>
        <Textarea
          id="edit-order-notes"
          value={form.notes ?? ""}
          onChange={(event) =>
            onChange((prev) => (prev ? { ...prev, notes: event.target.value } : prev))
          }
          rows={3}
        />
      </div>
      <div className="flex items-center justify-between rounded-md border p-3">
        <div>
          <p className="text-sm font-medium">Active Status</p>
          <p className="text-xs text-muted-foreground">Change order active status.</p>
        </div>
        <Switch
          checked={form.is_active}
          onCheckedChange={(checked) =>
            onChange((prev) => (prev ? { ...prev, is_active: checked } : prev))
          }
        />
      </div>
    </div>
  );
}
