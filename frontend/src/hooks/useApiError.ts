import { useState, useCallback } from "react";
import { toast } from "sonner";
import type { ApiError } from "@/lib/api";
import { ApiError as ApiErrorClass } from "@/lib/api";

export type ErrorDisplayMode = "toast" | "dialog" | "inline" | "silent";

export interface UseApiErrorOptions {
  /** How to display the error (default: "toast") */
  displayMode?: ErrorDisplayMode;
  /** Custom error title for dialog */
  errorTitle?: string;
  /** Custom error description for dialog */
  errorDescription?: string;
  /** Whether to show toast for dialog mode */
  showToast?: boolean;
  /** Callback when error is shown */
  onError?: (error: ApiError) => void;
  /** Whether to auto-dismiss dialog after action */
  autoClose?: boolean;
}

export interface UseApiErrorReturn {
  /** Current error object */
  error: ApiError | null;
  /** Whether dialog is open */
  isDialogOpen: boolean;
  /** Inline error message */
  errorMessage: string | null;
  /** Set error manually */
  setError: (error: ApiError | null) => void;
  /** Clear error */
  clearError: () => void;
  /** Handle error with display logic */
  handleError: (error: unknown, options?: Partial<UseApiErrorOptions>) => void;
  /** Close the dialog */
  closeDialog: () => void;
  /** Open the dialog */
  openDialog: () => void;
}

/**
 * Hook for centralized API error handling
 * Provides multiple display modes: toast, dialog, inline, or silent
 */
export function useApiError(options: UseApiErrorOptions = {}): UseApiErrorReturn {
  const {
    displayMode = "toast",
    // errorTitle,
    // errorDescription,
    // showToast = true,
    onError,
    autoClose = true,
  } = options;

  const [error, setErrorState] = useState<ApiError | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const setError = useCallback((newError: ApiError | null) => {
    setErrorState(newError);
    if (newError) {
      setErrorMessage(newError.getUserMessage());
    } else {
      setErrorMessage(null);
    }
  }, []);

  const clearError = useCallback(() => {
    setErrorState(null);
    setIsDialogOpen(false);
    setErrorMessage(null);
  }, []);

  const closeDialog = useCallback(() => {
    setIsDialogOpen(false);
    if (autoClose) {
      setErrorState(null);
      setErrorMessage(null);
    }
  }, [autoClose]);

  const openDialog = useCallback(() => {
    setIsDialogOpen(true);
  }, []);

  const handleError = useCallback(
    (unknownError: unknown, overrideOptions?: Partial<UseApiErrorOptions>) => {
      if (!(unknownError instanceof ApiErrorClass)) {
        // Handle non-API errors (network errors, etc.)
        const networkError = new ApiErrorClass(
          {
            success: false,
            error: "NetworkError",
            error_code: "network_error",
            message:
              unknownError instanceof Error
                ? unknownError.message
                : "Unable to connect to server. Please check your connection.",
            trace_id: "client-side",
          },
          0,
        );
        unknownError = networkError;
      }

      const apiError = unknownError as ApiErrorClass;
      const finalOptions = { ...options, ...overrideOptions };
      const mode = finalOptions.displayMode ?? displayMode;

      // Call onError callback
      finalOptions.onError?.(apiError);

      // Display based on mode
      switch (mode) {
        case "dialog":
          setError(apiError);
          setIsDialogOpen(true);
          if (finalOptions.showToast) {
            toast.error(apiError.getUserMessage(), {
              description: `Error: ${apiError.errorCode}`,
            });
          }
          break;

        case "toast":
          toast.error(apiError.getUserMessage(), {
            description: `${apiError.error} • Trace: ${apiError.traceId.slice(0, 8)}...`,
            duration: 5000,
            cancel: {
              label: "Details",
              onClick: () => {
                setError(apiError);
                setIsDialogOpen(true);
              },
            },
          });
          break;

        case "inline":
          setError(apiError);
          break;

        case "silent":
          setError(apiError);
          // No display, just store for programmatic handling
          break;
      }
    },
    [displayMode, options, onError],
  );

  return {
    error,
    isDialogOpen,
    errorMessage,
    setError,
    clearError,
    handleError,
    closeDialog,
    openDialog,
  };
}

/**
 * Simplified hook for toast-only error handling
 */
export function useApiToast() {
  const { handleError, error, setError } = useApiError({ displayMode: "toast" });

  return {
    handleError,
    error,
    setError,
  };
}

/**
 * Simplified hook for dialog-only error handling
 */
export function useApiDialog(options?: Omit<UseApiErrorOptions, "displayMode">) {
  const {
    error,
    isDialogOpen,
    closeDialog,
    handleError,
    setError,
    clearError,
  } = useApiError({ displayMode: "dialog", ...options });

  return {
    error,
    isDialogOpen,
    closeDialog,
    handleError,
    setError,
    clearError,
  };
}
