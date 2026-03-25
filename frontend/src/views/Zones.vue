<template>
  <div class="page-content">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">域名区域</h1>
        <p class="text-sm text-gray-500 mt-1">共 {{ zones.length }} 个区域</p>
      </div>
      <button @click="refresh" class="btn btn-secondary flex items-center gap-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        刷新
      </button>
    </div>

    <!-- Zones Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="zone in zones" :key="zone.id" class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <h3 class="font-semibold text-gray-800 font-mono">{{ zone.name }}</h3>
            <p class="text-xs text-gray-500 mt-1">ID: {{ zone.zone_id }}</p>
          </div>
          <div class="flex gap-1">
            <button @click="syncZone(zone.zone_id)" class="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors" title="同步记录">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
            <button @click="detectZone(zone.id)" class="p-1.5 text-green-600 hover:bg-green-50 rounded-lg transition-colors" title="检测">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </button>
          </div>
        </div>

        <div class="space-y-3">
          <div class="flex items-center text-sm">
            <span class="text-gray-500 w-20">用途:</span>
            <span class="text-gray-700">{{ zone.purpose || '-' }}</span>
          </div>
          <div class="flex items-center text-sm">
            <span class="text-gray-500 w-20">所属系统:</span>
            <span class="text-gray-700">{{ zone.system || '-' }}</span>
          </div>
          <div class="flex items-center text-sm">
            <span class="text-gray-500 w-20">所属单位:</span>
            <span class="text-gray-700">{{ zone.department || '-' }}</span>
          </div>
          <div class="flex items-center text-sm">
            <span class="text-gray-500 w-20">责任人:</span>
            <span class="text-gray-700">{{ zone.owner_name || '-' }}</span>
          </div>
          <div class="flex items-center text-sm">
            <span class="text-gray-500 w-20">TTL:</span>
            <span class="text-gray-700">{{ zone.default_ttl }}s</span>
          </div>
        </div>

        <div v-if="zone.views" class="mt-4 pt-4 border-t border-gray-100">
          <div class="text-xs text-gray-500 mb-2">Views</div>
          <div class="flex flex-wrap gap-1">
            <span v-for="view in JSON.parse(zone.views)" :key="view" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
              {{ view }}
            </span>
          </div>
        </div>
      </div>

      <div v-if="zones.length === 0" class="col-span-full">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
          <svg class="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-gray-500">暂无区域数据，请先同步数据</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/api'

const toast = useToast()
const zones = ref([])

const fetchZones = async () => {
  try {
    const res = await api.get('/zones/')
    zones.value = res.data
  } catch (error) {
    toast.error('获取区域失败')
  }
}

const syncZone = async (zoneId) => {
  try {
    const res = await api.post(`/sync/records/${zoneId}`)
    toast.success(`同步完成: ${res.data.synced_count} 条记录`)
    fetchZones()
  } catch (error) {
    toast.error('同步失败: ' + (error.response?.data?.detail || error.message))
  }
}

const detectZone = async (zoneId) => {
  try {
    const res = await api.post(`/detect/zone/${zoneId}`)
    toast.success(`已启动检测: ${res.data.records_count} 条记录`)
  } catch (error) {
    toast.error('检测启动失败')
  }
}

const refresh = () => fetchZones()

onMounted(() => fetchZones())
</script>