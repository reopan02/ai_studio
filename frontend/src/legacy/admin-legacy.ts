// @ts-nocheck
(function () {
    function getCookie(name) {
        const value = `; ${document.cookie || ''}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    function csrfHeaders() {
        const token = getCookie('csrf_token');
        return token ? { 'X-CSRF-Token': token } : {};
    }

    function escapeHtml(value) {
        return String(value ?? '')
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#39;');
    }

    async function readError(res) {
        const text = await res.text();
        try {
            const data = JSON.parse(text);
            return data?.detail || text;
        } catch {
            return text;
        }
    }

    function formatBytes(bytes) {
        const value = Number(bytes || 0);
        if (!Number.isFinite(value) || value <= 0) return '0 B';
        const units = ['B', 'KiB', 'MiB', 'GiB', 'TiB'];
        let size = value;
        let idx = 0;
        while (size >= 1024 && idx < units.length - 1) {
            size /= 1024;
            idx += 1;
        }
        const digits = idx === 0 ? 0 : (idx <= 2 ? 1 : 2);
        return `${size.toFixed(digits)} ${units[idx]}`;
    }

    function showBanner(message) {
        const el = document.getElementById('errorBanner');
        if (!el) return;
        if (!message) {
            el.style.display = 'none';
            el.textContent = '';
            return;
        }
        el.style.display = 'block';
        el.textContent = message;
    }

    function requireOk(res) {
        if (res.status === 401) {
            window.location.href = '/login?next=/admin';
            return false;
        }
        if (res.status === 403) {
            window.location.href = '/?error=Admin%20access%20required';
            return false;
        }
        return true;
    }

    const state = {
        limit: 50,
        offset: 0,
        lastPageSize: 0,
        selectedUserId: null,
        selectedUser: null,
        search: '',
        isActive: '',
        isAdmin: ''
    };

    function queryString() {
        const params = new URLSearchParams();
        params.set('limit', String(state.limit));
        params.set('offset', String(state.offset));
        if (state.search) params.set('search', state.search);
        if (state.isActive !== '') params.set('is_active', state.isActive);
        if (state.isAdmin !== '') params.set('is_admin', state.isAdmin);
        return params.toString();
    }

    async function loadStats() {
        const res = await fetch('/api/v1/admin/stats', { credentials: 'include' });
        if (!requireOk(res)) return;
        if (!res.ok) throw new Error(await readError(res) || 'Failed to load stats');
        const stats = await res.json();
        document.getElementById('statTotalUsers').textContent = String(stats.total_user_count ?? 0);
        document.getElementById('statActiveUsers').textContent = String(stats.active_user_count ?? 0);
        document.getElementById('statStorageUsed').textContent = formatBytes(stats.total_storage_used_bytes);
        document.getElementById('statStorageQuota').textContent = formatBytes(stats.total_storage_quota_bytes);
        document.getElementById('statVideos').textContent = String(stats.total_video_count ?? 0);
        document.getElementById('statImages').textContent = String(stats.total_image_count ?? 0);
        document.getElementById('statSessions').textContent = String(stats.active_session_count ?? 0);
    }

    function pill(label, cls) {
        return `<span class="pill ${cls}">${escapeHtml(label)}</span>`;
    }

    function renderUsers(users) {
        const tbody = document.getElementById('userTbody');
        if (!tbody) return;
        if (!Array.isArray(users) || users.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="meta-text">No users found.</td></tr>`;
            return;
        }

        tbody.innerHTML = users.map(u => {
            const activePill = u.is_active ? pill('Active', 'pill-green') : pill('Inactive', 'pill-red');
            const rolePill = u.is_admin ? pill('Admin', 'pill-blue') : pill('User', 'pill-gray');
            const storage = `${formatBytes(u.storage_used_bytes)} / ${formatBytes(u.storage_quota_bytes)}`;
            const created = u.created_at ? new Date(u.created_at).toLocaleString() : '-';
            const lastLogin = u.last_login_at ? new Date(u.last_login_at).toLocaleString() : '-';

            return `
                <tr>
                    <td>${escapeHtml(u.username)}</td>
                    <td>${escapeHtml(u.email)}</td>
                    <td>${activePill}</td>
                    <td>${rolePill}</td>
                    <td>${escapeHtml(storage)}</td>
                    <td>${escapeHtml(created)}</td>
                    <td>${escapeHtml(lastLogin)}</td>
                    <td>
                        <div class="row-actions">
                            <button class="btn btn-secondary btn-sm" type="button" data-action="view" data-user-id="${escapeHtml(u.id)}">View</button>
                            <button class="btn btn-secondary btn-sm" type="button" data-action="edit" data-user-id="${escapeHtml(u.id)}">Edit</button>
                            <button class="btn btn-secondary btn-sm" type="button" data-action="delete" data-user-id="${escapeHtml(u.id)}">Delete</button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    }

    async function loadUsers() {
        const res = await fetch(`/api/v1/admin/users?${queryString()}`, { credentials: 'include' });
        if (!requireOk(res)) return;
        if (!res.ok) throw new Error(await readError(res) || 'Failed to load users');
        const users = await res.json();
        state.lastPageSize = Array.isArray(users) ? users.length : 0;
        renderUsers(users);
        renderPagination();
    }

    function renderPagination() {
        const pageLabel = document.getElementById('pageLabel');
        if (pageLabel) {
            pageLabel.textContent = `Page ${Math.floor(state.offset / state.limit) + 1}`;
        }
        const prevBtn = document.getElementById('prevPageBtn');
        const nextBtn = document.getElementById('nextPageBtn');
        if (prevBtn) prevBtn.disabled = state.offset <= 0;
        if (nextBtn) nextBtn.disabled = state.lastPageSize < state.limit;
    }

    function setModalOpen(open) {
        const modal = document.getElementById('userModal');
        if (!modal) return;
        modal.classList.toggle('hidden', !open);
    }

    function fillLoginAttempts(attempts) {
        const tbody = document.getElementById('loginAttemptTbody');
        if (!tbody) return;
        if (!Array.isArray(attempts) || attempts.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="meta-text">No login attempts.</td></tr>`;
            return;
        }
        tbody.innerHTML = attempts.map(a => {
            const time = a.created_at ? new Date(a.created_at).toLocaleString() : '-';
            const result = a.success ? pill('Success', 'pill-green') : pill('Failed', 'pill-red');
            const reason = a.failure_reason ? escapeHtml(a.failure_reason) : '-';
            const ip = a.ip_address ? escapeHtml(a.ip_address) : '-';
            return `<tr><td>${escapeHtml(time)}</td><td>${result}</td><td>${reason}</td><td>${ip}</td></tr>`;
        }).join('');
    }

    async function fetchUserDetail(userId) {
        const res = await fetch(`/api/v1/admin/users/${encodeURIComponent(userId)}`, { credentials: 'include' });
        if (!requireOk(res)) return null;
        if (!res.ok) throw new Error(await readError(res) || 'Failed to load user');
        return await res.json();
    }

    async function openUserModal(userId) {
        showBanner('');
        const data = await fetchUserDetail(userId);
        if (!data) return;

        state.selectedUserId = userId;
        state.selectedUser = data;

        document.getElementById('userModalTitle').textContent = `User: ${data.username}`;
        document.getElementById('editEmail').value = data.email || '';
        document.getElementById('editQuota').value = String(data.storage_quota_bytes ?? 0);
        document.getElementById('editActive').checked = !!data.is_active;
        document.getElementById('editAdmin').checked = !!data.is_admin;

        document.getElementById('detailStorage').textContent =
            `${formatBytes(data.storage_used_bytes)} / ${formatBytes(data.storage_quota_bytes)}`;
        document.getElementById('detailVideos').textContent = String(data.total_video_count ?? 0);
        document.getElementById('detailImages').textContent = String(data.total_image_count ?? 0);
        document.getElementById('detailSessions').textContent = String(data.active_session_count ?? 0);
        fillLoginAttempts(data.recent_login_attempts || []);

        setModalOpen(true);
    }

    async function saveSelectedUser() {
        if (!state.selectedUserId) return;
        const payload = {
            email: String(document.getElementById('editEmail').value || '').trim(),
            is_active: !!document.getElementById('editActive').checked,
            is_admin: !!document.getElementById('editAdmin').checked,
            storage_quota_bytes: Number(document.getElementById('editQuota').value || 0)
        };

        const res = await fetch(`/api/v1/admin/users/${encodeURIComponent(state.selectedUserId)}`, {
            method: 'PATCH',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json', ...csrfHeaders() },
            body: JSON.stringify(payload)
        });
        if (!requireOk(res)) return;
        if (!res.ok) throw new Error(await readError(res) || 'Failed to update user');

        setModalOpen(false);
        state.selectedUserId = null;
        state.selectedUser = null;
        await loadUsers();
    }

    async function deleteSelectedUser() {
        if (!state.selectedUserId) return;
        if (!confirm('Delete this user permanently?')) return;

        const res = await fetch(`/api/v1/admin/users/${encodeURIComponent(state.selectedUserId)}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: { ...csrfHeaders() }
        });
        if (!requireOk(res)) return;
        if (!res.ok) throw new Error(await readError(res) || 'Failed to delete user');

        setModalOpen(false);
        state.selectedUserId = null;
        state.selectedUser = null;
        await loadStats();
        await loadUsers();
    }

    function debounce(fn, delayMs) {
        let timer = null;
        return (...args) => {
            if (timer) clearTimeout(timer);
            timer = setTimeout(() => fn(...args), delayMs);
        };
    }

    function wireEvents() {
        document.getElementById('refreshBtn').addEventListener('click', async () => {
            showBanner('');
            try {
                await loadStats();
                await loadUsers();
            } catch (e) {
                showBanner(e?.message || String(e));
            }
        });

        const onFilterChange = async () => {
            state.offset = 0;
            state.search = String(document.getElementById('searchInput').value || '').trim();
            state.isActive = String(document.getElementById('filterActive').value || '');
            state.isAdmin = String(document.getElementById('filterAdmin').value || '');
            showBanner('');
            try {
                await loadUsers();
            } catch (e) {
                showBanner(e?.message || String(e));
            }
        };

        document.getElementById('searchInput').addEventListener('input', debounce(onFilterChange, 250));
        document.getElementById('filterActive').addEventListener('change', onFilterChange);
        document.getElementById('filterAdmin').addEventListener('change', onFilterChange);

        document.getElementById('prevPageBtn').addEventListener('click', async () => {
            state.offset = Math.max(0, state.offset - state.limit);
            showBanner('');
            try {
                await loadUsers();
            } catch (e) {
                showBanner(e?.message || String(e));
            }
        });

        document.getElementById('nextPageBtn').addEventListener('click', async () => {
            state.offset += state.limit;
            showBanner('');
            try {
                await loadUsers();
            } catch (e) {
                showBanner(e?.message || String(e));
            }
        });

        document.getElementById('userTbody').addEventListener('click', async (evt) => {
            const btn = evt.target?.closest('button[data-action][data-user-id]');
            if (!btn) return;
            const action = btn.getAttribute('data-action');
            const userId = btn.getAttribute('data-user-id');
            if (!userId) return;

            showBanner('');
            try {
                if (action === 'delete') {
                    if (!confirm('Delete this user permanently?')) return;
                    const res = await fetch(`/api/v1/admin/users/${encodeURIComponent(userId)}`, {
                        method: 'DELETE',
                        credentials: 'include',
                        headers: { ...csrfHeaders() }
                    });
                    if (!requireOk(res)) return;
                    if (!res.ok) throw new Error(await readError(res) || 'Failed to delete user');
                    await loadStats();
                    await loadUsers();
                    return;
                }
                await openUserModal(userId);
            } catch (e) {
                showBanner(e?.message || String(e));
            }
        });

        document.getElementById('userModalClose').addEventListener('click', () => setModalOpen(false));
        document.getElementById('userModalBackdrop').addEventListener('click', () => setModalOpen(false));
        document.getElementById('cancelUserBtn').addEventListener('click', () => setModalOpen(false));
        document.getElementById('saveUserBtn').addEventListener('click', async () => {
            showBanner('');
            try {
                await saveSelectedUser();
            } catch (e) {
                showBanner(e?.message || String(e));
            }
        });
        document.getElementById('deleteUserBtn').addEventListener('click', async () => {
            showBanner('');
            try {
                await deleteSelectedUser();
            } catch (e) {
                showBanner(e?.message || String(e));
            }
        });
    }

    async function init() {
        showBanner('');
        try {
            await loadStats();
            await loadUsers();
        } catch (e) {
            showBanner(e?.message || String(e));
        }
        wireEvents();
    }

    document.addEventListener('DOMContentLoaded', init);
})();
