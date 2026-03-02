import { Plus, RefreshCw, Trash2 } from "lucide-react";

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

import { CreateSessionFormFields, EditSessionFormFields } from "../components/SessionForms";
import { SessionsTable } from "../components/SessionsTable";
import { useSessions } from "../hooks/useSessions";

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

export function SessionsPage() {
  const vm = useSessions();

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Session Management</h1>
        <p className="text-sm text-muted-foreground">
          Kelola session user/operator untuk binding ke multiple servers.
        </p>
      </header>

      {vm.errorMessage ? (
        <Card className="border-destructive/40 bg-destructive/10">
          <CardContent className="py-3 text-sm text-destructive">{vm.errorMessage}</CardContent>
        </Card>
      ) : null}

      <section className="grid gap-3 sm:grid-cols-3">
        <StatCard title="Total" value={vm.sessions.length.toString()} />
        <StatCard title="Active" value={vm.totalActive.toString()} />
        <StatCard title="Inactive" value={vm.totalInactive.toString()} />
      </section>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Sessions</CardTitle>
              <CardDescription>
                Menampilkan session aktif/non-aktif beserta informasi lengkap.
              </CardDescription>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button variant="secondary" onClick={() => void vm.loadSessions()}>
                <RefreshCw className="mr-2 h-4 w-4" /> Refresh
              </Button>
              <Button
                variant="destructive"
                disabled={vm.selectedCount === 0 || vm.isSubmitting}
                onClick={() => vm.setIsBulkDeleteConfirmOpen(true)}
              >
                <Trash2 className="mr-2 h-4 w-4" /> Delete Selected ({vm.selectedCount})
              </Button>

              <Dialog open={vm.isCreateDialogOpen} onOpenChange={vm.setIsCreateDialogOpen}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="mr-2 h-4 w-4" /> Add Session
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-lg">
                  <DialogHeader>
                    <DialogTitle>Create Session</DialogTitle>
                    <DialogDescription>
                      Buat session user/operator baru untuk binding ke servers.
                    </DialogDescription>
                  </DialogHeader>
                  <CreateSessionFormFields form={vm.createForm} onChange={vm.setCreateForm} />
                  <DialogFooter>
                    <Button onClick={() => void vm.createSession()} disabled={vm.isSubmitting}>
                      Save
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <SessionsTable
            sessions={vm.sessions}
            selectedSessionIds={vm.selectedSessionIds}
            isLoadingSessions={vm.isLoadingSessions}
            allSelected={vm.allSelected}
            pendingRowActions={vm.pendingRowActions}
            onToggleSelectAll={vm.toggleSelectAll}
            onToggleSelectSession={vm.toggleSelectSession}
            onOpenEditSession={vm.openEditSession}
            onToggleSessionStatus={vm.toggleSessionStatus}
            onOpenDeleteConfirm={vm.openDeleteConfirm}
          />
        </CardContent>
      </Card>

      <Dialog open={vm.isEditDialogOpen} onOpenChange={vm.setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Edit Session</DialogTitle>
            <DialogDescription>Update informasi session yang dipilih.</DialogDescription>
          </DialogHeader>
          {vm.editForm ? (
            <EditSessionFormFields form={vm.editForm} onChange={vm.setEditForm} />
          ) : null}
          <DialogFooter>
            <Button variant="secondary" onClick={() => vm.setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => void vm.saveEditSession()} disabled={vm.isSubmitting}>
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AlertDialog open={vm.isDeleteConfirmOpen} onOpenChange={vm.setIsDeleteConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete session?</AlertDialogTitle>
            <AlertDialogDescription>
              Session akan dihapus. Ini juga akan menghapus semua binding terkait.
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

      <AlertDialog
        open={vm.isBulkDeleteConfirmOpen}
        onOpenChange={vm.setIsBulkDeleteConfirmOpen}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete selected sessions?</AlertDialogTitle>
            <AlertDialogDescription>
              Total {vm.selectedCount} session akan dihapus beserta semua binding terkait.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={vm.isSubmitting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => void vm.confirmDeleteSelected()}
              disabled={vm.isSubmitting}
            >
              Delete All
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </section>
  );
}
