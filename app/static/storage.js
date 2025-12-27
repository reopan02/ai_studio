(function (root, factory) {
    if (typeof module === 'object' && module.exports) {
        module.exports = factory();
    } else {
        root.StoragePage = factory();
    }
})(typeof globalThis !== 'undefined' ? globalThis : window, function () {
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

    function renderEmpty(grid) {
        grid.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#d1d1d6" stroke-width="1.5" style="margin-bottom: 16px;">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="17 8 12 3 7 8"/>
                    <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                <p>暂无生成记录</p>
                <a href="/dashboard" style="color: var(--accent-color); text-decoration: none; margin-top: 8px; display: inline-block;">去生成视频</a>
            </div>
        `;
    }

    function renderVideos(grid, videos) {
        grid.innerHTML = videos.map(v => {
            const date = new Date(v.created_at).toLocaleString();
            const modelClass = `badge-${String(v.model || '').toLowerCase().split('-')[0]}`;
            const title = escapeHtml(v.title || '未命名任务');
            const prompt = escapeHtml(v.prompt || '');
            const videoUrl = String(v.video_url || '');

            return `
                <div class="video-card">
                    <div class="video-thumb">
                        <video src="${videoUrl}" controls preload="metadata"></video>
                    </div>
                    <div class="video-info">
                        <div class="video-title">${title}</div>
                        <div class="video-meta">
                            <span class="badge ${modelClass}">${escapeHtml(v.model)}</span>
                            <span>${escapeHtml(date)}</span>
                        </div>
                        <div class="video-prompt" title="${prompt}">${prompt}</div>
                        <div class="video-actions">
                            <a href="${videoUrl}" download class="btn btn-secondary" style="font-size: 12px; padding: 4px 8px;">下载</a>
                            <button onclick="StoragePage.deleteVideoAndReload('${escapeHtml(v.id)}')" class="btn btn-secondary danger" style="font-size: 12px; padding: 4px 8px;">删除</button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    function renderEmptyImages(grid) {
        grid.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <p style="margin-bottom: 8px;">No image records</p>
                <a href="/image" style="color: var(--accent-color); text-decoration: none;">Go to image editor</a>
            </div>
        `;
    }

    function renderImages(grid, images) {
        grid.innerHTML = images.map(img => {
            const date = new Date(img.created_at).toLocaleString();
            const title = escapeHtml(img.title || 'Untitled');
            const prompt = escapeHtml(img.prompt || '');
            const imageUrl = String(img.image_url || '');

            const media = imageUrl
                ? `<img src="${imageUrl}" alt="${title}" loading="lazy" />`
                : `<div style="color: #fff; font-size: 12px;">No preview</div>`;

            const download = imageUrl
                ? `<a href="${imageUrl}" download class="btn btn-secondary" style="font-size: 12px; padding: 4px 8px;">Download</a>`
                : ``;

            return `
                <div class="video-card">
                    <div class="video-thumb">
                        ${media}
                    </div>
                    <div class="video-info">
                        <div class="video-title">${title}</div>
                        <div class="video-meta">
                            <span class="badge">${escapeHtml(img.model)}</span>
                            <span>${escapeHtml(date)}</span>
                        </div>
                        <div class="video-prompt" title="${prompt}">${prompt}</div>
                        <div class="video-actions">
                            ${download}
                            <button onclick="StoragePage.deleteImageAndReload('${escapeHtml(img.id)}')" class="btn btn-secondary danger" style="font-size: 12px; padding: 4px 8px;">Delete</button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    async function loadVideos({ fetchFn, gridEl, onUnauthorized } = {}) {
        const grid = gridEl || (typeof document !== 'undefined' ? document.getElementById('storageGrid') : null);
        const fetchImpl = fetchFn || (typeof fetch !== 'undefined' ? fetch : null);
        if (!grid) throw new Error('storageGrid not found');
        if (!fetchImpl) throw new Error('fetch is not available');

        try {
            const res = await fetchImpl('/api/v1/videos', { credentials: 'include' });
            if (!res.ok) {
                if (res.status === 401) {
                    if (typeof onUnauthorized === 'function') onUnauthorized();
                    return;
                }
                throw new Error(await readError(res) || 'Failed to load videos');
            }

            const videos = await res.json();
            if (!Array.isArray(videos) || videos.length === 0) {
                renderEmpty(grid);
                return;
            }
            renderVideos(grid, videos);
        } catch (e) {
            grid.innerHTML = `<div class="empty-state" style="color: var(--error-color);">加载失败: ${escapeHtml(e?.message || String(e))}</div>`;
        }
    }

    async function loadImages({ fetchFn, gridEl, onUnauthorized } = {}) {
        const grid = gridEl || (typeof document !== 'undefined' ? document.getElementById('imageGrid') : null);
        const fetchImpl = fetchFn || (typeof fetch !== 'undefined' ? fetch : null);
        if (!grid) throw new Error('imageGrid not found');
        if (!fetchImpl) throw new Error('fetch is not available');

        try {
            const res = await fetchImpl('/api/v1/images', { credentials: 'include' });
            if (!res.ok) {
                if (res.status === 401) {
                    if (typeof onUnauthorized === 'function') onUnauthorized();
                    return;
                }
                throw new Error(await readError(res) || 'Failed to load images');
            }

            const images = await res.json();
            if (!Array.isArray(images) || images.length === 0) {
                renderEmptyImages(grid);
                return;
            }
            renderImages(grid, images);
        } catch (e) {
            grid.innerHTML = `<div class="empty-state" style="color: var(--error-color);">Load failed: ${escapeHtml(e?.message || String(e))}</div>`;
        }
    }

    async function deleteVideo(id, { fetchFn, confirmFn, onDeleted } = {}) {
        const fetchImpl = fetchFn || (typeof fetch !== 'undefined' ? fetch : null);
        if (!fetchImpl) throw new Error('fetch is not available');

        const confirmImpl = confirmFn || (typeof confirm !== 'undefined' ? confirm : null);
        if (confirmImpl && !confirmImpl('确定要删除这条记录吗？')) return;

        const res = await fetchImpl(`/api/v1/videos/${encodeURIComponent(id)}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: { ...csrfHeaders() }
        });
        if (!res.ok) {
            throw new Error(await readError(res) || '删除失败');
        }
        if (typeof onDeleted === 'function') onDeleted();
    }

    async function deleteImage(id, { fetchFn, confirmFn, onDeleted } = {}) {
        const fetchImpl = fetchFn || (typeof fetch !== 'undefined' ? fetch : null);
        if (!fetchImpl) throw new Error('fetch is not available');

        const confirmImpl = confirmFn || (typeof confirm !== 'undefined' ? confirm : null);
        if (confirmImpl && !confirmImpl('Delete this record?')) return;

        const res = await fetchImpl(`/api/v1/images/${encodeURIComponent(id)}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: { ...csrfHeaders() }
        });
        if (!res.ok) {
            throw new Error(await readError(res) || 'Delete failed');
        }
        if (typeof onDeleted === 'function') onDeleted();
    }

    async function deleteVideoAndReload(id) {
        try {
            await deleteVideo(id);
            await loadVideos({
                onUnauthorized: () => { window.location.href = '/login?next=/storage'; }
            });
        } catch (e) {
            if (typeof alert === 'function') {
                alert(e?.message || '删除出错');
            }
        }
    }

    async function deleteImageAndReload(id) {
        try {
            await deleteImage(id);
            await loadImages({
                onUnauthorized: () => { window.location.href = '/login?next=/storage'; }
            });
        } catch (e) {
            if (typeof alert === 'function') {
                alert(e?.message || 'Delete failed');
            }
        }
    }

    function init() {
        if (typeof document === 'undefined') return;
        document.addEventListener('DOMContentLoaded', () => {
            loadVideos({
                onUnauthorized: () => { window.location.href = '/login?next=/storage'; }
            });
            loadImages({
                onUnauthorized: () => { window.location.href = '/login?next=/storage'; }
            });
        });
    }

    return {
        getCookie,
        csrfHeaders,
        loadVideos,
        loadImages,
        deleteVideo,
        deleteImage,
        deleteVideoAndReload,
        deleteImageAndReload,
        init,
        _test: { escapeHtml, readError, renderEmpty, renderVideos }
    };
});
