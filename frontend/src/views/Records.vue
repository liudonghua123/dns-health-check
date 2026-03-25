<template>
  <div class="page-content">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">DNS 记录管理</h1>
        <p class="text-sm text-gray-500 mt-1">共 {{ total }} 条记录</p>
      </div>
      <div class="flex gap-2">
        <!-- Column Settings Button -->
        <div class="relative">
          <button @click="showColumnSettings = !showColumnSettings" class="btn btn-secondary flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            列设置
          </button>
          <!-- Column Settings Dropdown -->
          <div v-if="showColumnSettings" class="absolute right-0 mt-2 w-72 bg-white rounded-xl shadow-xl border border-gray-200 z-50">
            <div class="p-3 border-b border-gray-100">
              <div class="flex items-center justify-between">
                <span class="font-semibold text-gray-700">列设置</span>
                <button @click="showColumnSettings = false" class="text-gray-400 hover:text-gray-600">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <div class="p-3 max-h-80 overflow-y-auto">
              <p class="text-xs text-gray-500 mb-2">拖拽排序，点击切换显示/隐藏</p>
              <draggable v-model="columnConfig" item-key="key" class="space-y-1">
                <template #item="{ element }">
                  <div @click="toggleColumn(element.key)" class="flex items-center gap-2 px-2 py-2 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                    <svg class="w-4 h-4 text-gray-400 cursor-move" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                    </svg>
                    <div class="w-5 h-5 rounded border flex items-center justify-center" :class="element.visible ? 'bg-blue-500 border-blue-500' : 'border-gray-300'">
                      <svg v-if="element.visible" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <span class="text-sm" :class="element.visible ? 'text-gray-700' : 'text-gray-400'">{{ element.label }}</span>
                  </div>
                </template>
              </draggable>
            </div>
            <div class="p-3 border-t border-gray-100 flex gap-2">
              <button @click="resetColumns" class="flex-1 btn btn-sm btn-secondary">重置</button>
              <button @click="saveColumns" class="flex-1 btn btn-sm btn-primary">保存</button>
            </div>
          </div>
        </div>
        <button @click="refresh" class="btn btn-secondary flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          刷新
        </button>
      </div>
    </div>

    <!-- Filters Card -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 mb-6 overflow-hidden">
      <div class="p-4 bg-gray-50 border-b border-gray-100 flex items-center justify-between">
        <h3 class="font-semibold text-gray-700 flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          筛选条件
        </h3>
        <button @click="showFilters = !showFilters" class="text-gray-500 hover:text-gray-700">
          <svg class="w-5 h-5 transition-transform" :class="{'rotate-180': showFilters}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>
      <div v-show="showFilters" class="p-4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label class="form-label">搜索域名/IP</label>
            <input v-model="filters.search" type="text" class="form-input" placeholder="模糊搜索..." />
          </div>
          <div>
            <label class="form-label">记录类型</label>
            <select v-model="filters.type" class="form-input">
              <option value="">全部类型</option>
              <option value="A">A 记录</option>
              <option value="CNAME">CNAME</option>
              <option value="MX">MX 记录</option>
              <option value="NS">NS 记录</option>
            </select>
          </div>
          <div>
            <label class="form-label">所属区域</label>
            <select v-model="filters.zone_id" class="form-input">
              <option value="">全部区域</option>
              <option v-for="zone in zones" :key="zone.id" :value="zone.id">{{ zone.name }}</option>
            </select>
          </div>
          <div>
            <label class="form-label">检测状态</label>
            <select v-model="filters.ai_check_status" class="form-input">
              <option value="">全部状态</option>
              <option value="success">检测成功</option>
              <option value="failed">检测失败</option>
              <option value="running">检测中</option>
              <option value="pending">待检测</option>
            </select>
          </div>
          <div>
            <label class="form-label">域名用途</label>
            <input v-model="filters.purpose" type="text" class="form-input" placeholder="用途..." />
          </div>
          <div>
            <label class="form-label">所属系统</label>
            <input v-model="filters.system" type="text" class="form-input" placeholder="系统..." />
          </div>
          <div>
            <label class="form-label">所属单位</label>
            <input v-model="filters.department" type="text" class="form-input" placeholder="单位..." />
          </div>
          <div>
            <label class="form-label">责任人</label>
            <input v-model="filters.owner_name" type="text" class="form-input" placeholder="责任人..." />
          </div>
        </div>
        <div class="mt-4 flex gap-2">
          <button @click="applyFilters" class="btn btn-primary">应用筛选</button>
          <button @click="clearFilters" class="btn btn-secondary">重置</button>
        </div>
      </div>
    </div>

    <!-- Records Table -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-100">
              <th v-for="col in visibleColumns" :key="col.key" class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                {{ col.label }}
              </th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="record in records" :key="record.id" class="hover:bg-gray-50 transition-colors">
              <td v-for="col in visibleColumns" :key="col.key" class="px-4 py-3" :class="col.class">
                <template v-if="col.key === 'name'">
                  <div class="font-mono text-sm text-gray-900">{{ record.name }}</div>
                </template>
                <template v-else-if="col.key === 'type'">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="getTypeBadge(record.type)">
                    {{ record.type }}
                  </span>
                </template>
                <template v-else-if="col.key === 'rdata'">
                  <span class="font-mono text-sm text-gray-600">{{ record.rdata }}</span>
                </template>
                <template v-else-if="col.key === 'zone'">
                  <span class="text-sm text-gray-600">{{ record.zone_name || '-' }}</span>
                </template>
                <template v-else-if="col.key === 'purpose'">
                  <span class="text-sm text-gray-600">{{ record.purpose || '-' }}</span>
                </template>
                <template v-else-if="col.key === 'system'">
                  <span class="text-sm text-gray-600">{{ record.system || '-' }}</span>
                </template>
                <template v-else-if="col.key === 'department'">
                  <span class="text-sm text-gray-600">{{ record.department || '-' }}</span>
                </template>
                <template v-else-if="col.key === 'owner_name'">
                  <span class="text-sm text-gray-600">{{ record.owner_name || '-' }}</span>
                </template>
                <template v-else-if="col.key === 'owner_id'">
                  <span class="text-sm text-gray-600">{{ record.owner_id || '-' }}</span>
                </template>
                <template v-else-if="col.key === 'ping_status'">
                  <div class="flex items-center gap-1">
                    <span :class="['w-2 h-2 rounded-full', getStatusDot(record.ping_status)]"></span>
                    <span class="text-xs text-gray-500">{{ getStatusText(record.ping_status) }}</span>
                  </div>
                </template>
                <template v-else-if="col.key === 'curl_status'">
                  <div class="flex items-center gap-1">
                    <span :class="['w-2 h-2 rounded-full', getStatusDot(record.curl_status)]"></span>
                    <span class="text-xs text-gray-500">{{ getStatusText(record.curl_status) }}</span>
                  </div>
                </template>
                <template v-else-if="col.key === 'ai_check_status'">
                  <div class="flex items-center gap-1">
                    <span :class="['w-2 h-2 rounded-full', getStatusDot(record.ai_check_status)]"></span>
                    <span class="text-xs text-gray-500">{{ getStatusText(record.ai_check_status) }}</span>
                  </div>
                </template>
                <template v-else-if="col.key === 'playwright_status'">
                  <div class="flex items-center gap-1">
                    <span :class="['w-2 h-2 rounded-full', getStatusDot(record.playwright_status)]"></span>
                    <span class="text-xs text-gray-500">{{ getStatusText(record.playwright_status) }}</span>
                  </div>
                </template>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <button @click="detectRecord(record.id)" class="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors" title="检测">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                  </button>
                  <button @click="viewDetail(record)" class="p-1.5 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors" title="详情">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="px-4 py-3 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
        <div class="text-sm text-gray-500">
          第 {{ page }} / {{ totalPages }} 页，每页 {{ pageSize }} 条
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

    <!-- Detail Modal -->
    <div v-if="showDetail" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50">
          <h2 class="text-xl font-bold text-gray-800">记录详情</h2>
          <button @click="showDetail = false" class="p-1 hover:bg-gray-200 rounded-lg transition-colors">
            <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          <!-- Basic Info -->
          <div class="mb-6">
            <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">基本信息</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="text-xs text-gray-500 mb-1">域名</div>
                <div class="font-mono text-sm text-gray-900">{{ currentRecord?.name }}</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="text-xs text-gray-500 mb-1">类型</div>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="getTypeBadge(currentRecord?.type)">
                  {{ currentRecord?.type }}
                </span>
              </div>
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="text-xs text-gray-500 mb-1">解析值</div>
                <div class="font-mono text-sm text-gray-900">{{ currentRecord?.rdata }}</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="text-xs text-gray-500 mb-1">TTL</div>
                <div class="text-sm text-gray-900">{{ currentRecord?.ttl }}</div>
              </div>
            </div>
          </div>

          <!-- Custom Fields -->
          <div class="mb-6">
            <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">自定义字段</h3>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="text-xs text-gray-500 mb-1">域名用途</div>
                <div class="text-sm text-gray-900">{{ currentRecord?.purpose || '-' }}</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="text-xs text-gray-500 mb-1">所属系统</div>
                <div class="text-sm text-gray-900">{{ currentRecord?.system || '-' }}</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="text-xs text-gray-500 mb-1">所属单位</div>
                <div class="text-sm text-gray-900">{{ currentRecord?.department || '-' }}</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="text-xs text-gray-500 mb-1">责任人</div>
                <div class="text-sm text-gray-900">{{ currentRecord?.owner_name || '-' }}</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="text-xs text-gray-500 mb-1">责任人ID</div>
                <div class="text-sm text-gray-900">{{ currentRecord?.owner_id || '-' }}</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="text-xs text-gray-500 mb-1">备注</div>
                <div class="text-sm text-gray-900">{{ currentRecord?.remark || '-' }}</div>
              </div>
            </div>
          </div>

          <!-- Detection Status -->
          <div class="mb-6">
            <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">检测状态</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="bg-gray-50 rounded-lg p-4">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-gray-700">Ping 检测</span>
                  <span :class="['w-2 h-2 rounded-full', getStatusDot(currentRecord?.ping_status)]"></span>
                </div>
                <div class="text-xs text-gray-500">{{ getStatusText(currentRecord?.ping_status) }}</div>
                <div v-if="currentRecord?.ping_result" class="mt-2 text-xs text-gray-600 font-mono bg-gray-100 p-2 rounded truncate">{{ currentRecord?.ping_result }}</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-4">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-gray-700">HTTP 检测</span>
                  <span :class="['w-2 h-2 rounded-full', getStatusDot(currentRecord?.curl_status)]"></span>
                </div>
                <div class="text-xs text-gray-500">{{ getStatusText(currentRecord?.curl_status) }}</div>
                <div v-if="currentRecord?.curl_result" class="mt-2 text-xs text-gray-600 font-mono bg-gray-100 p-2 rounded truncate">{{ currentRecord?.curl_result }}</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-4">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-gray-700">AI 检测</span>
                  <span :class="['w-2 h-2 rounded-full', getStatusDot(currentRecord?.ai_check_status)]"></span>
                </div>
                <div class="text-xs text-gray-500">{{ getStatusText(currentRecord?.ai_check_status) }}</div>
                <div v-if="currentRecord?.ai_check_result" class="mt-2 text-xs text-gray-600 bg-gray-100 p-2 rounded">{{ currentRecord?.ai_check_result }}</div>
              </div>
            </div>
          </div>

          <!-- Screenshot -->
          <div v-if="currentRecord?.playwright_screenshot">
            <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">网站截图</h3>
            <div class="border border-gray-200 rounded-lg overflow-hidden">
              <img :src="'data:image/png;base64,' + currentRecord.playwright_screenshot" class="w-full" />
            </div>
            <button
              @click="downloadScreenshot(currentRecord)"
              class="mt-2 text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              下载截图
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { useToast } from 'vue-toastification'
import draggable from 'vuedraggable'
import api from '@/api'

const toast = useToast()
const records = ref([])
const zones = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const totalPages = ref(1)
const loading = ref(false)
const showDetail = ref(false)
const showFilters = ref(false)
const showColumnSettings = ref(false)
const currentRecord = ref(null)

// Column configuration
const defaultColumns = [
  { key: 'name', label: '域名', visible: true, class: '' },
  { key: 'type', label: '类型', visible: true, class: '' },
  { key: 'rdata', label: '解析值', visible: true, class: '' },
  { key: 'zone', label: '区域', visible: true, class: '' },
  { key: 'purpose', label: '域名用途', visible: false, class: '' },
  { key: 'system', label: '所属系统', visible: false, class: '' },
  { key: 'department', label: '所属单位', visible: false, class: '' },
  { key: 'owner_name', label: '责任人', visible: false, class: '' },
  { key: 'owner_id', label: '责任人ID', visible: false, class: '' },
  { key: 'ping_status', label: 'Ping', visible: true, class: '' },
  { key: 'curl_status', label: 'HTTP', visible: true, class: '' },
  { key: 'ai_check_status', label: 'AI检测', visible: true, class: '' },
  { key: 'playwright_status', label: '截图', visible: false, class: '' },
]

const columnConfig = ref([...defaultColumns])

const visibleColumns = computed(() => columnConfig.value.filter(col => col.visible))

const filters = reactive({
  search: '',
  type: '',
  zone_id: '',
  ai_check_status: '',
  purpose: '',
  system: '',
  department: '',
  owner_name: '',
})

// Load column settings from localStorage
const loadColumnSettings = () => {
  const saved = localStorage.getItem('records_column_settings')
  if (saved) {
    try {
      const savedConfig = JSON.parse(saved)
      // Merge with default to handle new columns
      columnConfig.value = defaultColumns.map(col => {
        const savedCol = savedConfig.find(s => s.key === col.key)
        return savedCol ? { ...col, visible: savedCol.visible } : col
      })
      // Reorder based on saved config
      columnConfig.value.sort((a, b) => {
        const aIdx = savedConfig.findIndex(s => s.key === a.key)
        const bIdx = savedConfig.findIndex(s => s.key === b.key)
        return aIdx - bIdx
      })
    } catch (e) {
      console.error('Failed to load column settings:', e)
    }
  }
}

const toggleColumn = (key) => {
  const col = columnConfig.value.find(c => c.key === key)
  if (col) {
    col.visible = !col.visible
  }
}

const saveColumns = () => {
  localStorage.setItem('records_column_settings', JSON.stringify(columnConfig.value))
  showColumnSettings.value = false
  toast.success('列设置已保存')
}

const resetColumns = () => {
  columnConfig.value = [...defaultColumns]
  localStorage.removeItem('records_column_settings')
  toast.info('列设置已重置')
}

// Close column settings when clicking outside
const closeColumnSettings = (e) => {
  if (showColumnSettings.value && !e.target.closest('.relative')) {
    showColumnSettings.value = false
  }
}

watch(showColumnSettings, (val) => {
  if (val) {
    document.addEventListener('click', closeColumnSettings)
  } else {
    document.removeEventListener('click', closeColumnSettings)
  }
})

const fetchRecords = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.search) params.search = filters.search
    if (filters.type) params.type = filters.type
    if (filters.zone_id) params.zone_id = filters.zone_id
    if (filters.ai_check_status) params.ai_check_status = filters.ai_check_status
    if (filters.purpose) params.purpose = filters.purpose
    if (filters.system) params.system = filters.system
    if (filters.department) params.department = filters.department
    if (filters.owner_name) params.owner_name = filters.owner_name

    const res = await api.get('/records/', { params })
    records.value = res.data.items
    total.value = res.data.total
    totalPages.value = res.data.total_pages
  } catch (error) {
    toast.error('获取记录失败')
  } finally {
    loading.value = false
  }
}

const fetchZones = async () => {
  try {
    const res = await api.get('/zones/')
    zones.value = res.data
  } catch (error) {
    console.error('Failed to fetch zones:', error)
  }
}

const applyFilters = () => {
  page.value = 1
  fetchRecords()
}

const clearFilters = () => {
  Object.keys(filters).forEach(key => filters[key] = '')
  page.value = 1
  fetchRecords()
}

const changePage = (delta) => {
  page.value += delta
  fetchRecords()
}

const refresh = () => fetchRecords()

const detectRecord = async (id) => {
  try {
    await api.post(`/detect/record/${id}`)
    toast.success('已启动检测')
    setTimeout(fetchRecords, 3000)
  } catch (error) {
    toast.error('检测启动失败')
  }
}

const viewDetail = (record) => {
  currentRecord.value = record
  showDetail.value = true
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

const getTypeBadge = (type) => {
  const map = {
    A: 'bg-blue-100 text-blue-800',
    CNAME: 'bg-purple-100 text-purple-800',
    MX: 'bg-orange-100 text-orange-800',
    NS: 'bg-teal-100 text-teal-800',
    TXT: 'bg-gray-100 text-gray-800',
  }
  return map[type] || 'bg-gray-100 text-gray-800'
}

const downloadScreenshot = (record) => {
  if (!record.playwright_screenshot) return
  const link = document.createElement('a')
  link.href = 'data:image/png;base64,' + record.playwright_screenshot
  link.download = `${record.name}_${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.png`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

onMounted(() => {
  loadColumnSettings()
  fetchRecords()
  fetchZones()
})
</script>