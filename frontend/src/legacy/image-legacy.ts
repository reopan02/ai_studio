// @ts-nocheck
const STORAGE_KEYS = {
    apiKey: 'global_api_key',
    baseUrl: 'global_base_url'
};

const IMAGE_PLACEHOLDER_SRC =
    'data:image/svg+xml;charset=utf-8,' +
    encodeURIComponent(
        '<svg xmlns="http://www.w3.org/2000/svg" width="320" height="200" viewBox="0 0 320 200">' +
            '<rect width="320" height="200" fill="#111827"/>' +
            '<rect x="52" y="40" width="216" height="120" rx="12" fill="none" stroke="#9CA3AF" stroke-width="6"/>' +
            '<path d="M76 142l54-64 44 52 30-36 70 84H76z" fill="#374151"/>' +
            '<circle cx="116" cy="82" r="10" fill="#6B7280"/>' +
            '<line x1="92" y1="62" x2="228" y2="138" stroke="#9CA3AF" stroke-width="6"/>' +
            '<line x1="228" y1="62" x2="92" y2="138" stroke="#9CA3AF" stroke-width="6"/>' +
        '</svg>'
    );

function normalizeApiKey(value) {
    const raw = String(value || '').trim();
    return raw.replace(/^bearer\s+/i, '').trim();
}

function applyImageFallbacks(root, selector) {
    if (!root) return;
    root.querySelectorAll(selector).forEach((img) => {
        img.addEventListener(
            'error',
            () => {
                if (img.dataset.fallbackApplied) return;
                img.dataset.fallbackApplied = 'true';
                img.alt = 'Image unavailable';
                img.src = IMAGE_PLACEHOLDER_SRC;
            },
            { once: true }
        );
    });
}

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

function normalizeApiBaseUrl(value) {
    const raw = String(value || '').trim();
    if (!raw) return null;

    let u;
    try {
        u = new URL(raw);
    } catch {
        throw new Error('Base URL is not a valid URL');
    }

    if (u.protocol !== 'https:') {
        throw new Error('Base URL must use HTTPS');
    }
    if (!u.hostname) {
        throw new Error('Base URL is missing host (e.g. https://api.example.com)');
    }

    return u.origin;
}

function clampInt(value, min, max, fallback) {
    const n = Number.parseInt(String(value ?? ''), 10);
    if (!Number.isFinite(n)) return fallback;
    return Math.min(max, Math.max(min, n));
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

function extractErrorMessage(data, fallback) {
    if (typeof data === 'string') return data;
    if (!data || typeof data !== 'object') return fallback;

    const detail = data.detail ?? data.error ?? data.message;
    if (typeof detail === 'string') return detail;
    try {
        return JSON.stringify(detail ?? data);
    } catch {
        return fallback;
    }
}

function extractImageUrls(result) {
    const urls = [];
    if (!result || typeof result !== 'object') return urls;

    const data = result.data;
    if (Array.isArray(data)) {
        for (const item of data) {
            if (!item || typeof item !== 'object') continue;
            if (typeof item.url === 'string' && item.url) urls.push(item.url);
            else if (typeof item.b64_json === 'string' && item.b64_json) urls.push(`data:image/png;base64,${item.b64_json}`);
            else if (typeof item.image_url === 'string' && item.image_url) urls.push(item.image_url);
            else if (typeof item.imageUrl === 'string' && item.imageUrl) urls.push(item.imageUrl);
        }
    }

    if (urls.length === 0) {
        if (typeof result.url === 'string' && result.url) urls.push(result.url);
        else if (typeof result.b64_json === 'string' && result.b64_json) urls.push(`data:image/png;base64,${result.b64_json}`);
        else if (typeof result.image_url === 'string' && result.image_url) urls.push(result.image_url);
        else if (typeof result.imageUrl === 'string' && result.imageUrl) urls.push(result.imageUrl);
    }

    return urls;
}

// ==========================================
// Application State
// ==========================================
	        const state = {
	            config: {
	                apiKey: localStorage.getItem(STORAGE_KEYS.apiKey) || localStorage.getItem('video_api_key') || localStorage.getItem('apiKey') || '',
	                baseUrl: localStorage.getItem(STORAGE_KEYS.baseUrl) || localStorage.getItem('video_base_url') || localStorage.getItem('baseUrl') || ''
	            },
	            images: [],
	            currentImageIndex: -1,
	            prompt: '',
	            promptHistory: (() => {
	                try {
	                    return JSON.parse(localStorage.getItem('promptHistory') || '[]');
	                } catch {
	                    localStorage.removeItem('promptHistory');
	                    return [];
	                }
	            })(),
	            generationHistory: (() => {
	                try {
	                    return JSON.parse(localStorage.getItem('generationHistory') || '[]');
	                } catch {
	                    localStorage.removeItem('generationHistory');
	                    return [];
	                }
	            })(),
            inlineHistoryCollapsed: localStorage.getItem('inlineHistoryCollapsed') === 'true',
            inlineHistoryLimit: 6,
            inlineHistoryShowAll: false,
            editingHistoryIndex: -1,

	            isGenerating: false,
	            currentZoom: 100,
	            canvasZoom: 100,
	            canvasHistory: [],
    canvasHistoryIndex: -1,
    // High-resolution canvas state
    originalImage: null,
    originalWidth: 0,
    originalHeight: 0,
    displayScale: 1
};

// ==========================================
// DOM Elements
// ==========================================
const elements = {
    // Model
    modelSelect: document.getElementById('modelSelect'),
    modelSearch: document.getElementById('modelSearch'),
    aspectRatio: document.getElementById('aspectRatio'),
    imageSize: document.getElementById('imageSize'),
    batchCount: document.getElementById('batchCount'),

    // Upload
    uploadArea: document.getElementById('uploadArea'),
    fileInput: document.getElementById('fileInput'),
    imagePreviewGrid: document.getElementById('imagePreviewGrid'),
    editMaskBtn: document.getElementById('editMaskBtn'),

    // Mask Modal
    maskModalOverlay: document.getElementById('maskModalOverlay'),
    closeMaskModal: document.getElementById('closeMaskModal'),
    cancelMaskBtn: document.getElementById('cancelMaskBtn'),

    // Canvas
    canvasContainer: document.getElementById('canvasContainer'),
    canvasWrapper: document.getElementById('canvasWrapper'),
    maskCanvas: document.getElementById('maskCanvas'),
    brushSize: document.getElementById('brushSize'),
    brushSizeLabel: document.getElementById('brushSizeLabel'),
    brushColor: document.getElementById('brushColor'),
    undoBtn: document.getElementById('undoBtn'),
    redoBtn: document.getElementById('redoBtn'),
    clearCanvasBtn: document.getElementById('clearCanvasBtn'),
    saveMaskBtn: document.getElementById('saveMaskBtn'),
    resetMaskBtn: document.getElementById('resetMaskBtn'),
    canvasZoomInBtn: document.getElementById('canvasZoomInBtn'),
    canvasZoomOutBtn: document.getElementById('canvasZoomOutBtn'),
    canvasZoomResetBtn: document.getElementById('canvasZoomResetBtn'),
    canvasZoomLevel: document.getElementById('canvasZoomLevel'),

    // Prompt
    promptInput: document.getElementById('promptInput'),
    charCount: document.getElementById('charCount'),
    showPromptHistory: document.getElementById('showPromptHistory'),
    promptHistoryDropdown: document.getElementById('promptHistoryDropdown'),



    // Image Preview Modal
    imagePreviewOverlay: document.getElementById('imagePreviewOverlay'),
    imagePreviewImg: document.getElementById('imagePreviewImg'),
    imagePreviewInfo: document.getElementById('imagePreviewInfo'),
    closeImagePreview: document.getElementById('closeImagePreview'),

    // Results
    resultArea: document.getElementById('resultArea'),
    resultPlaceholder: document.getElementById('resultPlaceholder'),
    loadingState: document.getElementById('loadingState'),
    resultContainer: document.getElementById('resultContainer'),
    resultImage: document.getElementById('resultImage'),

    // Controls
    generateBtn: document.getElementById('generateBtn'),
    downloadBtn: document.getElementById('downloadBtn'),
    shareBtn: document.getElementById('shareBtn'),
    fullscreenBtn: document.getElementById('fullscreenBtn'),
    zoomInBtn: document.getElementById('zoomInBtn'),
    zoomOutBtn: document.getElementById('zoomOutBtn'),
    zoomLevel: document.getElementById('zoomLevel'),

    // Status
    statusDot: document.getElementById('statusDot'),
    statusText: document.getElementById('statusText'),

    // History
    historyBtn: document.getElementById('historyBtn'),
    historyPanel: document.getElementById('historyPanel'),
    closeHistoryBtn: document.getElementById('closeHistoryBtn'),
    historyList: document.getElementById('historyList'),

    // Inline History
    inlineHistorySection: document.getElementById('inlineHistorySection'),
    inlineHistoryToggle: document.getElementById('inlineHistoryToggle'),
    inlineHistoryContent: document.getElementById('inlineHistoryContent'),
    inlineHistoryGrid: document.getElementById('inlineHistoryGrid'),
    inlineHistoryCount: document.getElementById('inlineHistoryCount'),
    inlineHistoryShowMore: document.getElementById('inlineHistoryShowMore'),
    showMoreHistoryBtn: document.getElementById('showMoreHistoryBtn'),

    // Edit Prompt Modal
    editPromptModalOverlay: document.getElementById('editPromptModalOverlay'),
    editPromptTextarea: document.getElementById('editPromptTextarea'),
    closeEditPromptModal: document.getElementById('closeEditPromptModal'),
    cancelEditPromptBtn: document.getElementById('cancelEditPromptBtn'),
    saveEditPromptBtn: document.getElementById('saveEditPromptBtn'),

    // Zoom
    imageZoomOverlay: document.getElementById('imageZoomOverlay'),
    zoomImage: document.getElementById('zoomImage'),
    closeZoomBtn: document.getElementById('closeZoomBtn'),

    // Toast
    toastContainer: document.getElementById('toastContainer')
};

// ==========================================
// Canvas Drawing State
// ==========================================
let canvasCtx = null;
let fullResCanvas = null;  // Hidden full-resolution canvas
let fullResCtx = null;
let isDrawing = false;
let currentTool = 'brush';
let lastX = 0;
let lastY = 0;

// ==========================================
// Utility Functions
// ==========================================
function showToast(type, title, message) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>',
        error: '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
        warning: '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
    };

    toast.innerHTML = `
        ${icons[type]}
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            ${message ? `<div class="toast-message">${message}</div>` : ''}
        </div>
        <button class="toast-close">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
        </button>
    `;

    elements.toastContainer.appendChild(toast);

    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.remove();
    });

    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function updateStatus(status, text) {
    elements.statusDot.className = 'status-dot ' + status;
    elements.statusText.textContent = text;
}

function formatTime(date) {
    return new Intl.DateTimeFormat('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

function formatDateTime(date) {
    return new Intl.DateTimeFormat('zh-CN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

// ==========================================
// Configuration Management
// ==========================================
function loadConfig() {
    // Load from global config keys (set in portal page)
    state.config.apiKey = localStorage.getItem(STORAGE_KEYS.apiKey) || localStorage.getItem('video_api_key') || '';
    state.config.baseUrl = localStorage.getItem(STORAGE_KEYS.baseUrl) || localStorage.getItem('video_base_url') || '';

    if (state.config.apiKey || state.config.baseUrl) updateStatus('connected', 'Configured');
    else updateStatus('', 'Ready');
}

// ==========================================
// Image Upload & Management
// ==========================================
function handleFileSelect(files) {
    Array.from(files).forEach(file => {
        if (!file.type.startsWith('image/')) {
            showToast('error', 'Invalid file type', 'Please upload an image file');
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            showToast('error', 'File too large', 'Maximum file size is 10MB');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            state.images.push({
                id: Date.now() + Math.random(),
                name: file.name,
                originalData: e.target.result,  // Keep original
                data: e.target.result,          // Current (may have mask)
                hasMask: false
            });
            renderImagePreviews();

            // Auto-select the first image
            if (state.images.length === 1) {
                selectImage(0);
            }
        };
        reader.readAsDataURL(file);
    });
}

function renderImagePreviews() {
    elements.imagePreviewGrid.innerHTML = state.images.map((img, index) => `
        <div class="image-preview-item ${index === state.currentImageIndex ? 'active' : ''}" data-index="${index}">
            <img src="${img.data}" alt="${img.name}">
            <button class="remove-btn" data-index="${index}">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
            </button>
            ${img.hasMask ? '<span class="edit-indicator">Mask</span>' : ''}
        </div>
    `).join('');

    // Add event listeners
    elements.imagePreviewGrid.querySelectorAll('.image-preview-item').forEach(item => {
        item.addEventListener('click', (e) => {
            if (!e.target.closest('.remove-btn')) {
                selectImage(parseInt(item.dataset.index));
            }
        });
    });

    elements.imagePreviewGrid.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            removeImage(parseInt(btn.dataset.index));
        });
    });

    // Update edit mask button state
    updateEditMaskButtonState();
}

function updateEditMaskButtonState() {
    elements.editMaskBtn.disabled = state.images.length === 0 || state.currentImageIndex < 0;
}

function selectImage(index) {
    state.currentImageIndex = index;
    renderImagePreviews();
}

function removeImage(index) {
    state.images.splice(index, 1);
    if (state.currentImageIndex >= state.images.length) {
        state.currentImageIndex = state.images.length - 1;
    }
    renderImagePreviews();
}

// ==========================================
// Mask Modal Functions
// ==========================================
function openMaskModal() {
    if (state.currentImageIndex < 0 || !state.images[state.currentImageIndex]) {
        showToast('warning', 'No image selected', 'Please select an image first');
        return;
    }
    elements.maskModalOverlay.classList.add('show');
    // Initialize canvas after modal is visible
    setTimeout(() => {
        initCanvas();
    }, 100);
}

function closeMaskModal() {
    elements.maskModalOverlay.classList.remove('show');
}

// ==========================================
// High-Precision Canvas Drawing
// ==========================================
function initCanvas() {
    if (state.currentImageIndex < 0 || !state.images[state.currentImageIndex]) {
        return;
    }

    state.canvasZoom = 100;
    updateCanvasZoomLevel();

    const img = new Image();
    img.onload = () => {
        // Store original dimensions
        state.originalWidth = img.width;
        state.originalHeight = img.height;
        state.originalImage = img;

        // Create hidden full-resolution canvas for actual drawing
        fullResCanvas = document.createElement('canvas');
        fullResCanvas.width = img.width;
        fullResCanvas.height = img.height;
        fullResCtx = fullResCanvas.getContext('2d');
        fullResCtx.drawImage(img, 0, 0);

        // Calculate display size (fit within modal container)
        const containerWidth = elements.canvasContainer.clientWidth - 40;
        const containerHeight = elements.canvasContainer.clientHeight - 40 || 500;

        let displayWidth = img.width;
        let displayHeight = img.height;

        // Scale to fit
        const scaleX = containerWidth / img.width;
        const scaleY = containerHeight / img.height;
        state.displayScale = Math.min(scaleX, scaleY, 1); // Don't upscale

        displayWidth = Math.floor(img.width * state.displayScale);
        displayHeight = Math.floor(img.height * state.displayScale);

        // Set display canvas size
        const canvas = elements.maskCanvas;
        canvas.width = displayWidth;
        canvas.height = displayHeight;
        canvas.style.width = displayWidth + 'px';
        canvas.style.height = displayHeight + 'px';

        canvasCtx = canvas.getContext('2d');
        canvasCtx.imageSmoothingEnabled = true;
        canvasCtx.imageSmoothingQuality = 'high';

        // Draw scaled image
        canvasCtx.drawImage(img, 0, 0, displayWidth, displayHeight);

        // Reset history
        state.canvasHistory = [{
            display: canvas.toDataURL(),
            fullRes: fullResCanvas.toDataURL()
        }];
        state.canvasHistoryIndex = 0;
    };

    // Use current data (which may already have mask applied)
    img.src = state.images[state.currentImageIndex].data;
}

function getCanvasCoordinates(e) {
    const rect = elements.maskCanvas.getBoundingClientRect();
    const scaleX = elements.maskCanvas.width / rect.width;
    const scaleY = elements.maskCanvas.height / rect.height;

    return {
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY
    };
}

function startDrawing(e) {
    if (!canvasCtx || !fullResCtx) return;
    isDrawing = true;
    const coords = getCanvasCoordinates(e);
    lastX = coords.x;
    lastY = coords.y;
}

function draw(e) {
    if (!isDrawing || !canvasCtx || !fullResCtx) return;

    const coords = getCanvasCoordinates(e);
    const x = coords.x;
    const y = coords.y;

    // Get brush settings
    const brushSize = parseInt(elements.brushSize.value);
    const color = elements.brushColor.value;

    // Draw on display canvas
    drawLine(canvasCtx, lastX, lastY, x, y, brushSize, color, currentTool === 'eraser');

    // Draw on full-resolution canvas (scale coordinates)
    const fullResLastX = lastX / state.displayScale;
    const fullResLastY = lastY / state.displayScale;
    const fullResX = x / state.displayScale;
    const fullResY = y / state.displayScale;
    const fullResBrushSize = brushSize / state.displayScale;

    drawLine(fullResCtx, fullResLastX, fullResLastY, fullResX, fullResY, fullResBrushSize, color, currentTool === 'eraser');

    lastX = x;
    lastY = y;
}

function drawLine(ctx, x1, y1, x2, y2, size, color, isEraser) {
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.strokeStyle = color;
    ctx.lineWidth = size;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    if (isEraser) {
        ctx.globalCompositeOperation = 'destination-out';
    } else {
        ctx.globalCompositeOperation = 'source-over';
    }

    ctx.stroke();
    ctx.globalCompositeOperation = 'source-over';
}

function stopDrawing() {
    if (isDrawing) {
        isDrawing = false;
        saveCanvasState();

        // Mark image as having unsaved changes
        if (state.currentImageIndex >= 0 && state.images[state.currentImageIndex]) {
            state.images[state.currentImageIndex].hasMask = true;
            renderImagePreviews();
        }
    }
}

function saveCanvasState() {
    if (!elements.maskCanvas || !fullResCanvas) return;

    state.canvasHistoryIndex++;
    state.canvasHistory = state.canvasHistory.slice(0, state.canvasHistoryIndex);
    state.canvasHistory.push({
        display: elements.maskCanvas.toDataURL(),
        fullRes: fullResCanvas.toDataURL()
    });

    // Limit history size
    if (state.canvasHistory.length > 50) {
        state.canvasHistory.shift();
        state.canvasHistoryIndex--;
    }
}

function undo() {
    if (state.canvasHistoryIndex > 0) {
        state.canvasHistoryIndex--;
        loadCanvasState();
    }
}

function redo() {
    if (state.canvasHistoryIndex < state.canvasHistory.length - 1) {
        state.canvasHistoryIndex++;
        loadCanvasState();
    }
}

function loadCanvasState() {
    const historyItem = state.canvasHistory[state.canvasHistoryIndex];
    if (!historyItem) return;

    // Load display canvas
    const displayImg = new Image();
    displayImg.onload = () => {
        canvasCtx.clearRect(0, 0, elements.maskCanvas.width, elements.maskCanvas.height);
        canvasCtx.drawImage(displayImg, 0, 0);
    };
    displayImg.src = historyItem.display;

    // Load full-res canvas
    const fullResImg = new Image();
    fullResImg.onload = () => {
        fullResCtx.clearRect(0, 0, fullResCanvas.width, fullResCanvas.height);
        fullResCtx.drawImage(fullResImg, 0, 0);
    };
    fullResImg.src = historyItem.fullRes;
}

function clearCanvas() {
    if (state.currentImageIndex >= 0 && state.images[state.currentImageIndex]) {
        // Reset to original image
        state.images[state.currentImageIndex].data = state.images[state.currentImageIndex].originalData;
        state.images[state.currentImageIndex].hasMask = false;
        initCanvas();
        renderImagePreviews();
    }
}

// ==========================================
// Save Mask - Apply mask to image
// ==========================================
function saveMask() {
    if (!fullResCanvas || state.currentImageIndex < 0) {
        showToast('warning', 'No mask to save', 'Please draw on the image first');
        return;
    }

    // Get the full-resolution masked image
    const maskedImageData = fullResCanvas.toDataURL('image/png');

    // Update the current image data
    state.images[state.currentImageIndex].data = maskedImageData;
    state.images[state.currentImageIndex].hasMask = true;

    // Save to drawing history
    saveToDrawingHistory(maskedImageData);

    // Update preview
    renderImagePreviews();

    // Close the modal
    closeMaskModal();

    showToast('success', 'Mask saved', 'The mask has been applied to the image');
}

function resetMask() {
    if (state.currentImageIndex >= 0 && state.images[state.currentImageIndex]) {
        state.images[state.currentImageIndex].data = state.images[state.currentImageIndex].originalData;
        state.images[state.currentImageIndex].hasMask = false;
        initCanvas();
        renderImagePreviews();
        showToast('success', 'Mask reset', 'Image restored to original');
    }
}

// ==========================================
// Canvas Zoom Controls
// ==========================================
function updateCanvasZoomLevel() {
    elements.canvasZoomLevel.textContent = `${state.canvasZoom}%`;
    elements.canvasWrapper.style.transform = `scale(${state.canvasZoom / 100})`;
}

function canvasZoomIn() {
    if (state.canvasZoom < 300) {
        state.canvasZoom += 25;
        updateCanvasZoomLevel();
    }
}

function canvasZoomOut() {
    if (state.canvasZoom > 50) {
        state.canvasZoom -= 25;
        updateCanvasZoomLevel();
    }
}

function canvasZoomReset() {
    state.canvasZoom = 100;
    updateCanvasZoomLevel();
}

	        // ==========================================
	        // API Integration for Image Repository
	        // ==========================================

	        async function checkAuthentication() {
	            try {
	                const res = await fetch('/api/v1/auth/me', { credentials: 'include' });
	                if (!res.ok) {
	                    window.location.href = '/login?next=/image';
	                    return false;
	                }
	                return true;
	            } catch (err) {
	                console.error('Authentication check failed:', err);
	                window.location.href = '/login?next=/image';
	                return false;
	            }
	        }

	        async function loadImagesFromRepository() {
	            try {
	                const res = await fetch('/api/v1/images?limit=50', { credentials: 'include' });
	                if (!res.ok) {
	                    if (res.status === 401) {
	                        window.location.href = '/login?next=/image';
	                        return;
	                    }
	                    throw new Error('Failed to load images');
	                }

	                const images = await res.json();
        // state.drawingHistory = images.map(img => ({ ... })); // Removed
        /*
	                state.drawingHistory = images.map(img => ({
	                    id: img.id,
	                    imageUrl: img.image_url,
	                    thumbnail: img.image_url,
	                    time: img.created_at,
	                    model: img.model,
	                    prompt: img.prompt,
	                    title: img.title
	                }));
        */

	                // renderDrawingHistory(); // Removed
	            } catch (err) {
	                console.error('Failed to load images from repository:', err);
	                showToast('error', 'Load failed', err.message || 'Failed to load images from repository');
	            }
	        }

	        async function saveImageToRepository(imageUrl, model, prompt) {
	            if (!imageUrl) {
	                console.warn('No image URL to save');
	                return null;
	            }

	            try {
	                const payload = {
	                    image_url: imageUrl,
	                    model: model || 'unknown',
	                    prompt: prompt || '',
	                    status: 'completed',
	                    title: null
	                };

	                const res = await fetch('/api/v1/images', {
	                    method: 'POST',
	                    headers: {
	                        'Content-Type': 'application/json',
	                        ...csrfHeaders()
	                    },
	                    credentials: 'include',
	                    body: JSON.stringify(payload)
	                });

	                if (!res.ok) {
	                    if (res.status === 413) {
	                        showToast('error', '存储空间不足', 'Storage quota exceeded');
	                        return null;
	                    }
	                    const errorText = await res.text();
	                    throw new Error(errorText || 'Failed to save image');
	                }

	                const savedImage = await res.json();
	                showToast('success', '保存成功', 'Image saved to repository');

	                // Reload images from repository
	                await loadImagesFromRepository();

	                return savedImage;
	            } catch (err) {
	                console.error('Failed to save image to repository:', err);
	                showToast('error', '保存失败', err.message || 'Failed to save image');
	                return null;
	            }
	        }

	        async function deleteImageFromRepository(imageId) {
	            if (!confirm('确定要删除这条记录吗？')) return;

	            try {
	                const res = await fetch(`/api/v1/images/${encodeURIComponent(imageId)}`, {
	                    method: 'DELETE',
	                    headers: csrfHeaders(),
	                    credentials: 'include'
	                });

	                if (!res.ok) {
	                    throw new Error('Failed to delete image');
	                }

	                showToast('success', '删除成功', 'Image deleted from repository');

	                // Reload images from repository
	                await loadImagesFromRepository();
	            } catch (err) {
	                console.error('Failed to delete image from repository:', err);
	                showToast('error', '删除失败', err.message || 'Failed to delete image');
	            }
	        }



	        // Show image preview modal
	        function showImagePreview(imageUrl, date) {
	            elements.imagePreviewImg.src = imageUrl;
	            elements.imagePreviewInfo.textContent = `生成时间: ${date}`;
	            elements.imagePreviewOverlay.classList.add('show');
	        }

	        // Close image preview modal
	        function closeImagePreview() {
	            elements.imagePreviewOverlay.classList.remove('show');
	            setTimeout(() => {
	                elements.imagePreviewImg.src = '';
	            }, 300);
	        }

	        // ==========================================
	        // Prompt Management
	        // ==========================================
function updateCharCount() {
    const count = elements.promptInput.value.length;
    elements.charCount.textContent = count;
}

	        function savePromptToHistory(prompt) {
	            if (!prompt.trim()) return;

	            // Remove duplicates
	            state.promptHistory = state.promptHistory.filter(p => p.text !== prompt);

    // Add new prompt
    state.promptHistory.unshift({
        text: prompt,
        time: new Date().toISOString()
    });

	            // Keep only last 20
	            state.promptHistory = state.promptHistory.slice(0, 20);

	            try {
	                localStorage.setItem('promptHistory', JSON.stringify(state.promptHistory));
	            } catch (err) {
	                console.warn('Failed to persist prompt history:', err);
	            }
	        }

	        function renderPromptHistory() {
	            if (state.promptHistory.length === 0) {
	                elements.promptHistoryDropdown.innerHTML = '<p style="padding: 12px; text-align: center; color: var(--text-muted);">No history yet</p>';
	                return;
	            }

	            elements.promptHistoryDropdown.innerHTML = state.promptHistory.map((item, index) => `
	                <div class="prompt-history-item" data-index="${index}">
	                    <span class="prompt-text">${item.text}</span>
	                    <div class="prompt-history-actions">
	                        <span class="prompt-time">${formatTime(new Date(item.time))}</span>
	                        <button class="prompt-history-delete" data-index="${index}" title="Delete">
	                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
	                                <path d="M18 6L6 18M6 6l12 12"/>
	                            </svg>
	                        </button>
	                    </div>
	                </div>
	            `).join('');

	            elements.promptHistoryDropdown.querySelectorAll('.prompt-history-item').forEach(item => {
	                item.addEventListener('click', (e) => {
	                    if (e.target.closest('.prompt-history-delete')) return;
	                    elements.promptInput.value = state.promptHistory[parseInt(item.dataset.index)].text;
	                    updateCharCount();
	                    elements.promptHistoryDropdown.classList.remove('show');
	                });
	            });

	            elements.promptHistoryDropdown.querySelectorAll('.prompt-history-delete').forEach(btn => {
	                btn.addEventListener('click', (e) => {
	                    e.stopPropagation();
	                    deletePromptHistoryItem(parseInt(btn.dataset.index));
	                });
	            });
	        }

	        function deletePromptHistoryItem(index) {
	            if (Number.isNaN(index) || index < 0 || index >= state.promptHistory.length) return;

	            state.promptHistory.splice(index, 1);
	            try {
	                localStorage.setItem('promptHistory', JSON.stringify(state.promptHistory));
	            } catch (err) {
	                console.warn('Failed to persist prompt history:', err);
	            }
	            renderPromptHistory();
	            showToast('success', 'Deleted', 'Prompt history item removed');
	        }

// ==========================================
// Generation History
// ==========================================
	        function saveToGenerationHistory(prompt, imageUrl) {
	            state.generationHistory.unshift({
	                prompt,
	                imageUrl,
	                model: elements.modelSelect.value,
	                time: new Date().toISOString()
	            });

	            // Keep only last 50
	            state.generationHistory = state.generationHistory.slice(0, 50);
	            try {
	                localStorage.setItem('generationHistory', JSON.stringify(state.generationHistory));
	            } catch (err) {
	                console.warn('Failed to persist generation history:', err);
	            }
	            renderGenerationHistory();
	            renderInlineHistory();
	        }

	        function renderGenerationHistory() {
	            if (state.generationHistory.length === 0) {
        elements.historyList.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: 40px 20px;">No generation history yet</p>';
        return;
    }

	            elements.historyList.innerHTML = state.generationHistory.map((item, index) => `
	                <div class="history-item" data-index="${index}">
	                    <img class="history-item-image" src="${item.imageUrl}" alt="Generated" loading="lazy" decoding="async">
	                    <div class="history-item-content">
	                        <div class="history-item-prompt">${item.prompt}</div>
	                        <div class="history-item-meta">${item.model} - ${formatTime(new Date(item.time))}</div>
	                    </div>
	                    <button class="history-item-delete" data-index="${index}" title="Delete">
	                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
	                            <path d="M18 6L6 18M6 6l12 12"/>
	                        </svg>
	                    </button>
	                </div>
	            `).join('');

	            elements.historyList.querySelectorAll('.history-item').forEach(item => {
	                item.addEventListener('click', (e) => {
	                    if (e.target.closest('.history-item-delete')) return;
	                    const historyItem = state.generationHistory[parseInt(item.dataset.index)];
	                    showResult(historyItem.imageUrl);
	                    elements.promptInput.value = historyItem.prompt;
	                    updateCharCount();
	                });
	            });

	            elements.historyList.querySelectorAll('.history-item-delete').forEach(btn => {
	                btn.addEventListener('click', (e) => {
	                    e.stopPropagation();
	                    deleteGenerationHistoryItem(parseInt(btn.dataset.index));
	                });
	            });

                applyImageFallbacks(elements.historyList, '.history-item-image');
	        }

// ==========================================
// Inline Generation History (below prompt)
// ==========================================
function renderInlineHistory() {
    const history = state.generationHistory;
    const count = history.length;

    // Update count badge
    elements.inlineHistoryCount.textContent = count;

    // Apply collapsed state
    if (state.inlineHistoryCollapsed) {
        elements.inlineHistorySection.classList.add('collapsed');
    } else {
        elements.inlineHistorySection.classList.remove('collapsed');
    }

    // Empty state
    if (count === 0) {
        elements.inlineHistoryGrid.innerHTML = '<p class="inline-history-empty">No generation history yet. Create your first image!</p>';
        elements.inlineHistoryShowMore.style.display = 'none';
        return;
    }

    // Determine how many items to show
    const limit = state.inlineHistoryShowAll ? count : Math.min(state.inlineHistoryLimit, count);
    const itemsToShow = history.slice(0, limit);

    // Render grid items
    elements.inlineHistoryGrid.innerHTML = itemsToShow.map((item, index) => {
        const truncatedPrompt = item.prompt.length > 100
            ? item.prompt.substring(0, 100) + '...'
            : item.prompt;
        const timeStr = formatDateTime(new Date(item.time));

        return `
            <div class="inline-history-item" data-index="${index}">
                <div class="inline-history-item-actions">
                    <button class="inline-history-action-btn load" data-index="${index}" title="Load prompt">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                            <polyline points="7 10 12 15 17 10"/>
                            <line x1="12" y1="15" x2="12" y2="3"/>
                        </svg>
                    </button>
                    <button class="inline-history-action-btn edit" data-index="${index}" title="Edit prompt">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                        </svg>
                    </button>
                    <button class="inline-history-action-btn delete" data-index="${index}" title="Delete">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                    </button>
                </div>
                <img class="inline-history-item-image" src="${item.imageUrl}" alt="Generated" loading="lazy">
                <div class="inline-history-item-info">
                    <div class="inline-history-item-prompt" title="${item.prompt.replace(/"/g, '&quot;')}">${truncatedPrompt}</div>
                    <div class="inline-history-item-meta">
                        <span>${item.model}</span>
                        <span>•</span>
                        <span>${timeStr}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    // Show/hide "Show more" button
    if (count > state.inlineHistoryLimit && !state.inlineHistoryShowAll) {
        elements.inlineHistoryShowMore.style.display = 'flex';
        elements.showMoreHistoryBtn.textContent = `Show more (${count - limit} more)`;
    } else if (state.inlineHistoryShowAll && count > state.inlineHistoryLimit) {
        elements.inlineHistoryShowMore.style.display = 'flex';
        elements.showMoreHistoryBtn.textContent = 'Show less';
    } else {
        elements.inlineHistoryShowMore.style.display = 'none';
    }

    // Add event listeners for inline history items
    initInlineHistoryEventListeners();

    applyImageFallbacks(elements.inlineHistoryGrid, '.inline-history-item-image');
}

function initInlineHistoryEventListeners() {
    // Click on item (load into result area)
    elements.inlineHistoryGrid.querySelectorAll('.inline-history-item').forEach(item => {
        item.addEventListener('click', (e) => {
            // Don't trigger if clicking on action buttons
            if (e.target.closest('.inline-history-action-btn')) return;

            const index = parseInt(item.dataset.index);
            loadHistoryItem(index);
        });
    });

    // Load button
    elements.inlineHistoryGrid.querySelectorAll('.inline-history-action-btn.load').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const index = parseInt(btn.dataset.index);
            loadHistoryItem(index);
        });
    });

    // Edit button
    elements.inlineHistoryGrid.querySelectorAll('.inline-history-action-btn.edit').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const index = parseInt(btn.dataset.index);
            openEditPromptModal(index);
        });
    });

    // Delete button
    elements.inlineHistoryGrid.querySelectorAll('.inline-history-action-btn.delete').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const index = parseInt(btn.dataset.index);
            deleteHistoryItem(index);
        });
    });
}

function loadHistoryItem(index) {
    const item = state.generationHistory[index];
    if (!item) return;

    showResult(item.imageUrl);
    elements.promptInput.value = item.prompt;
    updateCharCount();
    showToast('success', 'Loaded', 'Prompt and image loaded from history');
}

function deleteHistoryItem(index) {
    if (!confirm('Delete this generation from history?')) return;

    state.generationHistory.splice(index, 1);
    try {
        localStorage.setItem('generationHistory', JSON.stringify(state.generationHistory));
    } catch (err) {
        console.warn('Failed to persist generation history:', err);
    }

    // Sync both displays
    renderInlineHistory();
    renderGenerationHistory();

    showToast('success', 'Deleted', 'Generation removed from history');
}

function updateHistoryPrompt(index, newPrompt) {
    if (index < 0 || index >= state.generationHistory.length) return;

    state.generationHistory[index].prompt = newPrompt;
    try {
        localStorage.setItem('generationHistory', JSON.stringify(state.generationHistory));
    } catch (err) {
        console.warn('Failed to persist generation history:', err);
    }

    // Sync both displays
    renderInlineHistory();
    renderGenerationHistory();

    showToast('success', 'Updated', 'Prompt has been updated');
}

function openEditPromptModal(index) {
    const item = state.generationHistory[index];
    if (!item) return;

    state.editingHistoryIndex = index;
    elements.editPromptTextarea.value = item.prompt;
    elements.editPromptModalOverlay.classList.add('show');
    elements.editPromptTextarea.focus();
}

function closeEditPromptModal() {
    elements.editPromptModalOverlay.classList.remove('show');
    state.editingHistoryIndex = -1;
    elements.editPromptTextarea.value = '';
}

function saveEditedPrompt() {
    if (state.editingHistoryIndex < 0) return;

    const newPrompt = elements.editPromptTextarea.value.trim();
    if (!newPrompt) {
        showToast('error', 'Invalid', 'Prompt cannot be empty');
        return;
    }

    updateHistoryPrompt(state.editingHistoryIndex, newPrompt);
    closeEditPromptModal();
}

function toggleInlineHistory() {
    state.inlineHistoryCollapsed = !state.inlineHistoryCollapsed;
    localStorage.setItem('inlineHistoryCollapsed', state.inlineHistoryCollapsed.toString());

    if (state.inlineHistoryCollapsed) {
        elements.inlineHistorySection.classList.add('collapsed');
    } else {
        elements.inlineHistorySection.classList.remove('collapsed');
    }
}

function toggleShowMoreHistory() {
    state.inlineHistoryShowAll = !state.inlineHistoryShowAll;
    renderInlineHistory();
}

function deleteGenerationHistoryItem(index) {
    deleteHistoryItem(index);
}



// ==========================================
// API Call - Fixed to send masked images
// ==========================================
async function generateImage() {
    const prompt = elements.promptInput.value.trim();
    const batchCount = clampInt(elements.batchCount?.value, 1, 10, 1);
    if (elements.batchCount) elements.batchCount.value = String(batchCount);

    // Validation
    if (!prompt) {
        showToast('error', 'Prompt required', 'Please enter a prompt');
        return;
    }

    if (batchCount >= 6) {
        const ok = confirm(`将并发生成 ${batchCount} 张图片，确认继续？`);
        if (!ok) return;
    }

    // Update UI
    state.isGenerating = true;
    elements.generateBtn.disabled = true;
    elements.resultPlaceholder.style.display = 'none';
    elements.resultContainer.style.display = 'none';
    elements.loadingState.style.display = 'block';
    updateStatus('generating', 'Generating...');

    try {
        // Prepare form data
        const formData = new FormData();
        formData.append('model', elements.modelSelect.value);
        formData.append('prompt', prompt);
        formData.append('n', String(batchCount));
        formData.append('response_format', 'url');

        if (elements.aspectRatio.value) {
            formData.append('aspect_ratio', elements.aspectRatio.value);
        }

        if (elements.imageSize.value) {
            formData.append('image_size', elements.imageSize.value);
        }

        // Add images - use the current data which includes masks
        for (const img of state.images) {
            // Use img.data which contains the masked version if saved
            const imageData = img.data;
            const response = await fetch(imageData);
            const blob = await response.blob();
            formData.append('image', blob, img.name || 'image.png');
        }

        const apiKey = normalizeApiKey(state.config.apiKey);
        const baseUrl = normalizeApiBaseUrl(state.config.baseUrl);

        // Make API call via backend (/api/v1/images/edits)
        const response = await fetch('/api/v1/images/edits', {
            method: 'POST',
            credentials: 'include',
            headers: {
                ...csrfHeaders(),
                ...(apiKey ? { 'X-API-Key': apiKey } : {}),
                ...(baseUrl ? { 'X-Base-Url': baseUrl } : {}),
            },
            body: formData
        });

        if (!response.ok) {
            const data = await readJsonOrText(response);
            if (response.status === 401) {
                window.location.href = '/login?next=/image';
                return;
            }
            throw new Error(extractErrorMessage(data, `Request failed (HTTP ${response.status})`));
        }

        const data = await readJsonOrText(response);
        const result = data && typeof data === 'object' && data.response ? data.response : data;

        const imageUrls = extractImageUrls(result);
        if (!imageUrls.length) {
            throw new Error('No image URL in response');
        }

        // Show result
        showResult(imageUrls[0]);
        savePromptToHistory(prompt);
        for (let i = imageUrls.length - 1; i >= 0; i -= 1) {
            saveToGenerationHistory(prompt, imageUrls[i]);
        }
        showToast(
            'success',
            imageUrls.length > 1 ? 'Images generated' : 'Image generated',
            imageUrls.length > 1 ? `Generated ${imageUrls.length} images successfully` : 'Your image has been created successfully'
        );

        // Refresh repository to show the newly saved image
        loadImagesFromRepository();

    } catch (error) {
        console.error('Generation error:', error);
        showToast('error', 'Generation failed', error.message);
        elements.loadingState.style.display = 'none';
        elements.resultPlaceholder.style.display = 'block';
        updateStatus('error', 'Error');
    } finally {
        state.isGenerating = false;
        elements.generateBtn.disabled = false;
    }
}

function showResult(imageUrl) {
    elements.loadingState.style.display = 'none';
    elements.resultPlaceholder.style.display = 'none';
    elements.resultContainer.style.display = 'block';
    elements.resultImage.src = imageUrl;
    state.currentZoom = 100;
    updateZoomLevel();
    updateStatus('connected', 'Complete');
}

// ==========================================
// Zoom Controls
// ==========================================
function updateZoomLevel() {
    elements.zoomLevel.textContent = `${state.currentZoom}%`;
    elements.resultImage.style.transform = `scale(${state.currentZoom / 100})`;
}

function zoomIn() {
    if (state.currentZoom < 200) {
        state.currentZoom += 25;
        updateZoomLevel();
    }
}

function zoomOut() {
    if (state.currentZoom > 25) {
        state.currentZoom -= 25;
        updateZoomLevel();
    }
}

// ==========================================
// Download & Share
// ==========================================
function downloadImage() {
    const imageUrl = elements.resultImage.src;
    if (!imageUrl) return;

    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `generated-${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast('success', 'Download started', 'Image is being downloaded');
}

function shareImage() {
    const imageUrl = elements.resultImage.src;
    if (!imageUrl) return;

    if (navigator.share) {
        navigator.share({
            title: 'Generated Image',
            text: elements.promptInput.value,
            url: imageUrl
        }).catch(() => {});
    } else {
        navigator.clipboard.writeText(imageUrl).then(() => {
            showToast('success', 'Link copied', 'Image URL copied to clipboard');
        });
    }
}

function showFullscreen() {
    const imageUrl = elements.resultImage.src;
    if (!imageUrl) return;

    elements.zoomImage.src = imageUrl;
    elements.imageZoomOverlay.classList.add('show');
}

// ==========================================
// Model Search
// ==========================================
function filterModels() {
    const search = elements.modelSearch.value.toLowerCase();
    const options = elements.modelSelect.options;

    for (let i = 0; i < options.length; i++) {
        const option = options[i];
        const text = option.textContent.toLowerCase();
        option.style.display = text.includes(search) ? '' : 'none';
    }
}

// ==========================================
// Collapsible Sections
// ==========================================
function initCollapsibles() {
    document.querySelectorAll('.collapsible-header').forEach(header => {
        const targetId = header.dataset.target;
        const target = targetId ? document.getElementById(targetId) : null;
        if (!target) return;

        if (targetId === 'configContent') {
            header.classList.add('collapsed');
            target.classList.add('collapsed');
        }

        header.addEventListener('click', () => {
            const isCollapsed = header.classList.toggle('collapsed');
            target.classList.toggle('collapsed', isCollapsed);
        });
    });
}

// ==========================================
// Toggle Visibility
// ==========================================
function initToggleVisibility() {
    document.querySelectorAll('.toggle-visibility').forEach(btn => {
        btn.addEventListener('click', () => {
            const input = document.getElementById(btn.dataset.target);
            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
            btn.innerHTML = isPassword ?
                '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>' :
                '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';
        });
    });
}

// ==========================================
// Event Listeners
// ==========================================
function initEventListeners() {
    // File upload
    elements.fileInput.addEventListener('change', (e) => handleFileSelect(e.target.files));
    elements.uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.uploadArea.classList.add('drag-over');
    });
    elements.uploadArea.addEventListener('dragleave', () => {
        elements.uploadArea.classList.remove('drag-over');
    });
    elements.uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.uploadArea.classList.remove('drag-over');
        handleFileSelect(e.dataTransfer.files);
    });

    // Mask Modal
    elements.editMaskBtn.addEventListener('click', openMaskModal);
    elements.closeMaskModal.addEventListener('click', closeMaskModal);
    elements.cancelMaskBtn.addEventListener('click', closeMaskModal);
    elements.maskModalOverlay.addEventListener('click', (e) => {
        if (e.target === elements.maskModalOverlay) {
            closeMaskModal();
        }
    });

    // Image Preview Modal
    elements.closeImagePreview.addEventListener('click', closeImagePreview);
    elements.imagePreviewOverlay.addEventListener('click', (e) => {
        if (e.target === elements.imagePreviewOverlay) {
            closeImagePreview();
        }
    });

    // Canvas mouse events
    elements.maskCanvas.addEventListener('mousedown', startDrawing);
    elements.maskCanvas.addEventListener('mousemove', draw);
    elements.maskCanvas.addEventListener('mouseup', stopDrawing);
    elements.maskCanvas.addEventListener('mouseout', stopDrawing);

    // Touch support for canvas
    elements.maskCanvas.addEventListener('touchstart', (e) => {
        e.preventDefault();
        const touch = e.touches[0];
        startDrawing({clientX: touch.clientX, clientY: touch.clientY});
    });
    elements.maskCanvas.addEventListener('touchmove', (e) => {
        e.preventDefault();
        const touch = e.touches[0];
        draw({clientX: touch.clientX, clientY: touch.clientY});
    });
    elements.maskCanvas.addEventListener('touchend', stopDrawing);

    // Tool buttons
    document.querySelectorAll('[data-tool]').forEach(btn => {
        btn.addEventListener('click', () => {
            currentTool = btn.dataset.tool;
            document.querySelectorAll('[data-tool]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    // Brush size
    elements.brushSize.addEventListener('input', () => {
        elements.brushSizeLabel.textContent = elements.brushSize.value + 'px';
    });

    // Undo/Redo/Clear
    elements.undoBtn.addEventListener('click', undo);
    elements.redoBtn.addEventListener('click', redo);
    elements.clearCanvasBtn.addEventListener('click', clearCanvas);

    // Save/Reset Mask
    elements.saveMaskBtn.addEventListener('click', saveMask);
    elements.resetMaskBtn.addEventListener('click', resetMask);

    // Canvas zoom
    elements.canvasZoomInBtn.addEventListener('click', canvasZoomIn);
    elements.canvasZoomOutBtn.addEventListener('click', canvasZoomOut);
    elements.canvasZoomResetBtn.addEventListener('click', canvasZoomReset);

    // Drawing history - removed clearDrawingHistory event (now using API)

    // Prompt
    elements.promptInput.addEventListener('input', updateCharCount);
    elements.showPromptHistory.addEventListener('click', () => {
        renderPromptHistory();
        elements.promptHistoryDropdown.classList.toggle('show');
    });

    // Close prompt history when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.main-prompt-section')) {
            elements.promptHistoryDropdown.classList.remove('show');
        }
    });

    // Model search
    elements.modelSearch.addEventListener('input', filterModels);

    // Batch count
    elements.batchCount?.addEventListener('change', () => {
        const clamped = clampInt(elements.batchCount.value, 1, 10, 1);
        elements.batchCount.value = String(clamped);
    });

    // Generate
    elements.generateBtn.addEventListener('click', generateImage);

    // Zoom controls
    elements.zoomInBtn.addEventListener('click', zoomIn);
    elements.zoomOutBtn.addEventListener('click', zoomOut);

    // Download/Share
    elements.downloadBtn.addEventListener('click', downloadImage);
    elements.shareBtn.addEventListener('click', shareImage);
    elements.fullscreenBtn.addEventListener('click', showFullscreen);
    elements.resultImage.addEventListener('error', () => {
        const current = elements.resultImage.getAttribute('src') || '';
        if (current === IMAGE_PLACEHOLDER_SRC) return;
        elements.resultImage.alt = 'Image unavailable';
        elements.resultImage.src = IMAGE_PLACEHOLDER_SRC;
    });

    // Fullscreen overlay
    elements.closeZoomBtn.addEventListener('click', () => {
        elements.imageZoomOverlay.classList.remove('show');
    });
    elements.imageZoomOverlay.addEventListener('click', (e) => {
        if (e.target === elements.imageZoomOverlay) {
            elements.imageZoomOverlay.classList.remove('show');
        }
    });

    // History panel
    elements.historyBtn.addEventListener('click', () => {
        elements.historyPanel.classList.toggle('show');
    });
    elements.closeHistoryBtn.addEventListener('click', () => {
        elements.historyPanel.classList.remove('show');
    });

    // Inline History
    elements.inlineHistoryToggle.addEventListener('click', toggleInlineHistory);
    elements.showMoreHistoryBtn.addEventListener('click', toggleShowMoreHistory);

    // Edit Prompt Modal
    elements.closeEditPromptModal.addEventListener('click', closeEditPromptModal);
    elements.cancelEditPromptBtn.addEventListener('click', closeEditPromptModal);
    elements.saveEditPromptBtn.addEventListener('click', saveEditedPrompt);
    elements.editPromptModalOverlay.addEventListener('click', (e) => {
        if (e.target === elements.editPromptModalOverlay) {
            closeEditPromptModal();
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey || e.metaKey) {
            if (e.key === 'z') {
                e.preventDefault();
                if (e.shiftKey) {
                    redo();
                } else {
                    undo();
                }
            } else if (e.key === 'Enter') {
                e.preventDefault();
                generateImage();
            } else if (e.key === 's') {
                e.preventDefault();
                saveMask();
            }
        }

        if (e.key === 'Escape') {
            closeMaskModal();
            closeEditPromptModal();
            elements.imageZoomOverlay.classList.remove('show');
            elements.historyPanel.classList.remove('show');
        }
    });

    // Canvas wheel zoom
    elements.canvasContainer.addEventListener('wheel', (e) => {
        if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            if (e.deltaY < 0) {
                canvasZoomIn();
            } else {
                canvasZoomOut();
            }
        }
    });
}

// ==========================================
// Initialize Application
// ==========================================
function init() {
    loadConfig();
    initCollapsibles();
    initToggleVisibility();
    initEventListeners();
    renderGenerationHistory();
    renderInlineHistory();
    updateCharCount();

    // Check authentication and load images from API
    checkAuthentication().then(isAuth => {
        if (isAuth) {
            loadImagesFromRepository();
        }
    });
}

// Start the application
if (document.readyState !== 'loading') {
    init();
} else {
    document.addEventListener('DOMContentLoaded', init);
}

export {};
