import { useEffect, useMemo, useState } from "react";
import { Plus, RefreshCw, ServerCog, Trash2, Upload } from "lucide-react";

import { Badge } from "@/components/ui/badge";
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
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { apiRequest } from "@/lib/api";
import type {
  Server,
  ServerBulkCreateResult,
  ServerBulkPayload,
  ServerCreatePayload,
} from "@/types/server";

type SingleServerForm = {
  host: string;
  port: number;
  description: string;
  timeout: number;
  retries: number;
  wait_between_retries: number;
  max_requests_queued: number;
  is_active: boolean;
  notes: string;
  device_id: string;
};

const defaultSingleForm: SingleServerForm = {
  host: "http://10.0.0.3",
  port: 9900,
  description: "",
  timeout: 10,
  retries: 3,
  wait_between_retries: 1,
  max_requests_queued: 5,
  is_active: true,
  notes: "",
  device_id: "",
};

type BulkServerForm = {
  base_host: string;
  start_port: number;
  end_port: number;
  description: string;
  timeout: number;
  retries: number;
  wait_between_retries: number;
  max_requests_queued: number;
  is_active: boolean;
  notes: string;
  device_id: string;
};

const defaultBulkForm: BulkServerForm = {
  base_host: "http://10.0.0.3",
  start_port: 9900,
  end_port: 9909,
  description: "",
  timeout: 10,
  retries: 3,
  wait_between_retries: 1,
  max_requests_queued: 5,
  is_active: true,
  notes: "",
  device_id: "",
};

function App() {
  const [servers, setServers] = useState<Server[]>([]);
  const [isLoadingServers, setIsLoadingServers] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [isSingleDialogOpen, setIsSingleDialogOpen] = useState(false);
  const [isBulkDialogOpen, setIsBulkDialogOpen] = useState(false);
  const [singleForm, setSingleForm] = useState<SingleServerForm>(defaultSingleForm);
  const [bulkForm, setBulkForm] = useState<BulkServerForm>(defaultBulkForm);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [bulkResult, setBulkResult] = useState<ServerBulkCreateResult | null>(null);

  const totalActive = useMemo(
    () => servers.filter((server) => server.is_active).length,
    [servers],
  );

  const totalInactive = servers.length - totalActive;

  useEffect(() => {
    document.documentElement.classList.add("dark");
    void loadServers();
  }, []);

  async function loadServers(): Promise<void> {
    try {
      setIsLoadingServers(true);
      setErrorMessage(null);
      const payload = await apiRequest<Server[]>("/v1/servers", "GET");
      setServers(payload);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
    } finally {
      setIsLoadingServers(false);
    }
  }

  async function createSingleServer(): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);

      const normalizedHost = singleForm.host.trim().replace(/\/+$/, "");
      const payload: ServerCreatePayload = {
        port: singleForm.port,
        base_url: `${normalizedHost}:${singleForm.port}`,
        description: singleForm.description || null,
        timeout: singleForm.timeout,
        retries: singleForm.retries,
        wait_between_retries: singleForm.wait_between_retries,
        max_requests_queued: singleForm.max_requests_queued,
        is_active: singleForm.is_active,
        notes: singleForm.notes || null,
        device_id: singleForm.device_id || null,
      };

      await apiRequest<Server>("/v1/servers", "POST", payload);
      setSingleForm(defaultSingleForm);
      setIsSingleDialogOpen(false);
      await loadServers();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
    } finally {
      setIsSubmitting(false);
    }
  }

  function buildBulkPayload(): ServerBulkPayload {
    return {
      ...bulkForm,
      base_host: bulkForm.base_host.trim().replace(/\/+$/, ""),
      description: bulkForm.description || null,
      notes: bulkForm.notes || null,
      device_id: bulkForm.device_id || null,
    };
  }

  async function runBulkDryRun(): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      const payload = buildBulkPayload();
      const result = await apiRequest<ServerBulkCreateResult>(
        "/v1/servers/bulk/dry-run",
        "POST",
        payload,
      );
      setBulkResult(result);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function createBulkServers(): Promise<void> {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      const payload = buildBulkPayload();
      const result = await apiRequest<ServerBulkCreateResult>(
        "/v1/servers/bulk",
        "POST",
        payload,
      );
      setBulkResult(result);
      setIsBulkDialogOpen(false);
      await loadServers();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function toggleServerStatus(server: Server): Promise<void> {
    try {
      setErrorMessage(null);
      await apiRequest<Server>(`/v1/servers/${server.id}/status`, "PATCH", {
        is_active: !server.is_active,
      });
      await loadServers();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
    }
  }

  async function deleteServer(serverId: number): Promise<void> {
    try {
      setErrorMessage(null);
      await apiRequest<void>(`/v1/servers/${serverId}`, "DELETE");
      await loadServers();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unknown error");
    }
  }

  return (
    <main className="mx-auto min-h-screen max-w-7xl space-y-6 px-4 py-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Server Management</h1>
        <p className="text-sm text-muted-foreground">
          Kelola endpoint server IDV per domain dengan mode single dan bulk.
        </p>
      </header>

      {errorMessage ? (
        <Card className="border-destructive/40 bg-destructive/10">
          <CardContent className="py-3 text-sm text-destructive">
            {errorMessage}
          </CardContent>
        </Card>
      ) : null}

      <section className="grid gap-3 sm:grid-cols-3">
        <StatCard title="Total" value={servers.length.toString()} />
        <StatCard title="Active" value={totalActive.toString()} />
        <StatCard title="Inactive" value={totalInactive.toString()} />
      </section>

      <Tabs defaultValue="server-list" className="space-y-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <TabsList>
            <TabsTrigger value="server-list">Server List</TabsTrigger>
            <TabsTrigger value="bulk-dry-run">Bulk Dry Run</TabsTrigger>
          </TabsList>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={() => void loadServers()}>
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
            <Dialog open={isBulkDialogOpen} onOpenChange={setIsBulkDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="outline">
                  <Upload className="mr-2 h-4 w-4" /> Add Bulk
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-3xl">
                <DialogHeader>
                  <DialogTitle>Bulk Add Servers</DialogTitle>
                  <DialogDescription>
                    Buat banyak server sekaligus dari host dan port range.
                  </DialogDescription>
                </DialogHeader>
                <BulkServerFormFields form={bulkForm} onChange={setBulkForm} />
                <DialogFooter>
                  <Button
                    variant="secondary"
                    onClick={() => void runBulkDryRun()}
                    disabled={isSubmitting}
                  >
                    Dry Run
                  </Button>
                  <Button onClick={() => void createBulkServers()} disabled={isSubmitting}>
                    Create Servers
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            <Dialog open={isSingleDialogOpen} onOpenChange={setIsSingleDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" /> Add Single
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Add Single Server</DialogTitle>
                  <DialogDescription>
                    Buat satu endpoint server dengan parameter lengkap.
                  </DialogDescription>
                </DialogHeader>
                <SingleServerFormFields form={singleForm} onChange={setSingleForm} />
                <DialogFooter>
                  <Button onClick={() => void createSingleServer()} disabled={isSubmitting}>
                    Save
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        <TabsContent value="server-list">
          <Card>
            <CardHeader>
              <CardTitle>Servers</CardTitle>
              <CardDescription>
                Menampilkan endpoint aktif/non-aktif beserta konfigurasi retry.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>ID</TableHead>
                      <TableHead>Base URL</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead>Device ID</TableHead>
                      <TableHead>Timeout</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Updated</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {isLoadingServers ? (
                      <TableRow>
                        <TableCell colSpan={8} className="text-center text-muted-foreground">
                          Loading servers...
                        </TableCell>
                      </TableRow>
                    ) : servers.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={8} className="text-center text-muted-foreground">
                          Belum ada server.
                        </TableCell>
                      </TableRow>
                    ) : (
                      servers.map((server) => (
                        <TableRow key={server.id}>
                          <TableCell>#{server.id}</TableCell>
                          <TableCell className="font-mono text-xs">{server.base_url}</TableCell>
                          <TableCell>{server.description ?? "-"}</TableCell>
                          <TableCell className="font-mono text-xs">
                            {server.device_id ?? "-"}
                          </TableCell>
                          <TableCell>{server.timeout}s</TableCell>
                          <TableCell>
                            <Badge variant={server.is_active ? "default" : "secondary"}>
                              {server.is_active ? "Active" : "Inactive"}
                            </Badge>
                          </TableCell>
                          <TableCell>{new Date(server.updated_at).toLocaleString()}</TableCell>
                          <TableCell className="space-x-2 text-right">
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => void toggleServerStatus(server)}
                            >
                              <ServerCog className="mr-1 h-4 w-4" /> Toggle
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => void deleteServer(server.id)}
                            >
                              <Trash2 className="mr-1 h-4 w-4" /> Delete
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="bulk-dry-run" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Bulk Dry Run</CardTitle>
              <CardDescription>
                Preview hasil bulk sebelum commit create ke database.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <BulkServerFormFields form={bulkForm} onChange={setBulkForm} />
              <div className="flex gap-2">
                <Button variant="secondary" onClick={() => void runBulkDryRun()}>
                  Dry Run
                </Button>
                <Button onClick={() => void createBulkServers()}>Create</Button>
              </div>
            </CardContent>
          </Card>

          {bulkResult ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  Bulk Result
                  <Badge variant={bulkResult.dry_run ? "secondary" : "default"}>
                    {bulkResult.dry_run ? "DRY RUN" : "CREATED"}
                  </Badge>
                </CardTitle>
                <CardDescription>
                  Requested: {bulkResult.total_requested} | Created: {bulkResult.total_created} |
                  Skipped: {bulkResult.total_skipped} | Failed: {bulkResult.total_failed}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Port</TableHead>
                        <TableHead>Base URL</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Reason</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {bulkResult.items.map((item) => (
                        <TableRow key={item.base_url}>
                          <TableCell>{item.port}</TableCell>
                          <TableCell className="font-mono text-xs">{item.base_url}</TableCell>
                          <TableCell>{item.status}</TableCell>
                          <TableCell>{item.reason ?? "-"}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          ) : null}
        </TabsContent>
      </Tabs>
    </main>
  );
}

type StatCardProps = {
  title: string;
  value: string;
};

function StatCard({ title, value }: StatCardProps) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{title}</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-3xl font-semibold tracking-tight">{value}</p>
      </CardContent>
    </Card>
  );
}

type SingleServerFormFieldsProps = {
  form: SingleServerForm;
  onChange: React.Dispatch<React.SetStateAction<SingleServerForm>>;
};

function SingleServerFormFields({ form, onChange }: SingleServerFormFieldsProps) {
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
          onChange={(event) =>
            onChange((prev) => ({ ...prev, description: event.target.value }))
          }
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

function BulkServerFormFields({ form, onChange }: BulkServerFormFieldsProps) {
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
          onChange={(event) =>
            onChange((prev) => ({ ...prev, start_port: Number(event.target.value) }))
          }
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
          onChange={(event) =>
            onChange((prev) => ({ ...prev, description: event.target.value }))
          }
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

export default App;
