import { useState } from "react";

import { Button } from "@/components/ui/button";
import { AccountsPage } from "@/features/accounts/pages/AccountsPage";
import { ServersPage } from "@/features/servers/pages/ServersPage";

function App() {
  const [tab, setTab] = useState<"servers" | "accounts">("servers");

  return (
    <main className="min-h-screen w-full space-y-4 px-4 py-6 lg:px-8">
      <header className="sticky top-0 z-20 rounded-lg border bg-background/95 px-3 py-2 backdrop-blur">
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant={tab === "servers" ? "default" : "secondary"}
            onClick={() => setTab("servers")}
          >
            Servers
          </Button>
          <Button
            variant={tab === "accounts" ? "default" : "secondary"}
            onClick={() => setTab("accounts")}
          >
            Accounts
          </Button>
        </div>
      </header>

      {tab === "servers" ? <ServersPage /> : <AccountsPage />}
    </main>
  );
}

export default App;
