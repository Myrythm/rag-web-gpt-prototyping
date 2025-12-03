<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <div>
        <h2 class="text-3xl font-bold text-white mb-2">User Management</h2>
        <p class="text-gray-400">Manage system users and permissions</p>
      </div>
      <button 
        @click="openAddModal"
        class="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-6 py-3 rounded-xl font-semibold transition-all shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 flex items-center gap-2"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path d="M8 9a3 3 0 100-6 3 3 0 000 6zM8 11a6 6 0 016 6H2a6 6 0 016-6zM16 7a1 1 0 10-2 0v1h-1a1 1 0 100 2h1v1a1 1 0 102 0v-1h1a1 1 0 100-2h-1V7z" />
        </svg>
        Add User
      </button>
    </div>
    
    <div class="bg-gray-800/50 backdrop-blur-xl border border-gray-700/50 p-8 rounded-2xl">
      <!-- Search and Filter -->
      <div class="flex flex-col sm:flex-row gap-4 mb-6">
        <div class="relative flex-1">
          <input 
            v-model="searchQuery"
            @input="handleSearch"
            type="text" 
            placeholder="Search users..." 
            class="w-full bg-gray-900/50 border border-gray-700/50 text-white pl-10 pr-4 py-2.5 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all placeholder-gray-500"
          >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-500 absolute left-3 top-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <div class="w-full sm:w-48">
          <select 
            v-model="roleFilter"
            @change="handleFilter"
            class="w-full bg-gray-900/50 border border-gray-700/50 text-white px-4 py-2.5 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all cursor-pointer"
          >
            <option value="">All Roles</option>
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-700/50">
              <th class="p-4 text-left font-semibold text-gray-300 text-sm">User</th>
              <th class="p-4 text-left font-semibold text-gray-300 text-sm">Role</th>
              <th class="p-4 text-left font-semibold text-gray-300 text-sm">Created</th>
              <th class="p-4 text-right font-semibold text-gray-300 text-sm">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="user in users"
              :key="user.id"
              class="border-b border-gray-700/30 hover:bg-gray-700/20 transition-colors"
            >
              <td class="p-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold shadow-lg">
                    {{ user.username.charAt(0).toUpperCase() }}
                  </div>
                  <span class="text-gray-200 font-medium">{{ user.username }}</span>
                </div>
              </td>
              <td class="p-4">
                <span
                  :class="{
                    'bg-blue-500/20 text-blue-300 border-blue-500/50': user.role === 'user',
                    'bg-purple-500/20 text-purple-300 border-purple-500/50': user.role === 'admin',
                  }"
                  class="px-3 py-1.5 rounded-lg text-xs font-semibold uppercase border"
                >
                  {{ user.role }}
                </span>
              </td>
              <td class="p-4 text-gray-400 text-sm">
                {{ new Date(user.created_at).toLocaleDateString() }}
              </td>
              <td class="p-4">
                <div class="flex items-center justify-end gap-2">
                  <button
                    @click="openEditModal(user)"
                    class="px-4 py-2 text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 rounded-lg font-medium transition-all"
                  >
                    Edit
                  </button>
                  <button
                    @click="deleteUser(user.id)"
                    class="px-4 py-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg font-medium transition-all"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="loading">
              <td colspan="4" class="p-8 text-center text-gray-500">
                <div class="flex flex-col items-center justify-center gap-2">
                  <svg class="animate-spin h-8 w-8 text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <p>Loading users...</p>
                </div>
              </td>
            </tr>
            <tr v-else-if="users.length === 0">
              <td colspan="4" class="p-8 text-center text-gray-500">
                <p>No users found.</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <Pagination
        v-if="total > 0"
        :current-page="currentPage"
        :total="total"
        :limit="limit"
        @change="(page) => emit('page-change', page)"
      />
    </div>

    <!-- Add/Edit User Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-gray-800/90 backdrop-blur-xl border border-gray-700/50 p-8 rounded-2xl shadow-2xl w-full max-w-md">
        <div class="flex items-center gap-3 mb-6">
          <div class="p-3 bg-blue-500/10 rounded-xl">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path d="M8 9a3 3 0 100-6 3 3 0 000 6zM8 11a6 6 0 016 6H2a6 6 0 016-6zM16 7a1 1 0 10-2 0v1h-1a1 1 0 100 2h1v1a1 1 0 102 0v-1h1a1 1 0 100-2h-1V7z" />
            </svg>
          </div>
          <h3 class="text-2xl font-bold text-white">{{ editingUser ? 'Edit User' : 'Add New User' }}</h3>
        </div>

        <form @submit.prevent="saveUser" class="space-y-5">
          <div>
            <label class="block text-gray-300 text-sm font-semibold mb-2">Username</label>
            <input 
              v-model="formData.username" 
              type="text" 
              class="w-full border border-gray-600/50 bg-gray-900/50 text-white placeholder-gray-500 p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all backdrop-blur-sm"
              placeholder="Enter username"
              required
            >
          </div>
          
          <div>
            <label class="block text-gray-300 text-sm font-semibold mb-2">
              Password {{ editingUser ? '(leave blank to keep current)' : '' }}
            </label>
            <input 
              v-model="formData.password" 
              type="password" 
              class="w-full border border-gray-600/50 bg-gray-900/50 text-white placeholder-gray-500 p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all backdrop-blur-sm"
              placeholder="Enter password"
              :required="!editingUser"
            >
          </div>
          
          <div>
            <label class="block text-gray-300 text-sm font-semibold mb-2">Role</label>
            <select 
              v-model="formData.role" 
              class="w-full border border-gray-600/50 bg-gray-900/50 text-white p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all backdrop-blur-sm"
            >
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          
          <div class="flex gap-3 pt-4">
            <button 
              type="button" 
              @click="closeModal"
              class="flex-1 px-4 py-3 text-gray-300 hover:text-white hover:bg-gray-700/50 rounded-xl font-medium transition-all border border-gray-700/50"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              :disabled="isSubmitting"
              class="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-4 py-3 rounded-xl font-semibold transition-all shadow-lg shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <svg v-if="isSubmitting" class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isSubmitting ? 'Saving...' : (editingUser ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from "vue";
import api from "@/utils/api";
import Pagination from "@/components/common/Pagination.vue";

const props = defineProps({
  users: {
    type: Array,
    required: true
  },
  total: {
    type: Number,
    required: true
  },
  currentPage: {
    type: Number,
    required: true
  },
  limit: {
    type: Number,
    default: 20
  },
  loading: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['refresh', 'reset', 'page-change', 'search', 'filter']);

const users = computed(() => props.users);
const showModal = ref(false);
const editingUser = ref(null);
const isSubmitting = ref(false);
const searchQuery = ref("");
const roleFilter = ref("");
let searchTimeout = null;

const handleSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    emit('search', searchQuery.value);
  }, 300);
};

const handleFilter = () => {
  emit('filter', roleFilter.value);
};

const formData = ref({
  username: "",
  password: "",
  role: "user"
});

const openAddModal = () => {
  editingUser.value = null;
  formData.value = { username: "", password: "", role: "user" };
  showModal.value = true;
};

const openEditModal = (user) => {
  editingUser.value = user;
  formData.value = {
    username: user.username,
    password: "",
    role: user.role
  };
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  editingUser.value = null;
  formData.value = { username: "", password: "", role: "user" };
};

const saveUser = async () => {
  isSubmitting.value = true;
  try {
    if (editingUser.value) {
      await api.put(`/admin/users/${editingUser.value.id}`, formData.value);
      emit('refresh'); // Stay on current page for edit
    } else {
      await api.post("/admin/users", formData.value);
      emit('reset'); // Go to page 1 for new user
    }
    closeModal();
  } catch (e) {
    alert(e.response?.data?.detail || `Error ${editingUser.value ? 'updating' : 'creating'} user`);
  } finally {
    isSubmitting.value = false;
  }
};

const deleteUser = async (id) => {
  if (!confirm("Are you sure you want to delete this user? This action cannot be undone.")) return;
  try {
    await api.delete(`/admin/users/${id}`);
    emit('refresh'); // Tell parent to refresh data
  } catch (e) {
    alert(e.response?.data?.detail || "Error deleting user");
  }
};
</script>
