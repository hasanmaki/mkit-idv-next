import {
  Loader2,
  MoreHorizontal,
  PenSquare,
  ServerCog,
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
import type { Server } from "@/types/server";

type ServersTableProps = {
  servers: Server[];
  selectedServerIds: number[];
  isLoadingServers: boolean;
  allSelected: boolean;
  pendingRowActions: Record<number, string>;
  onToggleSelectAll: (checked: boolean) => void;
  onToggleSelectServer: (serverId: number, checked: boolean) => void;
  onOpenEditServer: (server: Server) => void;
  onToggleServerStatus: (server: Server) => Promise<void>;
  onOpenDeleteConfirm: (serverId: number) => void;
};

export function ServersTable({
  servers,
  selectedServerIds,
  isLoadingServers,
  allSelected,
  pendingRowActions,
  onToggleSelectAll,
  onToggleSelectServer,
  onOpenEditServer,
  onToggleServerStatus,
  onOpenDeleteConfirm,
}: ServersTableProps) {
  return (
    <div className="min-h-[440px] overflow-x-auto">
      <Table className="table-fixed">
        <TableHeader>
          <TableRow>
            <TableHead className="w-[42px]">
              <Checkbox checked={allSelected} onCheckedChange={(checked) => onToggleSelectAll(Boolean(checked))} />
            </TableHead>
            <TableHead className="w-[90px]">ID</TableHead>
            <TableHead className="w-[320px]">Base URL</TableHead>
            <TableHead>Description</TableHead>
            <TableHead className="w-[100px]">Timeout</TableHead>
            <TableHead className="w-[120px]">Status</TableHead>
            <TableHead className="w-[190px]">Updated</TableHead>
            <TableHead className="w-[90px] text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoadingServers ? (
            <TableRow>
              <TableCell colSpan={8} className="text-center text-muted-foreground">
                Loading servers...
              </TableCell>
            </TableRow>
          ) : servers.length === 0 ? (
            <TableRow>
              <TableCell colSpan={8} className="text-center text-muted-foreground">
                Belum ada server.
              </TableCell>
            </TableRow>
          ) : (
            servers.map((server) => {
              const rowAction = pendingRowActions[server.id];
              const isRowBusy = Boolean(rowAction);

              return (
                <TableRow key={server.id}>
                  <TableCell>
                    <Checkbox
                      checked={selectedServerIds.includes(server.id)}
                      onCheckedChange={(checked) =>
                        onToggleSelectServer(server.id, Boolean(checked))
                      }
                    />
                  </TableCell>
                  <TableCell>#{server.id}</TableCell>
                  <TableCell className="truncate font-mono text-xs">{server.base_url}</TableCell>
                  <TableCell className="truncate">{server.description ?? "-"}</TableCell>
                  <TableCell>{server.timeout}s</TableCell>
                  <TableCell>
                    <Badge variant={server.is_active ? "default" : "secondary"}>
                      {server.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs">{new Date(server.updated_at).toLocaleString()}</TableCell>
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
                        <DropdownMenuItem disabled={isRowBusy} onClick={() => onOpenEditServer(server)}>
                          <PenSquare className="mr-2 h-4 w-4" />
                          {rowAction === "edit" ? "Updating..." : "Edit"}
                        </DropdownMenuItem>
                        <DropdownMenuItem disabled={isRowBusy} onClick={() => void onToggleServerStatus(server)}>
                          <ServerCog className="mr-2 h-4 w-4" />
                          {rowAction === "toggle"
                            ? "Updating..."
                            : server.is_active
                              ? "Deactivate"
                              : "Activate"}
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          disabled={isRowBusy}
                          className="text-destructive"
                          onClick={() => onOpenDeleteConfirm(server.id)}
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
