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

import {
  BulkAccountFormFields,
  EditAccountFormFields,
  SingleAccountFormFields,
} from "../components/AccountForms";
import { AccountsTable } from "../components/AccountsTable";
import { useAccounts } from "../hooks/useAccounts";

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

export function AccountsPage() {
  const vm = useAccounts();

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Account Management</h1>
        <p className="text-sm text-muted-foreground">
          Kelola data MSISDN, batch, dan status akun.
        </p>
      </header>

      {vm.errorMessage ? (
        <Card className="border-destructive/40 bg-destructive/10">
          <CardContent className="py-3 text-sm text-destructive">{vm.errorMessage}</CardContent>
        </Card>
      ) : null}

      <section className="grid gap-3 sm:grid-cols-3">
        <StatCard title="Total" value={vm.accounts.length.toString()} />
        <StatCard title="Reseller" value={vm.totalReseller.toString()} />
        <StatCard
          title="Selected"
          value={vm.selectedCount.toString()}
        />
      </section>

      <div className="flex flex-wrap gap-2">
        <Button variant="secondary" onClick={() => void vm.loadAccounts()}>
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
              <DialogTitle>Bulk Add Accounts</DialogTitle>
              <DialogDescription>
                Masukkan list MSISDN, email dan batch untuk create banyak account.
              </DialogDescription>
            </DialogHeader>
            <BulkAccountFormFields form={vm.bulkForm} onChange={vm.setBulkForm} />
            <DialogFooter>
              <Button onClick={() => void vm.createBulkAccounts()} disabled={vm.isSubmitting}>
                Create Accounts
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
              <DialogTitle>Add Single Account</DialogTitle>
              <DialogDescription>
                Buat satu account MSISDN dengan email dan batch.
              </DialogDescription>
            </DialogHeader>
            <SingleAccountFormFields form={vm.singleForm} onChange={vm.setSingleForm} />
            <DialogFooter>
              <Button onClick={() => void vm.createSingleAccount()} disabled={vm.isSubmitting}>
                Save
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Accounts</CardTitle>
          <CardDescription>
            Data account dengan status dan informasi balance terakhir.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <AccountsTable
            accounts={vm.accounts}
            selectedAccountIds={vm.selectedAccountIds}
            isLoadingAccounts={vm.isLoadingAccounts}
            allSelected={vm.allSelected}
            pendingRowActions={vm.pendingRowActions}
            onToggleSelectAll={vm.toggleSelectAll}
            onToggleSelectAccount={vm.toggleSelectAccount}
            onOpenEditAccount={vm.openEditAccount}
            onOpenDeleteConfirm={vm.openDeleteConfirm}
          />
        </CardContent>
      </Card>

      <Dialog open={vm.isEditDialogOpen} onOpenChange={vm.setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Account</DialogTitle>
            <DialogDescription>Update data account yang dipilih.</DialogDescription>
          </DialogHeader>
          {vm.editForm ? <EditAccountFormFields form={vm.editForm} onChange={vm.setEditForm} /> : null}
          <DialogFooter>
            <Button variant="secondary" onClick={() => vm.setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => void vm.saveEditAccount()} disabled={vm.isSubmitting}>
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AlertDialog open={vm.isDeleteConfirmOpen} onOpenChange={vm.setIsDeleteConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete account?</AlertDialogTitle>
            <AlertDialogDescription>
              Account akan dihapus permanen dari database.
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
            <AlertDialogTitle>Delete selected accounts?</AlertDialogTitle>
            <AlertDialogDescription>
              Total {vm.selectedCount} account akan dihapus.
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
