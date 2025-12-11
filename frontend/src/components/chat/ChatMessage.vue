<template>
  <div
    :class="['flex mb-6', message.role === 'user' ? 'justify-end' : 'justify-start']"
  >
    <div
      :class="[
        'max-w-[80%] p-4 rounded-2xl shadow-lg transition-all duration-200 hover:shadow-xl',
        message.role === 'user'
          ? 'bg-gradient-to-br from-blue-600 to-purple-600 text-white rounded-br-none'
          : 'bg-gray-800/50 backdrop-blur-xl border border-gray-700/50 text-gray-100 rounded-bl-none',
      ]"
    >
      <!-- Loading indicator for assistant -->
      <div v-if="message.role === 'assistant' && message.streaming && !message.content" class="flex items-center gap-2">
        <div class="flex space-x-1">
          <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
          <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
          <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
        </div>
      </div>

      <!-- Render markdown for assistant messages -->
      <div v-else-if="message.role === 'assistant'">
        <MarkdownRenderer :content="message.content" />
        <span 
          v-if="message.streaming && message.content" 
          class="inline-block w-2 h-4 ml-1 bg-blue-400 animate-pulse align-middle"
        ></span>
        
        <!-- Sources Section -->
        <div v-if="message.sources && message.sources.length > 0 && !message.streaming" class="mt-4 pt-3 border-t border-gray-600/30">
          <div class="flex items-center gap-2 mb-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd" />
            </svg>
            <span class="text-xs font-semibold text-gray-400 uppercase tracking-wide">Sources</span>
          </div>
          <div class="space-y-1.5">
            <div 
              v-for="source in message.sources" 
              :key="source.number"
              class="flex items-center gap-2 text-sm bg-gray-700/30 rounded-lg px-3 py-2 hover:bg-gray-700/50 transition-colors"
            >
              <span class="w-5 h-5 flex items-center justify-center bg-blue-500/20 text-blue-400 rounded text-xs font-bold">
                {{ source.number }}
              </span>
              <span class="flex-1 text-gray-300 truncate">{{ source.source }}</span>
              <span 
                class="text-xs font-medium px-2 py-0.5 rounded-full"
                :class="getSimilarityClass(source.similarity)"
              >
                {{ source.similarity }}%
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Plain text for user messages -->
      <p v-else class="whitespace-pre-wrap leading-relaxed text-[15px]">
        {{ message.content }}
      </p>
    </div>
  </div>
</template>

<script setup>
import MarkdownRenderer from './MarkdownRenderer.vue';

defineProps(["message"]);

// Returns color classes based on similarity percentage
const getSimilarityClass = (similarity) => {
  if (similarity >= 70) {
    return 'bg-green-500/20 text-green-400';
  } else if (similarity >= 50) {
    return 'bg-yellow-500/20 text-yellow-400';
  } else {
    return 'bg-red-500/20 text-red-400';
  }
};
</script>

