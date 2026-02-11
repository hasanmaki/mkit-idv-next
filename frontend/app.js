document.addEventListener('alpine:init', () => {
    Alpine.data('app', () => ({
        tab: 'bindings',
        servers: [],
        accounts: [],
        bindings: [],
        transactions: [],
        bindingState: {},

        // Modals (only for create operations)
        showServerModal: false,
        showAccountModal: false,
        showAccountBulkModal: false,
        showBindingModal: false,

        // Forms
        serverForm: { base_url: '', port: 9900, description: '' },
        accountForm: { msisdn: '', email: '', batch_id: '', pin: '' },
        accountBulkForm: { msisdns_text: '', email: '', batch_id: '' },
        bindingForm: { server_id: '', account_id: '' },

        async init() {
            await this.loadAll();
            this.startPolling();
        },

        async loadAll() {
            await Promise.all([
                this.loadServers(),
                this.loadAccounts(),
                this.loadBindings(),
                this.loadTransactions()
            ]);
        },

        startPolling() {
            setInterval(async () => {
                if (this.tab === 'bindings') {
                    await Promise.all([this.loadBindings(), this.loadTransactions()]);
                }
            }, 5000);
        },

        // ========================
        // BINDING STATE HELPERS
        // ========================
        getBS(id) {
            if (!this.bindingState[id]) {
                this.bindingState[id] = {
                    verifyOtp: '', verifyPin: '',
                    trxOtp: '',
                    showStartTrx: false,
                    trxProductId: '650', trxEmail: '', trxLimitHarga: 100000,
                    loading: false
                };
            }
            return this.bindingState[id];
        },

        getActiveTransaction(bindingId) {
            return this.transactions.find(t =>
                t.binding_id === bindingId &&
                ['PROCESSING', 'PAUSED', 'RESUMED'].includes(t.status)
            );
        },

        getBindingControl(binding) {
            if (binding.step === 'LOGGED_OUT') return 'logged-out';
            if (binding.step === 'BOUND') return 'needs-verify';
            if (['OTP_REQUESTED', 'OTP_VERIFICATION', 'OTP_VERIFIED'].includes(binding.step)) return 'verifying';
            const trx = this.getActiveTransaction(binding.id);
            if (!trx) return 'ready';
            if (trx.status === 'PROCESSING' && trx.otp_required && trx.otp_status === 'PENDING') return 'needs-trx-otp';
            if (trx.status === 'PROCESSING' || trx.status === 'RESUMED') return 'processing';
            if (trx.status === 'PAUSED') return 'paused';
            return 'ready';
        },

        getMsisdn(accountId) {
            const a = this.accounts.find(x => x.id === accountId);
            return a ? a.msisdn : `#${accountId}`;
        },

        getServerPort(serverId) {
            const s = this.servers.find(x => x.id === serverId);
            return s ? `:${s.port}` : `#${serverId}`;
        },

        fmtBal(v) { return v != null ? 'Rp ' + v.toLocaleString() : '-'; },
        fmtTime(dt) {
            if (!dt) return '-';
            return new Date(dt).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        },

        // ========================
        // SERVERS
        // ========================
        async loadServers() {
            const d = await this.apiGet('/v1/servers/');
            if (d) this.servers = d;
        },
        async createServer() {
            const d = await this.apiPost('/v1/servers/', this.serverForm);
            if (d) {
                this.servers.push(d);
                this.showServerModal = false;
                this.serverForm = { base_url: '', port: 9900, description: '' };
            }
        },
        async toggleServerStatus(id, active) {
            const d = await this.apiPatch(`/v1/servers/${id}/status`, { is_active: active });
            if (d) { const i = this.servers.findIndex(s => s.id === id); if (i !== -1) this.servers[i] = d; }
        },
        async deleteServer(id) {
            if (!confirm('Delete server?')) return;
            if (await this.apiDelete(`/v1/servers/${id}`)) this.servers = this.servers.filter(s => s.id !== id);
        },

        // ========================
        // ACCOUNTS
        // ========================
        async loadAccounts() {
            const d = await this.apiGet('/v1/accounts/');
            if (d) this.accounts = d;
        },
        async createAccount() {
            const d = await this.apiPost('/v1/accounts/', this.accountForm);
            if (d) {
                this.accounts.push(d);
                this.showAccountModal = false;
                this.accountForm = { msisdn: '', email: '', batch_id: '', pin: '' };
            }
        },
        async createAccountsBulk() {
            const msisdns = this.accountBulkForm.msisdns_text.split('\n').map(s => s.trim()).filter(Boolean);
            const d = await this.apiPost('/v1/accounts/bulk', {
                msisdns, email: this.accountBulkForm.email, batch_id: this.accountBulkForm.batch_id
            });
            if (d) {
                this.accounts.push(...d);
                this.showAccountBulkModal = false;
                this.accountBulkForm = { msisdns_text: '', email: '', batch_id: '' };
            }
        },
        async deleteAccount(id) {
            if (!confirm('Delete account?')) return;
            if (await this.apiDeleteWithBody('/v1/accounts/', { id })) this.accounts = this.accounts.filter(a => a.id !== id);
        },

        // ========================
        // BINDINGS
        // ========================
        async loadBindings() {
            const d = await this.apiGet('/v1/bindings/');
            if (d) this.bindings = d;
        },
        async createBinding() {
            const d = await this.apiPost('/v1/bindings/', {
                server_id: parseInt(this.bindingForm.server_id),
                account_id: parseInt(this.bindingForm.account_id)
            });
            if (d) {
                this.bindings.push(d);
                this.showBindingModal = false;
                this.bindingForm = { server_id: '', account_id: '' };
            }
        },
        async verifyLogin(bindingId) {
            const bs = this.getBS(bindingId);
            if (!bs.verifyOtp) return;
            bs.loading = true;
            const payload = { otp: bs.verifyOtp };
            if (bs.verifyPin) payload.pin = bs.verifyPin;
            const d = await this.apiPost(`/v1/bindings/${bindingId}/verify-login`, payload);
            bs.loading = false;
            if (d) {
                bs.verifyOtp = '';
                bs.verifyPin = '';
                await Promise.all([this.loadBindings(), this.loadAccounts()]);
            }
        },
        async logoutBinding(id) {
            if (!confirm('Logout binding?')) return;
            const d = await this.apiPost(`/v1/bindings/${id}/logout`, { last_error_code: 'manual_logout' });
            if (d) await this.loadBindings();
        },
        async deleteBinding(id) {
            if (!confirm('Delete binding?')) return;
            if (await this.apiDelete(`/v1/bindings/${id}`)) {
                this.bindings = this.bindings.filter(b => b.id !== id);
                delete this.bindingState[id];
            }
        },

        // ========================
        // TRANSACTIONS (from binding inline controls)
        // ========================
        async loadTransactions() {
            const d = await this.apiGet('/v1/transactions/');
            if (d) this.transactions = d;
        },
        async startTransaction(bindingId) {
            const bs = this.getBS(bindingId);
            if (!bs.trxEmail || !bs.trxProductId) return;
            bs.loading = true;
            const d = await this.apiPost('/v1/transactions/start', {
                binding_id: bindingId,
                product_id: bs.trxProductId,
                email: bs.trxEmail,
                limit_harga: parseInt(bs.trxLimitHarga)
            });
            bs.loading = false;
            if (d) { this.transactions.unshift(d); bs.showStartTrx = false; }
        },
        async submitTrxOtp(bindingId) {
            const bs = this.getBS(bindingId);
            const trx = this.getActiveTransaction(bindingId);
            if (!trx || !bs.trxOtp) return;
            bs.loading = true;
            const d = await this.apiPost(`/v1/transactions/${trx.id}/otp`, { otp: bs.trxOtp });
            bs.loading = false;
            if (d) { this._upsertTrx(d); bs.trxOtp = ''; }
        },
        async continueTransaction(bindingId) {
            const trx = this.getActiveTransaction(bindingId);
            if (!trx) return;
            const d = await this.apiPost(`/v1/transactions/${trx.id}/continue`, {});
            if (d) this._upsertTrx(d);
        },
        async pauseTransaction(bindingId) {
            const trx = this.getActiveTransaction(bindingId);
            if (!trx) return;
            const d = await this.apiPost(`/v1/transactions/${trx.id}/pause`, { reason: 'manual_pause' });
            if (d) this._upsertTrx(d);
        },
        async resumeTransaction(bindingId) {
            const trx = this.getActiveTransaction(bindingId);
            if (!trx) return;
            const d = await this.apiPost(`/v1/transactions/${trx.id}/resume`, {});
            if (d) this._upsertTrx(d);
        },
        async stopTransaction(bindingId) {
            if (!confirm('Stop transaction?')) return;
            const trx = this.getActiveTransaction(bindingId);
            if (!trx) return;
            const d = await this.apiPost(`/v1/transactions/${trx.id}/stop`, { reason: 'manual_stop' });
            if (d) this._upsertTrx(d);
        },
        async checkBalance(bindingId) {
            const trx = this.getActiveTransaction(bindingId);
            if (!trx) return;
            const d = await this.apiPost(`/v1/transactions/${trx.id}/check`, {});
            if (d) {
                this._upsertTrx(d.transaction);
                alert(`Balance: ${this.fmtBal(d.current_balance)} | Action: ${d.action}`);
            }
        },
        _upsertTrx(trx) {
            const i = this.transactions.findIndex(t => t.id === trx.id);
            if (i !== -1) this.transactions[i] = trx;
            else this.transactions.unshift(trx);
        },

        // ========================
        // API HELPERS
        // ========================
        async apiGet(url) {
            try {
                const r = await fetch(url);
                if (!r.ok) throw new Error('API Error');
                return await r.json();
            } catch (e) { console.error('GET', url, e); return null; }
        },
        async apiPost(url, body) {
            try {
                const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
                const d = await r.json();
                if (!r.ok) throw new Error(d.message || d.detail || 'API Error');
                return d;
            } catch (e) { console.error('POST', url, e); alert('Error: ' + e.message); return null; }
        },
        async apiPatch(url, body) {
            try {
                const r = await fetch(url, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
                const d = await r.json();
                if (!r.ok) throw new Error(d.message || d.detail || 'API Error');
                return d;
            } catch (e) { console.error('PATCH', url, e); return null; }
        },
        async apiDelete(url) {
            try {
                const r = await fetch(url, { method: 'DELETE' });
                if (!r.ok) throw new Error('API Error');
                return true;
            } catch (e) { console.error('DELETE', url, e); return false; }
        },
        async apiDeleteWithBody(url, body) {
            try {
                const r = await fetch(url, { method: 'DELETE', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
                if (!r.ok) throw new Error('API Error');
                return true;
            } catch (e) { console.error('DELETE', url, e); return false; }
        }
    }));
});
