import { RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { useOrchestration } from "../hooks/useOrchestration";

export function OrchestrationPage() {
  const vm = useOrchestration();
  const allSelected =
    vm.bindings.length > 0 && vm.selectedBindingIds.length === vm.bindings.length;

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Orchestration</h1>
        <p className="text-sm text-muted-foreground">
          Control worker loop start/pause/resume/stop untuk binding terpilih.
        </p>
      </header>

      {vm.errorMessage ? (
        <Card className="border-destructive/40 bg-destructive/10">
          <CardContent className="py-3 text-sm text-destructive">{vm.errorMessage}</CardContent>
        </Card>
      ) : null}

      <section className="grid gap-3 sm:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Workers</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold tracking-tight">
              {vm.monitorResult?.total_workers ?? 0}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Active Workers</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold tracking-tight">
              {vm.monitorResult?.active_workers ?? 0}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Selected Bindings</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold tracking-tight">
              {vm.selectedBindingIds.length}
            </p>
          </CardContent>
        </Card>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Start Config</CardTitle>
          <CardDescription>Parameter loop transaksi untuk worker baru.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-3">
          <label className="grid gap-1 text-sm">
            Product ID
            <input
              className="h-9 rounded-md border bg-background px-2"
              value={vm.startForm.product_id}
              onChange={(event) =>
                vm.setStartForm((prev) => ({ ...prev, product_id: event.target.value }))
              }
            />
          </label>
          <label className="grid gap-1 text-sm">
            Email
            <input
              className="h-9 rounded-md border bg-background px-2"
              value={vm.startForm.email}
              onChange={(event) =>
                vm.setStartForm((prev) => ({ ...prev, email: event.target.value }))
              }
            />
          </label>
          <label className="grid gap-1 text-sm">
            Limit Harga
            <input
              className="h-9 rounded-md border bg-background px-2"
              value={vm.startForm.limit_harga}
              onChange={(event) =>
                vm.setStartForm((prev) => ({ ...prev, limit_harga: event.target.value }))
              }
            />
          </label>
          <label className="grid gap-1 text-sm">
            Interval (ms)
            <input
              className="h-9 rounded-md border bg-background px-2"
              value={vm.startForm.interval_ms}
              onChange={(event) =>
                vm.setStartForm((prev) => ({ ...prev, interval_ms: event.target.value }))
              }
            />
          </label>
          <label className="grid gap-1 text-sm">
            Max Retry Status
            <input
              className="h-9 rounded-md border bg-background px-2"
              value={vm.startForm.max_retry_status}
              onChange={(event) =>
                vm.setStartForm((prev) => ({
                  ...prev,
                  max_retry_status: event.target.value,
                }))
              }
            />
          </label>
          <label className="grid gap-1 text-sm">
            Cooldown Error (ms)
            <input
              className="h-9 rounded-md border bg-background px-2"
              value={vm.startForm.cooldown_on_error_ms}
              onChange={(event) =>
                vm.setStartForm((prev) => ({
                  ...prev,
                  cooldown_on_error_ms: event.target.value,
                }))
              }
            />
          </label>
          <div className="sm:col-span-3 flex flex-wrap gap-2">
            <Button disabled={vm.isSubmitting || vm.selectedBindingIds.length === 0} onClick={() => void vm.startSelected()}>
              Start
            </Button>
            <Button
              variant="secondary"
              disabled={vm.isSubmitting || vm.selectedBindingIds.length === 0}
              onClick={() => void vm.pauseSelected()}
            >
              Pause
            </Button>
            <Button
              variant="secondary"
              disabled={vm.isSubmitting || vm.selectedBindingIds.length === 0}
              onClick={() => void vm.resumeSelected()}
            >
              Resume
            </Button>
            <Button
              variant="destructive"
              disabled={vm.isSubmitting || vm.selectedBindingIds.length === 0}
              onClick={() => void vm.stopSelected()}
            >
              Stop
            </Button>
            <Button
              variant="outline"
              disabled={vm.selectedBindingIds.length === 0}
              onClick={() => void vm.fetchStatus(vm.selectedBindingIds)}
            >
              Status Selected
            </Button>
            <Button variant="outline" onClick={() => void vm.loadMonitor()}>
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh Monitor
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Bindings</CardTitle>
          <CardDescription>Pilih binding yang akan dikontrol worker-nya.</CardDescription>
        </CardHeader>
        <CardContent className="max-h-[360px] overflow-auto rounded-md border p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">
                  <input
                    type="checkbox"
                    checked={allSelected}
                    onChange={(event) => vm.toggleSelectAll(event.target.checked)}
                  />
                </TableHead>
                <TableHead>ID</TableHead>
                <TableHead>Server</TableHead>
                <TableHead>MSISDN</TableHead>
                <TableHead>Batch</TableHead>
                <TableHead>Step</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {vm.bindings.map((binding) => (
                <TableRow key={binding.id}>
                  <TableCell>
                    <input
                      type="checkbox"
                      checked={vm.selectedBindingIds.includes(binding.id)}
                      onChange={(event) =>
                        vm.toggleSelectBinding(binding.id, event.target.checked)
                      }
                    />
                  </TableCell>
                  <TableCell>#{binding.id}</TableCell>
                  <TableCell className="font-mono text-xs">{binding.server_base_url ?? "-"}</TableCell>
                  <TableCell className="font-mono text-xs">{binding.account_msisdn ?? "-"}</TableCell>
                  <TableCell>{binding.batch_id}</TableCell>
                  <TableCell>{binding.step}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <section className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Status Result</CardTitle>
            <CardDescription>Hasil endpoint status untuk binding terpilih.</CardDescription>
          </CardHeader>
          <CardContent className="max-h-[300px] overflow-auto">
            <pre className="text-xs">{JSON.stringify(vm.statusResult, null, 2)}</pre>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Last Control Result</CardTitle>
            <CardDescription>Hasil eksekusi terakhir start/pause/resume/stop.</CardDescription>
          </CardHeader>
          <CardContent className="max-h-[300px] overflow-auto">
            <pre className="text-xs">{JSON.stringify(vm.lastControlResult, null, 2)}</pre>
          </CardContent>
        </Card>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Monitor</CardTitle>
          <CardDescription>Active workers, lock owner, dan heartbeat terkini.</CardDescription>
        </CardHeader>
        <CardContent className="max-h-[420px] overflow-auto rounded-md border p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Binding</TableHead>
                <TableHead>State</TableHead>
                <TableHead>Reason</TableHead>
                <TableHead>Lock Owner</TableHead>
                <TableHead>HB Owner</TableHead>
                <TableHead>HB Cycle</TableHead>
                <TableHead>HB Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(vm.monitorResult?.items ?? []).map((item) => (
                <TableRow key={`monitor-${item.binding_id}`}>
                  <TableCell>#{item.binding_id}</TableCell>
                  <TableCell>{item.state}</TableCell>
                  <TableCell>{item.reason ?? "-"}</TableCell>
                  <TableCell className="font-mono text-xs">{item.lock_owner ?? "-"}</TableCell>
                  <TableCell className="font-mono text-xs">{item.heartbeat_owner ?? "-"}</TableCell>
                  <TableCell>{item.heartbeat_cycle ?? "-"}</TableCell>
                  <TableCell className="font-mono text-xs">{item.heartbeat_last_action ?? "-"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </section>
  );
}

