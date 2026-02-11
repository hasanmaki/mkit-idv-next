document.addEventListener('alpine:init', () => {
    Alpine.data('app', () => ({
        // View state
        view: 'servers',
        loading: false,
        userName: 'Admin User',
        userInitials: 'AU',

        // Navigation
        navItems: [
            { id: 'servers', name: 'Servers', icon: '<svg class="w-5 h-5 inline" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>' },
            { id: 'accounts', name: 'Accounts', icon: '<svg class="w-5 h-5 inline" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>' },
            { id: 'bindings', name: 'Bindings', icon: '<svg class="w-5 h-5 inline" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>' },
            { id: 'transactions', name: 'Transactions', icon: '<svg class="w-5 h-5 inline" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/></svg>' },
        ],

        // Data
        servers: [],
        accounts: [],
        bindings: [],
        transactions: [],

        // Modals
        showServerModal: false,
        showAccountModal: false,
        showAccountBulkModal: false,
        showBindingModal: false,
        showVerifyModal: false,
        showTransactionModal: false,
        showOtpSubmitModal: false,

        // Forms
        serverForm: { base_url: '', port: 9900, description: '', timeout: 10, retries: 3 },
        accountForm: { msisdn: '', email: '', batch_id: '', pin: '' },
        accountBulkForm: { msisdns_text: '', email: '', batch_id: '' },
        bindingForm: { server_id: '', account_id: '' },
        verifyForm: { otp: '', pin: '', binding_id: null },
        transactionForm: { binding_id: '', product_id: '650', email: '', limit_harga: 100000, otp_required: false },
        otpForm: { otp: '', transaction_id: null },

        // Initialize
        async init() {
            await this.loadAll();
        },

        async loadAll() {
            await Promise.all([
                this.loadServers(),
                this.loadAccounts(),
                this.loadBindings(),
                this.loadTransactions()
            ]);
        },

        // ====================
        // SERVERS
        // ====================
        async loadServers() {
            const data = await this.apiGet('/v1/servers/');
            if (data) this.servers = data;
        },

        async createServer() {
            const data = await this.apiPost('/v1/servers/', this.serverForm);
            if (data) {
                this.servers.push(data);
                this.showServerModal = false;
                this.serverForm = { base_url: '', port: 9900, description: '', timeout: 10, retries: 3 };
                this.notify('Server created successfully');
            }
        },

        async toggleServerStatus(serverId, isActive) {
            const data = await this.apiPatch(`/v1/servers/${serverId}/status`, { is_active: isActive });
            if (data) {
                const idx = this.servers.findIndex(s => s.id === serverId);
                if (idx !== -1) this.servers[idx] = data;
                this.notify(`Server ${isActive ? 'activated' : 'deactivated'}`);
            }
        },

        async deleteServer(serverId) {
            if (!confirm('Delete this server?')) return;
            const success = await this.apiDelete(`/v1/servers/${serverId}`);
            if (success) {
                this.servers = this.servers.filter(s => s.id !== serverId);
                this.notify('Server deleted');
            }
        },

        // ====================
        // ACCOUNTS
        // ====================
        async loadAccounts() {
            const data = await this.apiGet('/v1/accounts/');
            if (data) this.accounts = data;
        },

        async createAccount() {
            const data = await this.apiPost('/v1/accounts/', this.accountForm);
            if (data) {
                this.accounts.push(data);
                this.showAccountModal = false;
                this.accountForm = { msisdn: '', email: '', batch_id: '', pin: '' };
                this.notify('Account created successfully');
            }
        },

        async createAccountsBulk() {
            const msisdns = this.accountBulkForm.msisdns_text.split('\\n').map(s => s.trim()).filter(s => s);
            const payload = {
                msisdns,
                email: this.accountBulkForm.email,
                batch_id: this.accountBulkForm.batch_id
            };
            const data = await this.apiPost('/v1/accounts/bulk', payload);
            if (data) {
                this.accounts.push(...data);
                this.showAccountBulkModal = false;
                this.accountBulkForm = { msisdns_text: '', email: '', batch_id: '' };
                this.notify(`${data.length} accounts created successfully`);
            }
        },

        async deleteAccount(accountId) {
            if (!confirm('Delete this account?')) return;
            const success = await this.apiDeleteWithBody('/v1/accounts/', { id: accountId });
            if (success) {
                this.accounts = this.accounts.filter(a => a.id !== accountId);
                this.notify('Account deleted');
            }
        },

        // ====================
        // BINDINGS
        // ====================
        async loadBindings() {
            const data = await this.apiGet('/v1/bindings/');
            if (data) this.bindings = data;
        },

        async createBinding() {
            const data = await this.apiPost('/v1/bindings/', this.bindingForm);
            if (data) {
                this.bindings.push(data);
                this.showBindingModal = false;
                this.bindingForm = { server_id: '', account_id: '' };
                this.notify('Binding created successfully');
            }
        },

        showVerifyLoginModal(binding) {
            this.verifyForm.binding_id = binding.id;
            this.showVerifyModal = true;
        },

        async verifyLogin() {
            const { binding_id, otp, pin } = this.verifyForm;
            const payload = { otp };
            if (pin) payload.pin = pin;

            const data = await this.apiPost(`/v1/bindings/${binding_id}/verify-login`, payload);
            if (data) {
                await this.loadBindings();
                this.showVerifyModal = false;
                this.verifyForm = { otp: '', pin: '', binding_id: null };
                this.notify('Login verified successfully');
            }
        },

        async logoutBinding(bindingId) {
            if (!confirm('Logout this binding?')) return;
            const data = await this.apiPost(`/v1/bindings/${bindingId}/logout`, {
                last_error_code: 'manual_logout',
                last_error_message: 'User requested logout'
            });
            if (data) {
                await this.loadBindings();
                this.notify('Binding logged out');
            }
        },

        async deleteBinding(bindingId) {
            if (!confirm('Delete this binding?')) return;
            const success = await this.apiDelete(`/v1/bindings/${bindingId}`);
            if (success) {
                this.bindings = this.bindings.filter(b => b.id !== bindingId);
                this.notify('Binding deleted');
            }
        },

        // ====================
        // TRANSACTIONS
        // ====================
        async loadTransactions() {
            const data = await this.apiGet('/v1/transactions/');
            if (data) this.transactions = data;
        },

        async startTransaction() {
            const data = await this.apiPost('/v1/transactions/start', this.transactionForm);
            if (data) {
                this.transactions.push(data);
                this.showTransactionModal = false;
                this.transactionForm = { binding_id: '', product_id: '650', email: '', limit_harga: 100000, otp_required: false };
                this.notify('Transaction started successfully');
            }
        },

        showOtpModal(transaction) {
            this.otpForm.transaction_id = transaction.id;
            this.showOtpSubmitModal = true;
        },

        async submitOtp() {
            const { transaction_id, otp } = this.otpForm;
            const data = await this.apiPost(`/v1/transactions/${transaction_id}/otp`, { otp });
            if (data) {
                const idx = this.transactions.findIndex(t => t.id === transaction_id);
                if (idx !== -1) this.transactions[idx] = data;
                this.showOtpSubmitModal = false;
                this.otpForm = { otp: '', transaction_id: null };
                this.notify('OTP submitted successfully');
            }
        },

        async continueTransaction(transactionId) {
            const data = await this.apiPost(`/v1/transactions/${transactionId}/continue`, {});
            if (data) {
                const idx = this.transactions.findIndex(t => t.id === transactionId);
                if (idx !== -1) this.transactions[idx] = data;
                this.notify('Transaction continued');
            }
        },

        async pauseTransaction(transactionId) {
            const data = await this.apiPost(`/v1/transactions/${transactionId}/pause`, { reason: 'manual_pause' });
            if (data) {
                const idx = this.transactions.findIndex(t => t.id === transactionId);
                if (idx !== -1) this.transactions[idx] = data;
                this.notify('Transaction paused');
            }
        },

        async resumeTransaction(transactionId) {
            const data = await this.apiPost(`/v1/transactions/${transactionId}/resume`, {});
            if (data) {
                const idx = this.transactions.findIndex(t => t.id === transactionId);
                if (idx !== -1) this.transactions[idx] = data;
                this.notify('Transaction resumed');
            }
        },

        async stopTransaction(transactionId) {
            if (!confirm('Stop this transaction?')) return;
            const data = await this.apiPost(`/v1/transactions/${transactionId}/stop`, { reason: 'manual_stop' });
            if (data) {
                const idx = this.transactions.findIndex(t => t.id === transactionId);
                if (idx !== -1) this.transactions[idx] = data;
                this.notify('Transaction stopped');
            }
        },

        async checkBalance(transactionId) {
            const data = await this.apiPost(`/v1/transactions/${transactionId}/check`, {});
            if (data) {
                alert(`Balance Check:\nAction: ${data.action}\nCurrent Balance: Rp ${data.current_balance?.toLocaleString()}\nThreshold: Rp ${data.threshold?.toLocaleString()}`);
                const idx = this.transactions.findIndex(t => t.id === transactionId);
                if (idx !== -1) this.transactions[idx] = data.transaction;
            }
        },

        // ====================
        // API HELPERS
        // ====================
        async apiGet(endpoint) {
            this.loading = true;
            try {
                const response = await fetch(endpoint);
                if (!response.ok) throw new Error('API Error');
                return await response.json();
            } catch (error) {
                this.notify('Error: ' + error.message, 'error');
                return null;
            } finally {
                this.loading = false;
            }
        },

        async apiPost(endpoint, payload) {
            this.loading = true;
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await response.json();
                if (!response.ok) throw new Error(data.detail || 'API Error');
                return data;
            } catch (error) {
                this.notify('Error: ' + error.message, 'error');
                return null;
            } finally {
                this.loading = false;
            }
        },

        async apiPatch(endpoint, payload) {
            this.loading = true;
            try {
                const response = await fetch(endpoint, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await response.json();
                if (!response.ok) throw new Error(data.detail || 'API Error');
                return data;
            } catch (error) {
                this.notify('Error: ' + error.message, 'error');
                return null;
            } finally {
                this.loading = false;
            }
        },

        async apiDelete(endpoint) {
            this.loading = true;
            try {
                const response = await fetch(endpoint, { method: 'DELETE' });
                if (!response.ok) throw new Error('API Error');
                return true;
            } catch (error) {
                this.notify('Error: ' + error.message, 'error');
                return false;
            } finally {
                this.loading = false;
            }
        },

        async apiDeleteWithBody(endpoint, payload) {
            this.loading = true;
            try {
                const response = await fetch(endpoint, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (!response.ok) throw new Error('API Error');
                return true;
            } catch (error) {
                this.notify('Error: ' + error.message, 'error');
                return false;
            } finally {
                this.loading = false;
            }
        },

        notify(message, type = 'success') {
            // Simple notification (you can enhance this with a toast library)
            console.log(`[${type.toUpperCase()}] ${message}`);
            alert(message);
        }
    }));
});
