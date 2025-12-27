(function (root, factory) {
    if (typeof module === 'object' && module.exports) {
        module.exports = factory();
    } else {
        root.StoragePage = factory();
    }
})(typeof globalThis !== 'undefined' ? globalThis : window, function () {
    // State management
    const state = {
        activeTab: 'videos', // 'videos' or 'images'
        page: 1,
        size: 12,
        search: '',
        model: '',
        loading: false,
        total: 0,
        pages: 0
    };

    function getCookie(name, cookieString) {
        const source = typeof cookieString === 'string' ? cookieString : (typeof document !== 'undefined' ? document.cookie : '');
        const value = `; ${source}`;
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

    function renderEmpty() {
        const grid = document.getElementById('storageGrid');
        const typeText = state.activeTab === 'videos' ? '视频' : '图片';
        const link = state.activeTab === 'videos' ? '/dashboard' : '/image';
        
        grid.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#d1d1d6" stroke-width="1.5" style="margin-bottom: 16px;">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="17 8 12 3 7 8"/>
                    <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                <p>暂无${typeText}记录</p>
                <a href="${link}" style="color: var(--accent-color); text-decoration: none; margin-top: 8px; display: inline-block;">去生成${typeText}</a>
            </div>
        `;
    }

    function renderVideos(videos) {
        const grid = document.getElementById('storageGrid');
        grid.innerHTML = videos.map(v => {
            const date = new Date(v.created_at).toLocaleString();
            const modelClass = `badge-${String(v.model || '').toLowerCase().split('-')[0]}`;
            const title = escapeHtml(v.title || '未命名视频');
            const prompt = escapeHtml(v.prompt || '');
            const videoUrl = String(v.video_url || '');

            return `
                <div class="video-card">
                    <div class="video-thumb">
                        <video src="${videoUrl}" controls preload="metadata"></video>
                    </div>
                    <div class="video-info">
                        <div class="video-title" title="${title}">${title}</div>
                        <div class="video-meta">
                            <span class="badge ${modelClass}">${escapeHtml(v.model)}</span>
                            <span>${escapeHtml(date)}</span>
                        </div>
                        <div class="video-prompt" title="${prompt}">${prompt}</div>
                        <div class="video-actions">
                            <a href="${videoUrl}" download class="btn btn-secondary" style="font-size: 12px; padding: 4px 8px;">下载</a>
                            <button onclick="StoragePage.deleteItem('${escapeHtml(v.id)}')" class="btn btn-secondary danger" style="font-size: 12px; padding: 4px 8px;">删除</button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    function renderImages(images) {
        const grid = document.getElementById('storageGrid');
        grid.innerHTML = images.map(img => {
            const date = new Date(img.created_at).toLocaleString();
            const title = escapeHtml(img.title || '未命名图片');
            const prompt = escapeHtml(img.prompt || '');
            const imageUrl = String(img.image_url || '');

            const media = imageUrl
                ? `<img src="${imageUrl}" alt="${title}" loading="lazy" onclick="window.open('${imageUrl}', '_blank')" style="cursor: pointer;">`
                : `<div style="color: #fff; font-size: 12px;">无预览</div>`;

            return `
                <div class="video-card">
                    <div class="video-thumb">
                        ${media}
                    </div>
                    <div class="video-info">
                        <div class="video-title" title="${title}">${title}</div>
                        <div class="video-meta">
                            <span class="badge">${escapeHtml(img.model)}</span>
                            <span>${escapeHtml(date)}</span>
                        </div>
                        <div class="video-prompt" title="${prompt}">${prompt}</div>
                        <div class="video-actions">
                            ${imageUrl ? `<a href="${imageUrl}" download class="btn btn-secondary" style="font-size: 12px; padding: 4px 8px;">下载</a>` : ''}
                            <button onclick="StoragePage.deleteItem('${escapeHtml(img.id)}')" class="btn btn-secondary danger" style="font-size: 12px; padding: 4px 8px;">删除</button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    function renderPagination() {
        const container = document.getElementById('pagination');
        if (state.pages <= 1) {
            container.innerHTML = '';
            return;
        }

        let html = `
            <button class="page-btn" onclick="StoragePage.changePage(${state.page - 1})" ${state.page === 1 ? 'disabled' : ''}>上一页</button>
        `;

        // Simple pagination logic: show current, first, last, and some neighbors
        const start = Math.max(1, state.page - 2);
        const end = Math.min(state.pages, state.page + 2);

        if (start > 1) {
            html += `<button class="page-btn" onclick="StoragePage.changePage(1)">1</button>`;
            if (start > 2) html += `<span>...</span>`;
        }

        for (let i = start; i <= end; i++) {
            html += `<button class="page-btn ${i === state.page ? 'active' : ''}" onclick="StoragePage.changePage(${i})">${i}</button>`;
        }

        if (end < state.pages) {
            if (end < state.pages - 1) html += `<span>...</span>`;
            html += `<button class="page-btn" onclick="StoragePage.changePage(${state.pages})">${state.pages}</button>`;
        }

        html += `
            <button class="page-btn" onclick="StoragePage.changePage(${state.page + 1})" ${state.page === state.pages ? 'disabled' : ''}>下一页</button>
        `;

        container.innerHTML = html;
    }

    function updateModelFilter() {
        const select = document.getElementById('modelFilter');
        const models = state.activeTab === 'videos' 
            ? ['sora2-video', 'veo-video', 'seedance-video', 'luma-video', 'kling-video', 'runway-video']
            : ['dall-e-3', 'flux-pro', 'stable-diffusion-3', 'midjourney'];
        
        let html = '<option value="">所有模型</option>';
        models.forEach(m => {
            html += `<option value="${m}" ${state.model === m ? 'selected' : ''}>${m}</option>`;
        });
        select.innerHTML = html;
    }

    async function loadData() {
        if (state.loading) return;
        state.loading = true;
        
        const grid = document.getElementById('storageGrid');
        grid.innerHTML = '<div class="empty-state" style="grid-column: 1/-1;">加载中...</div>';

        const params = new URLSearchParams({
            page: state.page,
            size: state.size
        });
        if (state.search) params.append('search', state.search);
        if (state.model) params.append('model', state.model);

        const endpoint = state.activeTab === 'videos' ? '/api/v1/videos' : '/api/v1/images';
        
        try {
            const res = await fetch(`${endpoint}?${params.toString()}`, { credentials: 'include' });
            if (!res.ok) {
                if (res.status === 401) {
                    window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
                    return;
                }
                throw new Error(await readError(res) || '加载失败');
            }

            const data = await res.json();
            state.total = data.total;
            state.pages = data.pages;
            
            if (!data.items || data.items.length === 0) {
                renderEmpty();
            } else {
                if (state.activeTab === 'videos') {
                    renderVideos(data.items);
                } else {
                    renderImages(data.items);
                }
            }
            renderPagination();
        } catch (e) {
            grid.innerHTML = `<div class="empty-state" style="color: var(--error-color); grid-column: 1/-1;">加载失败: ${escapeHtml(e?.message || String(e))}</div>`;
        } finally {
            state.loading = false;
        }
    }

    // Public API
    return {
        init: function() {
            updateModelFilter();
            loadData();
        },

        switchTab: function(tab) {
            if (state.activeTab === tab) return;
            state.activeTab = tab;
            state.page = 1;
            state.model = '';
            
            document.getElementById('tabVideos').classList.toggle('active', tab === 'videos');
            document.getElementById('tabImages').classList.toggle('active', tab === 'images');
            
            updateModelFilter();
            loadData();
        },

        changePage: function(p) {
            if (p < 1 || p > state.pages || p === state.page) return;
            state.page = p;
            loadData();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        },

        handleSearch: function(val) {
            state.search = val.trim();
            state.page = 1;
            // Debounce search
            if (this.searchTimeout) clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => loadData(), 500);
        },

        handleFilter: function(val) {
            state.model = val;
            state.page = 1;
            loadData();
        },

        refresh: function() {
            loadData();
        },

        deleteItem: async function(id) {
            if (!confirm('确定要删除这条记录吗？')) return;
            
            const endpoint = state.activeTab === 'videos' ? `/api/v1/videos/${id}` : `/api/v1/images/${id}`;
            
            try {
                const res = await fetch(endpoint, {
                    method: 'DELETE',
                    credentials: 'include',
                    headers: { ...csrfHeaders() }
                });
                
                if (!res.ok) throw new Error(await readError(res) || '删除失败');
                
                loadData();
            } catch (e) {
                alert('删除失败: ' + (e?.message || String(e)));
            }
        }
    };
});
