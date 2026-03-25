<template>
  <div class="page-content">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">用户管理</h1>
        <p class="text-sm text-gray-500 mt-1">系统用户及权限管理</p>
      </div>
      <button @click="showCreate = true" class="btn btn-primary flex items-center gap-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        添加用户
      </button>
    </div>

    <!-- Users Table -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-100">
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">ID</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">用户名</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">邮箱</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">角色</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">状态</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">创建时间</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 text-sm text-gray-500">{{ user.id }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span class="text-sm font-medium text-blue-600">{{ user.username.charAt(0).toUpperCase() }}</span>
                  </div>
                  <span class="font-medium text-gray-900">{{ user.username }}</span>
                </div>
              </td>
              <td class="px-6 py-4 text-sm text-gray-600">{{ user.email || '-' }}</td>
              <td class="px-6 py-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="getRoleBadge(user.role)">
                  {{ getRoleText(user.role) }}
                </span>
              </td>
              <td class="px-6 py-4">
                <span :class="['inline-flex items-center gap-1.5 text-xs', user.is_active ? 'text-green-600' : 'text-red-600']">
                  <span :class="['w-2 h-2 rounded-full', user.is_active ? 'bg-green-500' : 'bg-red-500']"></span>
                  {{ user.is_active ? '激活' : '禁用' }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">{{ formatDate(user.created_at) }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                  <button @click="editUser(user)" class="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors" title="编辑">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button @click="deleteUser(user.id)" class="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors" title="删除">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreate || showEdit" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50 rounded-t-2xl">
          <h2 class="text-lg font-bold text-gray-800">{{ showEdit ? '编辑用户' : '添加用户' }}</h2>
          <button @click="closeModal" class="p-1 hover:bg-gray-200 rounded-lg transition-colors">
            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <form @submit.prevent="saveUser" class="p-6">
          <div class="space-y-4">
            <div>
              <label class="form-label">用户名</label>
              <input v-model="userForm.username" type="text" class="form-input" required :disabled="showEdit" />
            </div>
            <div>
              <label class="form-label">邮箱</label>
              <input v-model="userForm.email" type="email" class="form-input" />
            </div>
            <div>
              <label class="form-label">密码 {{ showEdit ? '(留空不修改)' : '' }}</label>
              <input v-model="userForm.password" type="password" class="form-input" :required="!showEdit" />
            </div>
            <div>
              <label class="form-label">角色</label>
              <select v-model="userForm.role" class="form-input">
                <option value="super_admin">超级管理员</option>
                <option value="admin">管理员</option>
                <option value="operator">操作员</option>
                <option value="viewer">查看者</option>
              </select>
            </div>
            <div>
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="userForm.is_active" type="checkbox" class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500" />
                <span class="text-sm text-gray-700">激活用户</span>
              </label>
            </div>
          </div>
          <div class="mt-6 flex gap-3">
            <button type="submit" class="btn btn-primary flex-1">{{ showEdit ? '保存' : '创建' }}</button>
            <button type="button" @click="closeModal" class="btn btn-secondary flex-1">取消</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/api'

const toast = useToast()
const users = ref([])
const showCreate = ref(false)
const showEdit = ref(false)
const editingId = ref(null)

const userForm = reactive({
  username: '',
  email: '',
  password: '',
  role: 'viewer',
  is_active: true,
})

const fetchUsers = async () => {
  try {
    const res = await api.get('/users/')
    users.value = res.data
  } catch (error) {
    toast.error('获取用户失败')
  }
}

const saveUser = async () => {
  try {
    if (showEdit) {
      await api.put(`/users/${editingId.value}`, userForm)
      toast.success('用户更新成功')
    } else {
      await api.post('/users/', userForm)
      toast.success('用户创建成功')
    }
    closeModal()
    fetchUsers()
  } catch (error) {
    toast.error(error.response?.data?.detail || '操作失败')
  }
}

const editUser = (user) => {
  editingId.value = user.id
  userForm.username = user.username
  userForm.email = user.email
  userForm.password = ''
  userForm.role = user.role
  userForm.is_active = user.is_active
  showEdit.value = true
}

const deleteUser = async (id) => {
  if (!confirm('确定要删除此用户吗?')) return
  try {
    await api.delete(`/users/${id}`)
    toast.success('用户删除成功')
    fetchUsers()
  } catch (error) {
    toast.error(error.response?.data?.detail || '删除失败')
  }
}

const closeModal = () => {
  showCreate.value = false
  showEdit.value = false
  editingId.value = null
  userForm.username = ''
  userForm.email = ''
  userForm.password = ''
  userForm.role = 'viewer'
  userForm.is_active = true
}

const getRoleBadge = (role) => {
  const map = {
    super_admin: 'bg-red-100 text-red-800',
    admin: 'bg-orange-100 text-orange-800',
    operator: 'bg-blue-100 text-blue-800',
    viewer: 'bg-gray-100 text-gray-800',
  }
  return map[role] || 'bg-gray-100 text-gray-800'
}

const getRoleText = (role) => {
  const map = {
    super_admin: '超级管理员',
    admin: '管理员',
    operator: '操作员',
    viewer: '查看者',
  }
  return map[role] || role
}

const formatDate = (date) => date ? new Date(date).toLocaleString() : ''

onMounted(() => fetchUsers())
</script>