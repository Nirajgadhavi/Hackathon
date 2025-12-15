import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Case } from '@/types'
import { casesApi } from '@/services/api'

export const useCasesStore = defineStore('cases', () => {
  const cases = ref<Case[]>([])
  const currentCase = ref<Case | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const processing = ref(false)
  const processingStep = ref('')

  async function fetchCases() {
    loading.value = true
    error.value = null
    try {
      cases.value = await casesApi.getAll()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch cases'
    } finally {
      loading.value = false
    }
  }

  async function fetchCase(id: string) {
    loading.value = true
    error.value = null
    try {
      currentCase.value = await casesApi.getById(id)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch case'
    } finally {
      loading.value = false
    }
  }

  async function processCase(id: string) {
    processing.value = true
    error.value = null
    
    const steps = [
      'Extracting clinical data from PA request...',
      'Analyzing biomarkers and disease stage...',
      'Evaluating policy criteria...',
      'Generating AI recommendation...',
      'Drafting provider and member letters...',
      'Finalizing case summary...'
    ]
    
    let stepIndex = 0
    processingStep.value = steps[stepIndex]
    
    const stepInterval = setInterval(() => {
      if (stepIndex < steps.length - 1) {
        stepIndex++
        processingStep.value = steps[stepIndex]
      }
    }, 2000)

    try {
      await casesApi.process(id)
      clearInterval(stepInterval)
      processingStep.value = 'Processing complete!'
      await fetchCase(id)
    } catch (e) {
      clearInterval(stepInterval)
      error.value = e instanceof Error ? e.message : 'Failed to process case'
    } finally {
      processing.value = false
      processingStep.value = ''
    }
  }

  async function submitDecision(
    id: string,
    data: {
      final_decision: string
      decision_notes: string
      provider_letter: string
      member_letter: string
    }
  ) {
    loading.value = true
    error.value = null
    try {
      await casesApi.submitDecision(id, data)
      await fetchCase(id)
      return true
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to submit decision'
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    cases,
    currentCase,
    loading,
    error,
    processing,
    processingStep,
    fetchCases,
    fetchCase,
    processCase,
    submitDecision,
  }
})
