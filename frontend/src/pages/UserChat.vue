<template>
  <div class="flex h-screen bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800 font-sans overflow-hidden">
    <!-- Sidebar with Glassmorphism -->
    <div 
      class="bg-gray-900/50 backdrop-blur-xl border-r border-gray-700/50 text-white w-72 flex-shrink-0 flex flex-col transition-all duration-300 absolute md:relative h-full z-50"
      :class="{ '-ml-72': !showSidebar }"
    >
      <!-- Header -->
      <div class="p-4 md:p-6 border-b border-gray-700/50">
        <!-- Close button for mobile -->
        <div class="flex justify-between items-center mb-4 md:hidden">
          <h3 class="text-lg font-bold text-white">Chats</h3>
          <button 
            @click="showSidebar = false"
            class="p-2 hover:bg-gray-700/50 rounded-lg transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="flex items-center gap-3 mb-4 md:mb-6">
          <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold shadow-lg">
            {{ userStore.user?.username?.charAt(0).toUpperCase() || 'R' }}
          </div>
          <div>
            <h2 class="font-bold text-base md:text-lg capitalize">{{ userStore.user?.username || 'User' }}</h2>
            <p class="text-xs text-gray-400">{{ userStore.user?.role || 'Member' }}</p>
          </div>
        </div>
        
        <button 
          @click="createNewChat" 
          class="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-4 py-2.5 md:py-3 rounded-xl font-medium transition-all duration-200 flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20 text-sm md:text-base"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-5 md:w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
          </svg>
          New Chat
        </button>
      </div>
      
      <!-- Sessions List -->
      <div class="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <div 
          v-for="session in chatStore.sessions" 
          :key="session.id"
          class="group relative p-2.5 md:p-3 rounded-lg cursor-pointer text-xs md:text-sm transition-all duration-200"
          :class="chatStore.currentSessionId === session.id 
            ? 'bg-gray-700/50 text-white' 
            : 'hover:bg-gray-800/50 text-gray-300'"
        >
          <div @click="selectSession(session.id)" class="flex items-center gap-2 pr-14 md:pr-16">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 md:h-4 md:w-4 opacity-50 group-hover:opacity-100 transition-opacity flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
            </svg>
            <span class="truncate flex-1">{{ session.title }}</span>
          </div>
          
          <!-- Action Buttons -->
          <div class="absolute right-1.5 md:right-2 top-1/2 -translate-y-1/2 flex gap-0.5 md:gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              @click.stop="openRenameModal(session)"
              class="p-1 md:p-1.5 hover:bg-gray-600/50 rounded transition-colors"
              title="Rename"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 md:h-4 md:w-4 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
              </svg>
            </button>
            <button
              @click.stop="handleDeleteSession(session.id)"
              class="p-1 md:p-1.5 hover:bg-gray-600/50 rounded transition-colors"
              title="Delete"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 md:h-4 md:w-4 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- User Section -->
      <div class="p-3 md:p-4 border-t border-gray-700/50">
        <button 
          @click="logout" 
          class="flex items-center gap-2 md:gap-3 text-gray-400 hover:text-red-400 transition-colors w-full p-2 rounded-lg hover:bg-gray-800/50 text-sm md:text-base"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-5 md:w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clip-rule="evenodd" />
          </svg>
          <span class="font-medium">Logout</span>
        </button>
      </div>
    </div>

    <!-- Overlay for mobile -->
    <div 
      v-if="showSidebar && isMobile"
      @click="showSidebar = false"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 md:hidden"
    ></div>

    <!-- Main Chat Area -->
    <div class="flex-1 flex flex-col h-full relative min-w-0">
      <!-- Header -->
      <header class="bg-gray-800/50 backdrop-blur-xl border-b border-gray-700/50 px-4 md:px-6 py-3 md:py-4 flex items-center justify-between">
        <div class="flex items-center gap-3 md:gap-4 min-w-0">
          <button 
            @click="toggleSidebar" 
            class="p-1.5 md:p-2 rounded-lg hover:bg-gray-700/50 text-gray-300 hover:text-white transition-all flex-shrink-0"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 md:h-6 md:w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div class="flex items-center gap-2 md:gap-3 min-w-0">
            <div class="w-7 h-7 md:w-9 md:h-9 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold shadow-lg shadow-blue-500/30 flex-shrink-0">
              😊
            </div>
            <div class="min-w-0">
              <h1 class="text-sm md:text-lg font-bold text-white truncate">Your</h1>
              <p class="text-xs text-gray-400 hidden sm:block">AI Assistant</p>
            </div>
          </div>
        </div>
        
        <!-- Theme Toggle -->
        <button 
          @click="themeStore.toggleTheme" 
          class="p-1.5 md:p-2.5 rounded-lg hover:bg-gray-700/50 text-gray-300 hover:text-white transition-all flex-shrink-0"
        >
          <svg v-if="themeStore.isDark" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-5 md:w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-5 md:w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
        </button>
      </header>

      <!-- Messages Area -->
      <div class="flex-1 overflow-y-auto p-3 md:p-6 space-y-4 md:space-y-6" ref="messagesContainer">
        <div class="max-w-4xl mx-auto">
          <!-- Empty State -->
          <div v-if="chatStore.messages.length === 0" class="text-center mt-16 md:mt-32">
            <div class="inline-block p-4 md:p-6 bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-2xl mb-4 md:mb-6">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 md:h-16 md:w-16 text-blue-400 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <h3 class="text-lg md:text-xl font-semibold text-white mb-2">Start a Conversation</h3>
            <p class="text-sm md:text-base text-gray-400">Ask me anything about your documents</p>
          </div>

          <!-- Messages -->
          <ChatMessage
            v-for="(msg, index) in chatStore.messages"
            :key="index"
            :message="msg"
          />
        </div>
      </div>

      <!-- Input Area -->
      <ChatInput :loading="chatStore.loading" @send="handleSend" />
    </div>

    <!-- Rename Modal -->
    <div v-if="showRenameModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-gray-800/90 backdrop-blur-xl border border-gray-700/50 p-5 md:p-6 rounded-2xl shadow-2xl w-full max-w-md">
        <h3 class="text-lg md:text-xl font-bold text-white mb-4">Rename Chat</h3>
        <input 
          v-model="renameTitle"
          type="text"
          class="w-full border border-gray-600/50 bg-gray-900/50 text-white placeholder-gray-500 p-2.5 md:p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all mb-4 text-sm md:text-base"
          placeholder="Enter new title"
          @keyup.enter="handleRename"
        >
        <div class="flex gap-3">
          <button 
            @click="showRenameModal = false"
            class="flex-1 px-4 py-2 md:py-2.5 text-gray-300 hover:text-white hover:bg-gray-700/50 rounded-xl font-medium transition-all text-sm md:text-base"
          >
            Cancel
          </button>
          <button 
            @click="handleRename"
            class="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-4 py-2 md:py-2.5 rounded-xl font-semibold transition-all text-sm md:text-base"
          >
            Rename
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, computed } from "vue";
import { useChatStore } from "@/stores/chat";
import { useUserStore } from "@/stores/user";
import { useThemeStore } from "@/stores/theme";
import ChatMessage from "@/components/chat/ChatMessage.vue";
import ChatInput from "@/components/chat/ChatInput.vue";

const chatStore = useChatStore();
const userStore = useUserStore();
const themeStore = useThemeStore();
const messagesContainer = ref(null);
const showSidebar = ref(true);
const windowWidth = ref(window.innerWidth);
const showRenameModal = ref(false);
const renameTitle = ref('');
const renamingSession = ref(null);

const isMobile = computed(() => windowWidth.value < 768);

const handleResize = () => {
  windowWidth.value = window.innerWidth;
  if (isMobile.value) showSidebar.value = false;
  else showSidebar.value = true;
};

onMounted(() => {
  window.addEventListener('resize', handleResize);
  handleResize();
  chatStore.fetchSessions();
  if (!chatStore.currentSessionId) {
    chatStore.clearChat();
  }
});

const toggleSidebar = () => {
  showSidebar.value = !showSidebar.value;
};

const createNewChat = () => {
  chatStore.clearChat();
  if (isMobile.value) showSidebar.value = false;
};

const selectSession = async (id) => {
  await chatStore.selectSession(id);
  if (isMobile.value) showSidebar.value = false;
};

const handleSend = async (text) => {
  await chatStore.sendMessage(text);
};

const logout = () => userStore.logout();

const openRenameModal = (session) => {
  renamingSession.value = session;
  renameTitle.value = session.title;
  showRenameModal.value = true;
};

const handleRename = async () => {
  if (!renameTitle.value.trim()) return;
  
  try {
    await chatStore.updateSession(renamingSession.value.id, renameTitle.value);
    showRenameModal.value = false;
    renamingSession.value = null;
    renameTitle.value = '';
  } catch (e) {
    alert('Failed to rename session');
  }
};

const handleDeleteSession = async (sessionId) => {
  if (!confirm('Are you sure you want to delete this chat? This action cannot be undone.')) return;
  
  try {
    await chatStore.deleteSession(sessionId);
  } catch (e) {
    alert('Failed to delete session');
  }
};

watch(
  () => chatStore.messages.length,
  () => {
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
      }
    });
  }
);
</script>
