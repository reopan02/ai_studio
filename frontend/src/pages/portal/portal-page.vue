<template>
  <div class="container">
    <header>
      <h1>Video API Portal</h1>
      <p style="color: var(--text-secondary); margin-top: 8px">请选择功能模块</p>
    </header>

    <section v-if="error" class="card error-banner" style="margin-bottom: 20px">
      {{ error }}
    </section>

    <div class="portal-grid">
      <a href="/video" class="card portal-card">
        <svg class="portal-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect>
          <line x1="7" y1="2" x2="7" y2="22"></line>
          <line x1="17" y1="2" x2="17" y2="22"></line>
          <line x1="2" y1="12" x2="22" y2="12"></line>
          <line x1="2" y1="7" x2="7" y2="7"></line>
          <line x1="2" y1="17" x2="7" y2="17"></line>
          <line x1="17" y1="17" x2="22" y2="17"></line>
          <line x1="17" y1="7" x2="22" y2="7"></line>
        </svg>
        <div class="portal-title">视频生成</div>
        <div class="portal-desc">Sora 2, Veo, Seedance 等模型视频生成</div>
      </a>

      <a href="/storage" class="card portal-card">
        <svg class="portal-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
        <div class="portal-title">存储库</div>
        <div class="portal-desc">查看历史生成记录</div>
      </a>

      <a href="/image" class="card portal-card">
        <svg class="portal-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <circle cx="8.5" cy="8.5" r="1.5"></circle>
          <polyline points="21 15 16 10 5 21"></polyline>
        </svg>
        <div class="portal-title">图像处理</div>
        <div class="portal-desc">多图参考的图像编辑（nano-banana）</div>
      </a>

      <a v-if="isAdmin" href="/admin" class="card portal-card">
        <svg class="portal-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path
            d="M12 1l3 5 5 1-3.5 4.2.8 5.8L12 15l-5.3 2.9.8-5.8L4 7l5-1 3-5z"
          ></path>
        </svg>
        <div class="portal-title">Admin</div>
        <div class="portal-desc">User management &amp; system stats</div>
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { getCurrentUser } from '@/shared/auth';

const error = ref<string>('');
const isAdmin = ref(false);

onMounted(async () => {
  const params = new URLSearchParams(window.location.search);
  error.value = params.get('error') || '';

  try {
    const me = await getCurrentUser();
    isAdmin.value = Boolean(me?.is_admin);
  } catch {
    isAdmin.value = false;
  }
});
</script>

<style scoped>
.portal-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-top: 40px;
}

.portal-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  text-decoration: none;
  color: inherit;
}

.portal-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.portal-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 20px;
  color: var(--accent-color);
}

.portal-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.portal-desc {
  color: var(--text-secondary);
}

.error-banner {
  border: 1px solid rgba(255, 59, 48, 0.25);
  background: rgba(255, 59, 48, 0.06);
  color: #b42318;
}
</style>

