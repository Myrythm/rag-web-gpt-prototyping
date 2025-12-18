<template>
  <div>
    <div class="mb-8">
      <h2 class="text-3xl font-bold text-white mb-2">Dashboard Overview</h2>
      <p class="text-gray-400">Monitor your RAG system performance</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Total Documents -->
      <div class="bg-gray-800/50 backdrop-blur-xl border border-gray-700/50 p-6 rounded-2xl hover:border-blue-500/50 transition-all duration-300 group">
        <div class="flex items-center justify-between mb-4">
          <div class="p-3 bg-blue-500/10 rounded-xl group-hover:bg-blue-500/20 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="text-right">
            <p class="text-4xl font-bold text-white">{{ stats.total_documents }}</p>
          </div>
        </div>
        <h3 class="text-gray-400 uppercase text-sm font-semibold">Total Documents</h3>
      </div>

      <!-- Total Chunks -->
      <div class="bg-gray-800/50 backdrop-blur-xl border border-gray-700/50 p-6 rounded-2xl hover:border-green-500/50 transition-all duration-300 group">
        <div class="flex items-center justify-between mb-4">
          <div class="p-3 bg-green-500/10 rounded-xl group-hover:bg-green-500/20 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-green-400" viewBox="0 0 20 20" fill="currentColor">
              <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z" />
            </svg>
          </div>
          <div class="text-right">
            <p class="text-4xl font-bold text-white">{{ stats.total_chunks }}</p>
          </div>
        </div>
        <h3 class="text-gray-400 uppercase text-sm font-semibold">Total Chunks</h3>
      </div>

      <!-- Total Users -->
      <div class="bg-gray-800/50 backdrop-blur-xl border border-gray-700/50 p-6 rounded-2xl hover:border-purple-500/50 transition-all duration-300 group">
        <div class="flex items-center justify-between mb-4">
          <div class="p-3 bg-purple-500/10 rounded-xl group-hover:bg-purple-500/20 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-purple-400" viewBox="0 0 20 20" fill="currentColor">
              <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
            </svg>
          </div>
          <div class="text-right">
            <p class="text-4xl font-bold text-white">{{ stats.total_users }}</p>
          </div>
        </div>
        <h3 class="text-gray-400 uppercase text-sm font-semibold">Total Users</h3>
      </div>
    </div>

    <!-- Recent Traces Section -->
    <div class="mt-8 bg-gray-800/50 backdrop-blur-xl border border-gray-700/50 p-6 rounded-2xl">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-amber-500/10 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-amber-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm2 10a1 1 0 10-2 0v3a1 1 0 102 0v-3zm2-3a1 1 0 011 1v5a1 1 0 11-2 0v-5a1 1 0 011-1zm4-1a1 1 0 10-2 0v7a1 1 0 102 0V8z" clip-rule="evenodd" />
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-white">Recent LLM Traces</h3>
        </div>
        <a 
          href="https://smith.langchain.com" 
          target="_blank"
          class="text-sm text-amber-400 hover:text-amber-300 transition-colors"
        >
          Open LangSmith →
        </a>
      </div>

      <div v-if="stats.recent_traces && stats.recent_traces.length > 0" class="space-y-3">
        <div 
          v-for="trace in stats.recent_traces" 
          :key="trace.id"
          class="flex items-center justify-between p-4 bg-gray-700/30 rounded-xl hover:bg-gray-700/50 transition-colors"
        >
          <div class="flex items-center gap-4">
            <span 
              class="px-2 py-1 text-xs font-medium rounded-full"
              :class="getStatusClass(trace.status)"
            >
              {{ trace.status }}
            </span>
            <span class="text-gray-200 font-medium">{{ trace.name }}</span>
          </div>
          <div class="flex items-center gap-6 text-sm">
            <span v-if="trace.latency" class="text-gray-400">
              {{ formatLatency(trace.latency) }}
            </span>
            <span class="text-gray-500">
              {{ formatTime(trace.start_time) }}
            </span>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-8 text-gray-500">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-3 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <p>No traces yet. Configure LANGCHAIN_API_KEY to enable tracing.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stats: {
    type: Object,
    required: true,
    default: () => ({ total_documents: 0, total_chunks: 0, total_users: 0, recent_traces: [] })
  }
});

const getStatusClass = (status) => {
  if (status === 'success') return 'bg-green-500/20 text-green-400';
  if (status === 'error') return 'bg-red-500/20 text-red-400';
  return 'bg-gray-500/20 text-gray-400';
};

const formatLatency = (ms) => {
  if (ms < 1000) return `${Math.round(ms)}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
};

const formatTime = (isoString) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  return date.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
};
</script>

