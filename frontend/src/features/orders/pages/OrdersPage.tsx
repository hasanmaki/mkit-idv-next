import { useState } from "react";
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

import { CreateOrderFormFields } from "../components/OrderForms";
import { OrdersTable } from "../components/OrdersTable";
import { useOrders } from "../hooks/useOrders";

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

export function OrdersPage() {
  const vm = useOrders();

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Order Management</h1>
        <p className="text-sm text-muted-foreground">
          Kelola customer orders untuk binding ke multiple servers.
        </p>
      </header>

      <section className="grid gap-3 sm:grid-cols-3">
        <StatCard title="Total" value={vm.orders.length.toString()} />
        <StatCard title="Active" value={vm.totalActive.toString()} />
        <StatCard title="Inactive" value={vm.totalInactive.toString()} />
      </section>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Orders</CardTitle>
              <CardDescription>
                Menampilkan order aktif/non-aktif beserta informasi lengkap.
              </CardDescription>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button variant="secondary" onClick={() => void vm.loadOrders()}>
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
                    <Plus className="mr-2 h-4 w-4" /> Add Order
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-lg">
                  <DialogHeader>
                    <DialogTitle>Add Order</DialogTitle>
                    <DialogDescription>
                      Buat order customer baru dengan email unik.
                    </DialogDescription>
                  </DialogHeader>
                  <CreateOrderFormFields form={vm.createForm} onChange={vm.setCreateForm} />
                  <DialogFooter>
                    <Button onClick={() => void vm.createOrder()} disabled={vm.isSubmitting}>
                      Save
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <OrdersTable
            orders={vm.orders}
            selectedOrderIds={vm.selectedOrderIds}
            isLoadingOrders={vm.isLoadingOrders}
            allSelected={vm.allSelected}
            pendingRowActions={vm.pendingRowActions}
            onToggleSelectAll={vm.toggleSelectAll}
            onToggleSelectOrder={vm.toggleSelectOrder}
            onToggleOrderStatus={vm.toggleOrderStatus}
            onOpenDeleteConfirm={vm.openDeleteConfirm}
          />
        </CardContent>
      </Card>

      <AlertDialog open={vm.isDeleteConfirmOpen} onOpenChange={vm.setIsDeleteConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete order?</AlertDialogTitle>
            <AlertDialogDescription>
              Order akan dihapus beserta semua binding terkait. Aksi ini tidak bisa dibatalkan.
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
            <AlertDialogTitle>Delete selected orders?</AlertDialogTitle>
            <AlertDialogDescription>
              Total {vm.selectedCount} order akan dihapus beserta semua binding terkait.
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
