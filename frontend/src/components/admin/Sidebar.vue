<template>
  <div class="w-full md:w-72 bg-gray-900/50 backdrop-blur-xl border-r border-gray-700/50 text-white h-screen p-4 md:p-6 flex flex-col">
    <!-- Header -->
    <div class="mb-6 md:mb-8">
      <!-- Close button for mobile -->
      <div class="flex justify-between items-center mb-4 md:hidden">
        <h3 class="text-lg font-bold text-white">Menu</h3>
        <button 
          @click="$emit('close')"
          class="p-2 hover:bg-gray-700/50 rounded-lg transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="flex items-center gap-3 mb-2">
        <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold shadow-lg">
          {{ userStore.user?.username?.charAt(0).toUpperCase() || 'A' }}
        </div>
        <div>
          <h2 class="text-lg md:text-xl font-bold capitalize">{{ userStore.user?.username || 'Admin' }}</h2>
          <p class="text-xs text-gray-400">{{ userStore.user?.role || 'Administrator' }}</p>
        </div>
      </div>
      <p class="text-xs md:text-sm text-gray-500">RAGWeb Management</p>
    </div>

    <!-- Navigation -->
    <ul class="flex-1 space-y-2">
      <li
        v-for="item in items"
        :key="item.id"
        class="p-3 cursor-pointer rounded-xl transition-all duration-200 group"
        :class="currentTab === item.id 
          ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/20' 
          : 'hover:bg-gray-800/50 text-gray-300'"
        @click="$emit('change-tab', item.id)"
      >
        <div class="flex items-center gap-3">
          <component :is="item.icon" class="h-5 w-5" />
          <span class="font-medium">{{ item.label }}</span>
        </div>
      </li>
    </ul>

    <!-- Logout -->
    <button
      @click="logout"
      class="mt-4 flex items-center gap-3 text-gray-400 hover:text-red-400 transition-colors p-3 rounded-xl hover:bg-gray-800/50 w-full"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clip-rule="evenodd" />
      </svg>
      <span class="font-medium">Logout</span>
    </button>
  </div>
</template>

<script setup>
import { h } from 'vue';
import { useUserStore } from "@/stores/user";

defineProps(["currentTab"]);
defineEmits(["change-tab"]);

const OverviewIcon = () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 20 20', fill: 'currentColor' }, [
  h('path', { d: 'M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z' })
]);

const DocumentsIcon = () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 20 20', fill: 'currentColor' }, [
  h('path', { 'fill-rule': 'evenodd', d: 'M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z', 'clip-rule': 'evenodd' })
]);

const UsersIcon = () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 20 20', fill: 'currentColor' }, [
  h('path', { d: 'M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z' })
]);

const items = [
  { id: "overview", label: "Dashboard", icon: OverviewIcon },
  { id: "documents", label: "Documents", icon: DocumentsIcon },
  { id: "users", label: "Users", icon: UsersIcon },
];

const userStore = useUserStore();
const logout = () => userStore.logout();
</script>
