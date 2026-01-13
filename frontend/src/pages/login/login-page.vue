<template>
  <div class="container">
    <main>
      <section class="card auth-card">
        <h2>登录</h2>
        <div class="form-group">
          <label for="email">邮箱</label>
          <input
            id="email"
            v-model="email"
            type="email"
            autocomplete="email"
            placeholder="name@example.com"
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
          <button class="btn btn-secondary" type="button" :disabled="isLoading" @click="signup">
            注册
          </button>
          <a class="meta-text" href="/" style="text-decoration: none">返回首页</a>
        </div>
        <div id="error" class="auth-error" role="alert" aria-live="polite">{{ error }}</div>
        <div class="auth-meta">
          使用 Supabase Auth（Email/Password）登录。
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { safeNextPath } from '@/shared/routing';
import { supabase } from '@/shared/supabase';

const email = ref('');
const password = ref('');
const error = ref('');
const isLoading = ref(false);

async function login() {
  error.value = '';
  const address = email.value.trim();
  if (!address || !password.value) {
    error.value = '请输入邮箱和密码';
    return;
  }

  isLoading.value = true;
  try {
    const { error: authError } = await supabase.auth.signInWithPassword({
      email: address,
      password: password.value,
    });
    if (authError) throw authError;
    window.location.href = safeNextPath();
  } catch (e: any) {
    error.value = e?.message || '登录失败';
  } finally {
    isLoading.value = false;
  }
}

async function signup() {
  error.value = '';
  const address = email.value.trim();
  if (!address || !password.value) {
    error.value = '请输入邮箱和密码';
    return;
  }

  isLoading.value = true;
  try {
    const { error: authError } = await supabase.auth.signUp({
      email: address,
      password: password.value,
    });
    if (authError) throw authError;
    window.location.href = safeNextPath();
  } catch (e: any) {
    error.value = e?.message || '注册失败';
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
