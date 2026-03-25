<template>
  <div class="page-content">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-800">仪表盘</h1>
      <p class="text-sm text-gray-500 mt-1">DNS 健康检测系统概览</p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500">域名区域</p>
            <p class="text-3xl font-bold text-gray-800 mt-1">{{ stats.zones }}</p>
          </div>
          <div class="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500">DNS 记录</p>
            <p class="text-3xl font-bold text-gray-800 mt-1">{{ stats.records }}</p>
          </div>
          <div class="w-12 h-12 bg-purple-50 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500">检测成功</p>
            <p class="text-3xl font-bold text-green-600 mt-1">{{ stats.success }}</p>
          </div>
          <div class="w-12 h-12 bg-green-50 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500">检测失败</p>
            <p class="text-3xl font-bold text-red-600 mt-1">{{ stats.failed }}</p>
          </div>
          <div class="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-8">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">快速操作</h2>
      <div class="flex flex-wrap gap-3">
        <button @click="syncAll" :disabled="syncing" class="btn btn-primary flex items-center gap-2">
          <svg v-if="!syncing" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <svg v-else class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ syncing ? '同步中...' : '同步所有数据' }}
        </button>
        <button @click="detectAll" :disabled="detecting" class="btn btn-secondary flex items-center gap-2">
          <svg v-if="!detecting" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          <svg v-else class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ detecting ? '检测中...' : '检测所有记录' }}
        </button>
      </div>
    </div>

    <!-- Recent Detection Results -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-100">
        <h2 class="text-lg font-semibold text-gray-800">最近检测结果</h2>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-gray-50">
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">域名</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">类型</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Ping</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">HTTP</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Playwright</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">AI检测</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="record in recentRecords" :key="record.id" class="hover:bg-gray-50">
              <td class="px-6 py-4">
                <span class="font-mono text-sm text-gray-900">{{ record.name }}</span>
              </td>
              <td class="px-6 py-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="getTypeBadge(record.type)">
                  {{ record.type }}
                </span>
              </td>
              <td class="px-6 py-4">
                <span :class="['inline-flex items-center gap-1.5 text-xs', getStatusColor(record.ping_status)]">
                  <span :class="['w-2 h-2 rounded-full', getStatusDot(record.ping_status)]"></span>
                  {{ getStatusText(record.ping_status) }}
                </span>
              </td>
              <td class="px-6 py-4">
                <span :class="['inline-flex items-center gap-1.5 text-xs', getStatusColor(record.curl_status)]">
                  <span :class="['w-2 h-2 rounded-full', getStatusDot(record.curl_status)]"></span>
                  {{ getStatusText(record.curl_status) }}
                </span>
              </td>
              <td class="px-6 py-4">
                <span :class="['inline-flex items-center gap-1.5 text-xs', getStatusColor(record.playwright_status)]">
                  <span :class="['w-2 h-2 rounded-full', getStatusDot(record.playwright_status)]"></span>
                  {{ getStatusText(record.playwright_status) }}
                </span>
              </td>
              <td class="px-6 py-4">
                <span :class="['inline-flex items-center gap-1.5 text-xs', getStatusColor(record.ai_check_status)]">
                  <span :class="['w-2 h-2 rounded-full', getStatusDot(record.ai_check_status)]"></span>
                  {{ getStatusText(record.ai_check_status) }}
                </span>
              </td>
            </tr>
            <tr v-if="recentRecords.length === 0">
              <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                暂无检测数据，请先同步数据并执行检测
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/api'

const toast = useToast()
const stats = ref({ zones: 0, records: 0, success: 0, failed: 0 })
const recentRecords = ref([])
const syncing = ref(false)
const detecting = ref(false)

const fetchStats = async () => {
  try {
    const [zonesRes, recordsRes] = await Promise.all([
      api.get('/zones/'),
      api.get('/records/?page_size=100'),
    ])
    const records = recordsRes.data.items || []
    stats.value.zones = zonesRes.data.length || 0
    stats.value.records = recordsRes.data.total || 0
    stats.value.success = records.filter(r => r.ai_check_status === 'success').length
    stats.value.failed = records.filter(r => r.ai_check_status === 'failed').length
    recentRecords.value = records.slice(0, 10)
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

const syncAll = async () => {
  syncing.value = true
  try {
    const res = await api.post('/sync/all')
    toast.success(`同步完成: ${res.data.synced_zones} 个区域, ${res.data.synced_records} 条记录`)
    fetchStats()
  } catch (error) {
    toast.error('同步失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    syncing.value = false
  }
}

const detectAll = async () => {
  detecting.value = true
  try {
    const res = await api.post('/detect/all')
    toast.success(`已启动检测: ${res.data.total_records} 条记录`)
    setTimeout(fetchStats, 5000)
  } catch (error) {
    toast.error('检测启动失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    detecting.value = false
  }
}

const getStatusDot = (status) => {
  const map = {
    success: 'bg-green-500',
    failed: 'bg-red-500',
    running: 'bg-yellow-500 animate-pulse',
    error: 'bg-red-500',
    pending: 'bg-gray-300'
  }
  return map[status] || 'bg-gray-300'
}

const getStatusText = (status) => {
  const map = {
    success: '成功',
    failed: '失败',
    running: '检测中',
    error: '错误',
    pending: '待检测'
  }
  return map[status] || '未知'
}

const getStatusColor = (status) => {
  const map = {
    success: 'text-green-600',
    failed: 'text-red-600',
    running: 'text-yellow-600',
    error: 'text-red-600',
    pending: 'text-gray-500'
  }
  return map[status] || 'text-gray-500'
}

const getTypeBadge = (type) => {
  const map = {
    A: 'bg-blue-100 text-blue-800',
    CNAME: 'bg-purple-100 text-purple-800',
    MX: 'bg-orange-100 text-orange-800',
    NS: 'bg-teal-100 text-teal-800',
  }
  return map[type] || 'bg-gray-100 text-gray-800'
}

onMounted(() => {
  fetchStats()
  // Auto refresh every 30 seconds
  setInterval(fetchStats, 30000)
})
</script>