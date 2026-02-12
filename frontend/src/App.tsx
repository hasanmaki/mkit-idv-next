import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { AccountsPage } from "@/features/accounts/pages/AccountsPage";
import { BindingsPage } from "@/features/bindings/pages/BindingsPage";
import { ServersPage } from "@/features/servers/pages/ServersPage";
import { TransactionsPage } from "@/features/transactions/pages/TransactionsPage";

type TabKey = "servers" | "accounts" | "bindings" | "transactions";

function resolveTab(raw: string | null): TabKey {
  if (raw === "accounts" || raw === "bindings" || raw === "transactions") {
    return raw;
  }
  return "servers";
}

function App() {
  const [tab, setTab] = useState<TabKey>(() => {
    const params = new URLSearchParams(window.location.search);
    return resolveTab(params.get("tab"));
  });

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    params.set("tab", tab);
    const nextUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState({}, "", nextUrl);
  }, [tab]);

  return (
    <main className="min-h-screen w-full space-y-4 px-4 py-6 lg:px-8">
      <header className="sticky top-0 z-20 rounded-lg border bg-background/95 px-3 py-2 backdrop-blur">
        <div className="flex flex-wrap items-center gap-2">
          <Button variant={tab === "servers" ? "default" : "secondary"} onClick={() => setTab("servers")}>
            Servers
          </Button>
          <Button variant={tab === "accounts" ? "default" : "secondary"} onClick={() => setTab("accounts")}>
            Accounts
          </Button>
          <Button variant={tab === "bindings" ? "default" : "secondary"} onClick={() => setTab("bindings")}>
            Bindings
          </Button>
          <Button
            variant={tab === "transactions" ? "default" : "secondary"}
            onClick={() => setTab("transactions")}
          >
            Transactions
          </Button>
        </div>
      </header>

      {tab === "servers" ? <ServersPage /> : null}
      {tab === "accounts" ? <AccountsPage /> : null}
      {tab === "bindings" ? <BindingsPage /> : null}
      {tab === "transactions" ? <TransactionsPage /> : null}
    </main>
  );
}

export default App;
