import { defineStore } from 'pinia'
import { ref } from 'vue'
import { statusApi } from '@/services/api'

export const useAppStore = defineStore('app', () => {
  const demoMode = ref(true)
  const loading = ref(false)

  async function fetchStatus() {
    loading.value = true
    try {
      const status = await statusApi.getDemoMode()
      demoMode.value = status.demo_mode
    } catch (e) {
      demoMode.value = true
    } finally {
      loading.value = false
    }
  }

  return {
    demoMode,
    loading,
    fetchStatus,
  }
})
