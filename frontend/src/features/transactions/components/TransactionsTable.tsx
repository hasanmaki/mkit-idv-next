import {
  CirclePause,
  CirclePlay,
  Loader2,
  MoreHorizontal,
  SearchCheck,
  ShieldCheck,
  SkipForward,
  Square,
  Trash2,
} from "lucide-react";

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

import type { Transaction } from "../types";

function statusVariant(status: Transaction["status"]): "default" | "secondary" | "destructive" {
  if (status === "SUKSES") {
    return "default";
  }
  if (status === "GAGAL") {
    return "destructive";
  }
  return "secondary";
}

type TransactionsTableProps = {
  transactions: Transaction[];
  isLoading: boolean;
  pendingRowActions: Record<number, string>;
  onOpenOtp: (transaction: Transaction) => void;
  onOpenPause: (transaction: Transaction) => void;
  onOpenStop: (transaction: Transaction) => void;
  onContinue: (id: number) => void;
  onResume: (id: number) => void;
  onCheck: (id: number) => void;
  onDelete: (id: number) => void;
};

export function TransactionsTable({
  transactions,
  isLoading,
  pendingRowActions,
  onOpenOtp,
  onOpenPause,
  onOpenStop,
  onContinue,
  onResume,
  onCheck,
  onDelete,
}: TransactionsTableProps) {
  return (
    <div className="min-h-[420px] overflow-x-auto">
      <Table className="table-fixed">
        <TableHeader>
          <TableRow>
            <TableHead className="w-[80px]">ID</TableHead>
            <TableHead className="w-[220px]">trx_id</TableHead>
            <TableHead className="w-[90px]">Bind</TableHead>
            <TableHead className="w-[100px]">Status</TableHead>
            <TableHead className="w-[100px]">OTP</TableHead>
            <TableHead className="w-[130px]">Limit</TableHead>
            <TableHead className="w-[180px]">Voucher</TableHead>
            <TableHead className="w-[90px] text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <TableRow>
              <TableCell colSpan={8} className="text-center text-muted-foreground">
                Loading transactions...
              </TableCell>
            </TableRow>
          ) : transactions.length === 0 ? (
            <TableRow>
              <TableCell colSpan={8} className="text-center text-muted-foreground">
                Belum ada transaksi.
              </TableCell>
            </TableRow>
          ) : (
            transactions.map((trx) => {
              const rowAction = pendingRowActions[trx.id];
              const isBusy = Boolean(rowAction);
              return (
                <TableRow key={trx.id}>
                  <TableCell>#{trx.id}</TableCell>
                  <TableCell className="truncate font-mono text-xs">{trx.trx_id}</TableCell>
                  <TableCell>{trx.binding_id}</TableCell>
                  <TableCell>
                    <Badge variant={statusVariant(trx.status)}>{trx.status}</Badge>
                  </TableCell>
                  <TableCell>{trx.otp_status ?? "-"}</TableCell>
                  <TableCell>{trx.limit_harga ?? "-"}</TableCell>
                  <TableCell className="truncate font-mono text-xs">{trx.voucher_code ?? "-"}</TableCell>
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
                        <DropdownMenuItem onClick={() => onCheck(trx.id)}>
                          <SearchCheck className="mr-2 h-4 w-4" /> Check
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onContinue(trx.id)}>
                          <SkipForward className="mr-2 h-4 w-4" /> Continue
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onOpenOtp(trx)}>
                          <ShieldCheck className="mr-2 h-4 w-4" /> Submit OTP
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onOpenPause(trx)}>
                          <CirclePause className="mr-2 h-4 w-4" /> Pause
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onResume(trx.id)}>
                          <CirclePlay className="mr-2 h-4 w-4" /> Resume
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onOpenStop(trx)}>
                          <Square className="mr-2 h-4 w-4" /> Stop
                        </DropdownMenuItem>
                        <DropdownMenuItem className="text-destructive" onClick={() => onDelete(trx.id)}>
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
