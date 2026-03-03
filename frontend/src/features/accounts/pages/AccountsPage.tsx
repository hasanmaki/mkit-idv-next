import { useEffect } from "react";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

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

  // Read order_id from URL params
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const orderId = params.get("order_id");
    if (orderId) {
      vm.setFilters((prev) => ({ ...prev, order_id: Number(orderId) }));
    }
  }, []);

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
        <StatCard title="Active" value={vm.accounts.filter(a => a.is_active).length.toString()} />
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
                Masukkan list MSISDN untuk create banyak account.
              </DialogDescription>
            </DialogHeader>
            <BulkAccountFormFields
              form={vm.bulkForm}
              onChange={vm.setBulkForm}
              orders={vm.orders}
              isLoadingOrders={vm.isLoadingOrders}
            />
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
                Buat satu account MSISDN dengan email.
              </DialogDescription>
            </DialogHeader>
            <SingleAccountFormFields
              form={vm.singleForm}
              onChange={vm.setSingleForm}
              orders={vm.orders}
              isLoadingOrders={vm.isLoadingOrders}
            />
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
          <CardTitle>Search & Filter</CardTitle>
          <CardDescription>Filter account berdasarkan msisdn, email, active status.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="filter-msisdn">MSISDN</Label>
              <Input
                id="filter-msisdn"
                value={vm.filters.msisdn}
                onChange={(event) =>
                  vm.setFilters((prev) => ({ ...prev, msisdn: event.target.value }))
                }
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="filter-email">Email</Label>
              <Input
                id="filter-email"
                value={vm.filters.email}
                onChange={(event) =>
                  vm.setFilters((prev) => ({ ...prev, email: event.target.value }))
                }
              />
            </div>
            <div className="space-y-2">
              <Label>Active Status</Label>
              <Select
                value={vm.filters.is_active || "__all__"}
                onValueChange={(value) =>
                  vm.setFilters((prev) => ({
                    ...prev,
                    is_active: value === "__all__" ? "" : (value as typeof prev.is_active),
                  }))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="All" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="__all__">All</SelectItem>
                  <SelectItem value="true">Yes</SelectItem>
                  <SelectItem value="false">No</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => void vm.applyFilters()}>
              Apply
            </Button>
            <Button variant="outline" onClick={() => void vm.resetFilters()}>
              Reset
            </Button>
          </div>
        </CardContent>
      </Card>

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
