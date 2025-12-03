<template>
  <div class="border-t border-gray-700/50 p-6 bg-gray-800/30 backdrop-blur-xl">
    <form @submit.prevent="handleSubmit" class="flex gap-3 max-w-4xl mx-auto">
      <input
        v-model="text"
        type="text"
        placeholder="Ask something..."
        class="flex-1 border border-gray-600/50 bg-gray-900/50 text-white placeholder-gray-500 p-4 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all backdrop-blur-sm"
        :disabled="loading"
      />
      <button
        type="submit"
        class="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-8 py-4 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40"
        :disabled="loading || !text.trim()"
      >
        <span v-if="!loading" class="flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
          </svg>
          Send
        </span>
        <span v-else class="flex items-center gap-2">
          <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue";

const props = defineProps(["loading"]);
const emit = defineEmits(["send"]);

const text = ref("");

const handleSubmit = () => {
  if (!text.value.trim()) return;
  emit("send", text.value);
  text.value = "";
};
</script>
