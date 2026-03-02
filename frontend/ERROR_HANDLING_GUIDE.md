# Error Handling Guide

Panduan lengkap untuk error handling di frontend aplikasi IDV.

## 📚 Overview

Sistem error handling baru menyediakan:
- ✅ **Structured errors** - Semua error dari backend ditangkap dengan lengkap
- ✅ **Multiple display modes** - Toast, Dialog, Inline, atau Silent
- ✅ **Rich error details** - Trace ID, error code, context untuk debugging
- ✅ **Centralized handling** - Hook `useApiError` untuk konsistensi
- ✅ **Error boundaries** - Fallback UI untuk unexpected errors

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   API Request                            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    ApiError Class                        │
│  - Captures: error, error_code, message, trace_id, ctx  │
│  - Provides: getUserMessage(), isClientError(), etc.    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  useApiError Hook                        │
│  - Centralized error state management                    │
│  - Display modes: toast, dialog, inline, silent          │
└─────────────────────────────────────────────────────────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
     ┌──────────┐  ┌──────────┐  ┌──────────┐
     │  Toast   │  │  Dialog  │  │  Inline  │
     │ (Sonner) │  │ (Modal)  │  │ (Banner) │
     └──────────┘  └──────────┘  └──────────┘
```

## 🚀 Usage

### 1. Basic Usage (Toast Mode - Default)

```typescript
import { useApiError } from "@/hooks/useApiError";

function MyComponent() {
  const { handleError } = useApiError();

  const fetchData = async () => {
    try {
      const data = await apiRequest("/api/data", "GET");
      // handle success
    } catch (error) {
      handleError(error); // Shows toast with error details
    }
  };

  return <Button onClick={fetchData}>Fetch Data</Button>;
}
```

### 2. Dialog Mode (Untuk Error Penting)

```typescript
import { useApiError } from "@/hooks/useApiError";
import { ErrorDialog } from "@/components/error";

function MyPage() {
  const {
    error,
    isDialogOpen,
    handleError,
    closeDialog,
  } = useApiError({
    displayMode: "dialog",
    errorTitle: "Operation Failed",
    errorDescription: "Please review the error details below.",
  });

  return (
    <>
      <Button onClick={performCriticalAction}>Critical Action</Button>
      
      <ErrorDialog
        error={error}
        open={isDialogOpen}
        onOpenChange={(open) => !open && closeDialog()}
      />
    </>
  );
}
```

### 3. Inline Mode (Form Validation Errors)

```typescript
import { useApiError } from "@/hooks/useApiError";
import { ErrorBanner } from "@/components/error";

function MyForm() {
  const { errorMessage, handleError } = useApiError({
    displayMode: "inline",
  });

  const handleSubmit = async (data) => {
    try {
      await apiRequest("/api/submit", "POST", data);
    } catch (error) {
      handleError(error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {errorMessage && (
        <ErrorBanner error={errorMessage} onDismiss={() => clearError()} />
      )}
      {/* form fields */}
    </form>
  );
}
```

### 4. Mixed Modes (Toast + Dialog on Demand)

```typescript
import { useApiError } from "@/hooks/useApiError";

function MyComponent() {
  const { handleError } = useApiError({ displayMode: "toast" });

  const handleNormalAction = async () => {
    try {
      await apiRequest("/api/normal", "POST");
    } catch (error) {
      handleError(error); // Shows toast
    }
  };

  const handleCriticalAction = async () => {
    try {
      await apiRequest("/api/critical", "POST");
    } catch (error) {
      handleError(error, { displayMode: "dialog" }); // Override to dialog
    }
  };

  return (
    <>
      <Button onClick={handleNormalAction}>Normal Action</Button>
      <Button onClick={handleCriticalAction}>Critical Action</Button>
    </>
  );
}
```

## 📖 API Reference

### `useApiError(options)`

#### Options

```typescript
interface UseApiErrorOptions {
  /** How to display the error (default: "toast") */
  displayMode?: "toast" | "dialog" | "inline" | "silent";
  
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
```

#### Return Value

```typescript
interface UseApiErrorReturn {
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
```

### `ApiError` Class

```typescript
class ApiError extends Error {
  // Properties from backend
  success: boolean;
  error: string;           // e.g., "ServerDuplicateError"
  errorCode: string;       // e.g., "server_duplicate"
  traceId: string;         // e.g., "abc123..."
  context?: object;        // Additional error context
  statusCode: number;      // HTTP status code
  
  // Helper methods
  getUserMessage(): string;     // User-friendly message
  isClientError(): boolean;     // 4xx errors
  isServerError(): boolean;     // 5xx errors
  toObject(): object;           // Convert to plain object
}
```

## 🎨 Components

### ErrorDialog

Modal untuk menampilkan error detail dengan:
- Error summary
- Technical details (error code, trace ID)
- Context viewer (JSON)
- Copy trace ID button
- Retry action

```typescript
import { ErrorDialog } from "@/components/error";

<ErrorDialog
  error={error}
  open={isDialogOpen}
  onOpenChange={setOpen}
  title="Operation Failed"
  description="Something went wrong"
  showCopyTrace={true}
  onRetry={() => retryAction()}
/>
```

### ErrorBanner

Inline error banner untuk form atau page-level errors:

```typescript
import { ErrorBanner } from "@/components/error";

<ErrorBanner
  error={errorMessage}
  title="Validation Error"
  variant="error" // | "warning" | "info"
  showIcon={true}
  onDismiss={() => clearError()}
/>
```

### FormFieldError

Error message untuk form fields:

```typescript
import { FormFieldError } from "@/components/error";

<input type="text" />
<FormFieldError error={fieldError} />
```

### ErrorBoundary

React Error Boundary untuk catch runtime errors:

```typescript
import { ErrorBoundary } from "@/components/error";

<ErrorBoundary
  onError={(error, errorInfo) => {
    console.error("Caught error:", error, errorInfo);
    toast.error("Something went wrong");
  }}
>
  <MyComponent />
</ErrorBoundary>
```

## 📝 Best Practices

### 1. Pilih Display Mode yang Tepat

- **Toast**: Untuk error ringan, network errors biasa
- **Dialog**: Untuk error critical, validation failures yang perlu user attention
- **Inline**: Untuk form validation errors
- **Silent**: Untuk error yang dihandle programmatically

### 2. Selalu Include Trace ID

Trace ID sangat penting untuk debugging. User bisa copy dan kirim ke support team.

### 3. Gunakan Error Boundaries

Wrap major sections dengan ErrorBoundary untuk graceful degradation:

```typescript
// In App.tsx
<ErrorBoundary onError={handleError}>
  <MainApp />
</ErrorBoundary>
```

### 4. Provide Actionable Messages

Error message harus jelas dan actionable:

```typescript
// ❌ Bad
"Error occurred"

// ✅ Good
"Port 9900 is already in use. Please choose a different port or remove the existing server."
```

### 5. Log Errors Appropriately

```typescript
const { handleError } = useApiError({
  onError: (error) => {
    // Log to analytics/monitoring
    analytics.track("api_error", {
      errorCode: error.errorCode,
      statusCode: error.statusCode,
      path: window.location.pathname,
    });
  },
});
```

## 🔧 Migration Guide

### From Old Pattern

```typescript
// ❌ Old way
try {
  await apiRequest("/api/data", "GET");
} catch (error) {
  setErrorMessage(error instanceof Error ? error.message : "Unknown error");
  toast.error("Gagal memuat data.");
}

// ✅ New way
const { handleError } = useApiError();

try {
  await apiRequest("/api/data", "GET");
} catch (error) {
  handleError(error);
}
```

## 📊 Backend Integration

Backend mengirim error dalam format:

```json
{
  "success": false,
  "error": "ServerDuplicateError",
  "error_code": "server_duplicate",
  "message": "Port '9900' is already in use",
  "trace_id": "abc-123-def",
  "context": {
    "port": 9900,
    "existing_server_id": 5
  },
  "datetime": "2026-03-03T10:30:00Z"
}
```

Frontend akan automatically parse dan tampilkan dengan proper formatting.

## 🎯 Examples

Lihat implementasi di:
- `features/servers/hooks/useServers.ts` - Complete example
- `features/servers/pages/ServersPage.tsx` - UI integration
- `App.tsx` - Error Boundary setup
