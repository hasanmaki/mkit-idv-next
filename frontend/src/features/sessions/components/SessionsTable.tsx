import { Loader2, MoreHorizontal, PenSquare, ServerCog, Trash2 } from "lucide-react";

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
import type { Session } from "../types";

type SessionsTableProps = {
  sessions: Session[];
  selectedSessionIds: number[];
  isLoadingSessions: boolean;
  allSelected: boolean;
  pendingRowActions: Record<number, string>;
  onToggleSelectAll: (checked: boolean) => void;
  onToggleSelectSession: (sessionId: number, checked: boolean) => void;
  onOpenEditSession: (session: Session) => void;
  onToggleSessionStatus: (session: Session) => Promise<void>;
  onOpenDeleteConfirm: (sessionId: number) => void;
};

export function SessionsTable({
  sessions,
  selectedSessionIds,
  isLoadingSessions,
  allSelected,
  pendingRowActions,
  onToggleSelectAll,
  onToggleSelectSession,
  onOpenEditSession,
  onToggleSessionStatus,
  onOpenDeleteConfirm,
}: SessionsTableProps) {
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
            <TableHead>Description</TableHead>
            <TableHead className="w-[120px]">Status</TableHead>
            <TableHead className="w-[190px]">Updated</TableHead>
            <TableHead className="w-[90px] text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoadingSessions ? (
            <TableRow>
              <TableCell colSpan={8} className="text-center text-muted-foreground">
                Loading sessions...
              </TableCell>
            </TableRow>
          ) : sessions.length === 0 ? (
            <TableRow>
              <TableCell colSpan={8} className="text-center text-muted-foreground">
                Belum ada session.
              </TableCell>
            </TableRow>
          ) : (
            sessions.map((session) => {
              const rowAction = pendingRowActions[session.id];
              const isRowBusy = Boolean(rowAction);

              return (
                <TableRow key={session.id}>
                  <TableCell>
                    <Checkbox
                      checked={selectedSessionIds.includes(session.id)}
                      onCheckedChange={(checked) =>
                        onToggleSelectSession(session.id, Boolean(checked))
                      }
                    />
                  </TableCell>
                  <TableCell>#{session.id}</TableCell>
                  <TableCell className="font-medium">{session.name}</TableCell>
                  <TableCell className="truncate text-sm">{session.email}</TableCell>
                  <TableCell className="truncate max-w-[200px] text-sm text-muted-foreground">
                    {session.description ?? "-"}
                  </TableCell>
                  <TableCell>
                    <Badge variant={session.is_active ? "default" : "secondary"}>
                      {session.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs">
                    {new Date(session.updated_at).toLocaleString()}
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
                        <DropdownMenuItem
                          disabled={isRowBusy}
                          onClick={() => onOpenEditSession(session)}
                        >
                          <PenSquare className="mr-2 h-4 w-4" />
                          {rowAction === "edit" ? "Updating..." : "Edit"}
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          disabled={isRowBusy}
                          onClick={() => void onToggleSessionStatus(session)}
                        >
                          <ServerCog className="mr-2 h-4 w-4" />
                          {rowAction === "toggle"
                            ? "Updating..."
                            : session.is_active
                              ? "Deactivate"
                              : "Activate"}
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          disabled={isRowBusy}
                          className="text-destructive"
                          onClick={() => onOpenDeleteConfirm(session.id)}
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
