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
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5" style="margin-bottom: 16px;">
                    <path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                </svg>
                <h3>暂无视频记录</h3>
                <p style="margin-top: 8px;">开始生成您的第一个视频吧</p>
                <a href="/video" style="color: #6366f1; text-decoration: none; margin-top: 12px; display: inline-block; font-weight: 500;">去生成视频 →</a>
            </div>
        `;
    }

    function renderVideos(grid, videos) {
        // Update count
        const countEl = typeof document !== 'undefined' ? document.getElementById('videoCount') : null;
        if (countEl) {
            countEl.textContent = `${videos.length} 个视频`;
        }

        grid.innerHTML = videos.map(v => {
            const date = new Date(v.created_at).toLocaleString('zh-CN');
            const modelLower = String(v.model || '').toLowerCase();
            let modelClass = 'badge-default';
            if (modelLower.includes('sora')) modelClass = 'badge-sora2';
            else if (modelLower.includes('veo')) modelClass = 'badge-veo';
            else if (modelLower.includes('seedance')) modelClass = 'badge-seedance';

            const title = escapeHtml(v.title || '未命名视频');
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
                            <span style="color: #94a3b8;">${escapeHtml(date)}</span>
                        </div>
                        <div class="video-prompt" title="${prompt}">${prompt}</div>
                        <div class="video-actions">
                            <a href="${videoUrl}" download class="btn btn-secondary btn-sm" style="text-decoration: none; flex: 1; justify-content: center;">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                    <polyline points="7 10 12 15 17 10"/>
                                    <line x1="12" y1="15" x2="12" y2="3"/>
                                </svg>
                                下载
                            </a>
                            <button onclick="StoragePage.deleteVideoAndReload('${escapeHtml(v.id)}')" class="btn btn-secondary btn-sm danger" style="flex: 1; justify-content: center;">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="3 6 5 6 21 6"/>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                                </svg>
                                删除
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    function renderEmptyImages(grid) {
        grid.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5" style="margin-bottom: 16px;">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                    <circle cx="8.5" cy="8.5" r="1.5"/>
                    <polyline points="21 15 16 10 5 21"/>
                </svg>
                <h3>暂无图像记录</h3>
                <p style="margin-top: 8px;">开始编辑您的第一张图像吧</p>
                <a href="/image" style="color: #6366f1; text-decoration: none; margin-top: 12px; display: inline-block; font-weight: 500;">去图像编辑 →</a>
            </div>
        `;
    }

    function renderImages(grid, images) {
        // Update count
        const countEl = typeof document !== 'undefined' ? document.getElementById('imageCount') : null;
        if (countEl) {
            countEl.textContent = `${images.length} 张图像`;
        }

        grid.innerHTML = images.map(img => {
            const date = new Date(img.created_at).toLocaleString('zh-CN');
            const title = escapeHtml(img.title || '未命名图像');
            const prompt = escapeHtml(img.prompt || '');
            const imageUrl = String(img.image_url || '');

            const media = imageUrl
                ? `<img src="${imageUrl}" alt="${title}" loading="lazy" />`
                : `<div style="color: #cbd5e1; font-size: 14px;">无预览</div>`;

            const download = imageUrl
                ? `<a href="${imageUrl}" download class="btn btn-secondary btn-sm" style="text-decoration: none; flex: 1; justify-content: center;">
                       <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                           <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                           <polyline points="7 10 12 15 17 10"/>
                           <line x1="12" y1="15" x2="12" y2="3"/>
                       </svg>
                       下载
                   </a>`
                : ``;

            return `
                <div class="video-card">
                    <div class="video-thumb">
                        ${media}
                    </div>
                    <div class="video-info">
                        <div class="video-title">${title}</div>
                        <div class="video-meta">
                            <span class="badge badge-default">${escapeHtml(img.model)}</span>
                            <span style="color: #94a3b8;">${escapeHtml(date)}</span>
                        </div>
                        <div class="video-prompt" title="${prompt}">${prompt}</div>
                        <div class="video-actions">
                            ${download}
                            <button onclick="StoragePage.deleteImageAndReload('${escapeHtml(img.id)}')" class="btn btn-secondary btn-sm danger" style="flex: 1; justify-content: center;">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="3 6 5 6 21 6"/>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                                </svg>
                                删除
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    async function loadVideos({ fetchFn, gridEl, onUnauthorized } = {}) {
        const grid = gridEl || (typeof document !== 'undefined' ? document.getElementById('storageGrid') : null);
        const countEl = typeof document !== 'undefined' ? document.getElementById('videoCount') : null;
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
            if (countEl) {
                countEl.textContent = videos.length === 0 ? '暂无记录' : `${videos.length} 个视频`;
            }
            if (!Array.isArray(videos) || videos.length === 0) {
                renderEmpty(grid);
                return;
            }
            renderVideos(grid, videos);
        } catch (e) {
            grid.innerHTML = `<div class="empty-state" style="color: #dc2626; grid-column: 1/-1;"><h3>加载失败</h3><p>${escapeHtml(e?.message || String(e))}</p></div>`;
            if (countEl) countEl.textContent = '加载失败';
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
