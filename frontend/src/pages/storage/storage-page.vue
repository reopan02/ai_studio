<template>
  <div class="storage-page">
      <div class="container">
          <!-- Header -->
          <header class="storage-header">
              <div class="storage-header-left">
                  <a href="/" class="btn btn-secondary" style="text-decoration: none;">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M19 12H5M12 19l-7-7 7-7"/>
                      </svg>
                      返回主页
                  </a>
                  <h1>我的存储库</h1>
              </div>
              <div class="header-actions">
                  <a href="/video" class="btn btn-secondary">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M19 12H5M12 19l-7-7 7-7"/>
                      </svg>
                      返回生成页
                  </a>
              </div>
          </header>
  
          <!-- Videos Section -->
          <section class="section">
              <div class="section-header">
                  <div style="display: flex; align-items: center; gap: 12px;">
                      <div class="section-title">
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                              <path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                          </svg>
                          视频生成记录
                      </div>
                      <span class="section-count">{{ videoCountLabel }}</span>
                  </div>
              </div>
              <div class="storage-grid">
                  <div v-if="loadingVideos" class="empty-state">
                      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                          <path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                      </svg>
                      <h3>加载中...</h3>
                  </div>

                  <div v-else-if="videos.length === 0" class="empty-state" style="grid-column: 1/-1;">
                      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5" style="margin-bottom: 16px;">
                          <path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                      </svg>
                      <h3>暂无视频记录</h3>
                      <p style="margin-top: 8px;">开始生成您的第一个视频吧</p>
                      <a href="/video" style="color: #6366f1; text-decoration: none; margin-top: 12px; display: inline-block; font-weight: 500;">去生成视频 →</a>
                  </div>

                  <div v-else v-for="v in videos" :key="v.id" class="video-card">
                      <div class="video-thumb">
                          <video v-if="v.video_url" :src="v.video_url" controls preload="metadata"></video>
                          <div v-else style="color: white; opacity: 0.9;">暂无预览</div>
                      </div>
                      <div class="video-info">
                          <div class="video-title">{{ v.title || '未命名视频' }}</div>
                          <div class="video-meta">
                              <span class="badge" :class="modelBadgeClass(v.model)">{{ v.model }}</span>
                              <span style="color: #94a3b8;">{{ formatDateTime(v.created_at) }}</span>
                          </div>
                          <div class="video-prompt" :title="v.prompt">{{ v.prompt }}</div>
                          <div class="video-actions">
                              <a
                                v-if="v.video_url"
                                :href="v.video_url"
                                download
                                class="btn btn-secondary btn-sm"
                                style="text-decoration: none; flex: 1; justify-content: center;"
                              >
                                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                      <polyline points="7 10 12 15 17 10"/>
                                      <line x1="12" y1="15" x2="12" y2="3"/>
                                  </svg>
                                  下载
                              </a>
                              <button
                                type="button"
                                class="btn btn-secondary btn-sm danger"
                                style="flex: 1; justify-content: center;"
                                @click="deleteVideo(v.id)"
                              >
                                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                      <polyline points="3 6 5 6 21 6"/>
                                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                                  </svg>
                                  删除
                              </button>
                          </div>
                      </div>
                  </div>
              </div>
          </section>
  
          <!-- Images Section -->
          <section class="section">
              <div class="section-header">
                  <div style="display: flex; align-items: center; gap: 12px;">
                      <div class="section-title">
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                              <rect x="3" y="3" width="18" height="18" rx="2"/>
                              <circle cx="8.5" cy="8.5" r="1.5"/>
                              <polyline points="21 15 16 10 5 21"/>
                          </svg>
                          图像生成记录
                      </div>
                      <span class="section-count">{{ imageCountLabel }}</span>
                  </div>
              </div>
              <div class="storage-grid">
                  <div v-if="loadingImages" class="empty-state">
                      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                          <rect x="3" y="3" width="18" height="18" rx="2"/>
                          <circle cx="8.5" cy="8.5" r="1.5"/>
                          <polyline points="21 15 16 10 5 21"/>
                      </svg>
                      <h3>加载中...</h3>
                  </div>

                  <div v-else-if="images.length === 0" class="empty-state" style="grid-column: 1/-1;">
                      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5" style="margin-bottom: 16px;">
                          <rect x="3" y="3" width="18" height="18" rx="2"/>
                          <circle cx="8.5" cy="8.5" r="1.5"/>
                          <polyline points="21 15 16 10 5 21"/>
                      </svg>
                      <h3>暂无图像记录</h3>
                      <p style="margin-top: 8px;">开始生成您的第一张图片吧</p>
                      <a href="/image-generate" style="color: #6366f1; text-decoration: none; margin-top: 12px; display: inline-block; font-weight: 500;">去生成图片 →</a>
                  </div>

                  <div v-else v-for="img in images" :key="img.id" class="video-card">
                      <div class="video-thumb">
                          <img v-if="img.image_url" :src="img.image_url" alt="Generated" loading="lazy" decoding="async" />
                          <div v-else style="color: white; opacity: 0.9;">暂无预览</div>
                      </div>
                      <div class="video-info">
                          <div class="video-title">{{ img.title || '未命名图像' }}</div>
                          <div class="video-meta">
                              <span class="badge" :class="modelBadgeClass(img.model)">{{ img.model }}</span>
                              <span style="color: #94a3b8;">{{ formatDateTime(img.created_at) }}</span>
                          </div>
                          <div class="video-prompt" :title="img.prompt">{{ img.prompt }}</div>
                          <div class="video-actions">
                              <a
                                v-if="img.image_url"
                                :href="img.image_url"
                                download
                                class="btn btn-secondary btn-sm"
                                style="text-decoration: none; flex: 1; justify-content: center;"
                              >
                                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                      <polyline points="7 10 12 15 17 10"/>
                                      <line x1="12" y1="15" x2="12" y2="3"/>
                                  </svg>
                                  下载
                              </a>
                              <button
                                type="button"
                                class="btn btn-secondary btn-sm danger"
                                style="flex: 1; justify-content: center;"
                                @click="deleteImage(img.id)"
                              >
                                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                      <polyline points="3 6 5 6 21 6"/>
                                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                                  </svg>
                                  删除
                              </button>
                          </div>
                      </div>
                  </div>
              </div>
          </section>
      </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { supabase } from '@/shared/supabase';

type UserVideoRow = {
  id: string;
  title: string | null;
  model: string;
  prompt: string;
  video_url: string | null;
  created_at: string;
};

type UserImageRow = {
  id: string;
  title: string | null;
  model: string;
  prompt: string;
  image_url: string | null;
  created_at: string;
};

const videos = ref<UserVideoRow[]>([]);
const images = ref<UserImageRow[]>([]);
const loadingVideos = ref(true);
const loadingImages = ref(true);

const videoCountLabel = computed(() => {
  if (loadingVideos.value) return '加载中...';
  if (videos.value.length === 0) return '暂无记录';
  return `${videos.value.length} 个视频`;
});

const imageCountLabel = computed(() => {
  if (loadingImages.value) return '加载中...';
  if (images.value.length === 0) return '暂无记录';
  return `${images.value.length} 个图像`;
});

function formatDateTime(value: string): string {
  try {
    return new Date(value).toLocaleString('zh-CN');
  } catch {
    return value;
  }
}

function modelBadgeClass(model: string): string {
  const value = String(model || '').toLowerCase();
  if (value.includes('sora')) return 'badge-sora2';
  if (value.includes('veo')) return 'badge-veo';
  if (value.includes('seedance')) return 'badge-seedance';
  return 'badge-default';
}

async function loadVideos() {
  loadingVideos.value = true;
  try {
    const { data, error } = await supabase
      .from('user_videos')
      .select('id,title,model,prompt,video_url,created_at')
      .order('created_at', { ascending: false })
      .limit(200);

    if (error) throw error;
    videos.value = (data || []) as UserVideoRow[];
  } finally {
    loadingVideos.value = false;
  }
}

async function loadImages() {
  loadingImages.value = true;
  try {
    const { data, error } = await supabase
      .from('user_images')
      .select('id,title,model,prompt,image_url,created_at')
      .order('created_at', { ascending: false })
      .limit(200);

    if (error) throw error;
    images.value = (data || []) as UserImageRow[];
  } finally {
    loadingImages.value = false;
  }
}

async function deleteVideo(id: string) {
  if (!confirm('确定要删除这条记录吗？')) return;
  const { error } = await supabase.from('user_videos').delete().eq('id', id);
  if (!error) {
    videos.value = videos.value.filter((v) => v.id !== id);
  }
}

async function deleteImage(id: string) {
  if (!confirm('确定要删除这条记录吗？')) return;
  const { error } = await supabase.from('user_images').delete().eq('id', id);
  if (!error) {
    images.value = images.value.filter((v) => v.id !== id);
  }
}

onMounted(() => {
  void loadVideos();
  void loadImages();
});
</script>

<style>
        body {
            background: #f5f7fa;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 24px;
        }

        /* Header */
        .storage-header {
            background: white;
            border-radius: 16px;
            padding: 24px 32px;
            margin-bottom: 32px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .storage-header-left {
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .storage-header h1 {
            font-size: 28px;
            font-weight: 700;
            color: #1a1a1a;
            margin: 0;
        }

        .header-actions {
            display: flex;
            gap: 12px;
        }

        /* Section */
        .section {
            background: white;
            border-radius: 16px;
            padding: 28px 32px;
            margin-bottom: 32px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }

        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 2px solid #f0f0f0;
        }

        .section-title {
            font-size: 20px;
            font-weight: 600;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .section-title svg {
            color: #6366f1;
        }

        .section-count {
            font-size: 14px;
            color: #94a3b8;
            font-weight: 500;
            background: #f1f5f9;
            padding: 4px 12px;
            border-radius: 12px;
        }

        /* Grid */
        .storage-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 24px;
        }

        .video-card {
            background: white;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            overflow: hidden;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .video-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
            border-color: #6366f1;
        }

        .video-thumb {
            width: 100%;
            height: 200px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }

        .video-thumb video,
        .video-thumb img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .video-thumb::after {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(to top, rgba(0,0,0,0.3), transparent 50%);
        }

        .video-info {
            padding: 20px;
        }

        .video-title {
            font-weight: 600;
            font-size: 16px;
            margin-bottom: 8px;
            color: #1e293b;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .video-meta {
            font-size: 13px;
            color: #64748b;
            margin-bottom: 12px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
        }

        .video-prompt {
            font-size: 14px;
            color: #475569;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            margin-bottom: 16px;
            line-height: 1.6;
            min-height: 44px;
        }

        .video-actions {
            display: flex;
            gap: 8px;
            padding-top: 12px;
            border-top: 1px solid #f1f5f9;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            white-space: nowrap;
        }

        .badge-sora2 { background: #dbeafe; color: #1e40af; }
        .badge-veo { background: #d1fae5; color: #065f46; }
        .badge-seedance { background: #fef3c7; color: #92400e; }
        .badge-default { background: #f1f5f9; color: #475569; }

        .empty-state {
            text-align: center;
            padding: 80px 20px;
            color: #94a3b8;
        }

        .empty-state svg {
            margin: 0 auto 24px;
            opacity: 0.5;
        }

        .empty-state h3 {
            font-size: 18px;
            font-weight: 600;
            color: #64748b;
            margin-bottom: 8px;
        }

        .empty-state p {
            font-size: 14px;
            margin-bottom: 24px;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 10px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
        }

        .btn-primary {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }

        .btn-secondary {
            background: white;
            color: #64748b;
            border: 1px solid #e2e8f0;
        }

        .btn-secondary:hover {
            background: #f8fafc;
            border-color: #cbd5e1;
        }

        .btn-secondary.danger:hover {
            background: #fef2f2;
            color: #dc2626;
            border-color: #fecaca;
        }

        .btn-sm {
            padding: 6px 12px;
            font-size: 13px;
        }

        @media (max-width: 768px) {
            .storage-grid {
                grid-template-columns: 1fr;
            }

            .storage-header {
                flex-direction: column;
                gap: 16px;
                align-items: flex-start;
            }
        }
</style>
