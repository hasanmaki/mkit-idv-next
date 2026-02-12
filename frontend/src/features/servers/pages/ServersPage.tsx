import { Plus, RefreshCw, Trash2, Upload } from "lucide-react";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

import {
  BulkServerFormFields,
  EditServerFormFields,
  SingleServerFormFields,
} from "../components/ServerForms";
import { ServersTable } from "../components/ServersTable";
import { useServers } from "../hooks/useServers";

function StatCard({ title, value }: { title: string; value: string }) {
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

export function ServersPage() {
  const vm = useServers();

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Server Management</h1>
        <p className="text-sm text-muted-foreground">
          Kelola endpoint server IDV per domain dengan mode single dan bulk.
        </p>
      </header>

      {vm.errorMessage ? (
        <Card className="border-destructive/40 bg-destructive/10">
          <CardContent className="py-3 text-sm text-destructive">{vm.errorMessage}</CardContent>
        </Card>
      ) : null}

      <section className="grid gap-3 sm:grid-cols-3">
        <StatCard title="Total" value={vm.servers.length.toString()} />
        <StatCard title="Active" value={vm.totalActive.toString()} />
        <StatCard title="Inactive" value={vm.totalInactive.toString()} />
      </section>

      <Tabs defaultValue="server-list" className="space-y-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <TabsList>
            <TabsTrigger value="server-list">Server List</TabsTrigger>
            <TabsTrigger value="bulk-dry-run">Bulk Dry Run</TabsTrigger>
          </TabsList>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={() => void vm.loadServers()}>
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
            <Button
              variant="destructive"
              disabled={vm.selectedCount === 0 || vm.isSubmitting}
              onClick={() => vm.setIsBulkDeleteConfirmOpen(true)}
            >
              <Trash2 className="mr-2 h-4 w-4" /> Delete Selected ({vm.selectedCount})
            </Button>

            <Dialog open={vm.isBulkDialogOpen} onOpenChange={vm.setIsBulkDialogOpen}>
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
                <BulkServerFormFields form={vm.bulkForm} onChange={vm.setBulkForm} />
                <DialogFooter>
                  <Button variant="secondary" onClick={() => void vm.runBulkDryRun()} disabled={vm.isSubmitting}>
                    Dry Run
                  </Button>
                  <Button onClick={() => void vm.createBulkServers()} disabled={vm.isSubmitting}>
                    Create Servers
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            <Dialog open={vm.isSingleDialogOpen} onOpenChange={vm.setIsSingleDialogOpen}>
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
                <SingleServerFormFields form={vm.singleForm} onChange={vm.setSingleForm} />
                <DialogFooter>
                  <Button onClick={() => void vm.createSingleServer()} disabled={vm.isSubmitting}>
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
              <ServersTable
                servers={vm.servers}
                selectedServerIds={vm.selectedServerIds}
                isLoadingServers={vm.isLoadingServers}
                allSelected={vm.allSelected}
                pendingRowActions={vm.pendingRowActions}
                onToggleSelectAll={vm.toggleSelectAll}
                onToggleSelectServer={vm.toggleSelectServer}
                onOpenEditServer={vm.openEditServer}
                onToggleServerStatus={vm.toggleServerStatus}
                onOpenDeleteConfirm={vm.openDeleteConfirm}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="bulk-dry-run" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Bulk Dry Run</CardTitle>
              <CardDescription>Preview hasil bulk sebelum commit create ke database.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <BulkServerFormFields form={vm.bulkForm} onChange={vm.setBulkForm} />
              <div className="flex gap-2">
                <Button variant="secondary" onClick={() => void vm.runBulkDryRun()}>
                  Dry Run
                </Button>
                <Button onClick={() => void vm.createBulkServers()}>Create</Button>
              </div>
            </CardContent>
          </Card>

          {vm.bulkResult ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  Bulk Result
                  <Badge variant={vm.bulkResult.dry_run ? "secondary" : "default"}>
                    {vm.bulkResult.dry_run ? "DRY RUN" : "CREATED"}
                  </Badge>
                </CardTitle>
                <CardDescription>
                  Requested: {vm.bulkResult.total_requested} | Created: {vm.bulkResult.total_created} | Skipped: {vm.bulkResult.total_skipped} | Failed: {vm.bulkResult.total_failed}
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
                      {vm.bulkResult.items.map((item) => (
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

      <Dialog open={vm.isEditDialogOpen} onOpenChange={vm.setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Server</DialogTitle>
            <DialogDescription>Update konfigurasi server yang dipilih.</DialogDescription>
          </DialogHeader>
          {vm.editForm ? <EditServerFormFields form={vm.editForm} onChange={vm.setEditForm} /> : null}
          <DialogFooter>
            <Button variant="secondary" onClick={() => vm.setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => void vm.saveEditServer()} disabled={vm.isSubmitting}>
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AlertDialog open={vm.isDeleteConfirmOpen} onOpenChange={vm.setIsDeleteConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete server?</AlertDialogTitle>
            <AlertDialogDescription>
              Server akan dinonaktifkan dulu, lalu dihapus. Aksi ini tidak bisa dibatalkan.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={vm.isSubmitting}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={() => void vm.confirmDeleteSingle()} disabled={vm.isSubmitting}>
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={vm.isBulkDeleteConfirmOpen} onOpenChange={vm.setIsBulkDeleteConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete selected servers?</AlertDialogTitle>
            <AlertDialogDescription>
              Total {vm.selectedCount} server akan dinonaktifkan lalu dihapus.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={vm.isSubmitting}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={() => void vm.confirmDeleteSelected()} disabled={vm.isSubmitting}>
              Delete All
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </section>
  );
}
