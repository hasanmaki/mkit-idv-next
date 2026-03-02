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
import { Badge } from "@/components/ui/badge";
import {
  CircleAlertIcon,
  TriangleAlertIcon,
  OctagonXIcon,
  CopyIcon,
  CheckIcon,
  BugIcon,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import type { ApiError } from "@/lib/api";

interface ErrorDialogProps {
  error: ApiError | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title?: string;
  description?: string;
  showCopyTrace?: boolean;
  onRetry?: () => void;
  onCancel?: () => void;
}

export function ErrorDialog({
  error,
  open,
  onOpenChange,
  title = "Terjadi Kesalahan",
  description,
  showCopyTrace = true,
  onRetry,
  onCancel,
}: ErrorDialogProps) {
  const [copied, setCopied] = useState(false);

  if (!error) return null;

  const isError = error.isServerError();

  const handleCopyTrace = () => {
    const traceInfo = `Trace ID: ${error.traceId}\nError: ${error.error}\nCode: ${error.errorCode}\nMessage: ${error.message}\nTime: ${error.datetime || "N/A"}`;
    navigator.clipboard.writeText(traceInfo);
    setCopied(true);
    toast.success("Trace ID copied to clipboard");
    setTimeout(() => setCopied(false), 2000);
  };

  const getContextEntries = () => {
    if (!error.context) return [];
    return Object.entries(error.context);
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent className="max-w-2xl">
        <AlertDialogHeader>
          <div className="flex items-start gap-3">
            <div
              className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${
                isError
                  ? "bg-red-100 text-red-600 dark:bg-red-900/20 dark:text-red-400"
                  : "bg-amber-100 text-amber-600 dark:bg-amber-900/20 dark:text-amber-400"
              }`}
            >
              {isError ? (
                <OctagonXIcon className="h-5 w-5" />
              ) : (
                <TriangleAlertIcon className="h-5 w-5" />
              )}
            </div>
            <div className="flex-1 space-y-1">
              <AlertDialogTitle className="text-left">{title}</AlertDialogTitle>
              {description && (
                <AlertDialogDescription className="text-left">
                  {description}
                </AlertDialogDescription>
              )}
            </div>
          </div>
        </AlertDialogHeader>

        <div className="space-y-4">
          {/* Error Summary */}
          <div className="rounded-lg border bg-muted p-4">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2">
                  <CircleAlertIcon className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">{error.error}</span>
                </div>
                <p className="text-sm text-muted-foreground">{error.getUserMessage()}</p>
              </div>
              <Badge variant={isError ? "destructive" : "secondary"} className="shrink-0">
                {error.statusCode}
              </Badge>
            </div>
          </div>

          {/* Error Details */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium">Error Details</h4>
              {showCopyTrace && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCopyTrace}
                  className="h-7 gap-1 text-xs"
                >
                  {copied ? (
                    <>
                      <CheckIcon className="h-3 w-3" />
                      Copied
                    </>
                  ) : (
                    <>
                      <CopyIcon className="h-3 w-3" />
                      Copy Trace
                    </>
                  )}
                </Button>
              )}
            </div>

            <div className="max-h-48 overflow-auto rounded-md border bg-muted/50 p-3">
              <dl className="space-y-2 text-sm">
                <div className="grid grid-cols-3 gap-2">
                  <dt className="text-muted-foreground">Error Code</dt>
                  <dd className="col-span-2 font-mono text-xs">{error.errorCode}</dd>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <dt className="text-muted-foreground">Trace ID</dt>
                  <dd className="col-span-2 font-mono text-xs break-all">{error.traceId}</dd>
                </div>
                {error.datetime && (
                  <div className="grid grid-cols-3 gap-2">
                    <dt className="text-muted-foreground">Time</dt>
                    <dd className="col-span-2 font-mono text-xs">{error.datetime}</dd>
                  </div>
                )}
                {getContextEntries().length > 0 && (
                  <div className="grid grid-cols-3 gap-2">
                    <dt className="text-muted-foreground">Context</dt>
                    <dd className="col-span-2">
                      <div className="max-h-24 overflow-auto rounded-md border bg-background p-2">
                        <pre className="text-xs">
                          {JSON.stringify(error.context, null, 2)}
                        </pre>
                      </div>
                    </dd>
                  </div>
                )}
              </dl>
            </div>
          </div>

          {/* Help Text */}
          <div className="flex items-start gap-2 rounded-md bg-blue-50 p-3 text-sm text-blue-700 dark:bg-blue-900/20 dark:text-blue-300">
            <BugIcon className="mt-0.5 h-4 w-4 shrink-0" />
            <div>
              <p className="font-medium">Need help?</p>
              <p className="text-xs opacity-80">
                Share the Trace ID with support team for faster troubleshooting.
              </p>
            </div>
          </div>
        </div>

        <AlertDialogFooter>
          <AlertDialogCancel onClick={onCancel}>Close</AlertDialogCancel>
          {onRetry && (
            <AlertDialogAction onClick={onRetry} className="gap-1">
              <CircleAlertIcon className="h-4 w-4" />
              Retry
            </AlertDialogAction>
          )}
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
