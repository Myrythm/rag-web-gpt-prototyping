import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(
    localStorage.getItem('theme') 
      ? localStorage.getItem('theme') === 'dark' 
      : true // Default to dark mode
  )

  function toggleTheme() {
    isDark.value = !isDark.value
  }

  function initTheme() {
    if (isDark.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  watch(isDark, (val) => {
    if (val) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  })

  return { isDark, toggleTheme, initTheme }
})
