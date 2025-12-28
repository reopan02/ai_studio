document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const els = {
        apiKey: document.getElementById('apiKey'),
        baseUrl: document.getElementById('baseUrl'),
        toggleApiKey: document.getElementById('toggleApiKey'),
        modelSelect: document.getElementById('modelSelect'),
        promptInput: document.getElementById('promptInput'),
        taskNameInput: document.getElementById('taskNameInput'),
        batchCount: document.getElementById('batchCount'),
        sora2Params: document.getElementById('sora2Params'),
        soraVariant: document.getElementById('soraVariant'),
        aspectRatio: document.getElementById('aspectRatio'),
        duration: document.getElementById('duration'),
        soraHd: document.getElementById('soraHd'),
        soraWatermark: document.getElementById('soraWatermark'),
        soraPrivate: document.getElementById('soraPrivate'),
        soraImages: document.getElementById('soraImages'),
        soraDropzone: document.getElementById('soraDropzone'),
        soraPickFiles: document.getElementById('soraPickFiles'),
        soraClearImages: document.getElementById('soraClearImages'),
        soraImageCount: document.getElementById('soraImageCount'),
        soraImagePreview: document.getElementById('soraImagePreview'),
        soraImageSourceInput: document.getElementById('soraImageSourceInput'),
        soraAddImageSources: document.getElementById('soraAddImageSources'),
        soraUploadFeedback: document.getElementById('soraUploadFeedback'),
        soraUploadText: document.getElementById('soraUploadText'),
        soraUploadProgress: document.getElementById('soraUploadProgress'),
        soraUploadMeta: document.getElementById('soraUploadMeta'),
        promptImages: document.getElementById('promptImages'),
        promptDropzone: document.getElementById('promptDropzone'),
        promptPickFiles: document.getElementById('promptPickFiles'),
        promptUploadFeedback: document.getElementById('promptUploadFeedback'),
        promptUploadText: document.getElementById('promptUploadText'),
        promptUploadProgress: document.getElementById('promptUploadProgress'),
        promptUploadMeta: document.getElementById('promptUploadMeta'),
        notifyHook: document.getElementById('notifyHook'),
        generateBtn: document.getElementById('generateBtn'),
        statusContainer: document.getElementById('statusContainer'),
        statusContent: document.getElementById('statusContent'),
        taskSummary: document.getElementById('taskSummary'),
        clearCompletedBtn: document.getElementById('clearCompletedBtn'),
        taskList: document.getElementById('taskList'),
        taskListFooter: document.getElementById('taskListFooter'),
        loadMoreTasksBtn: document.getElementById('loadMoreTasksBtn'),
        imageModal: document.getElementById('imageModal'),
        modalBackdrop: document.getElementById('modalBackdrop'),
        modalClose: document.getElementById('modalClose'),
        modalImage: document.getElementById('modalImage'),
        modalValue: document.getElementById('modalValue'),
        modalCopy: document.getElementById('modalCopy'),
        modalSave: document.getElementById('modalSave'),
        toastContainer: document.getElementById('toastContainer'),
        // New unified layout elements
        historyBtn: document.getElementById('historyBtn'),
        historyPanel: document.getElementById('historyPanel'),
        closeHistoryBtn: document.getElementById('closeHistoryBtn'),
        saveConfigBtn: document.getElementById('saveConfigBtn'),
        resetConfigBtn: document.getElementById('resetConfigBtn'),
        charCount: document.getElementById('charCount'),
        statusDot: document.getElementById('statusDot'),
        statusText: document.getElementById('statusText'),
        inlineHistorySection: document.getElementById('inlineHistorySection'),
        inlineHistoryToggle: document.getElementById('inlineHistoryToggle'),
        inlineHistoryContent: document.getElementById('inlineHistoryContent'),
        inlineHistoryGrid: document.getElementById('inlineHistoryGrid'),
        inlineHistoryCount: document.getElementById('inlineHistoryCount'),
        showMoreHistoryBtn: document.getElementById('showMoreHistoryBtn'),
        resultPlaceholder: document.getElementById('resultPlaceholder'),
        loadingState: document.getElementById('loadingState'),
        resultContainer: document.getElementById('resultContainer'),
        resultVideo: document.getElementById('resultVideo'),
        progressFill: document.getElementById('progressFill'),
        progressText: document.getElementById('progressText')
    };

    const CONFIG = {
        submitDebounceMs: 120,
        confirmBatchThreshold: 6,
        maxBatchCount: 20,
        renderPageSize: 20,
        maxTasks: 200,
        cleanupAfterMs: 10 * 60 * 1000,
        pollIntervalMs: 4000,
        pollJitterMs: 600,
        maxPollErrors: 3,
        createConcurrency: 4,
        pollConcurrency: 8,
        saveConcurrency: 2,
        maxLogsPerTask: 200,
        imageCompressThresholdBytes: 5 * 1024 * 1024,
        imageMaxDimension: 2048
    };

    const imagesState = {
        items: [],
        editingId: null,
        readingCount: 0
    };

    const tasksState = {
        byLocalId: new Map(),
        order: [],
        renderLimit: CONFIG.renderPageSize,
        nextIndex: 1,
        lastSubmitAt: 0,
        createQueue: createRequestQueue(CONFIG.createConcurrency),
        pollQueue: createRequestQueue(CONFIG.pollConcurrency),
        saveQueue: createRequestQueue(CONFIG.saveConcurrency)
    };

    // Load Config
    els.apiKey.value = localStorage.getItem('video_api_key') || '';
    const defaultBaseUrl = els.baseUrl.value || 'https://api.gpt-best.com';
    const savedBaseUrl = localStorage.getItem('video_base_url') || defaultBaseUrl;
    try {
        els.baseUrl.value = normalizeApiBaseUrl(savedBaseUrl);
    } catch {
        els.baseUrl.value = defaultBaseUrl;
        localStorage.removeItem('video_base_url');
    }

    // Load persisted UI state
    const savedModel = localStorage.getItem('video_model');
    if (savedModel && Array.from(els.modelSelect.options).some(o => o.value === savedModel)) {
        els.modelSelect.value = savedModel;
    }

    const savedSoraVariant = localStorage.getItem('video_sora_variant');
    if (savedSoraVariant && Array.from(els.soraVariant.options).some(o => o.value === savedSoraVariant)) {
        els.soraVariant.value = savedSoraVariant;
    }

    const savedAspectRatio = localStorage.getItem('video_aspect_ratio');
    if (savedAspectRatio && Array.from(els.aspectRatio.options).some(o => o.value === savedAspectRatio)) {
        els.aspectRatio.value = savedAspectRatio;
    }

    const savedDuration = localStorage.getItem('video_duration');
    if (savedDuration && Array.from(els.duration.options).some(o => o.value === savedDuration)) {
        els.duration.value = savedDuration;
    }

    const savedBatchCount = localStorage.getItem('video_batch_count');
    if (savedBatchCount) {
        const n = Number.parseInt(savedBatchCount, 10);
        if (Number.isFinite(n) && n >= 1 && n <= CONFIG.maxBatchCount) {
            els.batchCount.value = String(n);
        }
    }

    initToggleVisibility();

    function initToggleVisibility() {
        document.querySelectorAll('.toggle-visibility').forEach((btn) => {
            btn.addEventListener('click', () => {
                const targetId = btn.getAttribute('data-target') || '';
                const input = targetId ? document.getElementById(targetId) : null;
                if (!input) return;
                input.type = input.type === 'password' ? 'text' : 'password';
            });
        });
    }

    // --- Helpers (Restored) ---

    function createRequestQueue(concurrency) {
        let running = 0;
        const queue = [];
        const run = async () => {
            if (running >= concurrency || queue.length === 0) return;
            running++;
            const { fn, resolve, reject, signal } = queue.shift();
            if (signal?.aborted) {
                reject(new DOMException('Aborted', 'AbortError'));
                running--;
                run();
                return;
            }
            try {
                const res = await fn();
                resolve(res);
            } catch (e) {
                reject(e);
            } finally {
                running--;
                run();
            }
        };
        return {
            enqueue: (fn, { signal } = {}) => new Promise((resolve, reject) => {
                queue.push({ fn, resolve, reject, signal });
                run();
            })
        };
    }

    function clampInt(val, min, max, def) {
        const n = Number.parseInt(String(val), 10);
        return Number.isFinite(n) ? Math.min(max, Math.max(min, n)) : def;
    }

    function formatTime(ms) {
        if (!ms) return '—';
        return new Date(ms).toLocaleTimeString();
    }

    function formatDuration(ms) {
        if (!ms || ms < 0) return '0s';
        const s = Math.floor(ms / 1000);
        const m = Math.floor(s / 60);
        const remS = s % 60;
        return m > 0 ? `${m}m ${remS}s` : `${s}s`;
    }

    function getStatusLabel(status) {
        const map = {
            queued: '排队中',
            pending: '等待中',
            processing: '处理中',
            completed: '已完成',
            failed: '失败',
            cancelled: '已取消'
        };
        return map[status] || status;
    }

    function isTerminalStatus(status) {
        return ['completed', 'failed', 'cancelled'].includes(status);
    }

    function closeImageModal() {
        els.imageModal.classList.add('hidden');
        imagesState.editingId = null;
        els.modalValue.value = '';
        els.modalImage.src = '';
    }

    function addSourcesFromText(text) {
        const lines = parseLines(text);
        let count = 0;
        for (const line of lines) {
            if (isValidImageSource(line)) {
                imagesState.items.push({
                    id: Math.random().toString(36).slice(2),
                    kind: line.startsWith('data:image') ? 'data' : 'url',
                    value: line
                });
                count++;
            }
        }
        return count;
    }

    function buildTaskPayload(modelKey, prompt) {
        if (modelKey === 'sora2') {
            const variant = els.soraVariant.value;
            const duration = Number.parseInt(els.duration.value, 10);
            const aspectRatio = els.aspectRatio.value;
            const hd = els.soraHd.checked;
            const watermark = els.soraWatermark.checked;
            const isPrivate = els.soraPrivate.checked;
            
            const imageSources = imagesState.items.map(x => x.value);
            
            return {
                metaSummary: `Sora 2 (${variant}), ${duration}s, ${aspectRatio}`,
                payload: {
                    model: variant,
                    prompt,
                    aspect_ratio: aspectRatio,
                    duration,
                    hd,
                    watermark,
                    private: isPrivate,
                    image_sources: imageSources
                }
            };
        } else if (modelKey === 'veo') {
             return {
                metaSummary: 'Google Veo',
                payload: { model: 'veo', prompt }
            };
        } else if (modelKey === 'seedance') {
             return {
                metaSummary: 'Seedance',
                payload: { model: 'seedance', prompt }
            };
        } else {
             return {
                metaSummary: 'New Model',
                payload: { model: 'newmodel', prompt }
            };
        }
    }

    function parseProviderTask(data) {
        const d = data || {};
        const result = {
            taskId: d.id || d.task_id,
            status: d.status || 'pending',
            progress: typeof d.process === 'number' ? d.process : 0,
            failReason: d.fail_reason || d.error || '',
            videoUrl: d.video?.url || d.video_url || d.url || null,
            platform: 'api',
            action: 'generate',
            submitTimeMs: d.created_at ? new Date(d.created_at).getTime() : undefined,
            startTimeMs: d.started_at ? new Date(d.started_at).getTime() : undefined,
            finishTimeMs: d.finished_at ? new Date(d.finished_at).getTime() : undefined,
            cost: d.cost
        };
        
        if (result.status === 'succeeded' || result.status === 'SUCCESS') result.status = 'completed';
        if (result.status === 'failure' || result.status === 'FAILURE') result.status = 'failed';
        
        return result;
    }

    els.apiKey.addEventListener('change', () => localStorage.setItem('video_api_key', els.apiKey.value));
    els.baseUrl.addEventListener('change', () => {
        try {
            const normalized = normalizeApiBaseUrl(els.baseUrl.value);
            els.baseUrl.value = normalized;
            localStorage.setItem('video_base_url', normalized);
        } catch (e) {
            log(`错误: ${e.message}`, 'error');
            localStorage.removeItem('video_base_url');
            els.baseUrl.focus();
        }
    });

    // Persist UI state changes
    els.modelSelect.addEventListener('change', () => {
        localStorage.setItem('video_model', els.modelSelect.value);
        syncModelUI();
    });
    els.soraVariant.addEventListener('change', () => {
        localStorage.setItem('video_sora_variant', els.soraVariant.value);
        syncSoraConstraints();
    });
    els.aspectRatio.addEventListener('change', () => {
        localStorage.setItem('video_aspect_ratio', els.aspectRatio.value);
    });
    els.duration.addEventListener('change', () => {
        localStorage.setItem('video_duration', els.duration.value);
        syncSoraConstraints();
    });

    els.soraHd.addEventListener('change', syncSoraConstraints);

    els.batchCount.addEventListener('change', () => {
        const n = Number.parseInt(String(els.batchCount.value || '1'), 10);
        if (Number.isFinite(n)) {
            const clamped = Math.min(CONFIG.maxBatchCount, Math.max(1, n));
            els.batchCount.value = String(clamped);
            localStorage.setItem('video_batch_count', String(clamped));
        }
    });

    if (els.soraPickFiles && els.soraImages) {
        els.soraPickFiles.addEventListener('click', () => els.soraImages.click());
        els.soraImages.addEventListener('change', async () => {
            const files = els.soraImages.files ? Array.from(els.soraImages.files) : [];
            await addFiles(files, { source: 'sora' });
            els.soraImages.value = '';
        });
    }

    if (els.promptPickFiles && els.promptImages) {
        els.promptPickFiles.addEventListener('click', () => els.promptImages.click());
        els.promptImages.addEventListener('change', async () => {
            const files = els.promptImages.files ? Array.from(els.promptImages.files) : [];
            await addFiles(files, { source: 'prompt' });
            els.promptImages.value = '';
        });
    }

    if (els.soraClearImages) {
        els.soraClearImages.addEventListener('click', () => {
            imagesState.items = [];
            renderImagePreview();
            log('已清空参考图片', 'info');
        });
    }

    if (els.soraAddImageSources && els.soraImageSourceInput) {
        els.soraAddImageSources.addEventListener('click', () => {
            const raw = els.soraImageSourceInput.value;
            const added = addSourcesFromText(raw);
            if (added > 0) {
                els.soraImageSourceInput.value = '';
                renderImagePreview();
                log(`已添加 ${added} 个图片来源`, 'success');
            }
        });

        els.soraImageSourceInput.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                els.soraAddImageSources.click();
            }
        });
    }

    initDropzone();
    initModal();

    els.generateBtn.addEventListener('click', handleSubmit);
    els.clearCompletedBtn.addEventListener('click', () => {
        clearCompletedTasks();
        renderTaskList();
        toast('已清理已完成任务', 'info');
    });
    els.loadMoreTasksBtn.addEventListener('click', () => {
        tasksState.renderLimit += CONFIG.renderPageSize;
        renderTaskList();
    });

    // --- Unified Layout Event Handlers ---

    // History panel toggle
    if (els.historyBtn) {
        els.historyBtn.addEventListener('click', () => {
            els.historyPanel?.classList.add('open');
            document.body.classList.add('panel-open');
        });
    }
    if (els.closeHistoryBtn) {
        els.closeHistoryBtn.addEventListener('click', () => {
            els.historyPanel?.classList.remove('open');
            document.body.classList.remove('panel-open');
        });
    }

    // Close panel when clicking outside
    els.historyPanel?.addEventListener('click', (e) => {
        if (e.target === els.historyPanel) {
            els.historyPanel.classList.remove('open');
            document.body.classList.remove('panel-open');
        }
    });

    // Collapsible sections
    document.querySelectorAll('.collapsible-header').forEach(header => {
        const targetId = header.dataset.target;
        const content = document.getElementById(targetId);
        if (!content) return;

        // Restore collapsed state from localStorage
        // API Configuration (configContent) is collapsed by default
        const savedState = localStorage.getItem(`collapsed_${targetId}`);
        const defaultCollapsed = targetId === 'configContent';
        const shouldCollapse = savedState === null ? defaultCollapsed : savedState === 'true';

        if (shouldCollapse) {
            header.classList.add('collapsed');
            content.classList.add('collapsed');
        }

        header.addEventListener('click', () => {
            const isCollapsed = header.classList.toggle('collapsed');
            content.classList.toggle('collapsed', isCollapsed);
            localStorage.setItem(`collapsed_${targetId}`, String(isCollapsed));
        });
    });

    // Config save/reset buttons
    if (els.saveConfigBtn) {
        els.saveConfigBtn.addEventListener('click', () => {
            localStorage.setItem('video_api_key', els.apiKey.value);
            try {
                const normalized = normalizeApiBaseUrl(els.baseUrl.value);
                localStorage.setItem('video_base_url', normalized);
                els.baseUrl.value = normalized;
            } catch (e) {
                log(`Base URL 错误: ${e.message}`, 'error');
            }
            toast('配置已保存', 'success');
        });
    }

    if (els.resetConfigBtn) {
        els.resetConfigBtn.addEventListener('click', () => {
            if (confirm('确定要重置配置吗？这将清除保存的 API Key 和 Base URL。')) {
                localStorage.removeItem('video_api_key');
                localStorage.removeItem('video_base_url');
                els.apiKey.value = '';
                els.baseUrl.value = 'https://api.gpt-best.com';
                toast('配置已重置', 'info');
            }
        });
    }

    // Character count update
    if (els.promptInput && els.charCount) {
        const updateCharCount = () => {
            els.charCount.textContent = `${els.promptInput.value.length} 字符`;
        };
        els.promptInput.addEventListener('input', updateCharCount);
        updateCharCount();
    }

    // Inline history section toggle
    if (els.inlineHistoryToggle && els.inlineHistoryContent) {
        const savedHistoryState = localStorage.getItem('inlineHistoryCollapsed');
        if (savedHistoryState === 'true') {
            els.inlineHistorySection?.classList.add('collapsed');
        }

        els.inlineHistoryToggle.addEventListener('click', () => {
            const isCollapsed = els.inlineHistorySection?.classList.toggle('collapsed');
            localStorage.setItem('inlineHistoryCollapsed', String(isCollapsed));
        });
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Escape to close panels
        if (e.key === 'Escape') {
            if (els.historyPanel?.classList.contains('open')) {
                els.historyPanel.classList.remove('open');
                document.body.classList.remove('panel-open');
                e.preventDefault();
            }
            const editModal = document.getElementById('editPromptModalOverlay');
            if (editModal && !editModal.classList.contains('hidden')) {
                editModal.classList.add('hidden');
                e.preventDefault();
            }
        }
        // Ctrl+Enter to submit
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            if (document.activeElement === els.promptInput) {
                e.preventDefault();
                handleSubmit();
            }
        }
    });

    // --- Inline History State & Functions ---
    const inlineHistoryState = {
        items: [],
        displayLimit: 6,
        loading: false
    };

    async function loadInlineHistory() {
        if (inlineHistoryState.loading) return;
        inlineHistoryState.loading = true;

        try {
            const res = await fetch('/api/v1/videos?limit=50', {
                credentials: 'include',
                headers: csrfHeaders()
            });
            if (!res.ok) {
                if (res.status === 401) {
                    inlineHistoryState.items = [];
                    renderInlineHistory();
                    return;
                }
                throw new Error(`加载失败 (${res.status})`);
            }
            const data = await res.json();
            inlineHistoryState.items = Array.isArray(data) ? data : (data.items || []);
            renderInlineHistory();
        } catch (e) {
            log(`加载历史记录失败: ${e.message}`, 'error');
        } finally {
            inlineHistoryState.loading = false;
        }
    }

    function renderInlineHistory() {
        if (!els.inlineHistoryGrid || !els.inlineHistoryCount) return;

        const items = inlineHistoryState.items;
        els.inlineHistoryCount.textContent = items.length;

        if (items.length === 0) {
            els.inlineHistoryGrid.innerHTML = '<div class="inline-history-empty">暂无生成记录</div>';
            if (els.showMoreHistoryBtn) els.showMoreHistoryBtn.style.display = 'none';
            return;
        }

        const displayItems = items.slice(0, inlineHistoryState.displayLimit);
        els.inlineHistoryGrid.innerHTML = '';

        displayItems.forEach(item => {
            const card = document.createElement('div');
            card.className = 'inline-history-item';
            card.dataset.id = item.id;

            // Thumbnail
            const thumb = document.createElement('div');
            thumb.className = 'inline-history-thumb';
            if (item.video_url || item.thumbnail_url) {
                const video = document.createElement('video');
                video.src = item.video_url || '';
                video.muted = true;
                video.loop = true;
                video.playsInline = true;
                video.preload = 'metadata';
                thumb.appendChild(video);

                // Play on hover
                card.addEventListener('mouseenter', () => video.play().catch(() => {}));
                card.addEventListener('mouseleave', () => {
                    video.pause();
                    video.currentTime = 0;
                });
            } else {
                thumb.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>';
            }

            // Info
            const info = document.createElement('div');
            info.className = 'inline-history-info';

            const prompt = document.createElement('div');
            prompt.className = 'inline-history-prompt';
            prompt.textContent = (item.prompt || '无提示词').slice(0, 60) + ((item.prompt?.length > 60) ? '...' : '');
            prompt.title = item.prompt || '';

            const meta = document.createElement('div');
            meta.className = 'inline-history-meta';
            const modelName = item.model || 'unknown';
            const timeStr = item.created_at ? new Date(item.created_at).toLocaleDateString() : '';
            meta.textContent = `${modelName} · ${timeStr}`;

            info.appendChild(prompt);
            info.appendChild(meta);

            // Actions (hover-reveal)
            const actions = document.createElement('div');
            actions.className = 'inline-history-actions';

            const loadBtn = document.createElement('button');
            loadBtn.className = 'inline-history-btn';
            loadBtn.title = '加载';
            loadBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"></polyline><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path></svg>';
            loadBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                loadHistoryItem(item);
            });

            const editBtn = document.createElement('button');
            editBtn.className = 'inline-history-btn';
            editBtn.title = '编辑提示词';
            editBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>';
            editBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                openEditPromptModal(item);
            });

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'inline-history-btn danger';
            deleteBtn.title = '删除';
            deleteBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>';
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                deleteHistoryItem(item.id);
            });

            actions.appendChild(loadBtn);
            actions.appendChild(editBtn);
            actions.appendChild(deleteBtn);

            card.appendChild(thumb);
            card.appendChild(info);
            card.appendChild(actions);

            // Click to load
            card.addEventListener('click', () => loadHistoryItem(item));

            els.inlineHistoryGrid.appendChild(card);
        });

        // Show more button
        if (els.showMoreHistoryBtn) {
            els.showMoreHistoryBtn.style.display = items.length > inlineHistoryState.displayLimit ? '' : 'none';
        }
    }

    function loadHistoryItem(item) {
        if (item.prompt) {
            els.promptInput.value = item.prompt;
            if (els.charCount) {
                els.charCount.textContent = `${item.prompt.length} 字符`;
            }
        }
        // Show video in result area
        if (item.video_url && els.resultContainer && els.resultVideo) {
            els.resultPlaceholder?.classList.add('hidden');
            els.loadingState?.classList.add('hidden');
            els.resultContainer.classList.remove('hidden');
            els.resultVideo.src = item.video_url;
        }
        toast('已加载历史记录', 'success');
    }

    function openEditPromptModal(item) {
        const overlay = document.getElementById('editPromptModalOverlay');
        const textarea = document.getElementById('editPromptTextarea');
        const saveBtn = document.getElementById('saveEditPromptBtn');
        const cancelBtn = document.getElementById('cancelEditPromptBtn');

        if (!overlay || !textarea) return;

        textarea.value = item.prompt || '';
        overlay.classList.remove('hidden');
        textarea.focus();

        const handleSave = async () => {
            const newPrompt = textarea.value.trim();
            if (!newPrompt) {
                toast('提示词不能为空', 'error');
                return;
            }
            try {
                const res = await fetch(`/api/v1/videos/${item.id}`, {
                    method: 'PATCH',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        ...csrfHeaders()
                    },
                    body: JSON.stringify({ prompt: newPrompt })
                });
                if (!res.ok) throw new Error(`更新失败 (${res.status})`);
                overlay.classList.add('hidden');
                toast('提示词已更新', 'success');
                loadInlineHistory();
            } catch (e) {
                toast(`更新失败: ${e.message}`, 'error');
            }
        };

        const handleCancel = () => {
            overlay.classList.add('hidden');
        };

        // Remove old listeners
        const newSaveBtn = saveBtn.cloneNode(true);
        const newCancelBtn = cancelBtn.cloneNode(true);
        saveBtn.parentNode.replaceChild(newSaveBtn, saveBtn);
        cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);

        newSaveBtn.addEventListener('click', handleSave);
        newCancelBtn.addEventListener('click', handleCancel);
    }

    async function deleteHistoryItem(id) {
        if (!confirm('确定要删除这条记录吗？')) return;
        try {
            const res = await fetch(`/api/v1/videos/${id}`, {
                method: 'DELETE',
                credentials: 'include',
                headers: csrfHeaders()
            });
            if (!res.ok) throw new Error(`删除失败 (${res.status})`);
            toast('已删除', 'success');
            loadInlineHistory();
        } catch (e) {
            toast(`删除失败: ${e.message}`, 'error');
        }
    }

    // Show more history button
    if (els.showMoreHistoryBtn) {
        els.showMoreHistoryBtn.addEventListener('click', () => {
            inlineHistoryState.displayLimit += 6;
            renderInlineHistory();
        });
    }

    // Update status indicator
    function updateStatusIndicator(status) {
        if (!els.statusDot || !els.statusText) return;
        els.statusDot.className = 'status-dot';
        switch (status) {
            case 'ready':
                els.statusDot.classList.add('ready');
                els.statusText.textContent = '就绪';
                break;
            case 'generating':
                els.statusDot.classList.add('generating');
                els.statusText.textContent = '生成中...';
                break;
            case 'error':
                els.statusDot.classList.add('error');
                els.statusText.textContent = '错误';
                break;
            default:
                els.statusText.textContent = status;
        }
    }

    // Update result area based on task status
    function updateResultArea(task) {
        if (!els.resultPlaceholder || !els.loadingState || !els.resultContainer) return;

        if (!task) {
            els.resultPlaceholder.classList.remove('hidden');
            els.loadingState.classList.add('hidden');
            els.resultContainer.classList.add('hidden');
            updateStatusIndicator('ready');
            return;
        }

        if (task.status === 'completed' && task.videoUrl) {
            els.resultPlaceholder.classList.add('hidden');
            els.loadingState.classList.add('hidden');
            els.resultContainer.classList.remove('hidden');
            if (els.resultVideo) {
                els.resultVideo.src = task.videoUrl;
            }
            updateStatusIndicator('ready');
        } else if (['pending', 'processing', 'queued'].includes(task.status)) {
            els.resultPlaceholder.classList.add('hidden');
            els.loadingState.classList.remove('hidden');
            els.resultContainer.classList.add('hidden');
            const p = typeof task.progress === 'number' ? task.progress : 0;
            const clamped = Math.min(100, Math.max(0, p));
            const visible = clamped > 0 ? clamped : (task.status === 'queued' ? 1 : 2);
            if (els.progressFill) {
                els.progressFill.style.width = `${visible}%`;
            }
            if (els.progressText) {
                els.progressText.textContent = `${visible}%`;
            }
            updateStatusIndicator('generating');
        } else if (task.status === 'failed') {
            els.resultPlaceholder.classList.remove('hidden');
            els.loadingState.classList.add('hidden');
            els.resultContainer.classList.add('hidden');
            updateStatusIndicator('error');
        }
    }

    // Initialize: load inline history
    loadInlineHistory();
    updateStatusIndicator('ready');

    // --- Result Action Buttons ---
    const downloadBtn = document.getElementById('downloadBtn');
    const shareBtn = document.getElementById('shareBtn');
    const fullscreenBtn = document.getElementById('fullscreenBtn');
    const showPromptHistory = document.getElementById('showPromptHistory');
    const closeEditPromptModal = document.getElementById('closeEditPromptModal');

    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            const videoSrc = els.resultVideo?.src;
            if (!videoSrc) {
                toast('没有可下载的视频', 'warning');
                return;
            }
            const link = document.createElement('a');
            link.href = videoSrc;
            link.download = `video_${Date.now()}.mp4`;
            link.target = '_blank';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            toast('开始下载视频', 'success');
        });
    }

    if (shareBtn) {
        shareBtn.addEventListener('click', async () => {
            const videoSrc = els.resultVideo?.src;
            if (!videoSrc) {
                toast('没有可分享的视频', 'warning');
                return;
            }
            if (navigator.share) {
                try {
                    await navigator.share({
                        title: 'Generated Video',
                        url: videoSrc
                    });
                } catch (e) {
                    if (e.name !== 'AbortError') {
                        copyToClipboard(videoSrc);
                        toast('链接已复制到剪贴板', 'success');
                    }
                }
            } else {
                copyToClipboard(videoSrc);
                toast('链接已复制到剪贴板', 'success');
            }
        });
    }

    if (fullscreenBtn) {
        fullscreenBtn.addEventListener('click', () => {
            const video = els.resultVideo;
            if (!video) return;
            if (video.requestFullscreen) {
                video.requestFullscreen();
            } else if (video.webkitRequestFullscreen) {
                video.webkitRequestFullscreen();
            } else if (video.mozRequestFullScreen) {
                video.mozRequestFullScreen();
            }
        });
    }

    if (showPromptHistory) {
        showPromptHistory.addEventListener('click', () => {
            // Toggle inline history section visibility
            if (els.inlineHistorySection) {
                els.inlineHistorySection.classList.remove('collapsed');
                els.inlineHistorySection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }

    if (closeEditPromptModal) {
        closeEditPromptModal.addEventListener('click', () => {
            const overlay = document.getElementById('editPromptModalOverlay');
            if (overlay) overlay.classList.add('hidden');
        });
    }

    els.taskList.addEventListener('click', (e) => {
        const target = e.target instanceof Element ? e.target : null;
        if (!target) return;

        const btn = target.closest('button[data-action]');
        if (!btn) return;

        e.preventDefault();
        e.stopPropagation();

        const action = btn.getAttribute('data-action') || '';
        const root = btn.closest('[data-local-id]');
        const localId = root?.getAttribute('data-local-id');
        if (!localId) return;

        if (action === 'cancel') {
            cancelTask(localId);
            return;
        }
        if (action === 'retry') {
            retryTask(localId);
            return;
        }
        if (action === 'copy-url') {
            const task = tasksState.byLocalId.get(localId);
            const url = task?.videoUrl || '';
            if (url) {
                copyToClipboard(url);
                toast('已复制视频链接', 'success');
            }
            return;
        }
        if (action === 'save') {
            const task = tasksState.byLocalId.get(localId);
            if (task) saveToRepository(task, { manual: true });
            return;
        }
    });

    syncModelUI();
    renderImagePreview();
    renderTaskList();

    const toastDedupe = { message: '', type: '', at: 0 };

    // Logger (no on-page console; use toast + browser console)
    function log(msg, type = 'info') {
        const message = String(msg || '');
        const t = String(type || 'info');

        const consoleType = t === 'error' ? 'error' : t === 'warning' ? 'warn' : 'log';
        // eslint-disable-next-line no-console
        console[consoleType](`[${t}] ${message}`);

        const toastType = t === 'error' ? 'error' : t === 'warning' ? 'warning' : t === 'success' ? 'success' : 'info';
        const now = Date.now();
        if (message && (toastDedupe.message !== message || toastDedupe.type !== toastType || now - toastDedupe.at > 1200)) {
            toastDedupe.message = message;
            toastDedupe.type = toastType;
            toastDedupe.at = now;
            toast(message, toastType);
        }
    }

    function toast(message, type = 'info', opts = {}) {
        const durationMs = Number.parseInt(String(opts.durationMs ?? 2800), 10);
        const id = globalThis.crypto && globalThis.crypto.randomUUID ? globalThis.crypto.randomUUID() : `t-${Date.now()}-${Math.random().toString(16).slice(2)}`;

        const el = document.createElement('div');
        el.className = `toast toast-${type}`;
        el.setAttribute('data-toast-id', id);
        el.textContent = String(message || '');
        els.toastContainer.appendChild(el);

        requestAnimationFrame(() => {
            el.classList.add('show');
        });

        const remove = () => {
            el.classList.remove('show');
            el.classList.add('hide');
            setTimeout(() => el.remove(), 220);
        };

        setTimeout(remove, Number.isFinite(durationMs) ? durationMs : 2800);
        el.addEventListener('click', remove);
    }

    function syncModelUI() {
        const model = els.modelSelect.value;
        const showSora = model === 'sora2';
        els.sora2Params.classList.toggle('hidden', !showSora);
        if (showSora) syncSoraConstraints();
    }

    function syncSoraConstraints() {
        if (els.modelSelect.value !== 'sora2') return;

        const variant = els.soraVariant.value;
        const duration = Number.parseInt(els.duration.value, 10);

        const isPro = variant === 'sora-2-pro';
        const allow25 = isPro;
        const allowHd = isPro && duration !== 25;

        // Duration option 25: only for Pro.
        for (const opt of Array.from(els.duration.options)) {
            if (opt.value === '25') {
                opt.disabled = !allow25;
            }
        }
        if (!allow25 && duration === 25) {
            els.duration.value = '15';
        }

        // HD: only for Pro; disabled when duration=25.
        els.soraHd.disabled = !allowHd;
        if (!allowHd) {
            els.soraHd.checked = false;
        }
    }

    function initDropzone() {
        const dragClass = 'drag-over';
        const setups = [
            { zone: els.soraDropzone, input: els.soraImages, source: 'sora' },
            { zone: els.promptDropzone, input: els.promptImages, source: 'prompt' }
        ].filter((x) => x.zone && x.input);

        setups.forEach(({ zone, input, source }) => {
            const leaveIfOutside = (e) => {
                const related = e.relatedTarget;
                if (related instanceof Node && zone.contains(related)) return;
                zone.classList.remove(dragClass);
            };

            zone.addEventListener('dragenter', (e) => {
                e.preventDefault();
                e.stopPropagation();
                zone.classList.add(dragClass);
            });
            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.stopPropagation();
                zone.classList.add(dragClass);
            });
            zone.addEventListener('dragleave', (e) => {
                e.preventDefault();
                e.stopPropagation();
                leaveIfOutside(e);
            });
            zone.addEventListener('drop', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                zone.classList.remove(dragClass);

                const files = e.dataTransfer?.files ? Array.from(e.dataTransfer.files) : [];
                await addFiles(files, { source });
            });

            zone.addEventListener('paste', async (e) => {
                const items = e.clipboardData?.items ? Array.from(e.clipboardData.items) : [];
                const files = items
                    .filter((it) => it.kind === 'file')
                    .map((it) => it.getAsFile())
                    .filter(Boolean);
                if (files.length) {
                    e.preventDefault();
                    await addFiles(files, { source });
                }
            });

            zone.addEventListener('click', (e) => {
                const target = e.target;
                if (target instanceof HTMLElement && target.closest('button')) return;
                input.click();
            });
        });
    }

    function initModal() {
        const close = () => closeImageModal();
        els.modalBackdrop.addEventListener('click', close);
        els.modalClose.addEventListener('click', close);

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !els.imageModal.classList.contains('hidden')) {
                close();
            }
        });

        els.modalCopy.addEventListener('click', async () => {
            const text = String(els.modalValue.value || '');
            try {
                await navigator.clipboard.writeText(text);
                log('已复制到剪贴板', 'success');
            } catch {
                const ta = document.createElement('textarea');
                ta.value = text;
                ta.style.position = 'fixed';
                ta.style.opacity = '0';
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                ta.remove();
                log('已复制到剪贴板', 'success');
            }
        });

        els.modalSave.addEventListener('click', () => {
            const id = imagesState.editingId;
            if (!id) return;

            const next = String(els.modalValue.value || '').trim();
            if (!next) {
                log('错误: 图片内容不能为空', 'error');
                return;
            }
            if (!isValidImageSource(next)) {
                log('错误: 仅支持 http/https URL 或 data:image/...base64', 'error');
                return;
            }

            const item = imagesState.items.find((x) => x.id === id);
            if (!item) return;

            item.value = next;
            item.kind = next.startsWith('data:image') ? 'data' : 'url';
            renderImagePreview();
            closeImageModal();
            log('已更新图片内容', 'success');
        });
    }

    function readFileAsDataUrl(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(String(reader.result || ''));
            reader.onerror = () => reject(reader.error || new Error('读取文件失败'));
            reader.readAsDataURL(file);
        });
    }

    function parseLines(value) {
        return String(value || '')
            .split(/\r?\n/)
            .map((x) => x.trim())
            .filter(Boolean);
    }

    function isValidImageSource(value) {
        const src = String(value || '').trim();
        if (!src) return false;
        if (src.startsWith('data:image')) return true;
        try {
            const u = new URL(src);
            return ['http:', 'https:'].includes(u.protocol);
        } catch {
            return false;
        }
    }

    function validateNotifyHook(value) {
        if (!value) return null;
        const trimmed = value.trim();
        if (!trimmed) return null;
        let u;
        try {
            u = new URL(trimmed);
        } catch {
            throw new Error('notify_hook 必须是合法的 URL');
        }
        if (!['http:', 'https:'].includes(u.protocol)) {
            throw new Error('notify_hook 必须是 http/https URL');
        }
        return u.toString();
    }

    function normalizeApiBaseUrl(value) {
        const raw = String(value || '').trim();
        if (!raw) throw new Error('请输入 Base URL');

        let u;
        try {
            u = new URL(raw);
        } catch {
            throw new Error('Base URL 不是合法的 URL');
        }

        if (u.protocol !== 'https:') {
            throw new Error('Base URL 必须使用 HTTPS 协议');
        }
        if (!u.hostname) {
            throw new Error('Base URL 缺少 host，例如 https://api.example.com');
        }

        const normalized = u.origin;
        if (u.pathname !== '/' || u.search || u.hash) {
            log(`提示: Base URL 包含路径/参数，已自动使用 origin: ${normalized}`, 'warning');
        }
        return normalized;
    }

    function getProviderApiSpec(modelKey) {
        const enc = (v) => encodeURIComponent(String(v || ''));
        switch (modelKey) {
            case 'sora2':
                return {
                    createPath: '/v2/videos/generations',
                    statusPath: (taskId) => `/v2/videos/generations/${enc(taskId)}`
                };
            case 'veo':
                return {
                    createPath: '/v1/video/veo/text-to-video',
                    statusPath: (taskId) => `/v1/video/veo/tasks/${enc(taskId)}`
                };
            case 'seedance':
                return {
                    createPath: '/v1/video/seedance/text-to-video',
                    statusPath: (taskId) => `/v1/video/seedance/tasks/${enc(taskId)}`
                };
            case 'newmodel':
                return {
                    createPath: '/v1/video/newmodel/text-to-video',
                    statusPath: (taskId) => `/v1/video/newmodel/tasks/${enc(taskId)}`
                };
            default:
                throw new Error(`不支持的模型: ${modelKey}`);
        }
    }

    function buildProviderAuthHeaders(apiKey, includeContentType = false) {
        const key = normalizeApiKey(apiKey);
        const headers = {
            Authorization: `Bearer ${key}`
        };
        if (includeContentType) headers['Content-Type'] = 'application/json';
        return headers;
    }

    function normalizeApiKey(value) {
        const raw = String(value || '').trim();
        return raw.replace(/^bearer\\s+/i, '').trim();
    }

    async function readJsonOrText(response) {
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) return await response.json();
        const text = await response.text();
        try {
            return JSON.parse(text);
        } catch {
            return text;
        }
    }

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

    function extractErrorMessage(data, fallback) {
        if (typeof data === 'string') return data;
        if (!data || typeof data !== 'object') return fallback;

        const detail = data.detail ?? data.error ?? data.message;
        if (typeof detail === 'string') return detail;

        if (Array.isArray(detail)) {
            return detail
                .map((item) => {
                    if (!item || typeof item !== 'object') return String(item);
                    const loc = Array.isArray(item.loc) ? item.loc.join('.') : '';
                    const msg = item.msg ? String(item.msg) : JSON.stringify(item);
                    return loc ? `${loc}: ${msg}` : msg;
                })
                .join('; ');
        }

        try {
            return JSON.stringify(detail);
        } catch {
            return fallback;
        }
    }

    function setImagesBusy(isBusy) {
        if (els.soraDropzone) els.soraDropzone.classList.toggle('is-loading', isBusy);
        if (els.soraPickFiles) els.soraPickFiles.disabled = isBusy;
        if (els.soraClearImages) els.soraClearImages.disabled = isBusy || imagesState.items.length === 0;
        if (els.soraAddImageSources) els.soraAddImageSources.disabled = isBusy;
    }

    function formatBytes(bytes) {
        const n = Number(bytes || 0);
        if (!Number.isFinite(n) || n <= 0) return '0 B';
        const units = ['B', 'KB', 'MB', 'GB'];
        let idx = 0;
        let v = n;
        while (v >= 1024 && idx < units.length - 1) {
            v /= 1024;
            idx += 1;
        }
        const digits = idx === 0 ? 0 : idx === 1 ? 1 : 2;
        return `${v.toFixed(digits)} ${units[idx]}`;
    }

    function getUploadUi(source) {
        const key = source === 'prompt' ? 'prompt' : 'sora';
        return {
            zone: key === 'prompt' ? els.promptDropzone : els.soraDropzone,
            pickBtn: key === 'prompt' ? els.promptPickFiles : els.soraPickFiles,
            clearBtn: key === 'prompt' ? null : els.soraClearImages,
            textEl: key === 'prompt' ? els.promptUploadText : els.soraUploadText,
            progressEl: key === 'prompt' ? els.promptUploadProgress : els.soraUploadProgress,
            metaEl: key === 'prompt' ? els.promptUploadMeta : els.soraUploadMeta
        };
    }

    function setUploadFeedback(source, { isProcessing, state, text, progress, meta } = {}) {
        const ui = getUploadUi(source);
        if (!ui.zone) return;

        if (typeof isProcessing === 'boolean') ui.zone.classList.toggle('is-processing', isProcessing);
        if (state === 'success' || state === 'error') {
            ui.zone.classList.toggle('is-success', state === 'success');
            ui.zone.classList.toggle('is-error', state === 'error');
        } else if (state === 'clear') {
            ui.zone.classList.remove('is-success');
            ui.zone.classList.remove('is-error');
        }

        if (ui.textEl && typeof text === 'string') ui.textEl.textContent = text;
        if (ui.metaEl && typeof meta === 'string') ui.metaEl.textContent = meta;
        if (ui.progressEl && typeof progress === 'number') {
            const p = Math.min(100, Math.max(0, progress));
            ui.progressEl.style.width = `${p}%`;
        }
    }

    function setUploadBusy(source, isBusy) {
        const ui = getUploadUi(source);
        if (!ui.zone) return;
        ui.zone.classList.toggle('is-loading', isBusy);
        if (ui.pickBtn) ui.pickBtn.disabled = isBusy;
        if (ui.clearBtn) ui.clearBtn.disabled = isBusy || imagesState.items.length === 0;
        if (source !== 'prompt') {
            els.soraAddImageSources.disabled = isBusy;
        }
    }

    async function compressImageFile(file, opts = {}) {
        const thresholdBytes = Number(opts.thresholdBytes ?? CONFIG.imageCompressThresholdBytes);
        const maxDimension = Number(opts.maxDimension ?? CONFIG.imageMaxDimension);
        if (!file || !Number.isFinite(file.size) || file.size <= thresholdBytes) {
            return { file, compressed: false, originalBytes: file?.size || 0, outputBytes: file?.size || 0 };
        }

        const decode = async () => {
            if (globalThis.createImageBitmap) {
                return await globalThis.createImageBitmap(file);
            }
            const url = URL.createObjectURL(file);
            try {
                const img = new Image();
                img.decoding = 'async';
                img.src = url;
                await new Promise((resolve, reject) => {
                    img.onload = resolve;
                    img.onerror = () => reject(new Error('图片解码失败'));
                });
                return img;
            } finally {
                URL.revokeObjectURL(url);
            }
        };

        const bitmap = await decode();
        try {
            const srcW = bitmap.width || bitmap.naturalWidth || 0;
            const srcH = bitmap.height || bitmap.naturalHeight || 0;
            if (!srcW || !srcH) {
                return { file, compressed: false, originalBytes: file.size, outputBytes: file.size };
            }

            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d', { alpha: true });
            if (!ctx) throw new Error('Canvas 初始化失败');

            let scale = 1;
            const maxSide = Math.max(srcW, srcH);
            if (Number.isFinite(maxDimension) && maxDimension > 0 && maxSide > maxDimension) {
                scale = maxDimension / maxSide;
            }
            let outW = Math.max(1, Math.round(srcW * scale));
            let outH = Math.max(1, Math.round(srcH * scale));
            canvas.width = outW;
            canvas.height = outH;

            const attemptEncode = (mime, quality) =>
                new Promise((resolve) => {
                    canvas.toBlob(
                        (blob) => resolve(blob),
                        mime,
                        quality
                    );
                });

            const draw = () => {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
            };

            draw();

            const originalBytes = file.size;
            let bestBlob = null;
            let bestBytes = Infinity;
            let quality = 0.84;
            let mime = 'image/jpeg';

            for (let i = 0; i < 4; i += 1) {
                const blob = await attemptEncode(mime, quality);
                if (!blob) break;
                const bytes = blob.size || 0;
                if (bytes > 0 && bytes < bestBytes) {
                    bestBlob = blob;
                    bestBytes = bytes;
                }
                if (bytes > 0 && bytes <= thresholdBytes) break;
                quality = Math.max(0.58, quality - 0.12);
                outW = Math.max(1, Math.round(outW * 0.92));
                outH = Math.max(1, Math.round(outH * 0.92));
                canvas.width = outW;
                canvas.height = outH;
                draw();
            }

            if (!bestBlob || bestBytes >= originalBytes) {
                return { file, compressed: false, originalBytes, outputBytes: originalBytes };
            }

            const outFile = new File([bestBlob], file.name.replace(/\.\w+$/, '') + '.jpg', { type: mime, lastModified: Date.now() });
            return { file: outFile, compressed: true, originalBytes, outputBytes: outFile.size };
        } finally {
            if (typeof bitmap?.close === 'function') bitmap.close();
        }
    }

    async function addFiles(files, opts = {}) {
        const source = opts.source === 'prompt' ? 'prompt' : 'sora';
        const imageFiles = (files || []).filter((f) => f && String(f.type || '').startsWith('image/'));
        if (imageFiles.length === 0) {
            if (files && files.length) log('未检测到可用的图片文件', 'warning');
            return;
        }

        imagesState.readingCount += imageFiles.length;
        setUploadBusy(source, true);
        setUploadFeedback(source, {
            isProcessing: true,
            state: 'clear',
            text: '处理中…',
            progress: 0,
            meta: ''
        });
        try {
            const total = imageFiles.length;
            let completed = 0;

            for (let idx = 0; idx < total; idx += 1) {
                const f = imageFiles[idx];
                setUploadFeedback(source, {
                    text: f.size > CONFIG.imageCompressThresholdBytes ? '压缩中…' : '读取中…',
                    meta: `${idx + 1}/${total} · ${f.name} · ${formatBytes(f.size)}`,
                    progress: Math.round((completed / total) * 100)
                });

                let working = f;
                if (f.size > CONFIG.imageCompressThresholdBytes) {
                    const before = f.size;
                    const res = await compressImageFile(f, {
                        thresholdBytes: CONFIG.imageCompressThresholdBytes,
                        maxDimension: CONFIG.imageMaxDimension
                    });
                    working = res.file;
                    if (res.compressed) {
                        setUploadFeedback(source, {
                            text: '压缩完成，读取中…',
                            meta: `${idx + 1}/${total} · ${f.name} · ${formatBytes(before)} → ${formatBytes(working.size)}`
                        });
                    } else {
                        setUploadFeedback(source, {
                            text: '读取中…',
                            meta: `${idx + 1}/${total} · ${f.name} · ${formatBytes(before)}`
                        });
                    }
                }

                const src = await readFileAsDataUrl(working);
                const id =
                    globalThis.crypto && globalThis.crypto.randomUUID
                        ? globalThis.crypto.randomUUID()
                        : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
                imagesState.items.push({
                    id,
                    kind: 'data',
                    value: src,
                    name: working?.name || f?.name || 'image',
                    size: working?.size || f?.size || 0
                });
                completed += 1;
                setUploadFeedback(source, {
                    progress: Math.round((completed / total) * 100)
                });
            }

            renderImagePreview();
            setUploadFeedback(source, {
                state: 'success',
                text: `已添加 ${imageFiles.length} 张图片`,
                meta: `${imageFiles.length} 张 · ${imagesState.items.length} 张总计`,
                progress: 100
            });
            log(`已添加 ${imageFiles.length} 张图片（已转 Base64）`, 'success');
            setTimeout(() => {
                setUploadFeedback(source, { isProcessing: false });
            }, 900);
            setTimeout(() => {
                setUploadFeedback(source, { state: 'clear' });
            }, 1600);
        } catch (e) {
            setUploadFeedback(source, {
                state: 'error',
                text: '添加失败',
                meta: String(e?.message || e || ''),
                progress: 0
            });
            setTimeout(() => setUploadFeedback(source, { isProcessing: false }), 1400);
            log(`添加图片失败: ${e.message || e}`, 'error');
        } finally {
            imagesState.readingCount = Math.max(0, imagesState.readingCount - imageFiles.length);
            setUploadBusy(source, imagesState.readingCount > 0);
        }
    }

    function addSourcesFromText(text) {
        const sources = parseLines(text);
        let added = 0;
        for (const src of sources) {
            if (!isValidImageSource(src)) {
                log(`跳过无效图片来源: ${src.slice(0, 80)}${src.length > 80 ? '…' : ''}`, 'warning');
                continue;
            }
            const id =
                globalThis.crypto && globalThis.crypto.randomUUID
                    ? globalThis.crypto.randomUUID()
                    : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
            imagesState.items.push({
                id,
                kind: src.startsWith('data:image') ? 'data' : 'url',
                value: src,
                name: src.startsWith('data:image') ? 'base64' : 'url',
                size: 0
            });
            added += 1;
        }
        return added;
    }

    function renderImagePreview() {
        const n = imagesState.items.length;
        if (els.soraImageCount) {
            els.soraImageCount.textContent = `${n} 张图片（${n > 0 ? '图生视频' : '文生视频'}）`;
        }
        if (els.soraClearImages) {
            els.soraClearImages.disabled = imagesState.readingCount > 0 || n === 0;
        }

        if (!els.soraImagePreview) return;
        els.soraImagePreview.innerHTML = '';
        if (n === 0) return;

        const fallbackSvg = encodeURIComponent(
            `<svg xmlns="http://www.w3.org/2000/svg" width="200" height="150" viewBox="0 0 200 150">
                <rect width="200" height="150" rx="12" fill="#F5F5F7"/>
                <path d="M62 96l16-18 16 18 22-26 22 26" fill="none" stroke="#86868b" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="78" cy="58" r="10" fill="#d1d1d6"/>
                <text x="100" y="128" font-family="system-ui, -apple-system" font-size="12" fill="#86868b" text-anchor="middle">Preview unavailable</text>
            </svg>`
        );
        const fallbackSrc = `data:image/svg+xml,${fallbackSvg}`;

        for (const item of imagesState.items) {
            const el = document.createElement('div');
            el.className = 'preview-item';
            el.dataset.id = item.id;

            const img = document.createElement('img');
            img.className = 'preview-img';
            img.loading = 'lazy';
            img.alt = item.name || 'image';
            img.src = item.value;
            img.addEventListener('click', () => openImageModal(item.id));
            img.onerror = () => {
                img.src = fallbackSrc;
                img.classList.add('is-fallback');
            };

            const actions = document.createElement('div');
            actions.className = 'preview-actions';

            const editBtn = document.createElement('button');
            editBtn.type = 'button';
            editBtn.className = 'preview-btn';
            editBtn.textContent = '编辑';
            editBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                openImageModal(item.id);
            });

            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'preview-btn danger';
            removeBtn.textContent = '移除';
            removeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                imagesState.items = imagesState.items.filter((x) => x.id !== item.id);
                renderImagePreview();
                log('已移除图片', 'info');
            });

            actions.appendChild(editBtn);
            actions.appendChild(removeBtn);

            const caption = document.createElement('div');
            caption.className = 'preview-caption';
            caption.textContent = item.kind === 'url' ? 'URL' : 'Base64';

            el.appendChild(img);
            el.appendChild(actions);
            el.appendChild(caption);
            els.soraImagePreview.appendChild(el);
        }
    }

    function openImageModal(id) {
        const item = imagesState.items.find((x) => x.id === id);
        if (!item) return;

        imagesState.editingId = id;
        els.modalImage.src = item.value;
        els.modalValue.value = item.value;
        els.imageModal.classList.remove('hidden');
        document.body.classList.add('modal-open');
        els.modalValue.focus();
    }

    function closeImageModal() {
        imagesState.editingId = null;
        els.imageModal.classList.add('hidden');
        document.body.classList.remove('modal-open');
        els.modalImage.src = '';
        els.modalValue.value = '';
    }

    function copyToClipboard(text) {
        const value = String(text || '');
        if (!value) return;
        if (navigator.clipboard?.writeText) {
            navigator.clipboard.writeText(value).catch(() => {});
            return;
        }
        const ta = document.createElement('textarea');
        ta.value = value;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        ta.remove();
    }

    function clampInt(value, min, max, fallback) {
        const n = Number.parseInt(String(value ?? ''), 10);
        if (!Number.isFinite(n)) return fallback;
        return Math.min(max, Math.max(min, n));
    }

    function parseEpochMs(value) {
        const n = Number(value);
        if (!Number.isFinite(n) || n <= 0) return null;
        if (n < 10_000_000_000) return Math.round(n * 1000);
        return Math.round(n);
    }

    function parseProgress(value) {
        if (value == null) return 0;
        if (typeof value === 'number' && Number.isFinite(value)) {
            return Math.min(100, Math.max(0, Math.round(value)));
        }
        const s = String(value).trim();
        const m = s.match(/(\d+(?:\.\d+)?)/);
        const n = m ? Number.parseFloat(m[1]) : 0;
        if (!Number.isFinite(n)) return 0;
        return Math.min(100, Math.max(0, Math.round(n)));
    }

    function normalizeProviderStatus(value) {
        const s = String(value || '').trim().toLowerCase();
        if (!s) return 'pending';
        if (['success', 'succeeded', 'ok', 'completed', 'done', 'finished', 'finish'].includes(s)) return 'completed';
        if (['fail', 'failed', 'error', 'timeout'].includes(s)) return 'failed';
        if (['cancelled', 'canceled', 'cancel'].includes(s)) return 'cancelled';
        if (['processing', 'running', 'executing', 'in_progress', 'in-progress', 'working'].includes(s)) return 'processing';
        if (['queued', 'pending', 'waiting', 'created', 'init', 'initializing'].includes(s)) return 'pending';
        return 'pending';
    }

    function getStatusLabel(status) {
        const map = {
            queued: '排队中',
            pending: '等待',
            processing: '处理中',
            completed: '成功',
            failed: '失败',
            cancelled: '已取消'
        };
        return map[status] || '等待';
    }

    function isTerminalStatus(status) {
        return ['completed', 'failed', 'cancelled'].includes(String(status || ''));
    }

    function extractVideoUrl(data) {
        const direct = [
            data?.video_url,
            data?.videoUrl,
            data?.url,
            data?.data?.video_url,
            data?.data?.videoUrl,
            data?.data?.url,
            data?.data?.output
        ];
        for (const c of direct) {
            if (typeof c === 'string' && /^https?:\/\//i.test(c.trim())) return c.trim();
        }
        const output = data?.data?.output;
        if (output && typeof output === 'object') {
            const nested = [output.url, output.video_url, output.videoUrl];
            for (const c of nested) {
                if (typeof c === 'string' && /^https?:\/\//i.test(c.trim())) return c.trim();
            }
        }
        return null;
    }

    function parseProviderTask(data) {
        return {
            taskId: data?.task_id || data?.taskId || data?.id || null,
            platform: data?.platform || null,
            action: data?.action || null,
            rawStatus: data?.status || null,
            status: normalizeProviderStatus(data?.status),
            progress: parseProgress(data?.progress),
            failReason: data?.fail_reason || data?.failReason || data?.error || data?.detail || '',
            submitTimeMs: parseEpochMs(data?.submit_time),
            startTimeMs: parseEpochMs(data?.start_time),
            finishTimeMs: parseEpochMs(data?.finish_time),
            cost: typeof data?.cost === 'number' ? data.cost : null,
            videoUrl: extractVideoUrl(data)
        };
    }

    function formatTime(ms) {
        if (!ms) return '—';
        try {
            return new Date(ms).toLocaleString();
        } catch {
            return '—';
        }
    }

    function formatDuration(ms) {
        const total = Math.max(0, Math.floor(ms / 1000));
        const s = total % 60;
        const m = Math.floor(total / 60) % 60;
        const h = Math.floor(total / 3600);
        const pad = (n) => String(n).padStart(2, '0');
        if (h > 0) return `${h}:${pad(m)}:${pad(s)}`;
        return `${pad(m)}:${pad(s)}`;
    }

    function createRequestQueue(concurrency = 4) {
        let active = 0;
        const pending = [];

        const drain = () => {
            while (active < concurrency && pending.length > 0) {
                const job = pending.shift();
                if (!job || job.aborted) continue;

                job.started = true;
                active += 1;

                Promise.resolve()
                    .then(() => job.fn())
                    .then(job.resolve, job.reject)
                    .finally(() => {
                        active -= 1;
                        job.cleanup?.();
                        drain();
                    });
            }
        };

        const enqueue = (fn, opts = {}) => {
            const signal = opts.signal;
            return new Promise((resolve, reject) => {
                const job = {
                    fn,
                    resolve,
                    reject,
                    signal,
                    started: false,
                    aborted: false,
                    cleanup: null
                };

                if (signal?.aborted) {
                    reject(new DOMException('Aborted', 'AbortError'));
                    return;
                }

                const onAbort = () => {
                    if (job.started) return;
                    job.aborted = true;
                    const idx = pending.indexOf(job);
                    if (idx >= 0) pending.splice(idx, 1);
                    reject(new DOMException('Aborted', 'AbortError'));
                    drain();
                };

                if (signal) {
                    signal.addEventListener('abort', onAbort, { once: true });
                    job.cleanup = () => signal.removeEventListener('abort', onAbort);
                }

                pending.push(job);
                drain();
            });
        };

        const stats = () => ({ active, pending: pending.length, concurrency });
        return { enqueue, stats };
    }

    function buildTaskPayload(modelKey, prompt) {
        const trimmedPrompt = String(prompt || '').trim();

        if (modelKey === 'sora2') {
            const variant = els.soraVariant.value;
            const aspectRatio = els.aspectRatio.value;
            const duration = Number.parseInt(els.duration.value, 10);
            const watermark = Boolean(els.soraWatermark.checked);
            const isPrivate = Boolean(els.soraPrivate.checked);
            const hdRequested = Boolean(els.soraHd.checked);

            const isPro = variant === 'sora-2-pro';
            if (!isPro && hdRequested) throw new Error('sora-2 不支持 HD，请切换到 sora-2-pro');
            if (!isPro && duration === 25) throw new Error('sora-2 不支持 25 秒，请切换到 sora-2-pro');
            if (duration === 25 && hdRequested) throw new Error('duration=25 时 hd 不生效，请关闭 HD 或选择 10/15 秒');

            const notifyHook = validateNotifyHook(els.notifyHook.value);
            const images = imagesState.items.map((x) => x.value).filter(Boolean);

            const payload = {
                model: variant,
                prompt: trimmedPrompt,
                aspect_ratio: aspectRatio,
                duration,
                hd: hdRequested,
                watermark,
                private: isPrivate,
                ...(notifyHook ? { notify_hook: notifyHook } : {}),
                ...(images.length ? { images } : {})
            };

            const metaSummary = `${variant} · ${aspectRatio} · ${duration}s · images=${images.length}`;
            return { payload, metaSummary };
        }

        // Other models: keep minimal payload, model is provider key.
        return { payload: { model: modelKey, prompt: trimmedPrompt }, metaSummary: modelKey };
    }



    function createTaskRow(task) {
        const wrapper = document.createElement('div');
        wrapper.className = 'task-wrapper';
        wrapper.setAttribute('data-local-id', task.localId);

        const miniPreview = document.createElement('div');
        miniPreview.className = 'task-mini-preview hidden';

        const video = document.createElement('video');
        video.className = 'task-mini-video';
        video.muted = true;
        video.loop = true;
        video.playsInline = true;
        video.controls = true;

        const overlay = document.createElement('div');
        overlay.className = 'task-mini-preview-actions';

        const copyBtn = document.createElement('button');
        copyBtn.className = 'task-mini-btn';
        copyBtn.title = '复制视频链接';
        copyBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>';
        copyBtn.onclick = (e) => {
            e.preventDefault();
            copyToClipboard(task.videoUrl);
            toast('链接已复制', 'success');
        };

        const dlBtn = document.createElement('a');
        dlBtn.className = 'task-mini-btn';
        dlBtn.title = '下载视频';
        dlBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>';
        dlBtn.target = '_blank';

        overlay.appendChild(copyBtn);
        overlay.appendChild(dlBtn);
        miniPreview.appendChild(video);
        miniPreview.appendChild(overlay);

        const root = document.createElement('details');
        root.className = 'task-item';

        const summary = document.createElement('summary');
        summary.className = 'task-summary';

        const main = document.createElement('div');
        main.className = 'task-main';

        const title = document.createElement('div');
        title.className = 'task-title';

        const nameEl = document.createElement('div');
        nameEl.className = 'task-name';
        nameEl.textContent = task.name;

        const metaEl = document.createElement('div');
        metaEl.className = 'task-meta';
        metaEl.textContent = task.metaSummary || '';

        title.appendChild(nameEl);
        title.appendChild(metaEl);

        const idEl = document.createElement('div');
        idEl.className = 'task-id';
        idEl.textContent = 'ID: -';

        main.appendChild(title);
        main.appendChild(idEl);

        const right = document.createElement('div');
        right.className = 'task-right';

        const badge = document.createElement('span');
        badge.className = 'badge badge-pending';
        badge.textContent = '等待';

        const progressWrap = document.createElement('div');
        progressWrap.className = 'task-progress';

        const bar = document.createElement('div');
        bar.className = 'task-progress-bar';
        const fill = document.createElement('div');
        fill.className = 'task-progress-fill';
        fill.style.width = '0%';
        bar.appendChild(fill);

        const progressText = document.createElement('div');
        progressText.className = 'task-progress-text';
        progressText.textContent = '0%';

        progressWrap.appendChild(bar);
        progressWrap.appendChild(progressText);

        const timeEl = document.createElement('div');
        timeEl.className = 'task-time';
        timeEl.textContent = '—';

        const actions = document.createElement('div');
        actions.className = 'task-actions';

        const saveBtn = document.createElement('button');
        saveBtn.type = 'button';
        saveBtn.className = 'btn btn-secondary btn-sm';
        saveBtn.setAttribute('data-action', 'save');
        saveBtn.textContent = '保存到存储库';

        const retryBtn = document.createElement('button');
        retryBtn.type = 'button';
        retryBtn.className = 'btn btn-secondary btn-sm';
        retryBtn.setAttribute('data-action', 'retry');
        retryBtn.textContent = '重试';

        const cancelBtn = document.createElement('button');
        cancelBtn.type = 'button';
        cancelBtn.className = 'btn btn-secondary btn-sm';
        cancelBtn.setAttribute('data-action', 'cancel');
        cancelBtn.textContent = '取消';

        actions.appendChild(saveBtn);
        actions.appendChild(retryBtn);
        actions.appendChild(cancelBtn);

        right.appendChild(badge);
        right.appendChild(progressWrap);
        right.appendChild(timeEl);
        right.appendChild(actions);

        summary.appendChild(main);
        summary.appendChild(right);

        const details = document.createElement('div');
        details.className = 'task-details';

        const info = document.createElement('div');
        info.className = 'task-info';

        const infoLeft = document.createElement('div');
        infoLeft.className = 'task-info-grid';

        const platformEl = document.createElement('div');
        platformEl.className = 'task-info-line';
        const actionEl = document.createElement('div');
        actionEl.className = 'task-info-line';
        const submitEl = document.createElement('div');
        submitEl.className = 'task-info-line';
        const startEl = document.createElement('div');
        startEl.className = 'task-info-line';
        const finishEl = document.createElement('div');
        finishEl.className = 'task-info-line';
        const costEl = document.createElement('div');
        costEl.className = 'task-info-line';
        const repoStatusEl = document.createElement('div');
        repoStatusEl.className = 'task-info-line';
        repoStatusEl.textContent = '存储库: —';
        const repoErrorEl = document.createElement('div');
        repoErrorEl.className = 'task-error hidden';
        const errorEl = document.createElement('div');
        errorEl.className = 'task-error hidden';

        infoLeft.appendChild(platformEl);
        infoLeft.appendChild(actionEl);
        infoLeft.appendChild(submitEl);
        infoLeft.appendChild(startEl);
        infoLeft.appendChild(finishEl);
        infoLeft.appendChild(costEl);
        infoLeft.appendChild(repoStatusEl);
        infoLeft.appendChild(repoErrorEl);
        infoLeft.appendChild(errorEl);

        info.appendChild(infoLeft);

        details.appendChild(info);

        root.appendChild(summary);
        root.appendChild(details);

        wrapper.appendChild(miniPreview);
        wrapper.appendChild(root);

        task.dom = {
            root: wrapper,
            badge,
            fill,
            progressText,
            idEl,
            timeEl,
            metaEl,
            nameEl,
            saveBtn,
            retryBtn,
            cancelBtn,
            platformEl,
            actionEl,
            submitEl,
            startEl,
            finishEl,
            costEl,
            repoStatusEl,
            repoErrorEl,
            errorEl,
            miniPreview,
            miniVideo: video,
            miniDlBtn: dlBtn
        };

        root.addEventListener('toggle', () => {
            updateTaskRow(task);
        });

        return wrapper;
    }

    function updateTaskRow(task) {
        if (!task.dom) return;

        const badgeClass = task.status === 'processing' ? 'processing' : task.status === 'completed' ? 'completed' : task.status === 'failed' ? 'failed' : task.status === 'cancelled' ? 'cancelled' : 'pending';
        task.dom.badge.className = `badge badge-${badgeClass}`;
        task.dom.badge.textContent = getStatusLabel(task.status);

        task.dom.progressText.textContent = `${task.progress}%`;
        task.dom.fill.style.width = `${task.progress}%`;

        task.dom.idEl.textContent = `ID: ${task.taskId || '-'}`;

        updateTaskDuration(task);

        task.dom.platformEl.textContent = `平台: ${task.platform || '—'}`;
        task.dom.actionEl.textContent = `动作: ${task.action || '—'}`;
        task.dom.submitEl.textContent = `提交: ${formatTime(task.submitTimeMs)}`;
        task.dom.startEl.textContent = `开始: ${formatTime(task.startTimeMs)}`;
        task.dom.finishEl.textContent = `完成: ${formatTime(task.finishTimeMs)}`;
        task.dom.costEl.textContent = task.cost != null ? `花费: ${task.cost}` : '花费: —';

        const repoSave = task.repoSave || { status: 'idle', errorMessage: '' };
        let repoLabel = '—';
        if (task.status === 'completed') {
            if (!task.videoUrl) repoLabel = '缺少视频链接';
            else if (repoSave.status === 'saved') repoLabel = '已保存';
            else if (repoSave.status === 'saving') repoLabel = '保存中...';
            else if (repoSave.status === 'failed') repoLabel = '保存失败';
            else repoLabel = '待保存';
        }
        task.dom.repoStatusEl.textContent = `存储库: ${repoLabel}`;

        if (repoSave.status === 'failed' && String(repoSave.errorMessage || '').trim()) {
            task.dom.repoErrorEl.classList.remove('hidden');
            task.dom.repoErrorEl.textContent = `保存失败: ${String(repoSave.errorMessage).trim()}`;
        } else {
            task.dom.repoErrorEl.classList.add('hidden');
            task.dom.repoErrorEl.textContent = '';
        }

        const err = String(task.failReason || '').trim();
        if (err) {
            task.dom.errorEl.classList.remove('hidden');
            task.dom.errorEl.textContent = `错误: ${err}`;
        } else {
            task.dom.errorEl.classList.add('hidden');
            task.dom.errorEl.textContent = '';
        }

        const canCancel = !isTerminalStatus(task.status) && !task.controller.signal.aborted;
        task.dom.cancelBtn.disabled = !canCancel;

        const canRetry = isTerminalStatus(task.status) && task.status !== 'completed';
        task.dom.retryBtn.style.display = canRetry ? '' : 'none';

        const canShowSave = task.status === 'completed' && !!task.videoUrl;
        task.dom.saveBtn.style.display = canShowSave ? '' : 'none';
        if (canShowSave) {
            if (repoSave.status === 'saved') {
                task.dom.saveBtn.textContent = '已保存';
                task.dom.saveBtn.disabled = true;
            } else if (repoSave.status === 'saving') {
                task.dom.saveBtn.textContent = '保存中...';
                task.dom.saveBtn.disabled = true;
            } else if (repoSave.status === 'failed') {
                task.dom.saveBtn.textContent = '重试保存';
                task.dom.saveBtn.disabled = false;
            } else {
                task.dom.saveBtn.textContent = '保存到存储库';
                task.dom.saveBtn.disabled = false;
            }
        } else {
            task.dom.saveBtn.disabled = true;
        }

        if (task.videoUrl) {
            task.dom.miniPreview.classList.remove('hidden');
            const currentSrc = task.dom.miniVideo.getAttribute('src');
            if (currentSrc !== task.videoUrl) {
                task.dom.miniVideo.src = task.videoUrl;
                task.dom.miniDlBtn.href = task.videoUrl;
                try {
                     const u = new URL(task.videoUrl);
                     const name = u.pathname.split('/').pop();
                     task.dom.miniDlBtn.download = name || `video_${task.taskId}.mp4`;
                } catch {
                     task.dom.miniDlBtn.download = `video_${task.taskId}.mp4`;
                }
            }
        } else {
            task.dom.miniPreview.classList.add('hidden');
            if (task.dom.miniVideo.getAttribute('src')) {
                task.dom.miniVideo.removeAttribute('src');
                task.dom.miniVideo.load();
            }
        }
    }

    function updateTaskDuration(task) {
        if (!task?.dom?.timeEl) return;
        const now = Date.now();
        const start = task.startTimeMs || task.submitTimeMs || task.createdAt || now;
        const end = task.finishTimeMs || (isTerminalStatus(task.status) ? task.updatedAt : null);
        const duration = (end || now) - start;
        task.dom.timeEl.textContent = `耗时 ${formatDuration(duration)}`;
    }

    function updateTaskSummary() {
        const total = tasksState.order.length;
        let processing = 0;
        let completed = 0;
        let failed = 0;
        let cancelled = 0;
        for (const id of tasksState.order) {
            const t = tasksState.byLocalId.get(id);
            if (!t) continue;
            if (t.status === 'processing') processing += 1;
            else if (t.status === 'completed') completed += 1;
            else if (t.status === 'failed') failed += 1;
            else if (t.status === 'cancelled') cancelled += 1;
        }
        els.taskSummary.textContent = `${total} 个任务 · 处理中 ${processing} · 成功 ${completed} · 失败 ${failed} · 取消 ${cancelled}`;
    }

    function renderTaskList() {
        updateTaskSummary();

        const total = tasksState.order.length;
        if (els.statusContainer) {
            els.statusContainer.classList.toggle('hidden', total > 0);
        }

        // Render only first N tasks (lazy load)
        const visible = tasksState.order.slice(0, tasksState.renderLimit);
        els.taskList.innerHTML = '';
        for (const id of visible) {
            const task = tasksState.byLocalId.get(id);
            if (!task) continue;
            if (!task.dom) createTaskRow(task);
            updateTaskRow(task);
            els.taskList.appendChild(task.dom.root);
        }

        if (els.taskListFooter) {
            els.taskListFooter.classList.toggle('hidden', total <= tasksState.renderLimit);
        }
    }

    function addTaskLog(task, message, type = 'info') {
        const t = typeof task === 'string' ? tasksState.byLocalId.get(task) : task;
        if (!t) return;
        const entry = {
            time: new Date().toLocaleTimeString(),
            type,
            message: String(message || '')
        };
        if (!Array.isArray(t.logs)) t.logs = [];
        t.logs.push(entry);
        if (t.logs.length > CONFIG.maxLogsPerTask * 3) {
            t.logs.splice(0, t.logs.length - CONFIG.maxLogsPerTask * 2);
        }
        updateTaskRow(t);
    }

    function setTaskStatus(task, status, extra = {}) {
        const next = String(status || '').trim();
        if (!next) return;
        const prev = task.status;
        task.status = next;
        task.updatedAt = Date.now();
        Object.assign(task, extra);
        if (prev !== next) {
            addTaskLog(task, `状态更新: ${getStatusLabel(prev)} -> ${getStatusLabel(next)}`, 'info');
        }
        updateTaskRow(task);
        updateTaskSummary();

        // Sync inline history when a task completes
        if (next === 'completed' && prev !== 'completed') {
            setTimeout(() => {
                if (typeof loadInlineHistory === 'function') loadInlineHistory();
            }, 1500);
        }

        // Update result area for the most recent task
        if (tasksState.order.length > 0) {
            const latestId = tasksState.order[0];
            const latestTask = tasksState.byLocalId.get(latestId);
            if (latestTask && latestTask.localId === task.localId) {
                if (typeof updateResultArea === 'function') updateResultArea(task);
            }
        }
    }

    function pruneTasks() {
        if (tasksState.order.length <= CONFIG.maxTasks) return;

        // Prefer removing oldest terminal tasks.
        const toRemove = tasksState.order.slice().reverse().filter((id) => {
            const t = tasksState.byLocalId.get(id);
            return t && isTerminalStatus(t.status);
        });
        while (tasksState.order.length > CONFIG.maxTasks && toRemove.length > 0) {
            removeTask(toRemove.shift());
        }
        while (tasksState.order.length > CONFIG.maxTasks) {
            removeTask(tasksState.order[tasksState.order.length - 1]);
        }
    }

    function removeTask(localId) {
        const id = String(localId || '');
        const task = tasksState.byLocalId.get(id);
        if (!task) return;

        task.cleanupTimer && clearTimeout(task.cleanupTimer);
        task.pollTimer && clearTimeout(task.pollTimer);
        if (!task.controller.signal.aborted && !isTerminalStatus(task.status)) {
            try {
                task.controller.abort();
            } catch {}
        }

        tasksState.byLocalId.delete(id);
        tasksState.order = tasksState.order.filter((x) => x !== id);
        if (task.dom?.root && task.dom.root.parentElement) {
            task.dom.root.remove();
        }
    }

    function clearCompletedTasks() {
        const ids = tasksState.order.slice();
        for (const id of ids) {
            const task = tasksState.byLocalId.get(id);
            if (task && isTerminalStatus(task.status)) removeTask(id);
        }
    }

    function scheduleCleanup(task) {
        task.cleanupTimer && clearTimeout(task.cleanupTimer);
        task.cleanupTimer = setTimeout(() => {
            removeTask(task.localId);
            renderTaskList();
        }, CONFIG.cleanupAfterMs);
    }

    function cancelTask(localId) {
        const task = tasksState.byLocalId.get(String(localId || ''));
        if (!task) return;
        if (isTerminalStatus(task.status)) return;

        addTaskLog(task, '用户取消任务（停止轮询）', 'warning');
        try {
            task.controller.abort();
        } catch {}
        task.pollTimer && clearTimeout(task.pollTimer);
        task.finishTimeMs = task.finishTimeMs || Date.now();
        setTaskStatus(task, 'cancelled');
        scheduleCleanup(task);
        toast(`已取消：${task.name}`, 'info');
    }

    function retryTask(localId) {
        const task = tasksState.byLocalId.get(String(localId || ''));
        if (!task) return;
        if (!task.request) return;

        const nextName = `${task.request.name || task.name}（重试）`;
        submitTaskFromRequest({ ...task.request, name: nextName });
    }

    async function pollOnce(task) {
        if (!task.taskId) return;
        const url = `${task.baseUrl}${task.apiSpec.statusPath(task.taskId)}`;
        const response = await fetch(url, {
            headers: buildProviderAuthHeaders(task.apiKey, false),
            signal: task.controller.signal
        });
        const data = await readJsonOrText(response);
        if (!response.ok) {
            const msg = data?.detail || data?.error || (typeof data === 'string' ? data : null);
            throw new Error(msg || `轮询失败（HTTP ${response.status}）`);
        }
        return data;
    }

    function buildRepositoryPayload(task) {
        const videoUrl = String(task?.videoUrl || '').trim();
        if (!videoUrl) throw new Error('缺少视频链接');

        const rawPrompt = task?.request?.payload?.prompt ?? task?.payload?.prompt ?? task?.request?.prompt ?? '';
        const rawModel = task?.request?.payload?.model ?? task?.payload?.model ?? task?.request?.model ?? task?.platform ?? task?.modelKey ?? 'unknown';

        const prompt = String(rawPrompt || '').trim() || 'No prompt';
        const model = String(rawModel || '').trim() || 'unknown';

        const metadata = {
            provider_task_id: task?.taskId || null,
            platform: task?.platform || null,
            action: task?.action || null,
            cost: task?.cost ?? null,
        };

        return {
            title: task?.name || (task?.taskId ? `Task ${task.taskId}` : '未命名任务'),
            model,
            prompt,
            video_url: videoUrl,
            status: 'completed',
            metadata
        };
    }

    async function saveToRepository(task, { manual = false } = {}) {
        const t = task;
        if (!t) return;

        const current = t.repoSave || { status: 'idle', errorMessage: '', savedVideoId: null, payload: null };
        if (current.status === 'saving') {
            if (manual) toast('正在保存...', 'info', { durationMs: 1800 });
            return;
        }
        if (current.status === 'saved') {
            if (manual) toast('已保存到存储库', 'success', { durationMs: 1800 });
            return;
        }
        if (t.status !== 'completed') {
            if (manual) toast('仅支持保存已完成的任务', 'warning');
            return;
        }

        let payload;
        try {
            payload = buildRepositoryPayload(t);
        } catch (e) {
            const msg = String(e?.message || e || '保存数据无效');
            t.repoSave = { status: 'failed', errorMessage: msg, savedVideoId: null, payload: null };
            updateTaskRow(t);
            log(`保存失败: ${msg}`, 'error');
            return;
        }

        t.repoSave = { status: 'saving', errorMessage: '', savedVideoId: current.savedVideoId || null, payload };
        updateTaskRow(t);
        addTaskLog(t, '开始保存到存储库', 'info');

        const doSave = async () => {
            let res;
            try {
                res = await fetch('/api/v1/videos', {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        ...csrfHeaders()
                    },
                    body: JSON.stringify(payload)
                });
            } catch (e) {
                const msg = String(e?.message || e || '网络错误');
                t.repoSave = { status: 'failed', errorMessage: msg, savedVideoId: null, payload };
                updateTaskRow(t);
                addTaskLog(t, `保存失败: ${msg}`, 'error');
                toast(`保存失败：${msg}`, 'error');
                return;
            }

            if (res.status === 401) {
                const msg = '登录已过期，请重新登录后再保存';
                t.repoSave = { status: 'failed', errorMessage: msg, savedVideoId: null, payload };
                updateTaskRow(t);
                addTaskLog(t, `保存失败: ${msg}`, 'warning');
                toast(msg, 'warning');
                window.location.href = '/login?next=/dashboard';
                return;
            }

            const data = await readJsonOrText(res);
            if (!res.ok) {
                let msg = extractErrorMessage(data, `保存失败（HTTP ${res.status}）`);
                if (res.status === 403 && msg.toLowerCase().includes('csrf')) {
                    msg = `${msg}（请刷新页面后重试）`;
                }
                t.repoSave = { status: 'failed', errorMessage: msg, savedVideoId: null, payload };
                updateTaskRow(t);
                addTaskLog(t, `保存失败: ${msg}`, 'error');
                toast(`保存失败：${msg}`, 'error', { durationMs: 5200 });
                return;
            }

            const savedVideoId = data?.id || null;
            t.repoSave = { status: 'saved', errorMessage: '', savedVideoId, payload };
            updateTaskRow(t);
            addTaskLog(t, '已保存到存储库', 'success');
            toast(`已保存到存储库：${t.name || t.taskId || ''}`.trim(), 'success', { durationMs: 2200 });
        };

        tasksState.saveQueue.enqueue(doSave).catch((e) => {
            const msg = String(e?.message || e || '保存失败');
            t.repoSave = { status: 'failed', errorMessage: msg, savedVideoId: null, payload };
            updateTaskRow(t);
            addTaskLog(t, `保存失败: ${msg}`, 'error');
            log(`保存失败: ${msg}`, 'error');
        });
    }

    function startPollingTask(task) {
        if (!task.taskId || task.controller.signal.aborted) return;
        if (task.pollTimer) clearTimeout(task.pollTimer);

        const tick = async () => {
            if (task.controller.signal.aborted) return;
            if (isTerminalStatus(task.status)) return;

            try {
                const data = await tasksState.pollQueue.enqueue(() => pollOnce(task), { signal: task.controller.signal });
                task.pollErrorCount = 0;

                const parsed = parseProviderTask(data);
                let normalizedStatus = parsed.status;
                if (parsed.videoUrl && parsed.progress >= 100 && !['failed', 'cancelled'].includes(normalizedStatus)) {
                    normalizedStatus = 'completed';
                }
                const prevStatus = task.status;

                if (parsed.taskId) task.taskId = String(parsed.taskId);
                task.platform = parsed.platform || task.platform;
                task.action = parsed.action || task.action;
                task.progress = parsed.progress;
                task.failReason = parsed.failReason || task.failReason;
                task.submitTimeMs = parsed.submitTimeMs || task.submitTimeMs;
                task.startTimeMs = parsed.startTimeMs || task.startTimeMs;
                task.finishTimeMs = parsed.finishTimeMs || task.finishTimeMs;
                task.cost = parsed.cost != null ? parsed.cost : task.cost;
                task.videoUrl = parsed.videoUrl || task.videoUrl;
                task.updatedAt = Date.now();

                setTaskStatus(task, normalizedStatus);

                if (prevStatus !== task.status && isTerminalStatus(task.status)) {
                    const msg = task.status === 'completed' ? '任务成功' : task.status === 'failed' ? '任务失败' : '任务已取消';
                    addTaskLog(task, msg, task.status === 'completed' ? 'success' : task.status === 'failed' ? 'error' : 'warning');
                    
                    // Auto-save to repository if completed
                    if (task.status === 'completed' && task.videoUrl) {
                        saveToRepository(task);
                    }
                }

                if (task.status === 'completed' && task.videoUrl) {
                    // Auto preview removed
                }

                if (isTerminalStatus(task.status)) {
                    if (task.status === 'completed' && task.videoUrl) {
                        toast(`完成：${task.name}`, 'success');
                    } else if (task.status === 'failed') {
                        toast(`失败：${task.name}`, 'error');
                    }
                    scheduleCleanup(task);
                    return;
                }
            } catch (e) {
                if (e?.name === 'AbortError') return;
                task.pollErrorCount += 1;
                addTaskLog(task, `轮询错误(${task.pollErrorCount}/${CONFIG.maxPollErrors}): ${e.message || e}`, 'warning');
                if (task.pollErrorCount >= CONFIG.maxPollErrors) {
                    task.failReason = task.failReason || String(e.message || e);
                    setTaskStatus(task, 'failed');
                    scheduleCleanup(task);
                    toast(`轮询失败：${task.name}`, 'error');
                    return;
                }
            } finally {
                const delay = CONFIG.pollIntervalMs + Math.floor(Math.random() * CONFIG.pollJitterMs);
                task.pollTimer = setTimeout(tick, delay);
            }
        };

        // first poll after a short delay
        task.pollTimer = setTimeout(tick, 1000);
    }

    function submitTaskFromRequest(request) {
        const localId =
            globalThis.crypto && globalThis.crypto.randomUUID
                ? globalThis.crypto.randomUUID()
                : `${Date.now()}-${Math.random().toString(16).slice(2)}`;

        const task = {
            localId,
            name: request.name,
            modelKey: request.modelKey,
            metaSummary: request.metaSummary,
            baseUrl: request.baseUrl,
            apiKey: request.apiKey,
            apiSpec: request.apiSpec,
            payload: request.payload,
            request,
            status: 'queued',
            progress: 0,
            taskId: null,
            platform: null,
            action: null,
            failReason: '',
            videoUrl: null,
            createdAt: Date.now(),
            updatedAt: Date.now(),
            submitTimeMs: null,
            startTimeMs: null,
            finishTimeMs: null,
            cost: null,
            logs: [],
            pollTimer: null,
            pollErrorCount: 0,
            cleanupTimer: null,
            controller: new AbortController(),
            dom: null
        };

        tasksState.byLocalId.set(localId, task);
        tasksState.order.unshift(localId);
        pruneTasks();
        createTaskRow(task);
        addTaskLog(task, '已加入队列', 'info');
        renderTaskList();

        const createPromise = tasksState.createQueue.enqueue(async () => {
                setTaskStatus(task, 'pending');

                const response = await fetch(`${task.baseUrl}${task.apiSpec.createPath}`, {
                    method: 'POST',
                    headers: buildProviderAuthHeaders(task.apiKey, true),
                    body: JSON.stringify(task.payload),
                    signal: task.controller.signal
                });
                const data = await readJsonOrText(response);
                if (!response.ok) {
                    const msg = data?.detail || data?.error || (typeof data === 'string' ? data : null);
                    throw new Error(msg || `请求失败（HTTP ${response.status}）`);
                }
                return data;
            }, { signal: task.controller.signal });

        task.createPromise = createPromise;

        createPromise
            .then((data) => {
                const parsed = parseProviderTask(data);
                let normalizedStatus = parsed.status;
                if (parsed.videoUrl && parsed.progress >= 100 && !['failed', 'cancelled'].includes(normalizedStatus)) {
                    normalizedStatus = 'completed';
                }
                task.taskId = parsed.taskId ? String(parsed.taskId) : task.taskId;
                task.platform = parsed.platform || task.platform;
                task.action = parsed.action || task.action;
                task.progress = parsed.progress;
                task.failReason = parsed.failReason || '';
                task.submitTimeMs = parsed.submitTimeMs || task.submitTimeMs;
                task.startTimeMs = parsed.startTimeMs || task.startTimeMs;
                task.finishTimeMs = parsed.finishTimeMs || task.finishTimeMs;
                task.cost = parsed.cost != null ? parsed.cost : task.cost;
                task.videoUrl = parsed.videoUrl || task.videoUrl;

                if (!task.taskId) {
                    task.failReason = task.failReason || '响应缺少 task_id';
                    setTaskStatus(task, 'failed');
                    scheduleCleanup(task);
                    toast(`创建失败：${task.name}`, 'error');
                    return;
                }

                setTaskStatus(task, normalizedStatus);
                addTaskLog(task, `任务创建成功: ${task.taskId}`, 'success');
                toast(`已提交：${task.name}`, 'success', { durationMs: 1800 });

                if (task.status === 'completed' && task.videoUrl) {
                    saveToRepository(task);
                }

                if (isTerminalStatus(task.status)) {
                    scheduleCleanup(task);
                    return;
                }
                startPollingTask(task);
            })
            .catch((e) => {
                if (e?.name === 'AbortError') {
                    setTaskStatus(task, 'cancelled');
                    scheduleCleanup(task);
                    return;
                }
                task.failReason = String(e?.message || e);
                setTaskStatus(task, 'failed');
                addTaskLog(task, `创建失败: ${task.failReason}`, 'error');
                scheduleCleanup(task);
                toast(`创建失败：${task.name}`, 'error');
            });

        return task;
    }

    function handleSubmit() {
        const now = Date.now();
        if (now - tasksState.lastSubmitAt < CONFIG.submitDebounceMs) return;
        tasksState.lastSubmitAt = now;

        const apiKey = normalizeApiKey(els.apiKey.value);
        if (!apiKey) {
            toast('请先输入 API Key', 'error');
            els.apiKey.focus();
            return;
        }

        let baseUrl;
        try {
            baseUrl = normalizeApiBaseUrl(els.baseUrl.value);
        } catch (e) {
            toast(e.message || 'Base URL 无效', 'error');
            els.baseUrl.focus();
            return;
        }

        const prompt = els.promptInput.value.trim();
        if (!prompt) {
            toast('请输入提示词', 'error');
            els.promptInput.focus();
            return;
        }

        const modelKey = els.modelSelect.value;
        let apiSpec;
        try {
            apiSpec = getProviderApiSpec(modelKey);
        } catch (e) {
            toast(e.message || '模型不支持', 'error');
            return;
        }

        if (modelKey === 'sora2' && imagesState.readingCount > 0) {
            toast('图片读取中，请稍候…', 'warning');
            return;
        }

        // Flush pending image sources into preview list (Sora only)
        if (modelKey === 'sora2') {
            const pendingSources = String(els.soraImageSourceInput.value || '').trim();
            if (pendingSources) {
                const added = addSourcesFromText(pendingSources);
                if (added > 0) {
                    els.soraImageSourceInput.value = '';
                    renderImagePreview();
                }
            }
        }

        let payloadInfo;
        try {
            payloadInfo = buildTaskPayload(modelKey, prompt);
        } catch (e) {
            toast(e.message || '参数有误', 'error');
            return;
        }

        const batchCount = clampInt(els.batchCount.value, 1, CONFIG.maxBatchCount, 1);
        if (batchCount >= CONFIG.confirmBatchThreshold) {
            const ok = confirm(`将提交 ${batchCount} 个任务，确认继续？`);
            if (!ok) return;
        }

        const baseName = String(els.taskNameInput.value || '').trim();
        const nameSeed = baseName || prompt.slice(0, 18) || '任务';

        const requests = Array.from({ length: batchCount }, (_, idx) => {
            const suffix = batchCount > 1 ? ` #${idx + 1}` : '';
            const name = `${nameSeed}${suffix}`;
            return {
                name,
                modelKey,
                metaSummary: payloadInfo.metaSummary,
                baseUrl,
                apiKey,
                apiSpec,
                payload: payloadInfo.payload
            };
        });

        toast(`已加入队列：${batchCount} 个任务`, 'success');

        const tasks = requests.map((req) => {
            const task = submitTaskFromRequest({ ...req, request: null });
            task.request = {
                name: req.name,
                modelKey: req.modelKey,
                metaSummary: req.metaSummary,
                baseUrl: req.baseUrl,
                apiKey: req.apiKey,
                apiSpec: req.apiSpec,
                payload: req.payload
            };
            return task;
        });

        Promise.allSettled(tasks.map((t) => t.createPromise))
            .then((results) => {
                const ok = results.filter((r) => r.status === 'fulfilled').length;
                const bad = results.length - ok;
                if (results.length > 1) {
                    toast(`创建结果：成功 ${ok}，失败 ${bad}`, bad ? 'warning' : 'success', { durationMs: 3600 });
                }
            })
            .catch(() => {});
    }

    // Keep durations fresh for visible tasks
    setInterval(() => {
        const visible = tasksState.order.slice(0, tasksState.renderLimit);
        for (const id of visible) {
            const t = tasksState.byLocalId.get(id);
            if (t) updateTaskDuration(t);
        }
    }, 1000);
});
