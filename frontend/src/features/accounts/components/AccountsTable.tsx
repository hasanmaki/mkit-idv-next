import {
  Loader2,
  MoreHorizontal,
  PenSquare,
  Trash2,
} from "lucide-react";

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

import type { Account } from "../types";

function statusBadgeVariant(status: Account["status"]): "default" | "secondary" | "destructive" {
  if (status === "active") {
    return "default";
  }
  if (status === "disabled") {
    return "destructive";
  }
  return "secondary";
}

type AccountsTableProps = {
  accounts: Account[];
  selectedAccountIds: number[];
  isLoadingAccounts: boolean;
  allSelected: boolean;
  pendingRowActions: Record<number, string>;
  onToggleSelectAll: (checked: boolean) => void;
  onToggleSelectAccount: (accountId: number, checked: boolean) => void;
  onOpenEditAccount: (account: Account) => void;
  onOpenDeleteConfirm: (accountId: number) => void;
};

export function AccountsTable({
  accounts,
  selectedAccountIds,
  isLoadingAccounts,
  allSelected,
  pendingRowActions,
  onToggleSelectAll,
  onToggleSelectAccount,
  onOpenEditAccount,
  onOpenDeleteConfirm,
}: AccountsTableProps) {
  return (
    <div className="min-h-[440px] overflow-x-auto">
      <Table className="table-fixed">
        <TableHeader>
          <TableRow>
            <TableHead className="w-[42px]">
              <Checkbox checked={allSelected} onCheckedChange={(checked) => onToggleSelectAll(Boolean(checked))} />
            </TableHead>
            <TableHead className="w-[90px]">ID</TableHead>
            <TableHead className="w-[170px]">MSISDN</TableHead>
            <TableHead className="w-[220px]">Email</TableHead>
            <TableHead className="w-[170px]">Batch</TableHead>
            <TableHead className="w-[120px]">Status</TableHead>
            <TableHead className="w-[90px]">Reseller</TableHead>
            <TableHead className="w-[120px]">Balance</TableHead>
            <TableHead className="w-[90px] text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoadingAccounts ? (
            <TableRow>
              <TableCell colSpan={9} className="text-center text-muted-foreground">
                Loading accounts...
              </TableCell>
            </TableRow>
          ) : accounts.length === 0 ? (
            <TableRow>
              <TableCell colSpan={9} className="text-center text-muted-foreground">
                Belum ada account.
              </TableCell>
            </TableRow>
          ) : (
            accounts.map((account) => {
              const rowAction = pendingRowActions[account.id];
              const isRowBusy = Boolean(rowAction);

              return (
                <TableRow key={account.id}>
                  <TableCell>
                    <Checkbox
                      checked={selectedAccountIds.includes(account.id)}
                      onCheckedChange={(checked) =>
                        onToggleSelectAccount(account.id, Boolean(checked))
                      }
                    />
                  </TableCell>
                  <TableCell>#{account.id}</TableCell>
                  <TableCell className="font-mono text-xs">{account.msisdn}</TableCell>
                  <TableCell className="truncate text-xs">{account.email}</TableCell>
                  <TableCell className="truncate text-xs">{account.batch_id}</TableCell>
                  <TableCell>
                    <Badge variant={statusBadgeVariant(account.status)}>{account.status}</Badge>
                  </TableCell>
                  <TableCell>{account.is_reseller ? "Yes" : "No"}</TableCell>
                  <TableCell>{account.balance_last ?? "-"}</TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button size="icon" variant="outline" disabled={isRowBusy}>
                          {isRowBusy ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <MoreHorizontal className="h-4 w-4" />
                          )}
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem disabled={isRowBusy} onClick={() => onOpenEditAccount(account)}>
                          <PenSquare className="mr-2 h-4 w-4" />
                          {rowAction === "edit" ? "Updating..." : "Edit"}
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          disabled={isRowBusy}
                          className="text-destructive"
                          onClick={() => onOpenDeleteConfirm(account.id)}
                        >
                          <Trash2 className="mr-2 h-4 w-4" /> Delete
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
