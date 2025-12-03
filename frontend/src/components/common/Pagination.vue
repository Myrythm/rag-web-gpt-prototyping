<template>
  <div class="flex items-center justify-between border-t border-gray-700/50 px-4 py-3 sm:px-6 mt-4">
    <div class="flex-1 flex justify-between sm:hidden">
      <button
        @click="$emit('change', currentPage - 1)"
        :disabled="currentPage === 1"
        class="relative inline-flex items-center px-4 py-2 border border-gray-700 text-sm font-medium rounded-md text-gray-300 bg-gray-800 hover:bg-gray-700 disabled:opacity-50"
      >
        Previous
      </button>
      <button
        @click="$emit('change', currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-700 text-sm font-medium rounded-md text-gray-300 bg-gray-800 hover:bg-gray-700 disabled:opacity-50"
      >
        Next
      </button>
    </div>
    <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
      <div>
        <p class="text-sm text-gray-400">
          Showing
          <span class="font-medium text-white">{{ (currentPage - 1) * limit + 1 }}</span>
          to
          <span class="font-medium text-white">{{ Math.min(currentPage * limit, total) }}</span>
          of
          <span class="font-medium text-white">{{ total }}</span>
          results
        </p>
      </div>
      <div>
        <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
          <button
            @click="$emit('change', currentPage - 1)"
            :disabled="currentPage === 1"
            class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-700 bg-gray-800 text-sm font-medium text-gray-400 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span class="sr-only">Previous</span>
            <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </button>
          
          <button
            v-for="page in pages"
            :key="page"
            @click="$emit('change', page)"
            :class="[
              page === currentPage
                ? 'z-10 bg-blue-600 border-blue-600 text-white'
                : 'bg-gray-800 border-gray-700 text-gray-400 hover:bg-gray-700',
              'relative inline-flex items-center px-4 py-2 border text-sm font-medium'
            ]"
          >
            {{ page }}
          </button>

          <button
            @click="$emit('change', currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-700 bg-gray-800 text-sm font-medium text-gray-400 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span class="sr-only">Next</span>
            <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
          </button>
        </nav>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  currentPage: {
    type: Number,
    required: true
  },
  total: {
    type: Number,
    required: true
  },
  limit: {
    type: Number,
    default: 20
  }
});

const emit = defineEmits(['change']);

const totalPages = computed(() => Math.ceil(props.total / props.limit));

const pages = computed(() => {
  const p = [];
  if (totalPages.value <= 0) return p;
  
  let start = Math.max(1, props.currentPage - 2);
  let end = Math.min(totalPages.value, start + 4);
  
  if (end - start < 4) {
    start = Math.max(1, end - 4);
  }

  for (let i = start; i <= end; i++) {
    p.push(i);
  }
  return p;
});
</script>
