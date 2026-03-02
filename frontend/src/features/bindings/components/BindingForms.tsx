import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import type { Binding } from "../types";

type BindAccountFormFieldsProps = {
  form: {
    session_id: number;
    server_id: number;
    account_id: number;
    priority: number;
    description: string;
    notes: string;
  };
  onChange: React.Dispatch<
    React.SetStateAction<{
      session_id: number;
      server_id: number;
      account_id: number;
      priority: number;
      description: string;
      notes: string;
    }>
  >;
  sessions?: { id: number; name: string }[];
  servers?: { id: number; name: string }[];
};

export function BindAccountFormFields({
  form,
  onChange,
  sessions = [],
  servers = [],
}: BindAccountFormFieldsProps) {
  return (
    <div className="grid gap-4 py-2">
      <div className="grid gap-2">
        <Label htmlFor="session_id">Session</Label>
        <Input
          id="session_id"
          type="number"
          value={form.session_id}
          onChange={(event) =>
            onChange((prev) => ({ ...prev, session_id: Number(event.target.value) }))
          }
          placeholder="Session ID"
        />
        {sessions.length > 0 && (
          <p className="text-xs text-muted-foreground">
            Available: {sessions.map((s) => s.name).join(", ")}
          </p>
        )}
      </div>
      <div className="grid gap-2">
        <Label htmlFor="server_id">Server</Label>
        <Input
          id="server_id"
          type="number"
          value={form.server_id}
          onChange={(event) =>
            onChange((prev) => ({ ...prev, server_id: Number(event.target.value) }))
          }
          placeholder="Server ID"
        />
        {servers.length > 0 && (
          <p className="text-xs text-muted-foreground">
            Available: {servers.map((s) => s.name).join(", ")}
          </p>
        )}
      </div>
      <div className="grid gap-2">
        <Label htmlFor="account_id">Account ID</Label>
        <Input
          id="account_id"
          type="number"
          value={form.account_id}
          onChange={(event) =>
            onChange((prev) => ({ ...prev, account_id: Number(event.target.value) }))
          }
          placeholder="Account ID to bind"
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="priority">Priority</Label>
        <Input
          id="priority"
          type="number"
          value={form.priority}
          onChange={(event) =>
            onChange((prev) => ({ ...prev, priority: Number(event.target.value) }))
          }
          placeholder="1"
        />
        <p className="text-xs text-muted-foreground">Lower = higher priority</p>
      </div>
      <div className="grid gap-2">
        <Label htmlFor="description">Description</Label>
        <Input
          id="description"
          value={form.description}
          onChange={(event) =>
            onChange((prev) => ({ ...prev, description: event.target.value }))
          }
          placeholder="Optional description"
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="notes">Notes</Label>
        <Textarea
          id="notes"
          value={form.notes}
          onChange={(event) => onChange((prev) => ({ ...prev, notes: event.target.value }))}
          rows={3}
          placeholder="Additional notes"
        />
      </div>
    </div>
  );
}

type BulkBindFormFieldsProps = {
  form: {
    session_id: number;
    server_id: number;
    account_ids: string | number[];
    priority: number;
    description: string;
    notes: string;
  };
  onChange: React.Dispatch<
    React.SetStateAction<{
      session_id: number;
      server_id: number;
      account_ids: string | number[];
      priority: number;
      description: string;
      notes: string;
    }>
  >;
};

export function BulkBindFormFields({ form, onChange }: BulkBindFormFieldsProps) {
  return (
    <div className="grid gap-4 py-2">
      <div className="grid gap-2">
        <Label htmlFor="bulk-session_id">Session</Label>
        <Input
          id="bulk-session_id"
          type="number"
          value={form.session_id}
          onChange={(event) =>
            onChange((prev) => ({ ...prev, session_id: Number(event.target.value) }))
          }
          placeholder="Session ID"
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="bulk-server_id">Server</Label>
        <Input
          id="bulk-server_id"
          type="number"
          value={form.server_id}
          onChange={(event) =>
            onChange((prev) => ({ ...prev, server_id: Number(event.target.value) }))
          }
          placeholder="Server ID"
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="bulk-account_ids">Account IDs (comma-separated)</Label>
        <Input
          id="bulk-account_ids"
          value={typeof form.account_ids === "string" ? form.account_ids : form.account_ids.join(",")}
          onChange={(event) =>
            onChange((prev) => ({ ...prev, account_ids: event.target.value }))
          }
          placeholder="100, 101, 102"
        />
        <p className="text-xs text-muted-foreground">Example: 100, 101, 102</p>
      </div>
      <div className="grid gap-2">
        <Label htmlFor="bulk-priority">Priority</Label>
        <Input
          id="bulk-priority"
          type="number"
          value={form.priority}
          onChange={(event) =>
            onChange((prev) => ({ ...prev, priority: Number(event.target.value) }))
          }
          placeholder="1"
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="bulk-description">Description</Label>
        <Input
          id="bulk-description"
          value={form.description}
          onChange={(event) =>
            onChange((prev) => ({ ...prev, description: event.target.value }))
          }
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="bulk-notes">Notes</Label>
        <Textarea
          id="bulk-notes"
          value={form.notes}
          onChange={(event) => onChange((prev) => ({ ...prev, notes: event.target.value }))}
          rows={3}
        />
      </div>
    </div>
  );
}

type OTPDialogFieldsProps = {
  binding: Binding | null;
  mode: "request" | "verify";
  pin: string;
  otp: string;
  onPinChange: (pin: string) => void;
  onOTPChange: (otp: string) => void;
};

export function OTPDialogFields({
  binding,
  mode,
  pin,
  otp,
  onPinChange,
  onOTPChange,
}: OTPDialogFieldsProps) {
  if (!binding) return null;

  return (
    <div className="grid gap-4 py-2">
      <div className="rounded-md border p-3">
        <p className="text-sm font-medium">Binding #{binding.id}</p>
        <p className="text-xs text-muted-foreground">
          Account {binding.account_id} → Server {binding.server_id}
        </p>
        <p className="text-xs text-muted-foreground">Step: {binding.step}</p>
      </div>

      {mode === "request" ? (
        <div className="grid gap-2">
          <Label htmlFor="pin">PIN</Label>
          <Input
            id="pin"
            type="password"
            value={pin}
            onChange={(event) => onPinChange(event.target.value)}
            placeholder="Enter your PIN"
            maxLength={10}
          />
        </div>
      ) : (
        <div className="grid gap-2">
          <Label htmlFor="otp">OTP Code</Label>
          <Input
            id="otp"
            type="text"
            value={otp}
            onChange={(event) => onOTPChange(event.target.value)}
            placeholder="Enter OTP code"
            maxLength={10}
          />
        </div>
      )}
    </div>
  );
}

type BalanceDialogFieldsProps = {
  binding: Binding | null;
  balance: number;
  source: "MANUAL" | "AUTO_CHECK";
  onBalanceChange: (balance: number) => void;
  onSourceChange: (source: "MANUAL" | "AUTO_CHECK") => void;
};

export function BalanceDialogFields({
  binding,
  balance,
  source,
  onBalanceChange,
  onSourceChange,
}: BalanceDialogFieldsProps) {
  if (!binding) return null;

  return (
    <div className="grid gap-4 py-2">
      <div className="rounded-md border p-3">
        <p className="text-sm font-medium">Binding #{binding.id}</p>
        <p className="text-xs text-muted-foreground">
          Account {binding.account_id} → Server {binding.server_id}
        </p>
        <p className="text-xs text-muted-foreground">
          Current Balance: {binding.balance_start ?? "Not set"}
        </p>
      </div>

      <div className="grid gap-2">
        <Label htmlFor="balance">Balance Start</Label>
        <Input
          id="balance"
          type="number"
          value={balance}
          onChange={(event) => onBalanceChange(Number(event.target.value))}
          placeholder="50000"
        />
      </div>

      <div className="grid gap-2">
        <Label>Source</Label>
        <div className="flex gap-2">
          <button
            type="button"
            className={`flex-1 rounded-md border p-2 text-sm ${
              source === "MANUAL"
                ? "border-primary bg-primary/10"
                : "border-muted"
            }`}
            onClick={() => onSourceChange("MANUAL")}
          >
            Manual Input
          </button>
          <button
            type="button"
            className={`flex-1 rounded-md border p-2 text-sm ${
              source === "AUTO_CHECK"
                ? "border-primary bg-primary/10"
                : "border-muted"
            }`}
            onClick={() => onSourceChange("AUTO_CHECK")}
          >
            Auto Check
          </button>
        </div>
      </div>
    </div>
  );
}
