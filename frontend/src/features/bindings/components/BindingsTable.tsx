import { Loader2, MoreHorizontal, LogOut, RefreshCcw, Settings, Wallet } from "lucide-react";

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
  onMarkVerified: (bindingId: number) => void;
  onSetBalance: (bindingId: number) => void;
  onRelease: (bindingId: number) => void;
};

export function BindingsTable({
  bindings,
  isLoadingBindings,
  pendingRowActions,
  onRequestOTP,
  onVerifyOTP,
  onMarkVerified,
  onSetBalance,
  onRelease,
}: BindingsTableProps) {
  const getStepColor = (step: string) => {
    switch (step) {
      case "BINDED":
        return "secondary";
      case "REQUEST_OTP":
        return "warning";
      case "VERIFY_OTP":
        return "warning";
      case "VERIFIED":
        return "default";
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
            <TableHead className="w-[90px]">ID</TableHead>
            <TableHead className="w-[90px]">Session</TableHead>
            <TableHead className="w-[90px]">Server</TableHead>
            <TableHead className="w-[90px]">Account</TableHead>
            <TableHead className="w-[120px]">Step</TableHead>
            <TableHead className="w-[100px]">Balance</TableHead>
            <TableHead className="w-[90px]">Priority</TableHead>
            <TableHead className="w-[120px]">Status</TableHead>
            <TableHead className="w-[190px]">Updated</TableHead>
            <TableHead className="w-[90px] text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoadingBindings ? (
            <TableRow>
              <TableCell colSpan={10} className="text-center text-muted-foreground">
                Loading bindings...
              </TableCell>
            </TableRow>
          ) : bindings.length === 0 ? (
            <TableRow>
              <TableCell colSpan={10} className="text-center text-muted-foreground">
                Belum ada bindings.
              </TableCell>
            </TableRow>
          ) : (
            bindings.map((binding) => {
              const rowAction = pendingRowActions[binding.id];
              const isRowBusy = Boolean(rowAction);

              return (
                <TableRow key={binding.id}>
                  <TableCell>#{binding.id}</TableCell>
                  <TableCell>#{binding.order_id}</TableCell>
                  <TableCell>#{binding.server_id}</TableCell>
                  <TableCell className="font-medium">#{binding.account_id}</TableCell>
                  <TableCell>
                    <Badge variant={getStepColor(binding.step)}>{binding.step}</Badge>
                  </TableCell>
                  <TableCell>
                    {binding.balance_start ? (
                      <div className="text-sm">
                        <span className="font-medium">{binding.balance_start.toLocaleString()}</span>
                        <span className="text-xs text-muted-foreground ml-1">
                          ({binding.balance_source})
                        </span>
                      </div>
                    ) : (
                      <span className="text-muted-foreground text-sm">Not set</span>
                    )}
                  </TableCell>
                  <TableCell>{binding.priority}</TableCell>
                  <TableCell>
                    <Badge variant={binding.is_active ? "default" : "secondary"}>
                      {binding.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs">
                    {binding.last_used_at
                      ? new Date(binding.last_used_at).toLocaleString()
                      : "-"}
                  </TableCell>
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
                        {binding.step === "BINDED" && (
                          <DropdownMenuItem
                            disabled={isRowBusy}
                            onClick={() => onRequestOTP(binding.id)}
                          >
                            <RefreshCcw className="mr-2 h-4 w-4" />
                            {rowAction === "request_otp" ? "Requesting..." : "Request OTP"}
                          </DropdownMenuItem>
                        )}
                        {binding.step === "REQUEST_OTP" && (
                          <DropdownMenuItem
                            disabled={isRowBusy}
                            onClick={() => onVerifyOTP(binding.id)}
                          >
                            <RefreshCcw className="mr-2 h-4 w-4" />
                            {rowAction === "verify_otp" ? "Verifying..." : "Verify OTP"}
                          </DropdownMenuItem>
                        )}
                        {binding.step === "VERIFY_OTP" && (
                          <DropdownMenuItem
                            disabled={isRowBusy}
                            onClick={() => onMarkVerified(binding.id)}
                          >
                            <Settings className="mr-2 h-4 w-4" />
                            {rowAction === "mark_verified" ? "Marking..." : "Mark Verified"}
                          </DropdownMenuItem>
                        )}
                        {binding.step === "VERIFIED" && (
                          <>
                            <DropdownMenuItem
                              disabled={isRowBusy}
                              onClick={() => onSetBalance(binding.id)}
                            >
                              <Wallet className="mr-2 h-4 w-4" />
                              Set Balance
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              disabled={isRowBusy}
                              onClick={() => onRelease(binding.id)}
                              className="text-destructive"
                            >
                              <LogOut className="mr-2 h-4 w-4" />
                              {rowAction === "release" ? "Releasing..." : "Release"}
                            </DropdownMenuItem>
                          </>
                        )}
                        {binding.step === "LOGGED_OUT" && (
                          <DropdownMenuItem disabled className="text-muted-foreground">
                            Released (no actions)
                          </DropdownMenuItem>
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
