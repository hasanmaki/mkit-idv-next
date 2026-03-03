import { Loader2, MoreHorizontal, PenSquare, ServerCog, Trash2, Users, UserPlus, Eye } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Order } from "../types";

type OrdersTableProps = {
  orders: Order[];
  selectedOrderIds: number[];
  isLoadingOrders: boolean;
  allSelected: boolean;
  pendingRowActions: Record<number, string>;
  onToggleSelectAll: (checked: boolean) => void;
  onToggleSelectOrder: (orderId: number, checked: boolean) => void;
  onOpenEditOrder: (order: Order) => void;
  onToggleOrderStatus: (order: Order) => Promise<void>;
  onOpenDeleteConfirm: (orderId: number) => void;
  onAddAccount: (orderId: number) => void;
  onNavigateToAccounts: (orderId: number) => void;
};

export function OrdersTable({
  orders,
  selectedOrderIds,
  isLoadingOrders,
  allSelected,
  pendingRowActions,
  onToggleSelectAll,
  onToggleSelectOrder,
  onOpenEditOrder,
  onToggleOrderStatus,
  onOpenDeleteConfirm,
  onAddAccount,
  onNavigateToAccounts,
}: OrdersTableProps) {
  return (
    <div className="min-h-[440px] overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[42px]">
              <Checkbox
                checked={allSelected}
                onCheckedChange={(checked) => onToggleSelectAll(Boolean(checked))}
              />
            </TableHead>
            <TableHead className="w-[90px]">ID</TableHead>
            <TableHead>Name</TableHead>
            <TableHead>Email</TableHead>
            <TableHead className="w-[120px]">Accounts</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="w-[120px]">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoadingOrders ? (
            <TableRow>
              <TableCell colSpan={7} className="h-32 text-center">
                <div className="flex items-center justify-center gap-2">
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Loading orders...
                </div>
              </TableCell>
            </TableRow>
          ) : orders.length === 0 ? (
            <TableRow>
              <TableCell colSpan={7} className="h-32 text-center text-muted-foreground">
                No orders found
              </TableCell>
            </TableRow>
          ) : (
            orders.map((order) => {
              const isPending = pendingRowActions[order.id] !== undefined;
              return (
                <TableRow key={order.id}>
                  <TableCell>
                    <Checkbox
                      checked={selectedOrderIds.includes(order.id)}
                      onCheckedChange={(checked) =>
                        onToggleSelectOrder(order.id, Boolean(checked))
                      }
                      disabled={isPending}
                    />
                  </TableCell>
                  <TableCell className="font-mono text-xs">#{order.id}</TableCell>
                  <TableCell className="font-medium">{order.name}</TableCell>
                  <TableCell className="text-sm">{order.email}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4 text-muted-foreground" />
                      <Badge variant={order.account_count > 0 ? "outline" : "destructive"}>
                        {order.account_count} {order.account_count === 1 ? 'account' : 'accounts'}
                      </Badge>
                      {order.account_count === 0 && (
                        <span className="text-xs text-destructive">⚠️ No accounts</span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={order.is_active ? "default" : "secondary"}>
                      {order.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild disabled={isPending}>
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => onNavigateToAccounts(order.id)}>
                          <Eye className="mr-2 h-4 w-4" />
                          View Accounts ({order.account_count})
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onAddAccount(order.id)}>
                          <UserPlus className="mr-2 h-4 w-4" />
                          Add Account
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onOpenEditOrder(order)}>
                          <PenSquare className="mr-2 h-4 w-4" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onToggleOrderStatus(order)}>
                          <ServerCog className="mr-2 h-4 w-4" />
                          Toggle Status
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => onOpenDeleteConfirm(order.id)}
                          className="text-destructive"
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              );
            })
          )}
        </TableBody>
      </Table>
    </div>
  );
}
