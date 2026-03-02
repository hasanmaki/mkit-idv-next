import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";

type CreateSessionFormFieldsProps = {
  form: {
    name: string;
    email: string;
    description: string;
    is_active: boolean;
    notes: string;
  };
  onChange: React.Dispatch<
    React.SetStateAction<{
      name: string;
      email: string;
      description: string;
      is_active: boolean;
      notes: string;
    }>
  >;
};

export function CreateSessionFormFields({
  form,
  onChange,
}: CreateSessionFormFieldsProps) {
  return (
    <div className="grid gap-4 py-2">
      <div className="grid gap-2">
        <Label htmlFor="session-name">Name</Label>
        <Input
          id="session-name"
          value={form.name}
          onChange={(event) => onChange((prev) => ({ ...prev, name: event.target.value }))}
          placeholder="Operator 1"
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="session-email">Email</Label>
        <Input
          id="session-email"
          type="email"
          value={form.email}
          onChange={(event) => onChange((prev) => ({ ...prev, email: event.target.value }))}
          placeholder="operator@example.com"
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="session-description">Description</Label>
        <Input
          id="session-description"
          value={form.description}
          onChange={(event) => onChange((prev) => ({ ...prev, description: event.target.value }))}
          placeholder="Main operator session"
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="session-notes">Notes</Label>
        <Textarea
          id="session-notes"
          value={form.notes}
          onChange={(event) => onChange((prev) => ({ ...prev, notes: event.target.value }))}
          rows={3}
          placeholder="Additional notes..."
        />
      </div>
      <div className="flex items-center justify-between rounded-md border p-3">
        <div>
          <p className="text-sm font-medium">Active Status</p>
          <p className="text-xs text-muted-foreground">Set session active status on creation.</p>
        </div>
        <Switch
          checked={form.is_active}
          onCheckedChange={(checked) => onChange((prev) => ({ ...prev, is_active: checked }))}
        />
      </div>
    </div>
  );
}

type EditSessionFormFieldsProps = {
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

export function EditSessionFormFields({ form, onChange }: EditSessionFormFieldsProps) {
  if (!form) return null;

  return (
    <div className="grid gap-4 py-2">
      <div className="grid gap-2">
        <Label htmlFor="edit-name">Name</Label>
        <Input
          id="edit-name"
          value={form.name}
          onChange={(event) =>
            onChange((prev) => (prev ? { ...prev, name: event.target.value } : prev))
          }
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="edit-email">Email</Label>
        <Input
          id="edit-email"
          type="email"
          value={form.email}
          onChange={(event) =>
            onChange((prev) => (prev ? { ...prev, email: event.target.value } : prev))
          }
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="edit-description">Description</Label>
        <Input
          id="edit-description"
          value={form.description ?? ""}
          onChange={(event) =>
            onChange((prev) => (prev ? { ...prev, description: event.target.value } : prev))
          }
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="edit-notes">Notes</Label>
        <Textarea
          id="edit-notes"
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
          <p className="text-xs text-muted-foreground">Change session active status.</p>
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
