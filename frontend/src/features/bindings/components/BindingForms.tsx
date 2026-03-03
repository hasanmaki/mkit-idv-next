import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { Binding } from "../types";

type BindAccountFormFieldsProps = {
  form: {
    order_id: number;
    server_id: number;
    account_id: number;
    is_reseller: boolean;
    priority: number;
    description: string;
    notes: string;
  };
  onChange: React.Dispatch<React.SetStateAction<any>>;
  orders: { id: number; name: string }[];
  servers: { id: number; name: string; port: number }[];
  accounts: { id: number; msisdn: string }[];
  isLoadingOptions: boolean;
  onOrderChange: (orderId: number) => void;
};

export function BindAccountFormFields({
  form,
  onChange,
  orders = [],
  servers = [],
  accounts = [],
  isLoadingOptions,
  onOrderChange,
}: BindAccountFormFieldsProps) {
  return (
    <div className="grid gap-4 py-2">
      <div className="grid gap-2">
        <Label>Session / Order</Label>
        <Select
          value={form.order_id.toString()}
          onValueChange={(value) => onOrderChange(Number(value))}
          disabled={isLoadingOptions}
        >
          <SelectTrigger>
            <SelectValue placeholder="Pilih Session" />
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

      <div className="grid grid-cols-2 gap-4">
        <div className="grid gap-2">
          <Label>Akun (MSISDN)</Label>
          <Select
            value={form.account_id.toString()}
            onValueChange={(value) =>
              onChange((prev: any) => ({ ...prev, account_id: Number(value) }))
            }
            disabled={isLoadingOptions || accounts.length === 0}
          >
            <SelectTrigger>
              <SelectValue placeholder="Pilih Akun" />
            </SelectTrigger>
            <SelectContent>
              {accounts.map((account) => (
                <SelectItem key={account.id} value={account.id.toString()}>
                  {account.msisdn}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="grid gap-2">
          <Label>Server IDV</Label>
          <Select
            value={form.server_id.toString()}
            onValueChange={(value) =>
              onChange((prev: any) => ({ ...prev, server_id: Number(value) }))
            }
            disabled={isLoadingOptions}
          >
            <SelectTrigger>
              <SelectValue placeholder="Pilih Server" />
            </SelectTrigger>
            <SelectContent>
              {servers.map((server) => (
                <SelectItem key={server.id} value={server.id.toString()}>
                  {server.name} (:{server.port})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="flex items-center justify-between rounded-md border p-3">
        <div className="space-y-0.5">
          <Label>Reseller Account</Label>
          <p className="text-[10px] text-muted-foreground">Aktifkan jika akun ini adalah reseller.</p>
        </div>
        <Switch
          checked={form.is_reseller}
          onCheckedChange={(checked) => onChange((prev: any) => ({ ...prev, is_reseller: checked }))}
        />
      </div>

      <div className="grid gap-2">
        <Label htmlFor="priority">Prioritas Antrean</Label>
        <Input
          id="priority"
          type="number"
          value={form.priority}
          onChange={(event) =>
            onChange((prev: any) => ({ ...prev, priority: Number(event.target.value) }))
          }
        />
      </div>

      <div className="grid gap-2">
        <Label htmlFor="notes">Catatan Internal</Label>
        <Textarea
          id="notes"
          value={form.notes}
          onChange={(event) => onChange((prev: any) => ({ ...prev, notes: event.target.value }))}
          rows={2}
          placeholder="Tambahkan info tambahan..."
        />
      </div>
    </div>
  );
}

type EditBindingFormFieldsProps = {
  form: {
    server_id: number;
    is_reseller: boolean;
    priority: number;
    description: string;
    notes: string;
  };
  onChange: React.Dispatch<React.SetStateAction<any>>;
  servers: { id: number; name: string; port: number }[];
};

export function EditBindingFormFields({
  form,
  onChange,
  servers = [],
}: EditBindingFormFieldsProps) {
  return (
    <div className="grid gap-4 py-2">
      <div className="grid gap-2">
        <Label>Pindah ke Server</Label>
        <Select
          value={form.server_id.toString()}
          onValueChange={(value) =>
            onChange((prev: any) => ({ ...prev, server_id: Number(value) }))
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="Pilih Server Baru" />
          </SelectTrigger>
          <SelectContent>
            {servers.map((server) => (
              <SelectItem key={server.id} value={server.id.toString()}>
                {server.name} (:{server.port})
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex items-center justify-between rounded-md border p-3 bg-muted/30">
        <div className="space-y-0.5">
          <Label>Tipe Reseller</Label>
          <p className="text-[10px] text-muted-foreground">Ubah mode operasi akun.</p>
        </div>
        <Switch
          checked={form.is_reseller}
          onCheckedChange={(checked) => onChange((prev: any) => ({ ...prev, is_reseller: checked }))}
        />
      </div>

      <div className="grid gap-2">
        <Label htmlFor="edit-priority">Prioritas Antrean</Label>
        <Input
          id="edit-priority"
          type="number"
          value={form.priority}
          onChange={(event) =>
            onChange((prev: any) => ({ ...prev, priority: Number(event.target.value) }))
          }
        />
      </div>

      <div className="grid gap-2">
        <Label htmlFor="edit-notes">Update Catatan</Label>
        <Textarea
          id="edit-notes"
          value={form.notes}
          onChange={(event) => onChange((prev: any) => ({ ...prev, notes: event.target.value }))}
          rows={3}
        />
      </div>
    </div>
  );
}

type BulkBindFormFieldsProps = {
  form: {
    order_id: number;
    server_id: number;
    account_ids: string | number[];
    is_reseller: boolean;
    priority: number;
    description: string;
    notes: string;
  };
  onChange: React.Dispatch<React.SetStateAction<any>>;
};

export function BulkBindFormFields({ form, onChange }: BulkBindFormFieldsProps) {
  return (
    <div className="grid gap-4 py-2">
      <div className="grid grid-cols-2 gap-4">
        <div className="grid gap-2">
          <Label htmlFor="bulk-order_id">Session ID</Label>
          <Input
            id="bulk-order_id"
            type="number"
            value={form.order_id}
            onChange={(event) =>
              onChange((prev: any) => ({ ...prev, order_id: Number(event.target.value) }))
            }
          />
        </div>
        <div className="grid gap-2">
          <Label htmlFor="bulk-server_id">Server ID</Label>
          <Input
            id="bulk-server_id"
            type="number"
            value={form.server_id}
            onChange={(event) =>
              onChange((prev: any) => ({ ...prev, server_id: Number(event.target.value) }))
            }
          />
        </div>
      </div>

      <div className="grid gap-2">
        <Label htmlFor="bulk-account_ids">List Account ID (pisahkan koma)</Label>
        <Input
          id="bulk-account_ids"
          value={typeof form.account_ids === "string" ? form.account_ids : form.account_ids.join(",")}
          onChange={(event) =>
            onChange((prev: any) => ({ ...prev, account_ids: event.target.value }))
          }
          placeholder="Contoh: 101, 102, 103"
        />
      </div>

      <div className="flex items-center justify-between rounded-md border p-3">
        <div className="space-y-0.5">
          <Label>Set sebagai Reseller</Label>
          <p className="text-[10px] text-muted-foreground">Terapkan ke semua akun dalam batch ini.</p>
        </div>
        <Switch
          checked={form.is_reseller}
          onCheckedChange={(checked) => onChange((prev: any) => ({ ...prev, is_reseller: checked }))}
        />
      </div>

      <div className="grid gap-2">
        <Label htmlFor="bulk-priority">Default Priority</Label>
        <Input
          id="bulk-priority"
          type="number"
          value={form.priority}
          onChange={(event) =>
            onChange((prev: any) => ({ ...prev, priority: Number(event.target.value) }))
          }
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
      <div className="rounded-md bg-muted/50 p-3 text-xs space-y-1">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Akun:</span>
          <span className="font-mono font-medium">{binding.account_msisdn}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Server:</span>
          <span>{binding.server_name}</span>
        </div>
        <div className="flex justify-between border-t pt-1 mt-1">
          <span className="text-muted-foreground">Step Saat Ini:</span>
          <span className="font-bold text-primary">{binding.step}</span>
        </div>
      </div>

      {mode === "request" ? (
        <div className="grid gap-2">
          <Label htmlFor="pin">PIN Provider</Label>
          <Input
            id="pin"
            type="password"
            value={pin}
            onChange={(event) => onPinChange(event.target.value)}
            placeholder="Masukkan PIN Akun"
            maxLength={10}
          />
        </div>
      ) : (
        <div className="grid gap-2">
          <Label htmlFor="otp">Kode OTP (SMS)</Label>
          <Input
            id="otp"
            type="text"
            value={otp}
            onChange={(event) => onOTPChange(event.target.value)}
            placeholder="Contoh: 123456"
            maxLength={10}
            className="text-center text-lg tracking-widest font-bold"
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
      <div className="rounded-md border p-3 bg-muted/20">
        <p className="text-xs text-muted-foreground mb-1">Update Saldo Terakhir</p>
        <p className="text-sm font-bold">{binding.account_msisdn}</p>
        <p className="text-xs text-muted-foreground mt-2 italic">
          Saldo Saat Ini: {binding.balance_start ? `Rp${binding.balance_start.toLocaleString()}` : "Belum ada data"}
        </p>
      </div>

      <div className="grid gap-2">
        <Label htmlFor="balance">Saldo Baru (Nominal)</Label>
        <Input
          id="balance"
          type="number"
          value={balance}
          onChange={(event) => onBalanceChange(Number(event.target.value))}
          placeholder="Contoh: 50000"
        />
      </div>

      <div className="grid gap-2">
        <Label>Metode Input</Label>
        <div className="flex gap-2">
          <Button
            type="button"
            variant={source === "MANUAL" ? "default" : "outline"}
            className="flex-1 text-xs"
            onClick={() => onSourceChange("MANUAL")}
          >
            Manual
          </Button>
          <Button
            type="button"
            variant={source === "AUTO_CHECK" ? "default" : "outline"}
            className="flex-1 text-xs"
            onClick={() => onSourceChange("AUTO_CHECK")}
          >
            Auto Check
          </Button>
        </div>
      </div>
    </div>
  );
}
