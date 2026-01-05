<template>
  <div class="admin-page">
      <div class="admin-container">
          <header class="admin-header">
              <div>
                  <h1>Admin Dashboard</h1>
                  <div class="meta-text">User management and system stats</div>
              </div>
              <div class="header-actions">
                  <a href="/" class="btn btn-secondary" style="text-decoration:none;">Home</a>
                  <a href="/video" class="btn btn-secondary" style="text-decoration:none;">Video</a>
                  <a href="/storage" class="btn btn-secondary" style="text-decoration:none;">Storage</a>
              </div>
          </header>

          <!-- Tab Navigation -->
          <div class="admin-tabs">
              <button
                class="admin-tab"
                :class="{ active: activeTab === 'users' }"
                @click="activeTab = 'users'"
              >用户管理</button>
              <button
                class="admin-tab"
                :class="{ active: activeTab === 'targets' }"
                @click="activeTab = 'targets'; loadTargetTypes()"
              >目标类型管理</button>
          </div>

          <!-- Users Tab -->
          <div v-show="activeTab === 'users'">
              <section id="errorBanner" class="card admin-banner" style="display:none;"></section>

              <section class="stats-grid" id="statsGrid">
                  <div class="card stat-card">
                      <div class="stat-label">Total Users</div>
                      <div class="stat-value" id="statTotalUsers">-</div>
                  </div>
                  <div class="card stat-card">
                      <div class="stat-label">Active Users</div>
                      <div class="stat-value" id="statActiveUsers">-</div>
                  </div>
                  <div class="card stat-card">
                      <div class="stat-label">Storage Used</div>
                      <div class="stat-value" id="statStorageUsed">-</div>
                  </div>
                  <div class="card stat-card">
                      <div class="stat-label">Storage Quota</div>
                      <div class="stat-value" id="statStorageQuota">-</div>
                  </div>
                  <div class="card stat-card">
                      <div class="stat-label">Videos</div>
                      <div class="stat-value" id="statVideos">-</div>
                  </div>
                  <div class="card stat-card">
                      <div class="stat-label">Images</div>
                      <div class="stat-value" id="statImages">-</div>
                  </div>
                  <div class="card stat-card">
                      <div class="stat-label">Active Sessions</div>
                      <div class="stat-value" id="statSessions">-</div>
                  </div>
              </section>

              <section class="card">
                  <div class="toolbar">
                      <div class="toolbar-left">
                          <input id="searchInput" type="text" placeholder="Search username or email…" />
                          <select id="filterActive" aria-label="Filter active status">
                              <option value="">All statuses</option>
                              <option value="true">Active</option>
                              <option value="false">Inactive</option>
                          </select>
                          <select id="filterAdmin" aria-label="Filter admin role">
                              <option value="">All roles</option>
                              <option value="true">Admins</option>
                              <option value="false">Non-admin</option>
                          </select>
                      </div>
                      <div class="toolbar-right">
                          <button class="btn btn-secondary" id="refreshBtn" type="button">Refresh</button>
                      </div>
                  </div>

                  <div class="table-wrap">
                      <table class="admin-table" aria-label="User table">
                          <thead>
                              <tr>
                                  <th>Username</th>
                                  <th>Email</th>
                                  <th>Status</th>
                                  <th>Role</th>
                                  <th>Storage</th>
                                  <th>Created</th>
                                  <th>Last Login</th>
                                  <th style="width: 200px;">Actions</th>
                              </tr>
                          </thead>
                          <tbody id="userTbody">
                              <tr>
                                  <td colspan="8" class="meta-text">Loading…</td>
                              </tr>
                          </tbody>
                      </table>
                  </div>

                  <div class="pagination">
                      <button class="btn btn-secondary btn-sm" id="prevPageBtn" type="button">Prev</button>
                      <span class="meta-text" id="pageLabel">Page 1</span>
                      <button class="btn btn-secondary btn-sm" id="nextPageBtn" type="button">Next</button>
                  </div>
              </section>
          </div>

          <!-- Target Types Tab -->
          <div v-show="activeTab === 'targets'" class="targets-tab">
              <section class="card">
                  <div class="toolbar">
                      <div class="toolbar-left">
                          <h2 class="section-title">目标类型列表</h2>
                      </div>
                      <div class="toolbar-right">
                          <button class="btn btn-primary" @click="showAddDialog">
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                  <line x1="12" y1="5" x2="12" y2="19"/>
                                  <line x1="5" y1="12" x2="19" y2="12"/>
                              </svg>
                              添加目标类型
                          </button>
                      </div>
                  </div>

                  <div class="table-wrap">
                      <table class="admin-table" aria-label="Target types table">
                          <thead>
                              <tr>
                                  <th style="width: 100px;">名称</th>
                                  <th style="width: 250px;">占位提示</th>
                                  <th>默认模板</th>
                                  <th style="width: 80px;">排序</th>
                                  <th style="width: 140px;">操作</th>
                              </tr>
                          </thead>
                          <tbody>
                              <tr v-if="loadingTargets">
                                  <td colspan="5" class="meta-text">加载中...</td>
                              </tr>
                              <tr v-else-if="targetTypes.length === 0">
                                  <td colspan="5" class="meta-text">暂无目标类型</td>
                              </tr>
                              <tr v-for="target in targetTypes" :key="target.id">
                                  <td>{{ target.name }}</td>
                                  <td class="text-truncate">{{ target.placeholder || '-' }}</td>
                                  <td class="text-truncate">{{ target.default_template || '-' }}</td>
                                  <td>{{ target.sort_order }}</td>
                                  <td>
                                      <div class="row-actions">
                                          <button class="btn btn-ghost btn-sm" @click="editTarget(target)">编辑</button>
                                          <button class="btn btn-ghost btn-sm btn-danger" @click="confirmDeleteTarget(target)">删除</button>
                                      </div>
                                  </td>
                              </tr>
                          </tbody>
                      </table>
                  </div>
              </section>
          </div>
      </div>

      <!-- User Modal (existing) -->
      <div id="userModal" class="modal hidden" role="dialog" aria-modal="true" aria-labelledby="userModalTitle">
          <div class="modal-backdrop" id="userModalBackdrop"></div>
          <div class="modal-content admin-modal" role="document">
              <div class="modal-header">
                  <h3 id="userModalTitle">User</h3>
                  <button id="userModalClose" class="btn btn-ghost btn-icon" type="button" aria-label="Close">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <line x1="18" y1="6" x2="6" y2="18"></line>
                          <line x1="6" y1="6" x2="18" y2="18"></line>
                      </svg>
                  </button>
              </div>
              <div class="modal-body">
                  <div class="form-grid">
                      <div class="form-group">
                          <label for="editEmail">Email</label>
                          <input id="editEmail" type="email" autocomplete="off" />
                      </div>
                      <div class="form-group">
                          <label for="editQuota">Storage quota (bytes)</label>
                          <input id="editQuota" type="number" min="0" step="1" />
                          <div class="form-hint">Bytes (e.g. 1073741824 for 1 GiB)</div>
                      </div>
                  </div>
                  <div class="checkbox-row">
                      <label class="checkbox-item"><input type="checkbox" id="editActive" /> Active</label>
                      <label class="checkbox-item"><input type="checkbox" id="editAdmin" /> Admin</label>
                  </div>

                  <div class="admin-kv" aria-label="User stats">
                      <div class="card">
                          <div class="kv-label">Storage</div>
                          <div class="kv-value" id="detailStorage">-</div>
                      </div>
                      <div class="card">
                          <div class="kv-label">Videos</div>
                          <div class="kv-value" id="detailVideos">-</div>
                      </div>
                      <div class="card">
                          <div class="kv-label">Images</div>
                          <div class="kv-value" id="detailImages">-</div>
                      </div>
                      <div class="card">
                          <div class="kv-label">Active Sessions</div>
                          <div class="kv-value" id="detailSessions">-</div>
                      </div>
                  </div>

                  <div class="login-attempts">
                      <h2 style="margin-top: 8px;">Recent login attempts</h2>
                      <div class="table-wrap" style="min-width: 0;">
                          <table aria-label="Login attempts table">
                              <thead>
                                  <tr>
                                      <th>Time</th>
                                      <th>Result</th>
                                      <th>Reason</th>
                                      <th>IP</th>
                                  </tr>
                              </thead>
                              <tbody id="loginAttemptTbody">
                                  <tr><td colspan="4" class="meta-text">-</td></tr>
                              </tbody>
                          </table>
                      </div>
                  </div>
              </div>
              <div class="modal-actions">
                  <button id="deleteUserBtn" type="button" class="btn btn-secondary">Delete</button>
                  <div style="flex: 1;"></div>
                  <button id="cancelUserBtn" type="button" class="btn btn-secondary">Cancel</button>
                  <button id="saveUserBtn" type="button" class="btn btn-primary">Save</button>
              </div>
          </div>
      </div>

      <!-- Target Type Modal -->
      <div v-if="showTargetModal" class="modal" role="dialog" aria-modal="true">
          <div class="modal-backdrop" @click="closeTargetModal"></div>
          <div class="modal-content admin-modal" role="document">
              <div class="modal-header">
                  <h3>{{ editingTarget ? '编辑目标类型' : '添加目标类型' }}</h3>
                  <button class="btn btn-ghost btn-icon" type="button" @click="closeTargetModal" aria-label="Close">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <line x1="18" y1="6" x2="6" y2="18"></line>
                          <line x1="6" y1="6" x2="18" y2="18"></line>
                      </svg>
                  </button>
              </div>
              <div class="modal-body">
                  <div class="form-group">
                      <label for="targetName">名称 *</label>
                      <input id="targetName" type="text" v-model="targetForm.name" placeholder="例如：主图、详情页" />
                  </div>
                  <div class="form-group">
                      <label for="targetPlaceholder">占位提示</label>
                      <textarea id="targetPlaceholder" v-model="targetForm.placeholder" rows="2" placeholder="用户选择此类型后显示的输入提示"></textarea>
                  </div>
                  <div class="form-group">
                      <label for="targetTemplate">默认模板</label>
                      <textarea id="targetTemplate" v-model="targetForm.default_template" rows="3" placeholder="选择此类型后自动填充的默认描述文本"></textarea>
                  </div>
                  <div class="form-group">
                      <label for="targetSort">排序</label>
                      <input id="targetSort" type="number" v-model.number="targetForm.sort_order" min="0" placeholder="0" />
                      <div class="form-hint">数字越小排序越靠前</div>
                  </div>
              </div>
              <div class="modal-actions">
                  <div style="flex: 1;"></div>
                  <button type="button" class="btn btn-secondary" @click="closeTargetModal">取消</button>
                  <button type="button" class="btn btn-primary" @click="saveTarget" :disabled="savingTarget">
                      {{ savingTarget ? '保存中...' : '保存' }}
                  </button>
              </div>
          </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <div v-if="showDeleteModal" class="modal" role="dialog" aria-modal="true">
          <div class="modal-backdrop" @click="showDeleteModal = false"></div>
          <div class="modal-content admin-modal" style="max-width: 400px;" role="document">
              <div class="modal-header">
                  <h3>确认删除</h3>
              </div>
              <div class="modal-body">
                  <p>确定要删除目标类型 <strong>{{ targetToDelete?.name }}</strong> 吗？此操作不可恢复。</p>
              </div>
              <div class="modal-actions">
                  <div style="flex: 1;"></div>
                  <button type="button" class="btn btn-secondary" @click="showDeleteModal = false">取消</button>
                  <button type="button" class="btn btn-primary btn-danger" @click="deleteTarget" :disabled="deletingTarget">
                      {{ deletingTarget ? '删除中...' : '确认删除' }}
                  </button>
              </div>
          </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';

// Types
interface TargetType {
  id: string;
  name: string;
  placeholder: string | null;
  default_template: string | null;
  sort_order: number;
}

// State
const activeTab = ref<'users' | 'targets'>('users');
const targetTypes = ref<TargetType[]>([]);
const loadingTargets = ref(false);
const showTargetModal = ref(false);
const showDeleteModal = ref(false);
const editingTarget = ref<TargetType | null>(null);
const targetToDelete = ref<TargetType | null>(null);
const savingTarget = ref(false);
const deletingTarget = ref(false);

const targetForm = reactive({
  name: '',
  placeholder: '',
  default_template: '',
  sort_order: 0
});

function getCsrfToken(): string {
  const match = document.cookie.match(/csrf_token=([^;]+)/);
  return match ? match[1] : '';
}

async function loadTargetTypes() {
  if (loadingTargets.value) return;
  loadingTargets.value = true;

  try {
    const res = await fetch('/api/v1/target-types', {
      credentials: 'include'
    });

    if (!res.ok) {
      throw new Error('Failed to fetch target types');
    }

    const data = await res.json();
    targetTypes.value = data.target_types || [];
  } catch (e) {
    console.error('Failed to load target types:', e);
  } finally {
    loadingTargets.value = false;
  }
}

function showAddDialog() {
  editingTarget.value = null;
  targetForm.name = '';
  targetForm.placeholder = '';
  targetForm.default_template = '';
  targetForm.sort_order = targetTypes.value.length;
  showTargetModal.value = true;
}

function editTarget(target: TargetType) {
  editingTarget.value = target;
  targetForm.name = target.name;
  targetForm.placeholder = target.placeholder || '';
  targetForm.default_template = target.default_template || '';
  targetForm.sort_order = target.sort_order;
  showTargetModal.value = true;
}

function closeTargetModal() {
  showTargetModal.value = false;
  editingTarget.value = null;
}

async function saveTarget() {
  if (!targetForm.name.trim()) {
    alert('请输入目标类型名称');
    return;
  }

  savingTarget.value = true;

  try {
    const payload = {
      name: targetForm.name.trim(),
      placeholder: targetForm.placeholder.trim() || null,
      default_template: targetForm.default_template.trim() || null,
      sort_order: targetForm.sort_order
    };

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-CSRF-Token': getCsrfToken()
    };

    let res: Response;
    if (editingTarget.value) {
      res = await fetch(`/api/v1/target-types/${editingTarget.value.id}`, {
        method: 'PUT',
        credentials: 'include',
        headers,
        body: JSON.stringify(payload)
      });
    } else {
      res = await fetch('/api/v1/target-types', {
        method: 'POST',
        credentials: 'include',
        headers,
        body: JSON.stringify(payload)
      });
    }

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `HTTP ${res.status}`);
    }

    closeTargetModal();
    await loadTargetTypes();
  } catch (e: any) {
    alert('保存失败: ' + (e.message || '未知错误'));
  } finally {
    savingTarget.value = false;
  }
}

function confirmDeleteTarget(target: TargetType) {
  targetToDelete.value = target;
  showDeleteModal.value = true;
}

async function deleteTarget() {
  if (!targetToDelete.value) return;

  deletingTarget.value = true;

  try {
    const res = await fetch(`/api/v1/target-types/${targetToDelete.value.id}`, {
      method: 'DELETE',
      credentials: 'include',
      headers: {
        'X-CSRF-Token': getCsrfToken()
      }
    });

    if (!res.ok && res.status !== 204) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `HTTP ${res.status}`);
    }

    showDeleteModal.value = false;
    targetToDelete.value = null;
    await loadTargetTypes();
  } catch (e: any) {
    alert('删除失败: ' + (e.message || '未知错误'));
  } finally {
    deletingTarget.value = false;
  }
}
</script>

<style>
        .admin-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .admin-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin: 8px 0 20px;
        }

        .admin-header h1 {
            text-align: left;
            margin: 0;
        }

        .admin-header .header-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: flex-end;
        }

        /* Admin Tabs */
        .admin-tabs {
            display: flex;
            gap: 4px;
            margin-bottom: 20px;
            border-bottom: 1px solid rgba(209, 209, 214, 0.65);
            padding-bottom: 0;
        }

        .admin-tab {
            padding: 12px 24px;
            background: transparent;
            border: none;
            border-bottom: 2px solid transparent;
            font-size: 14px;
            font-weight: 500;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s ease;
            margin-bottom: -1px;
        }

        .admin-tab:hover {
            color: var(--text-primary);
            background: rgba(0, 0, 0, 0.02);
        }

        .admin-tab.active {
            color: var(--primary, #0071e3);
            border-bottom-color: var(--primary, #0071e3);
        }

        .section-title {
            font-size: 16px;
            font-weight: 600;
            margin: 0;
        }

        .text-truncate {
            max-width: 250px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .btn-danger {
            color: #b42318 !important;
        }

        .btn-danger:hover {
            background: rgba(255, 59, 48, 0.08) !important;
        }

        .btn.btn-primary.btn-danger {
            background: #dc2626;
            color: white !important;
        }

        .btn.btn-primary.btn-danger:hover {
            background: #b91c1c;
        }

        .admin-banner {
            border: 1px solid rgba(255, 59, 48, 0.25);
            background: rgba(255, 59, 48, 0.06);
            color: #b42318;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin-bottom: 16px;
        }

        .stat-card {
            padding: 16px;
        }

        .stat-label {
            font-size: 12px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .stat-value {
            margin-top: 8px;
            font-size: 22px;
            font-weight: 700;
        }

        .toolbar {
            display: flex;
            gap: 10px;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            margin-bottom: 14px;
        }

        .toolbar-left {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }

        .toolbar input[type="text"] {
            width: 320px;
            max-width: 100%;
        }

        .table-wrap {
            overflow: auto;
            border-radius: var(--radius-md);
            border: 1px solid rgba(209, 209, 214, 0.65);
        }

        table.admin-table {
            width: 100%;
            border-collapse: collapse;
            min-width: 980px;
            background: #fff;
        }

        .admin-table th,
        .admin-table td {
            text-align: left;
            padding: 12px 14px;
            border-bottom: 1px solid rgba(209, 209, 214, 0.55);
            vertical-align: middle;
            font-size: 13px;
        }

        .admin-table th {
            position: sticky;
            top: 0;
            background: rgba(245, 245, 247, 0.95);
            backdrop-filter: blur(6px);
            font-weight: 700;
            z-index: 1;
        }

        .pill {
            display: inline-flex;
            align-items: center;
            padding: 4px 8px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            gap: 6px;
        }

        .pill-green { background: rgba(52, 199, 89, 0.16); color: #0f7a2a; }
        .pill-red { background: rgba(255, 59, 48, 0.12); color: #b42318; }
        .pill-blue { background: rgba(0, 113, 227, 0.12); color: #004e9a; }
        .pill-gray { background: rgba(134, 134, 139, 0.12); color: #4b5563; }

        .row-actions {
            display: flex;
            gap: 8px;
            align-items: center;
        }

        .pagination {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 12px;
        }

        .modal-content.admin-modal {
            max-width: 860px;
        }

        .admin-kv {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin: 12px 0 6px;
        }

        .admin-kv .card {
            padding: 14px;
            margin: 0;
        }

        .admin-kv .kv-label {
            font-size: 12px;
            color: var(--text-secondary);
        }

        .admin-kv .kv-value {
            margin-top: 6px;
            font-weight: 700;
        }

        .login-attempts {
            margin-top: 14px;
        }

        .login-attempts table {
            width: 100%;
            border-collapse: collapse;
        }

        .login-attempts th,
        .login-attempts td {
            padding: 10px 12px;
            border-bottom: 1px solid rgba(209, 209, 214, 0.55);
            font-size: 12px;
            text-align: left;
        }
</style>
