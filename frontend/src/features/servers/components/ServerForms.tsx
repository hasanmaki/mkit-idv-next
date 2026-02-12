import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import type { BulkServerForm, EditServerForm, SingleServerForm } from "../types";

type ConfigFieldsProps = {
  timeout: number;
  retries: number;
  wait_between_retries: number;
  max_requests_queued: number;
  onChange: (
    key: "timeout" | "retries" | "wait_between_retries" | "max_requests_queued",
    value: number,
  ) => void;
};

function ConfigFields({
  timeout,
  retries,
  wait_between_retries,
  max_requests_queued,
  onChange,
}: ConfigFieldsProps) {
  return (
    <>
      <div className="space-y-2">
        <Label htmlFor="timeout">Timeout</Label>
        <Input
          id="timeout"
          type="number"
          value={timeout}
          onChange={(event) => onChange("timeout", Number(event.target.value))}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="retries">Retries</Label>
        <Input
          id="retries"
          type="number"
          value={retries}
          onChange={(event) => onChange("retries", Number(event.target.value))}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="wait-between">Wait Between Retries</Label>
        <Input
          id="wait-between"
          type="number"
          value={wait_between_retries}
          onChange={(event) => onChange("wait_between_retries", Number(event.target.value))}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="max-queued">Max Requests Queued</Label>
        <Input
          id="max-queued"
          type="number"
          value={max_requests_queued}
          onChange={(event) => onChange("max_requests_queued", Number(event.target.value))}
        />
      </div>
    </>
  );
}

type SingleServerFormFieldsProps = {
  form: SingleServerForm;
  onChange: React.Dispatch<React.SetStateAction<SingleServerForm>>;
};

export function SingleServerFormFields({ form, onChange }: SingleServerFormFieldsProps) {
  return (
    <div className="grid gap-4 py-2 md:grid-cols-2">
      <div className="space-y-2">
        <Label htmlFor="single-host">Host</Label>
        <Input
          id="single-host"
          value={form.host}
          onChange={(event) => onChange((prev) => ({ ...prev, host: event.target.value }))}
          placeholder="http://10.0.0.3"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="single-port">Port</Label>
        <Input
          id="single-port"
          type="number"
          value={form.port}
          onChange={(event) => onChange((prev) => ({ ...prev, port: Number(event.target.value) }))}
        />
      </div>
      <div className="space-y-2 md:col-span-2">
        <Label htmlFor="single-description">Description</Label>
        <Input
          id="single-description"
          value={form.description}
          onChange={(event) => onChange((prev) => ({ ...prev, description: event.target.value }))}
        />
      </div>
      <ConfigFields
        timeout={form.timeout}
        retries={form.retries}
        wait_between_retries={form.wait_between_retries}
        max_requests_queued={form.max_requests_queued}
        onChange={(key, value) => onChange((prev) => ({ ...prev, [key]: value }))}
      />
      <div className="space-y-2">
        <Label htmlFor="single-device-id">Device ID</Label>
        <Input
          id="single-device-id"
          value={form.device_id}
          onChange={(event) => onChange((prev) => ({ ...prev, device_id: event.target.value }))}
        />
      </div>
      <div className="space-y-2 md:col-span-2">
        <Label htmlFor="single-notes">Notes</Label>
        <Textarea
          id="single-notes"
          value={form.notes}
          onChange={(event) => onChange((prev) => ({ ...prev, notes: event.target.value }))}
          rows={3}
        />
      </div>
      <Separator className="md:col-span-2" />
      <div className="flex items-center justify-between rounded-md border p-3 md:col-span-2">
        <div>
          <p className="text-sm font-medium">Active Status</p>
          <p className="text-xs text-muted-foreground">Toggle status server saat dibuat.</p>
        </div>
        <Switch
          checked={form.is_active}
          onCheckedChange={(checked) => onChange((prev) => ({ ...prev, is_active: checked }))}
        />
      </div>
    </div>
  );
}

type BulkServerFormFieldsProps = {
  form: BulkServerForm;
  onChange: React.Dispatch<React.SetStateAction<BulkServerForm>>;
};

export function BulkServerFormFields({ form, onChange }: BulkServerFormFieldsProps) {
  return (
    <div className="grid gap-4 py-2 md:grid-cols-2">
      <div className="space-y-2 md:col-span-2">
        <Label htmlFor="bulk-host">Base Host</Label>
        <Input
          id="bulk-host"
          value={form.base_host}
          onChange={(event) => onChange((prev) => ({ ...prev, base_host: event.target.value }))}
          placeholder="http://10.0.0.3"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="bulk-start-port">Start Port</Label>
        <Input
          id="bulk-start-port"
          type="number"
          value={form.start_port}
          onChange={(event) => onChange((prev) => ({ ...prev, start_port: Number(event.target.value) }))}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="bulk-end-port">End Port</Label>
        <Input
          id="bulk-end-port"
          type="number"
          value={form.end_port}
          onChange={(event) => onChange((prev) => ({ ...prev, end_port: Number(event.target.value) }))}
        />
      </div>
      <div className="space-y-2 md:col-span-2">
        <Label htmlFor="bulk-description">Description</Label>
        <Input
          id="bulk-description"
          value={form.description}
          onChange={(event) => onChange((prev) => ({ ...prev, description: event.target.value }))}
        />
      </div>
      <ConfigFields
        timeout={form.timeout}
        retries={form.retries}
        wait_between_retries={form.wait_between_retries}
        max_requests_queued={form.max_requests_queued}
        onChange={(key, value) => onChange((prev) => ({ ...prev, [key]: value }))}
      />
      <div className="space-y-2">
        <Label htmlFor="bulk-device-id">Device ID</Label>
        <Input
          id="bulk-device-id"
          value={form.device_id}
          onChange={(event) => onChange((prev) => ({ ...prev, device_id: event.target.value }))}
        />
      </div>
      <div className="space-y-2 md:col-span-2">
        <Label htmlFor="bulk-notes">Notes</Label>
        <Textarea
          id="bulk-notes"
          rows={3}
          value={form.notes}
          onChange={(event) => onChange((prev) => ({ ...prev, notes: event.target.value }))}
        />
      </div>
      <Separator className="md:col-span-2" />
      <div className="flex items-center justify-between rounded-md border p-3 md:col-span-2">
        <div>
          <p className="text-sm font-medium">Active Status</p>
          <p className="text-xs text-muted-foreground">Terapkan status untuk semua server pada range.</p>
        </div>
        <Switch
          checked={form.is_active}
          onCheckedChange={(checked) => onChange((prev) => ({ ...prev, is_active: checked }))}
        />
      </div>
    </div>
  );
}

type EditServerFormFieldsProps = {
  form: EditServerForm;
  onChange: React.Dispatch<React.SetStateAction<EditServerForm | null>>;
};

export function EditServerFormFields({ form, onChange }: EditServerFormFieldsProps) {
  return (
    <div className="grid gap-4 py-2 md:grid-cols-2">
      <div className="space-y-2 md:col-span-2">
        <Label htmlFor="edit-description">Description</Label>
        <Input
          id="edit-description"
          value={form.description}
          onChange={(event) =>
            onChange((prev) => (prev ? { ...prev, description: event.target.value } : prev))
          }
        />
      </div>
      <ConfigFields
        timeout={form.timeout}
        retries={form.retries}
        wait_between_retries={form.wait_between_retries}
        max_requests_queued={form.max_requests_queued}
        onChange={(key, value) => onChange((prev) => (prev ? { ...prev, [key]: value } : prev))}
      />
      <div className="space-y-2">
        <Label htmlFor="edit-device-id">Device ID</Label>
        <Input
          id="edit-device-id"
          value={form.device_id}
          onChange={(event) =>
            onChange((prev) => (prev ? { ...prev, device_id: event.target.value } : prev))
          }
        />
      </div>
      <div className="space-y-2 md:col-span-2">
        <Label htmlFor="edit-notes">Notes</Label>
        <Textarea
          id="edit-notes"
          rows={3}
          value={form.notes}
          onChange={(event) =>
            onChange((prev) => (prev ? { ...prev, notes: event.target.value } : prev))
          }
        />
      </div>
      <Separator className="md:col-span-2" />
      <div className="flex items-center justify-between rounded-md border p-3 md:col-span-2">
        <div>
          <p className="text-sm font-medium">Active Status</p>
          <p className="text-xs text-muted-foreground">Ubah status aktif server ini.</p>
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
