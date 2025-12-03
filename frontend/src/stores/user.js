import { defineStore } from 'pinia'
import api from '../utils/api'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')

  async function login(username, password) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    
    try {
      const response = await api.post('/auth/token', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      token.value = response.data.access_token
      localStorage.setItem('token', token.value)
      
      const payload = JSON.parse(atob(token.value.split('.')[1]))
      user.value = { username: payload.sub, role: payload.role }
      
      return true
    } catch (error) {
      console.error('Login failed', error)
      return false
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    window.location.href = '/login'
  }

  return { user, token, login, logout }
})
