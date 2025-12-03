<template>
  <div>
    <div class="mb-8">
      <h2 class="text-3xl font-bold text-white mb-2">Document Management</h2>
      <p class="text-gray-400">Upload and manage your knowledge base</p>
    </div>

    <!-- Upload Section -->
    <div class="mb-8 bg-gray-800/50 backdrop-blur-xl border border-gray-700/50 p-8 rounded-2xl">
      <div class="flex items-center gap-3 mb-6">
        <div class="p-3 bg-blue-500/10 rounded-xl">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>
        <h3 class="text-xl font-bold text-white">Upload Document</h3>
      </div>
      
      <div class="flex flex-col sm:flex-row items-stretch gap-4">
        <input
          type="file"
          @change="handleFileChange"
          class="flex-1 block text-sm text-gray-400 file:mr-4 file:py-3 file:px-6 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-gradient-to-r file:from-blue-600 file:to-purple-600 file:text-white hover:file:from-blue-500 hover:file:to-purple-500 file:transition-all file:shadow-lg file:shadow-blue-500/20 cursor-pointer bg-gray-900/50 border border-gray-700/50 rounded-xl p-3"
        />
        <button
          @click="uploadFile"
          class="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-8 py-3 rounded-xl disabled:opacity-50 transition-all font-semibold shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 whitespace-nowrap"
          :disabled="uploading || !selectedFile"
        >
          {{ uploading ? "Uploading..." : "Upload" }}
        </button>
      </div>
    </div>

    <!-- Documents List -->
    <div class="bg-gray-800/50 backdrop-blur-xl border border-gray-700/50 p-8 rounded-2xl">
      <div class="flex items-center gap-3 mb-6">
        <div class="p-3 bg-purple-500/10 rounded-xl">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-purple-400" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9 2a2 2 0 00-2 2v8a2 2 0 002 2h6a2 2 0 002-2V6.414A2 2 0 0016.414 5L14 2.586A2 2 0 0012.586 2H9z" />
            <path d="M3 8a2 2 0 012-2v10h8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" />
          </svg>
        </div>
        <h3 class="text-xl font-bold text-white">Document Library</h3>
      </div>
      
      <!-- Search -->
      <div class="mb-6">
        <div class="relative">
          <input 
            v-model="searchQuery"
            @input="handleSearch"
            type="text" 
            placeholder="Search documents..." 
            class="w-full bg-gray-900/50 border border-gray-700/50 text-white pl-10 pr-4 py-2.5 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all placeholder-gray-500"
          >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-500 absolute left-3 top-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>
      
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-700/50">
              <th class="p-4 text-left font-semibold text-gray-300 text-sm">Filename</th>
              <th class="p-4 text-left font-semibold text-gray-300 text-sm">Chunks</th>
              <th class="p-4 text-right font-semibold text-gray-300 text-sm">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="doc in documents"
              :key="doc.id"
              class="border-b border-gray-700/30 hover:bg-gray-700/20 transition-colors"
            >
              <td class="p-4 text-gray-200">
                <div class="flex items-center gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd" />
                  </svg>
                  {{ doc.filename }}
                </div>
              </td>
              <td class="p-4 text-gray-300">
                <span class="px-3 py-1 bg-blue-500/10 text-blue-400 rounded-lg text-sm font-medium">
                  {{ doc.chunk_count }}
                </span>
              </td>
              <td class="p-4 text-right">
                <button
                  @click="deleteDoc(doc.id)"
                  class="px-4 py-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg font-medium transition-all"
                >
                  Delete
                </button>
              </td>
            </tr>
            <tr v-if="loading">
              <td colspan="3" class="p-8 text-center text-gray-500">
                <div class="flex flex-col items-center justify-center gap-2">
                  <svg class="animate-spin h-8 w-8 text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <p>Loading documents...</p>
                </div>
              </td>
            </tr>
            <tr v-else-if="documents.length === 0">
              <td colspan="3" class="p-8 text-center text-gray-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-3 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p>No documents found. Upload your first document to get started.</p>
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
  </div>
</template>

<script setup>
import { ref, watch, computed } from "vue";
import api from "@/utils/api";
import Pagination from "@/components/common/Pagination.vue";

const props = defineProps({
  documents: {
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

const emit = defineEmits(['refresh', 'page-change', 'search']);

const documents = computed(() => props.documents);
const selectedFile = ref(null);
const uploading = ref(false);
const searchQuery = ref("");
let searchTimeout = null;

const handleSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    emit('search', searchQuery.value);
  }, 300);
};

const handleFileChange = (e) => {
  selectedFile.value = e.target.files[0];
};

const uploadFile = async () => {
  if (!selectedFile.value) return;
  uploading.value = true;
  const formData = new FormData();
  formData.append("file", selectedFile.value);

  try {
    await api.post("/admin/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    selectedFile.value = null;
    emit('refresh'); // Tell parent to refresh data
  } catch (e) {
    alert("Upload failed");
    console.error(e);
  } finally {
    uploading.value = false;
  }
};

const deleteDoc = async (id) => {
  if (!confirm("Are you sure you want to delete this document?")) return;
  try {
    await api.delete(`/admin/documents/${id}`);
    emit('refresh'); // Tell parent to refresh data
  } catch (e) {
    console.error(e);
  }
};
</script>
