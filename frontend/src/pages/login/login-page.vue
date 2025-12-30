<template>
  <div class="container">
    <main>
      <section class="card auth-card">
        <h2>登录</h2>
        <div class="form-group">
          <label for="usernameOrEmail">用户名或邮箱</label>
          <input
            id="usernameOrEmail"
            v-model="usernameOrEmail"
            type="text"
            autocomplete="username"
            placeholder="输入用户名或邮箱"
          />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="输入密码"
            @keydown.enter="login"
          />
        </div>
        <div class="auth-actions">
          <button
            id="loginBtn"
            class="primary-btn"
            type="button"
            :class="{ loading: isLoading }"
            :disabled="isLoading"
            @click="login"
          >
            <span class="btn-text">登录</span>
            <span class="loader"></span>
          </button>
          <a class="meta-text" href="/" style="text-decoration: none">返回首页</a>
        </div>
        <div id="error" class="auth-error" role="alert" aria-live="polite">{{ error }}</div>
        <div class="auth-meta">
          没有账号？请使用 <code>POST /api/v1/auth/register</code> 注册后再登录。
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { safeNextPath } from '@/shared/routing';
import { readErrorText } from '@/shared/http';

const usernameOrEmail = ref('');
const password = ref('');
const error = ref('');
const isLoading = ref(false);

async function login() {
  error.value = '';
  const username = usernameOrEmail.value.trim();
  if (!username || !password.value) {
    error.value = '请输入用户名/邮箱和密码';
    return;
  }

  isLoading.value = true;
  try {
    const res = await fetch('/api/v1/auth/login?set_cookie=1', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ username_or_email: username, password: password.value })
    });
    if (!res.ok) throw new Error(await readErrorText(res));
    window.location.href = safeNextPath();
  } catch (e: any) {
    error.value = e?.message || '登录失败';
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.auth-card {
  max-width: 520px;
  margin: 10vh auto;
}

.auth-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
}

.auth-error {
  color: #c0392b;
  margin-top: 10px;
}

.auth-meta {
  font-size: 12px;
  opacity: 0.75;
  margin-top: 12px;
}
</style>
