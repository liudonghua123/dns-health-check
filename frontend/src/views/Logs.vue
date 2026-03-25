<template>
  <div class="page-content">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">系统日志</h1>
        <p class="text-sm text-gray-500 mt-1">操作审计与系统日志</p>
      </div>
      <button @click="refresh" class="btn btn-secondary flex items-center gap-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        刷新
      </button>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="form-label">操作类型</label>
          <select v-model="filters.action" class="form-input" @change="applyFilters">
            <option value="">全部</option>
            <option value="user_login">用户登录</option>
            <option value="sync_zones">同步区域</option>
            <option value="sync_records">同步记录</option>
            <option value="sync_all">同步所有</option>
            <option value="detect_record">检测记录</option>
            <option value="detect_zone">检测区域</option>
            <option value="detect_all">检测所有</option>
            <option value="user_create">创建用户</option>
            <option value="user_update">更新用户</option>
            <option value="user_delete">删除用户</option>
          </select>
        </div>
        <div>
          <label class="form-label">日志级别</label>
          <select v-model="filters.level" class="form-input" @change="applyFilters">
            <option value="">全部</option>
            <option value="info">信息</option>
            <option value="warning">警告</option>
            <option value="error">错误</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Logs Table -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-100">
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">时间</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">操作</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">级别</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">用户ID</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">详情</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">IP</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="log in logs" :key="log.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 text-sm text-gray-500 whitespace-nowrap">{{ formatDate(log.created_at) }}</td>
              <td class="px-6 py-4">
                <span class="text-sm font-medium text-gray-900">{{ log.action }}</span>
              </td>
              <td class="px-6 py-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="getLevelBadge(log.level)">
                  {{ getLevelText(log.level) }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">{{ log.user_id || '-' }}</td>
              <td class="px-6 py-4 text-sm text-gray-600 max-w-xs truncate" :title="log.details">{{ log.details || '-' }}</td>
              <td class="px-6 py-4 text-sm text-gray-500">{{ log.ip_address || '-' }}</td>
            </tr>
            <tr v-if="logs.length === 0">
              <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                暂无日志数据
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="px-6 py-4 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
        <div class="text-sm text-gray-500">
          第 {{ page }} / {{ totalPages }} 页
        </div>
        <div class="flex gap-2">
          <button @click="changePage(-1)" :disabled="page <= 1" class="btn btn-sm btn-secondary" :class="{'opacity-50 cursor-not-allowed': page <= 1}">
            上一页
          </button>
          <button @click="changePage(1)" :disabled="page >= totalPages" class="btn btn-sm btn-secondary" :class="{'opacity-50 cursor-not-allowed': page >= totalPages}">
            下一页
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/api'

const toast = useToast()
const logs = ref([])
const page = ref(1)
const pageSize = ref(50)
const total = ref(0)
const totalPages = ref(1)

const filters = reactive({
  action: '',
  level: '',
})

const fetchLogs = async () => {
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.action) params.action = filters.action
    if (filters.level) params.level = filters.level

    const res = await api.get('/logs/', { params })
    logs.value = res.data.items
    total.value = res.data.total
    totalPages.value = res.data.total_pages
  } catch (error) {
    toast.error('获取日志失败')
  }
}

const applyFilters = () => {
  page.value = 1
  fetchLogs()
}

const changePage = (delta) => {
  page.value += delta
  fetchLogs()
}

const refresh = () => fetchLogs()

const getLevelBadge = (level) => {
  const map = {
    info: 'bg-blue-100 text-blue-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800',
    debug: 'bg-gray-100 text-gray-800',
  }
  return map[level] || 'bg-gray-100 text-gray-800'
}

const getLevelText = (level) => {
  const map = {
    info: '信息',
    warning: '警告',
    error: '错误',
    debug: '调试',
  }
  return map[level] || level
}

const formatDate = (date) => date ? new Date(date).toLocaleString() : ''

onMounted(() => fetchLogs())
</script>