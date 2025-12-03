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
      <p class="whitespace-pre-wrap leading-relaxed text-[15px]">{{ message.content }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps(["message"]);
</script>
