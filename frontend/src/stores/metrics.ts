import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Metrics, Case } from '@/types'
import { metricsApi, casesApi } from '@/services/api'

export const useMetricsStore = defineStore('metrics', () => {
  const metrics = ref<Metrics | null>(null)
  const decidedCases = ref<Case[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchMetrics() {
    loading.value = true
    error.value = null
    try {
      metrics.value = await metricsApi.get()
      const allCases = await casesApi.getAll()
      decidedCases.value = allCases.filter(c => c.final_decision)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch metrics'
    } finally {
      loading.value = false
    }
  }

  return {
    metrics,
    decidedCases,
    loading,
    error,
    fetchMetrics,
  }
})
