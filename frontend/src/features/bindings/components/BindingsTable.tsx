import {
  BadgeCheck,
  KeyRound,
  Loader2,
  LogOut,
  MoreHorizontal,
  RefreshCw,
  ScanSearch,
  ShieldCheck,
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

import type { Binding } from "../types";

function badgeVariant(step: Binding["step"]): "default" | "secondary" | "destructive" {
  if (step === "logged_out") {
    return "secondary";
  }
  if (step === "otp_verification") {
    return "destructive";
  }
  return "default";
}

function tokenBadge(binding: Binding): { label: string; variant: "default" | "secondary" | "destructive" } {
  if (!binding.token_location || !binding.token_location_refreshed_at) {
    return { label: "Empty", variant: "secondary" };
  }
  const rawTs = binding.token_location_refreshed_at;
  const hasTz = /(?:Z|[+\-]\d{2}:\d{2})$/.test(rawTs);
  const normalizedTs = hasTz ? rawTs : `${rawTs}Z`;
  const refreshedAtMs = new Date(normalizedTs).getTime();
  const ageMinutes = (Date.now() - refreshedAtMs) / 60000;
  if (Number.isNaN(ageMinutes)) {
    return { label: "Stale", variant: "destructive" };
  }
  if (ageMinutes <= 10) {
    return { label: "Fresh", variant: "default" };
  }
  return { label: "Stale", variant: "destructive" };
}

type BindingsTableProps = {
  bindings: Binding[];
  selectedBindingIds: number[];
  allSelected: boolean;
  isLoading: boolean;
  pendingRowActions: Record<number, string>;
  onToggleSelectAll: (checked: boolean) => void;
  onToggleSelectBinding: (bindingId: number, checked: boolean) => void;
  onCheckBalance: (bindingId: number) => void;
  onRefreshTokenLocation: (bindingId: number) => void;
  onVerifyReseller: (bindingId: number) => void;
  onOpenRequestLogin: (binding: Binding) => void;
  onOpenVerify: (binding: Binding) => void;
  onOpenLogout: (binding: Binding) => void;
  onDelete: (bindingId: number) => void;
};

export function BindingsTable({
  bindings,
  selectedBindingIds,
  allSelected,
  isLoading,
  pendingRowActions,
  onToggleSelectAll,
  onToggleSelectBinding,
  onCheckBalance,
  onRefreshTokenLocation,
  onVerifyReseller,
  onOpenRequestLogin,
  onOpenVerify,
  onOpenLogout,
  onDelete,
}: BindingsTableProps) {
  return (
    <div className="min-h-[420px] overflow-x-auto">
      <Table className="table-fixed">
        <TableHeader>
          <TableRow>
            <TableHead className="w-[42px]">
              <Checkbox
                checked={allSelected}
                onCheckedChange={(checked) => onToggleSelectAll(Boolean(checked))}
              />
            </TableHead>
            <TableHead className="w-[80px]">ID</TableHead>
            <TableHead className="w-[220px]">Server</TableHead>
            <TableHead className="w-[220px]">Account</TableHead>
            <TableHead className="w-[150px]">Batch</TableHead>
            <TableHead className="w-[150px]">Step</TableHead>
            <TableHead className="w-[100px]">Reseller</TableHead>
            <TableHead className="w-[120px]">Balance</TableHead>
            <TableHead className="w-[100px]">token_loc</TableHead>
            <TableHead className="w-[160px]">Device</TableHead>
            <TableHead className="w-[90px] text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <TableRow>
              <TableCell colSpan={11} className="text-center text-muted-foreground">
                Loading bindings...
              </TableCell>
            </TableRow>
          ) : bindings.length === 0 ? (
            <TableRow>
              <TableCell colSpan={11} className="text-center text-muted-foreground">
                Belum ada binding.
              </TableCell>
            </TableRow>
          ) : (
            bindings.map((binding) => {
              const rowAction = pendingRowActions[binding.id];
              const isBusy = Boolean(rowAction);
              const tokenInfo = tokenBadge(binding);
              return (
                <TableRow key={binding.id}>
                  <TableCell>
                    <Checkbox
                      checked={selectedBindingIds.includes(binding.id)}
                      onCheckedChange={(checked) =>
                        onToggleSelectBinding(binding.id, Boolean(checked))
                      }
                    />
                  </TableCell>
                  <TableCell>#{binding.id}</TableCell>
                  <TableCell className="truncate text-xs">
                    {binding.server_base_url ? (
                      <span className="font-mono">{binding.server_base_url}</span>
                    ) : (
                      `ID ${binding.server_id}`
                    )}
                  </TableCell>
                  <TableCell className="truncate text-xs">
                    {binding.account_msisdn ? (
                      <span className="font-mono">
                        {binding.account_msisdn} ({binding.account_batch_id ?? binding.batch_id})
                      </span>
                    ) : (
                      `ID ${binding.account_id}`
                    )}
                  </TableCell>
                  <TableCell className="truncate text-xs">{binding.batch_id}</TableCell>
                  <TableCell>
                    <Badge variant={badgeVariant(binding.step)}>{binding.step}</Badge>
                  </TableCell>
                  <TableCell>{binding.is_reseller ? "Yes" : "No"}</TableCell>
                  <TableCell>
                    {binding.balance_start ?? "-"} / {binding.balance_last ?? "-"}
                  </TableCell>
                  <TableCell>
                    <Badge variant={tokenInfo.variant} title={binding.token_location_refreshed_at ?? "-"}>
                      {tokenInfo.label}
                    </Badge>
                  </TableCell>
                  <TableCell className="truncate font-mono text-xs">
                    {binding.device_id ?? binding.server_device_id ?? "-"}
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button size="icon" variant="outline" disabled={isBusy}>
                          {isBusy ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <MoreHorizontal className="h-4 w-4" />
                          )}
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => onCheckBalance(binding.id)}>
                          <BadgeCheck className="mr-2 h-4 w-4" /> Check Balance
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onRefreshTokenLocation(binding.id)}>
                          <RefreshCw className="mr-2 h-4 w-4" /> Refresh token_loc
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onVerifyReseller(binding.id)}>
                          <ScanSearch className="mr-2 h-4 w-4" /> Verify Reseller
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onOpenRequestLogin(binding)}>
                          <KeyRound className="mr-2 h-4 w-4" /> Request Login
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onOpenVerify(binding)}>
                          <ShieldCheck className="mr-2 h-4 w-4" /> Verify Login
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onOpenLogout(binding)}>
                          <LogOut className="mr-2 h-4 w-4" /> Logout
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-destructive"
                          onClick={() => onDelete(binding.id)}
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
