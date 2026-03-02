import { CircleAlertIcon, InfoIcon, TriangleAlertIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ApiError } from "@/lib/api";

interface ErrorBannerProps {
  error: ApiError | string | null;
  className?: string;
  title?: string;
  showIcon?: boolean;
  variant?: "error" | "warning" | "info";
  onDismiss?: () => void;
}

export function ErrorBanner({
  error,
  className,
  title = "Error",
  showIcon = true,
  variant = "error",
  onDismiss,
}: ErrorBannerProps) {
  if (!error) return null;

  const message = typeof error === "string" ? error : error.getUserMessage();
  const errorCode = typeof error === "string" ? null : error.errorCode;

  const variants = {
    error: {
      bg: "bg-red-50 dark:bg-red-900/20",
      border: "border-red-200 dark:border-red-800",
      text: "text-red-800 dark:text-red-200",
      icon: "text-red-500",
    },
    warning: {
      bg: "bg-amber-50 dark:bg-amber-900/20",
      border: "border-amber-200 dark:border-amber-800",
      text: "text-amber-800 dark:text-amber-200",
      icon: "text-amber-500",
    },
    info: {
      bg: "bg-blue-50 dark:bg-blue-900/20",
      border: "border-blue-200 dark:border-blue-800",
      text: "text-blue-800 dark:text-blue-200",
      icon: "text-blue-500",
    },
  };

  const Icon = variant === "error" ? CircleAlertIcon : variant === "warning" ? TriangleAlertIcon : InfoIcon;

  return (
    <div
      className={cn(
        "flex items-start gap-3 rounded-lg border p-4",
        variants[variant].bg,
        variants[variant].border,
        variants[variant].text,
        className,
      )}
    >
      {showIcon && <Icon className={cn("mt-0.5 h-5 w-5 shrink-0", variants[variant].icon)} />}
      <div className="flex-1 space-y-1">
        {title && <p className="font-medium">{title}</p>}
        <p className="text-sm">{message}</p>
        {errorCode && (
          <p className="text-xs opacity-70 font-mono">Code: {errorCode}</p>
        )}
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="ml-2 text-current opacity-70 hover:opacity-100"
          aria-label="Dismiss error"
        >
          ×
        </button>
      )}
    </div>
  );
}

interface FormFieldErrorProps {
  error: string | null;
  className?: string;
}

export function FormFieldError({ error, className }: FormFieldErrorProps) {
  if (!error) return null;

  return (
    <p
      className={cn(
        "text-sm font-medium text-red-600 dark:text-red-400",
        className,
      )}
    >
      {error}
    </p>
  );
}
