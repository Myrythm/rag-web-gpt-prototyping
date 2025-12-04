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
    
    // Add placeholder for assistant message
    const assistantMessageIndex = messages.value.length
    messages.value.push({ role: 'assistant', content: '', streaming: true })
    
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/v1/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          query: text,
          session_id: currentSessionId.value
        })
      })

      if (!response.ok) {
        throw new Error('Failed to stream response')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        
        // Keep the last incomplete line in the buffer
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.type === 'session_id') {
                if (!currentSessionId.value && data.session_id) {
                  currentSessionId.value = data.session_id
                  await fetchSessions()
                }
              } else if (data.type === 'token') {
                messages.value[assistantMessageIndex].content += data.content
              } else if (data.type === 'done') {
                messages.value[assistantMessageIndex].streaming = false
                loading.value = false
              } else if (data.type === 'error') {
                throw new Error(data.message)
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e)
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat failed', error)
      messages.value[assistantMessageIndex].content = 'Sorry, something went wrong. Please try again.'
      messages.value[assistantMessageIndex].streaming = false
    } finally {
      loading.value = false
      if (messages.value[assistantMessageIndex]) {
        messages.value[assistantMessageIndex].streaming = false
      }
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
