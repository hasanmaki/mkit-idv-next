import { Loader2, MoreHorizontal, LogOut, RefreshCcw, Settings, Wallet, UserCheck, ShieldCheck } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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

type BindingsTableProps = {
  bindings: Binding[];
  isLoadingBindings: boolean;
  pendingRowActions: Record<number, string>;
  onRequestOTP: (bindingId: number) => void;
  onVerifyOTP: (bindingId: number) => void;
  onSetBalance: (bindingId: number) => void;
  onRelease: (bindingId: number) => void;
};

export function BindingsTable({
  bindings,
  isLoadingBindings,
  pendingRowActions,
  onRequestOTP,
  onVerifyOTP,
  onSetBalance,
  onRelease,
}: BindingsTableProps) {
  const getStepColor = (step: string) => {
    switch (step) {
      case "BINDED":
        return "secondary";
      case "REQUEST_OTP":
        return "warning";
      case "VERIFIED":
        return "default";
      case "CHECK_BALANCE":
        return "info";
      case "COMPLETED":
        return "success";
      case "LOGGED_OUT":
        return "outline";
      default:
        return "secondary";
    }
  };

  return (
    <div className="min-h-[440px] overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[80px]">ID</TableHead>
            <TableHead className="w-[100px]">Order/Session</TableHead>
            <TableHead className="w-[100px]">Server</TableHead>
            <TableHead className="w-[120px]">Account</TableHead>
            <TableHead className="w-[130px]">Reseller</TableHead>
            <TableHead className="w-[140px]">Step</TableHead>
            <TableHead className="w-[120px]">Balance</TableHead>
            <TableHead className="w-[150px]">Token Info</TableHead>
            <TableHead className="w-[90px] text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoadingBindings ? (
            <TableRow>
              <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">
                <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
                Loading bindings...
              </TableCell>
            </TableRow>
          ) : bindings.length === 0 ? (
            <TableRow>
              <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">
                Belum ada bindings aktif.
              </TableCell>
            </TableRow>
          ) : (
            bindings.map((binding) => {
              const rowAction = pendingRowActions[binding.id];
              const isRowBusy = Boolean(rowAction);

              return (
                <TableRow key={binding.id}>
                  <TableCell className="font-mono text-xs">#{binding.id}</TableCell>
                  <TableCell>
                    <div className="font-medium text-sm">Session #{binding.order_id}</div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">Server #{binding.server_id}</div>
                  </TableCell>
                  <TableCell>
                    <div className="font-medium text-sm">Acc #{binding.account_id}</div>
                  </TableCell>
                  <TableCell>
                    {binding.is_reseller ? (
                      <Badge variant="default" className="bg-blue-600 hover:bg-blue-700">
                        <UserCheck className="mr-1 h-3 w-3" /> Reseller
                      </Badge>
                    ) : (
                      <span className="text-muted-foreground text-xs">Normal</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge variant={getStepColor(binding.step) as any}>{binding.step}</Badge>
                  </TableCell>
                  <TableCell>
                    {binding.balance_start !== null ? (
                      <div className="text-sm">
                        <span className="font-bold text-green-600">
                          Rp{binding.balance_start.toLocaleString()}
                        </span>
                      </div>
                    ) : (
                      <span className="text-muted-foreground text-xs italic">Not Checked</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {binding.token_location ? (
                      <div className="flex items-center text-[10px] font-mono text-muted-foreground truncate max-w-[140px]" title={binding.token_location}>
                        <ShieldCheck className="mr-1 h-3 w-3 text-green-500 shrink-0" />
                        {binding.token_location.split('/').pop()}
                      </div>
                    ) : (
                      <span className="text-[10px] text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button size="icon" variant="ghost" disabled={isRowBusy}>
                          {isRowBusy ? (
                            <Loader2 className="h-4 w-4 animate-spin text-primary" />
                          ) : (
                            <MoreHorizontal className="h-4 w-4" />
                          )}
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        {(binding.step === "BINDED" || binding.step === "LOGGED_OUT") && (
                          <DropdownMenuItem
                            disabled={isRowBusy}
                            onClick={() => onRequestOTP(binding.id)}
                          >
                            <RefreshCcw className="mr-2 h-4 w-4 text-warning" />
                            Request OTP
                          </DropdownMenuItem>
                        )}
                        {binding.step === "REQUEST_OTP" && (
                          <DropdownMenuItem
                            disabled={isRowBusy}
                            onClick={() => onVerifyOTP(binding.id)}
                          >
                            <ShieldCheck className="mr-2 h-4 w-4 text-primary" />
                            Verify OTP
                          </DropdownMenuItem>
                        )}
                        {binding.step === "VERIFIED" && (
                          <>
                            <DropdownMenuItem
                              disabled={isRowBusy}
                              onClick={() => onSetBalance(binding.id)}
                            >
                              <Wallet className="mr-2 h-4 w-4 text-green-600" />
                              Update Balance
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              disabled={isRowBusy}
                              onClick={() => onRelease(binding.id)}
                              className="text-destructive"
                            >
                              <LogOut className="mr-2 h-4 w-4" />
                              Release Session
                            </DropdownMenuItem>
                          </>
                        )}
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
