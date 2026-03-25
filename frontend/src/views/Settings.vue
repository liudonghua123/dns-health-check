<template>
  <div class="page-content">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">系统设置</h1>
        <p class="text-sm text-gray-500 mt-1">配置系统参数与检测策略</p>
      </div>
      <div class="flex gap-2">
        <button @click="resetCategory" :disabled="!activeCategory" class="btn btn-secondary flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          重置当前分类
        </button>
        <button @click="saveAll" :disabled="saving" class="btn btn-primary flex items-center gap-2">
          <svg v-if="saving" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span v-else>保存全部</span>
        </button>
      </div>
    </div>

    <!-- Category Tabs -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 mb-6">
      <div class="flex overflow-x-auto border-b border-gray-100">
        <button
          v-for="cat in categories"
          :key="cat.key"
          @click="activeCategory = cat.key"
          class="px-6 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors"
          :class="activeCategory === cat.key
            ? 'border-blue-500 text-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
        >
          <div class="flex items-center gap-2">
            <component :is="cat.icon" class="w-4 h-4" />
            {{ cat.label }}
          </div>
        </button>
      </div>
    </div>

    <!-- Settings Content -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <svg class="w-8 h-8 animate-spin text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <div v-else-if="activeConfigs.length === 0" class="text-center py-12 text-gray-500">
        暂无配置数据
      </div>

      <div v-else class="space-y-6">
        <div v-for="config in activeConfigs" :key="config.id" class="flex flex-col md:flex-row md:items-start gap-4 p-4 bg-gray-50 rounded-lg">
          <div class="flex-1">
            <label class="form-label flex items-center gap-2">
              {{ config.key }}
              <span v-if="config.description" class="text-xs text-gray-400 font-normal">({{ config.description }})</span>
            </label>

            <!-- String input -->
            <input
              v-if="config.value_type === 'string' && !isPasswordField(config.key)"
              v-model="config.value"
              type="text"
              class="form-input"
            />

            <!-- Password input -->
            <div v-else-if="isPasswordField(config.key)" class="relative">
              <input
                v-model="config.value"
                :type="showPasswords[config.key] ? 'text' : 'password'"
                class="form-input pr-10"
              />
              <button
                @click="togglePassword(config.key)"
                class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <svg v-if="showPasswords[config.key]" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
            </div>

            <!-- Boolean toggle -->
            <label v-else-if="config.value_type === 'bool'" class="flex items-center gap-3 cursor-pointer">
              <div class="relative">
                <input
                  type="checkbox"
                  v-model="config.value"
                  true-value="true"
                  false-value="false"
                  class="sr-only peer"
                />
                <div class="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:bg-blue-500 transition-colors"></div>
                <div class="absolute left-0.5 top-0.5 w-5 h-5 bg-white rounded-full shadow peer-checked:translate-x-5 transition-transform"></div>
              </div>
              <span class="text-sm text-gray-600">{{ config.value === 'true' ? '已启用' : '已禁用' }}</span>
            </label>

            <!-- Number input -->
            <input
              v-else-if="config.value_type === 'int'"
              v-model="config.value"
              type="number"
              class="form-input"
            />

            <!-- Textarea for long text -->
            <textarea
              v-else-if="config.key.includes('prompt') || config.key.includes('template')"
              v-model="config.value"
              rows="3"
              class="form-input font-mono text-sm"
            ></textarea>

            <!-- Default input -->
            <input v-else v-model="config.value" type="text" class="form-input" />
          </div>

          <div class="flex items-center gap-2 mt-6 md:mt-0">
            <span class="text-xs px-2 py-1 bg-gray-200 rounded text-gray-600">{{ config.value_type }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { useToast } from 'vue-toastification'
import { configApi } from '@/api'

const toast = useToast()

// Icon components
const SystemIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' })
  ])
}

const AiIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' })
  ])
}

const DetectionIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4' })
  ])
}

const ZdnsIcon = {
  render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M4 6h16M4 10h16M4 14h16M4 18h16' })
  ])
}

const categories = [
  { key: 'system', label: '系统设置', icon: SystemIcon },
  { key: 'ai', label: 'AI 配置', icon: AiIcon },
  { key: 'detection', label: '检测策略', icon: DetectionIcon },
  { key: 'zdns', label: 'ZDNS 配置', icon: ZdnsIcon },
]

const loading = ref(false)
const saving = ref(false)
const activeCategory = ref('system')
const allConfigs = ref([])
const showPasswords = ref({})

const activeConfigs = computed(() => {
  return allConfigs.value
    .filter(cat => cat.category === activeCategory.value)
    .flatMap(cat => cat.configs)
    .filter(c => c.is_visible)
})

const fetchConfigs = async () => {
  loading.value = true
  try {
    const res = await configApi.getAll()
    allConfigs.value = res.data
    console.log('[SETTINGS] Loaded configs:', allConfigs.value)
  } catch (error) {
    toast.error('获取配置失败')
  } finally {
    loading.value = false
  }
}

const saveAll = async () => {
  saving.value = true
  try {
    const configsToUpdate = activeConfigs.value.map(c => {
      const value = c.value_type === 'bool' ? String(c.value) : String(c.value)
      return {
        category: activeCategory.value,
        key: c.key,
        value: value
      }
    })
    console.log('[SETTINGS] Saving configs:', configsToUpdate)
    await configApi.bulkUpdate(configsToUpdate)
    toast.success('配置已保存')
  } catch (error) {
    console.error('[SETTINGS] Save error:', error)
    toast.error('保存失败')
  } finally {
    saving.value = false
  }
}

const resetCategory = async () => {
  if (!activeCategory.value) return
  try {
    await configApi.reset(activeCategory.value)
    toast.success('已重置为默认值')
    await fetchConfigs()
  } catch (error) {
    toast.error('重置失败')
  }
}

const isPasswordField = (key) => {
  return key.toLowerCase().includes('password') ||
         key.toLowerCase().includes('secret') ||
         key.toLowerCase().includes('api_key')
}

const togglePassword = (key) => {
  showPasswords.value[key] = !showPasswords.value[key]
}

onMounted(() => fetchConfigs())
</script>