<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800 p-4">
    <div class="bg-gray-800/50 backdrop-blur-xl border border-gray-700/50 p-8 rounded-2xl shadow-2xl w-full max-w-md">
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center text-white font-bold text-2xl mx-auto mb-4 shadow-lg shadow-blue-500/30">
          R
        </div>
        <h1 class="text-3xl font-bold text-white mb-2">Welcome Back</h1>
        <p class="text-gray-400">Sign in to continue</p>
      </div>
      
      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div>
          <label class="block text-gray-300 text-sm font-semibold mb-2">Username</label>
          <input
            v-model="username"
            type="text"
            class="w-full border border-gray-600/50 bg-gray-900/50 text-white placeholder-gray-500 p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all backdrop-blur-sm"
            placeholder="Enter your username"
            required
          />
        </div>
        
        <div>
          <label class="block text-gray-300 text-sm font-semibold mb-2">Password</label>
          <input
            v-model="password"
            type="password"
            class="w-full border border-gray-600/50 bg-gray-900/50 text-white placeholder-gray-500 p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all backdrop-blur-sm"
            placeholder="Enter your password"
            required
          />
        </div>
        
        <button
          type="submit"
          class="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white p-3 rounded-xl transition-all font-semibold shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40"
        >
          Sign In
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useUserStore } from "@/stores/user";
import { useRouter } from "vue-router";

const username = ref("");
const password = ref("");
const userStore = useUserStore();
const router = useRouter();

const handleSubmit = async () => {
  const success = await userStore.login(username.value, password.value);
  if (success) {
    if (userStore.user.role === "admin") {
      router.push("/admin");
    } else {
      router.push("/");
    }
  } else {
    alert("Login failed");
  }
};
</script>
