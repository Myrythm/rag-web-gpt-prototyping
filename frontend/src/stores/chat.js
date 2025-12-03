import { defineStore } from 'pinia'
import api from '@/utils/api'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const messages = ref([])
  const loading = ref(false)
  const sessions = ref([])
  const currentSessionId = ref(null)

  async function sendMessage(text) {
    messages.value.push({ role: 'user', content: text })
    loading.value = true
    
    try {
      const response = await api.post('/chat', { 
        query: text,
        session_id: currentSessionId.value
      })
      const answer = response.data.answer
      
      // If this was a new session, update the ID and refresh list
      if (!currentSessionId.value && response.data.session_id) {
        currentSessionId.value = response.data.session_id
        await fetchSessions()
      }
      
      messages.value.push({ role: 'assistant', content: answer })
    } catch (error) {
      console.error('Chat failed', error)
      messages.value.push({ role: 'assistant', content: 'Sorry, something went wrong. Please try again.' })
    } finally {
      loading.value = false
    }
  }
  
  function clearChat() {
    messages.value = []
    currentSessionId.value = null
  }

  async function fetchSessions() {
    try {
      const response = await api.get('/chat/sessions')
      sessions.value = response.data
    } catch (error) {
      console.error('Failed to fetch sessions', error)
    }
  }

  async function selectSession(sessionId) {
    currentSessionId.value = sessionId
    loading.value = true
    try {
      const response = await api.get(`/chat/history/${sessionId}`)
      messages.value = response.data.map(msg => ({
        role: msg.role,
        content: msg.content
      }))
    } catch (error) {
      console.error('Failed to fetch history', error)
    } finally {
      loading.value = false
    }
  }

  async function updateSession(sessionId, newTitle) {
    try {
      await api.put(`/chat/sessions/${sessionId}`, { title: newTitle })
      await fetchSessions()
    } catch (error) {
      console.error('Failed to update session', error)
      throw error
    }
  }

  async function deleteSession(sessionId) {
    try {
      await api.delete(`/chat/sessions/${sessionId}`)
      
      // If deleting current session, clear chat
      if (currentSessionId.value === sessionId) {
        clearChat()
      }
      
      await fetchSessions()
    } catch (error) {
      console.error('Failed to delete session', error)
      throw error
    }
  }

  return { 
    messages, 
    loading, 
    sessions, 
    currentSessionId, 
    sendMessage, 
    clearChat, 
    fetchSessions, 
    selectSession,
    updateSession,
    deleteSession
  }
})
