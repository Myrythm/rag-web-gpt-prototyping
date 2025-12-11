<template>
  <div>
    <div class="mb-8">
      <h2 class="text-3xl font-bold text-white mb-2">Document Management</h2>
      <p class="text-gray-400">Upload and manage your knowledge base</p>
    </div>

    <!-- Upload Section -->
    <div
      class="mb-8 bg-gray-800/50 backdrop-blur-xl border border-gray-700/50 p-8 rounded-2xl"
    >
      <div class="flex items-center gap-3 mb-6">
        <div class="p-3 bg-blue-500/10 rounded-xl">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6 text-blue-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
        </div>
        <h3 class="text-xl font-bold text-white">Upload Documents</h3>
      </div>

      <div class="flex flex-col gap-4">
        <div class="flex flex-col sm:flex-row items-stretch gap-4">
          <div class="flex-1 relative">
            <input
              type="file"
              multiple
              accept=".pdf,.docx,.doc,.txt,.md"
              @change="handleFileChange"
              class="w-full text-sm text-gray-400 file:mr-4 file:py-3 file:px-6 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-gradient-to-r file:from-blue-600 file:to-purple-600 file:text-white hover:file:from-blue-500 hover:file:to-purple-500 file:transition-all file:shadow-lg file:shadow-blue-500/20 cursor-pointer bg-gray-900/50 border border-gray-700/50 rounded-xl p-3"
            />
          </div>
          <button
            @click="uploadFiles"
            class="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-8 py-3 rounded-xl disabled:opacity-50 transition-all font-semibold shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 whitespace-nowrap"
            :disabled="uploading || selectedFiles.length === 0"
          >
            {{ uploading ? `Uploading (${uploadProgress}/${selectedFiles.length})...` : `Upload ${selectedFiles.length > 0 ? `(${selectedFiles.length} files)` : ''}` }}
          </button>
        </div>
        
        <!-- Selected Files Preview -->
        <div v-if="selectedFiles.length > 0" class="flex flex-wrap gap-2">
          <div 
            v-for="(file, index) in selectedFiles" 
            :key="index"
            class="flex items-center gap-2 bg-gray-700/30 px-3 py-1.5 rounded-lg text-sm"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" :class="getFileIconColor(file.name)" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd" />
            </svg>
            <span class="text-gray-300 truncate max-w-[200px]">{{ file.name }}</span>
            <span class="text-xs px-1.5 py-0.5 rounded" :class="getFileTypeBadgeClass(file.name)">
              {{ getFileExtension(file.name) }}
            </span>
            <button @click="removeFile(index)" class="text-gray-500 hover:text-red-400 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Documents List -->
    <div
      class="bg-gray-800/50 backdrop-blur-xl border border-gray-700/50 p-8 rounded-2xl"
    >
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="p-3 bg-purple-500/10 rounded-xl">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-purple-400"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                d="M9 2a2 2 0 00-2 2v8a2 2 0 002 2h6a2 2 0 002-2V6.414A2 2 0 0016.414 5L14 2.586A2 2 0 0012.586 2H9z"
              />
              <path d="M3 8a2 2 0 012-2v10h8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-white">Document Library</h3>
        </div>
        
        <!-- Bulk Delete Button -->
        <button
          v-if="selectedDocIds.length > 0"
          @click="bulkDelete"
          :disabled="deleting"
          class="flex items-center gap-2 px-4 py-2 bg-red-500/20 text-red-400 hover:bg-red-500/30 rounded-xl font-medium transition-all border border-red-500/30"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          {{ deleting ? 'Deleting...' : `Delete Selected (${selectedDocIds.length})` }}
        </button>
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
          />
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5 text-gray-500 absolute left-3 top-3"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-700/50">
              <th class="p-4 text-left w-12">
                <input
                  type="checkbox"
                  :checked="isAllSelected"
                  :indeterminate="isIndeterminate"
                  @change="toggleSelectAll"
                  class="w-4 h-4 rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500 focus:ring-offset-gray-800 cursor-pointer"
                />
              </th>
              <th class="p-4 text-left font-semibold text-gray-300 text-sm">
                Filename
              </th>
              <th class="p-4 text-left font-semibold text-gray-300 text-sm">
                Chunks
              </th>
              <th class="p-4 text-right font-semibold text-gray-300 text-sm">
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="doc in documents"
              :key="doc.id"
              class="border-b border-gray-700/30 hover:bg-gray-700/20 transition-colors"
              :class="{ 'bg-blue-500/10': selectedDocIds.includes(doc.id) }"
            >
              <td class="p-4">
                <input
                  type="checkbox"
                  :checked="selectedDocIds.includes(doc.id)"
                  @change="toggleSelect(doc.id)"
                  class="w-4 h-4 rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500 focus:ring-offset-gray-800 cursor-pointer"
                />
              </td>
              <td class="p-4 text-gray-200">
                <div class="flex items-center gap-2">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5 text-blue-400"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
                      clip-rule="evenodd"
                    />
                  </svg>
                  {{ doc.filename }}
                </div>
              </td>
              <td class="p-4 text-gray-300">
                <span
                  class="px-3 py-1 bg-blue-500/10 text-blue-400 rounded-lg text-sm font-medium"
                >
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
              <td colspan="4" class="p-8 text-center text-gray-500">
                <div class="flex flex-col items-center justify-center gap-2">
                  <svg
                    class="animate-spin h-8 w-8 text-blue-400"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      class="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      stroke-width="4"
                    ></circle>
                    <path
                      class="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  <p>Loading documents...</p>
                </div>
              </td>
            </tr>
            <tr v-else-if="documents.length === 0">
              <td colspan="4" class="p-8 text-center text-gray-500">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-12 w-12 mx-auto mb-3 opacity-50"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <p>
                  No documents found. Upload your first document to get started.
                </p>
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
    required: true,
  },
  total: {
    type: Number,
    required: true,
  },
  currentPage: {
    type: Number,
    required: true,
  },
  limit: {
    type: Number,
    default: 20,
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["refresh", "page-change", "search"]);

const documents = computed(() => props.documents);
const selectedFiles = ref([]);
const uploading = ref(false);
const uploadProgress = ref(0);
const searchQuery = ref("");
const selectedDocIds = ref([]);
const deleting = ref(false);

// Computed props for select all checkbox state
const isAllSelected = computed(() => {
  return props.documents.length > 0 && selectedDocIds.value.length === props.documents.length;
});

const isIndeterminate = computed(() => {
  return selectedDocIds.value.length > 0 && selectedDocIds.value.length < props.documents.length;
});
let searchTimeout = null;

const handleSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    emit("search", searchQuery.value);
  }, 300);
};

const handleFileChange = (e) => {
  selectedFiles.value = Array.from(e.target.files);
};

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1);
};

const uploadFiles = async () => {
  if (selectedFiles.value.length === 0) return;
  
  uploading.value = true;
  uploadProgress.value = 0;
  
  const formData = new FormData();
  selectedFiles.value.forEach((file) => {
    formData.append("files", file);
  });

  try {
    const response = await api.post("/admin/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    
    const { uploaded, failed, errors } = response.data;
    
    if (failed > 0) {
      const errorMessages = errors.map(e => `${e.filename}: ${e.error}`).join('\n');
      alert(`Uploaded: ${uploaded} files\nFailed: ${failed} files\n\nErrors:\n${errorMessages}`);
    }
    
    selectedFiles.value = [];
    emit("refresh");
  } catch (e) {
    alert("Upload failed");
    console.error(e);
  } finally {
    uploading.value = false;
    uploadProgress.value = 0;
  }
};

const deleteDoc = async (id) => {
  if (!confirm("Are you sure you want to delete this document?")) return;
  try {
    await api.delete(`/admin/documents/${id}`);
    selectedDocIds.value = selectedDocIds.value.filter(docId => docId !== id);
    emit("refresh");
  } catch (e) {
    console.error(e);
  }
};

// Multi-select functions
const toggleSelect = (id) => {
  const index = selectedDocIds.value.indexOf(id);
  if (index === -1) {
    selectedDocIds.value.push(id);
  } else {
    selectedDocIds.value.splice(index, 1);
  }
};

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedDocIds.value = [];
  } else {
    selectedDocIds.value = props.documents.map(doc => doc.id);
  }
};

const bulkDelete = async () => {
  if (selectedDocIds.value.length === 0) return;
  
  const count = selectedDocIds.value.length;
  if (!confirm(`Are you sure you want to delete ${count} document(s)?`)) return;
  
  deleting.value = true;
  try {
    const response = await api.post('/admin/documents/bulk-delete', {
      document_ids: selectedDocIds.value
    });
    
    const { deleted_count, errors } = response.data;
    
    if (errors && errors.length > 0) {
      alert(`Deleted ${deleted_count} documents. ${errors.length} failed.`);
    }
    
    selectedDocIds.value = [];
    emit("refresh");
  } catch (e) {
    console.error(e);
    alert('Failed to delete documents');
  } finally {
    deleting.value = false;
  }
};

// File type helper functions
const getFileExtension = (filename) => {
  return filename.split('.').pop().toUpperCase();
};

const getFileIconColor = (filename) => {
  const ext = filename.split('.').pop().toLowerCase();
  switch (ext) {
    case 'pdf': return 'text-red-400';
    case 'docx':
    case 'doc': return 'text-blue-400';
    case 'txt': return 'text-yellow-400';
    case 'md': return 'text-purple-400';
    default: return 'text-gray-400';
  }
};

const getFileTypeBadgeClass = (filename) => {
  const ext = filename.split('.').pop().toLowerCase();
  switch (ext) {
    case 'pdf': return 'bg-red-500/20 text-red-400';
    case 'docx':
    case 'doc': return 'bg-blue-500/20 text-blue-400';
    case 'txt': return 'bg-yellow-500/20 text-yellow-400';
    case 'md': return 'bg-purple-500/20 text-purple-400';
    default: return 'bg-gray-500/20 text-gray-400';
  }
};
</script>
