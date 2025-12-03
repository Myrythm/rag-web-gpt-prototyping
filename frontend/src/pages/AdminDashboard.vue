<template>
  <div class="flex h-screen bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800 font-sans overflow-hidden">
    <!-- Sidebar -->
    <div 
      class="bg-gray-900/50 backdrop-blur-xl border-r border-gray-700/50 text-white w-72 flex-shrink-0 flex flex-col transition-all duration-300 absolute md:relative h-full z-50"
      :class="{ '-ml-72': !showSidebar }"
    >
      <Sidebar :currentTab="currentTab" @change-tab="handleTabChange" @close="showSidebar = false" />
    </div>

    <!-- Overlay for mobile -->
    <div 
      v-if="showSidebar && isMobile"
      @click="showSidebar = false"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 md:hidden"
    ></div>
    
    <!-- Main Content -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Mobile Header -->
      <div class="md:hidden bg-gray-800/50 backdrop-blur-xl border-b border-gray-700/50 px-4 py-3 flex items-center justify-between">
        <button 
          @click="showSidebar = !showSidebar"
          class="p-2 rounded-lg hover:bg-gray-700/50 text-gray-300 hover:text-white"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <h1 class="text-lg font-bold text-white">{{ getPageTitle() }}</h1>
        <div class="w-10"></div> <!-- Spacer -->
      </div>



      <!-- Content -->
      <div class="flex-1 p-4 md:p-8 overflow-y-auto">
        <OverviewSection v-if="currentTab === 'overview'" :stats="stats" />
        <DocumentsSection 
          v-if="currentTab === 'documents'" 
          :documents="documents" 
          :total="docsTotal"
          :current-page="docsPage"
          :limit="docsLimit"
          :loading="loading"
          @refresh="fetchDocuments(docsPage)" 
          @page-change="fetchDocuments"
          @search="handleDocsSearch"
        />
        <UsersSection 
          v-if="currentTab === 'users'" 
          :users="users" 
          :total="usersTotal"
          :current-page="usersPage"
          :limit="usersLimit"
          :loading="loading"
          @refresh="fetchUsers(usersPage)" 
          @reset="fetchUsers(1)"
          @page-change="fetchUsers"
          @search="handleUsersSearch"
          @filter="handleUsersFilter"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from "vue";
import api from "@/utils/api";
import Sidebar from "@/components/admin/Sidebar.vue";
import OverviewSection from "@/components/admin/OverviewSection.vue";
import DocumentsSection from "@/components/admin/DocumentsSection.vue";
import UsersSection from "@/components/admin/UsersSection.vue";

const currentTab = ref("overview");
// const initialLoading = ref(true); // Removed for instant load
const showSidebar = ref(false);
const windowWidth = ref(window.innerWidth);

const isMobile = computed(() => windowWidth.value < 768);

// Centralized data
const stats = ref({ total_documents: 0, total_chunks: 0, total_users: 0 });
const documents = ref([]);
const users = ref([]);

// Pagination state
const docsPage = ref(1);
const docsTotal = ref(0);
const docsLimit = ref(10);
const docsSearch = ref("");

const usersPage = ref(1);
const usersTotal = ref(0);
const usersLimit = ref(10);
const usersSearch = ref("");
const usersRoleFilter = ref("");

const loading = ref(false);

// Handle window resize
const handleResize = () => {
  windowWidth.value = window.innerWidth;
  showSidebar.value = !isMobile.value;
};

const fetchStats = async () => {
  try {
    const res = await api.get("/admin/stats");
    stats.value = res.data;
  } catch (e) {
    console.error("Error fetching stats:", e);
  }
};

const fetchDocuments = async (page = 1) => {
  loading.value = true;
  try {
    const res = await api.get("/admin/documents", { 
      params: { 
        page, 
        limit: docsLimit.value,
        search: docsSearch.value
      } 
    });
    documents.value = res.data.items;
    docsTotal.value = res.data.total;
    docsPage.value = res.data.page;
    // Update stats count
    stats.value.total_documents = res.data.total;
  } catch (e) {
    console.error("Error fetching documents:", e);
  } finally {
    loading.value = false;
  }
};

const fetchUsers = async (page = 1) => {
  loading.value = true;
  try {
    const res = await api.get("/admin/users", { 
      params: { 
        page, 
        limit: usersLimit.value,
        search: usersSearch.value,
        role: usersRoleFilter.value
      } 
    });
    users.value = res.data.items;
    usersTotal.value = res.data.total;
    usersPage.value = res.data.page;
    // Update stats count
    stats.value.total_users = res.data.total;
  } catch (e) {
    console.error("Error fetching users:", e);
  } finally {
    loading.value = false;
  }
};

const handleDocsSearch = (query) => {
  docsSearch.value = query;
  fetchDocuments(1);
};

const handleUsersSearch = (query) => {
  usersSearch.value = query;
  fetchUsers(1);
};

const handleUsersFilter = (role) => {
  usersRoleFilter.value = role;
  fetchUsers(1);
};

// Watch tab change to lazy load
watch(currentTab, async (newTab) => {
  if (newTab === 'documents' && documents.value.length === 0) await fetchDocuments();
  if (newTab === 'users' && users.value.length === 0) await fetchUsers();
  if (newTab === 'overview') await fetchStats();
});

onMounted(async () => {
  window.addEventListener('resize', handleResize);
  handleResize();
  
  // Non-blocking fetch
  fetchStats();
  if (currentTab.value === 'documents') fetchDocuments();
  if (currentTab.value === 'users') fetchUsers();
});

const handleTabChange = (tab) => {
  currentTab.value = tab;
  if (isMobile.value) {
    showSidebar.value = false;
  }
};

const getPageTitle = () => {
  const titles = {
    overview: 'Dashboard',
    documents: 'Documents',
    users: 'Users'
  };
  return titles[currentTab.value] || 'Admin';
};

</script>
