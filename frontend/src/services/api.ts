import axios from 'axios'
import type { Case, Metrics, DemoModeStatus } from '@/types'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const casesApi = {
  getAll: async (): Promise<Case[]> => {
    const response = await api.get('/cases')
    return response.data
  },

  getById: async (id: string): Promise<Case> => {
    const response = await api.get(`/cases/${id}`)
    return response.data
  },

  process: async (id: string): Promise<{ status: string; message: string }> => {
    const response = await api.post(`/cases/${id}/process`)
    return response.data
  },

  submitDecision: async (
    id: string,
    data: {
      final_decision: string
      decision_notes: string
      provider_letter: string
      member_letter: string
    }
  ): Promise<{ status: string; message: string }> => {
    const response = await api.post(`/cases/${id}/decide`, data)
    return response.data
  },
}

export const metricsApi = {
  get: async (): Promise<Metrics> => {
    const response = await api.get('/metrics')
    return response.data
  },
}

export const statusApi = {
  getDemoMode: async (): Promise<DemoModeStatus> => {
    const response = await api.get('/status')
    return response.data
  },
}

export default api
