import { Loader2, MoreHorizontal, LogOut, RefreshCcw, Wallet, UserCheck, ShieldCheck, Edit2 } from "lucide-react";

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
  onEdit: (binding: Binding) => void;
  onSetBalance: (bindingId: number) => void;
  onRelease: (bindingId: number) => void;
};

export function BindingsTable({
  bindings,
  isLoadingBindings,
  pendingRowActions,
  onRequestOTP,
  onVerifyOTP,
  onEdit,
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
            <TableHead className="w-[60px]">ID</TableHead>
            <TableHead className="w-[180px]">Session / Order</TableHead>
            <TableHead className="w-[140px]">Server Instance</TableHead>
            <TableHead className="w-[160px]">Account (MSISDN)</TableHead>
            <TableHead className="w-[100px]">Type</TableHead>
            <TableHead className="w-[130px]">Status Step</TableHead>
            <TableHead className="w-[120px]">Last Balance</TableHead>
            <TableHead className="w-[150px]">Token Location</TableHead>
            <TableHead className="w-[80px] text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoadingBindings ? (
            <TableRow>
              <TableCell colSpan={9} className="text-center py-12 text-muted-foreground">
                <Loader2 className="h-8 w-8 animate-spin mx-auto mb-3 text-primary" />
                Memuat data bindings...
              </TableCell>
            </TableRow>
          ) : bindings.length === 0 ? (
            <TableRow>
              <TableCell colSpan={9} className="text-center py-12 text-muted-foreground">
                Tidak ada antrean binding aktif saat ini.
              </TableCell>
            </TableRow>
          ) : (
            bindings.map((binding) => {
              const rowAction = pendingRowActions[binding.id];
              const isRowBusy = Boolean(rowAction);

              return (
                <TableRow key={binding.id} className={binding.is_active ? "" : "opacity-60 bg-muted/20"}>
                  <TableCell className="font-mono text-[10px] text-muted-foreground">#{binding.id}</TableCell>
                  <TableCell>
                    <div className="font-semibold text-sm truncate max-w-[170px]" title={binding.order_name || ""}>
                      {binding.order_name || `Order #${binding.order_id}`}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm font-medium text-muted-foreground">
                      {binding.server_name || `Srv:${binding.server_id}`}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="font-mono text-sm font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded w-fit">
                      {binding.account_msisdn || binding.account_id}
                    </div>
                  </TableCell>
                  <TableCell>
                    {binding.is_reseller ? (
                      <Badge variant="default" className="bg-indigo-600 hover:bg-indigo-700 h-5 px-1.5 text-[9px] font-bold">
                        <UserCheck className="mr-1 h-3 w-3" /> RESELLER
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="h-5 px-1.5 text-[9px] text-muted-foreground font-medium">
                        NORMAL
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge variant={getStepColor(binding.step) as any} className="font-mono text-[10px] py-0 px-2">
                      {binding.step}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {binding.balance_start !== null ? (
                      <div className="text-sm font-black text-green-700">
                        Rp{binding.balance_start.toLocaleString()}
                      </div>
                    ) : (
                      <span className="text-muted-foreground text-[10px] italic">N/A</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {binding.token_location ? (
                      <div className="flex items-center text-[10px] font-mono text-muted-foreground truncate max-w-[140px]" title={binding.token_location}>
                        <ShieldCheck className="mr-1 h-3 w-3 text-green-500 shrink-0" />
                        {binding.token_location.split('/').pop()}
                      </div>
                    ) : (
                      <span className="text-[10px] text-muted-foreground italic">None</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button size="icon" variant="ghost" disabled={isRowBusy} className="h-8 w-8">
                          {isRowBusy ? (
                            <Loader2 className="h-4 w-4 animate-spin text-primary" />
                          ) : (
                            <MoreHorizontal className="h-4 w-4" />
                          )}
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-[160px]">
                        <DropdownMenuItem
                          disabled={isRowBusy}
                          onClick={() => onEdit(binding)}
                        >
                          <Edit2 className="mr-2 h-4 w-4 text-blue-600" />
                          Edit Binding
                        </DropdownMenuItem>
                        
                        {(binding.step === "BINDED" || binding.step === "LOGGED_OUT") && (
                          <DropdownMenuItem
                            disabled={isRowBusy}
                            onClick={() => onRequestOTP(binding.id)}
                          >
                            <RefreshCcw className="mr-2 h-4 w-4 text-orange-500" />
                            Request OTP
                          </DropdownMenuItem>
                        )}
                        {binding.step === "REQUEST_OTP" && (
                          <DropdownMenuItem
                            disabled={isRowBusy}
                            onClick={() => onVerifyOTP(binding.id)}
                          >
                            <ShieldCheck className="mr-2 h-4 w-4 text-green-600" />
                            Verify OTP
                          </DropdownMenuItem>
                        )}
                        {binding.step === "VERIFIED" && (
                          <DropdownMenuItem
                            disabled={isRowBusy}
                            onClick={() => onSetBalance(binding.id)}
                          >
                            <Wallet className="mr-2 h-4 w-4 text-emerald-600" />
                            Update Balance
                          </DropdownMenuItem>
                        )}
                        
                        <DropdownMenuItem
                          disabled={isRowBusy}
                          onClick={() => onRelease(binding.id)}
                          className="text-destructive focus:text-destructive"
                        >
                          <LogOut className="mr-2 h-4 w-4" />
                          Unbind Akun
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
