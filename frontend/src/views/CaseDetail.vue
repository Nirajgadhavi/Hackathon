<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCasesStore } from '@/stores/cases'

const route = useRoute()
const router = useRouter()
const casesStore = useCasesStore()

const activeLetterTab = ref('provider')
const decisionSubmitted = ref(false)
const formData = ref({
  final_decision: '',
  decision_notes: '',
  provider_letter: '',
  member_letter: ''
})

const caseId = computed(() => route.params.id as string)
const currentCase = computed(() => casesStore.currentCase)
const loading = computed(() => casesStore.loading)
const processing = computed(() => casesStore.processing)
const processingStep = computed(() => casesStore.processingStep)
const error = computed(() => casesStore.error)

onMounted(async () => {
  await casesStore.fetchCase(caseId.value)
  if (route.query.decided === 'true') {
    decisionSubmitted.value = true
  }
})

watch(currentCase, (newCase) => {
  if (newCase) {
    formData.value = {
      final_decision: newCase.final_decision || '',
      decision_notes: newCase.final_decision_notes || '',
      provider_letter: newCase.provider_letter || '',
      member_letter: newCase.member_letter || ''
    }
  }
})

async function handleProcess() {
  await casesStore.processCase(caseId.value)
}

async function handleSubmitDecision() {
  const success = await casesStore.submitDecision(caseId.value, formData.value)
  if (success) {
    decisionSubmitted.value = true
  }
}

function getCriterionClass(status: string) {
  switch (status) {
    case 'met': return 'criteria-met'
    case 'unmet': return 'criteria-unmet'
    case 'unknown': return 'criteria-unknown'
    default: return ''
  }
}

function getRecommendationClass(recommendation: string) {
  switch (recommendation) {
    case 'approve': return 'recommendation-approve'
    case 'deny': return 'recommendation-deny'
    case 'pend': return 'recommendation-pend'
    default: return ''
  }
}

function getRecommendationIcon(recommendation: string) {
  switch (recommendation) {
    case 'approve': return '✅'
    case 'deny': return '❌'
    case 'pend': return '⏸️'
    default: return ''
  }
}

function getBiomarkerClass(status: string) {
  if (status === 'positive' || status === 'wild type' || status === 'negative') {
    if (status === 'positive') return 'badge-success'
    if (status === 'wild type') return 'badge-success'
    if (status === 'negative') return 'badge-success'
  }
  return 'badge-secondary'
}
</script>

<template>
  <div>
    <div class="loading-overlay" v-if="processing">
      <div class="spinner"></div>
      <p class="mt-3 text-muted">{{ processingStep }}</p>
    </div>

    <nav class="breadcrumb mb-3">
      <router-link to="/" class="breadcrumb-item">Cases</router-link>
      <span class="breadcrumb-item active">{{ caseId }}</span>
    </nav>

    <div v-if="loading && !currentCase" class="text-center py-5">
      <div class="spinner"></div>
      <p class="mt-3 text-muted">Loading case...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-else-if="currentCase">
      <div class="case-header mb-4">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h3 class="mb-1">{{ currentCase.title }}</h3>
            <p class="text-muted mb-0">
              <span class="me-3">💊 {{ currentCase.drug_name || 'N/A' }}</span>
              <span class="me-3">📋 {{ currentCase.indication || 'N/A' }}</span>
              <span :class="['status-badge', `status-${currentCase.status}`]">{{ currentCase.status }}</span>
              <span v-if="currentCase.complexity" :class="['badge', `complexity-${currentCase.complexity}`, 'ms-2']">
                {{ currentCase.complexity }} complexity
              </span>
            </p>
          </div>
          <div>
            <button
              v-if="currentCase.status === 'pending'"
              class="btn btn-primary btn-lg"
              @click="handleProcess"
              :disabled="processing"
            >
              🤖 Process with AI
            </button>
          </div>
        </div>
      </div>

      <div v-if="decisionSubmitted" class="alert alert-success">
        ✅ Decision has been recorded successfully!
      </div>

      <div class="row">
        <div class="col-lg-6 mb-4">
          <div class="card h-100">
            <div class="card-header">
              📄 Raw PA Request
            </div>
            <div class="card-body">
              <div class="raw-text-box">{{ currentCase.raw_text }}</div>
            </div>
          </div>
        </div>

        <div class="col-lg-6 mb-4">
          <div class="card h-100">
            <div class="card-header">
              📋 AI-Extracted Summary
            </div>
            <div class="card-body">
              <div v-if="currentCase.extracted_data">
                <div class="summary-card p-3 rounded mb-3">
                  <h6 class="mb-3">👤 Patient Information</h6>
                  <div class="row mb-2">
                    <div class="col-4 text-muted">Name:</div>
                    <div class="col-8">{{ currentCase.extracted_data.patient_info?.name || 'N/A' }}</div>
                  </div>
                  <div class="row mb-2">
                    <div class="col-4 text-muted">DOB:</div>
                    <div class="col-8">{{ currentCase.extracted_data.patient_info?.dob || 'N/A' }}</div>
                  </div>
                  <div class="row">
                    <div class="col-4 text-muted">Member ID:</div>
                    <div class="col-8">{{ currentCase.extracted_data.patient_info?.member_id || 'N/A' }}</div>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-6 mb-3">
                    <div class="card bg-light h-100">
                      <div class="card-body p-3">
                        <h6>📋 Diagnosis</h6>
                        <p class="mb-1"><strong>{{ currentCase.extracted_data.diagnosis?.primary || 'N/A' }}</strong></p>
                        <small class="text-muted">{{ currentCase.extracted_data.diagnosis?.icd10 || '' }}</small>
                        <p v-if="currentCase.extracted_data.diagnosis?.histology" class="mb-0 mt-1">
                          <small>{{ currentCase.extracted_data.diagnosis.histology }}</small>
                        </p>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <div class="card bg-light h-100">
                      <div class="card-body p-3">
                        <h6>📊 Disease Stage</h6>
                        <p class="mb-1"><strong>{{ currentCase.extracted_data.disease_stage?.stage || 'N/A' }}</strong></p>
                        <small v-if="currentCase.extracted_data.disease_stage?.tnm" class="text-muted">
                          {{ currentCase.extracted_data.disease_stage.tnm }}
                        </small>
                        <p v-if="currentCase.extracted_data.disease_stage?.metastatic_sites?.length" class="mb-0 mt-1">
                          <small>Mets: {{ currentCase.extracted_data.disease_stage.metastatic_sites.join(', ') }}</small>
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="card bg-light mb-3">
                  <div class="card-body p-3">
                    <h6>🧬 Biomarkers</h6>
                    <div class="row">
                      <div class="col-md-4 mb-2">
                        <strong>PD-L1:</strong><br>
                        <span :class="['badge', getBiomarkerClass(currentCase.extracted_data.biomarkers?.pd_l1?.status)]">
                          {{ currentCase.extracted_data.biomarkers?.pd_l1?.status || 'N/A' }}
                        </span>
                        <small v-if="currentCase.extracted_data.biomarkers?.pd_l1?.value">
                          ({{ currentCase.extracted_data.biomarkers.pd_l1.value }})
                        </small>
                      </div>
                      <div class="col-md-4 mb-2">
                        <strong>EGFR:</strong><br>
                        <span :class="['badge', getBiomarkerClass(currentCase.extracted_data.biomarkers?.egfr?.status)]">
                          {{ currentCase.extracted_data.biomarkers?.egfr?.status || 'N/A' }}
                        </span>
                        <small v-if="currentCase.extracted_data.biomarkers?.egfr?.mutation">
                          ({{ currentCase.extracted_data.biomarkers.egfr.mutation }})
                        </small>
                      </div>
                      <div class="col-md-4 mb-2">
                        <strong>ALK:</strong><br>
                        <span :class="['badge', getBiomarkerClass(currentCase.extracted_data.biomarkers?.alk?.status)]">
                          {{ currentCase.extracted_data.biomarkers?.alk?.status || 'N/A' }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-6 mb-3">
                    <div class="card bg-light h-100">
                      <div class="card-body p-3">
                        <h6>📊 Performance Status</h6>
                        <p class="mb-0"><strong>ECOG {{ currentCase.extracted_data.performance_status?.ecog || 'N/A' }}</strong></p>
                        <small class="text-muted">{{ currentCase.extracted_data.performance_status?.description || '' }}</small>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <div class="card bg-light h-100">
                      <div class="card-body p-3">
                        <h6>💊 Prior Therapy</h6>
                        <p class="mb-0">
                          <span v-if="currentCase.extracted_data.prior_therapy?.has_prior_systemic" class="badge badge-warning">
                            Has Prior Treatment
                          </span>
                          <span v-else class="badge badge-success">
                            No Prior Systemic
                          </span>
                        </p>
                        <small v-if="currentCase.extracted_data.prior_therapy?.treatments?.length" class="text-muted">
                          {{ currentCase.extracted_data.prior_therapy.treatments.join(', ') }}
                        </small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center text-muted py-5">
                <div style="font-size: 3rem;">🤖</div>
                <p class="mt-3">Click "Process with AI" to extract clinical data</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row">
        <div class="col-lg-6 mb-4">
          <div class="card h-100">
            <div class="card-header">
              ✅ Policy Criteria Evaluation
            </div>
            <div class="card-body">
              <div v-if="currentCase.criteria_evaluation?.length">
                <h6 class="mb-3">
                  <strong>{{ currentCase.drug_name }}</strong> - {{ currentCase.indication }}
                </h6>

                <div
                  v-for="criterion in currentCase.criteria_evaluation"
                  :key="criterion.id"
                  :class="['p-3', 'mb-2', 'rounded', getCriterionClass(criterion.status)]"
                >
                  <div class="d-flex justify-content-between align-items-start">
                    <div>
                      <strong>{{ criterion.id }}: {{ criterion.description }}</strong>
                      <span v-if="criterion.required" class="badge badge-secondary ms-2">Required</span>
                    </div>
                    <span :class="['badge', criterion.status === 'met' ? 'badge-success' : criterion.status === 'unmet' ? 'badge-danger' : 'badge-warning']">
                      {{ criterion.status?.toUpperCase() }}
                    </span>
                  </div>
                  <p v-if="criterion.evidence" class="mb-0 mt-2" style="font-size: 0.875rem;">
                    ℹ️ {{ criterion.evidence }}
                  </p>
                </div>

                <hr>
                <h6>Clinical Guidelines</h6>
                <div
                  v-for="(guideline, index) in currentCase.policy_guidelines"
                  :key="index"
                  class="guideline-snippet"
                >
                  <strong>{{ guideline.source }}:</strong>
                  <p class="mb-0 mt-1">{{ guideline.text }}</p>
                </div>
              </div>
              <div v-else class="text-center text-muted py-5">
                <div style="font-size: 3rem;">📋</div>
                <p class="mt-3">Process case to evaluate policy criteria</p>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-6 mb-4">
          <div class="card h-100">
            <div class="card-header">
              💡 AI Recommendation
            </div>
            <div class="card-body">
              <div v-if="currentCase.ai_recommendation">
                <div :class="['p-4', 'rounded', 'mb-4', getRecommendationClass(currentCase.ai_recommendation.recommendation)]">
                  <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="mb-0">
                      {{ getRecommendationIcon(currentCase.ai_recommendation.recommendation) }}
                      {{ currentCase.ai_recommendation.recommendation?.toUpperCase() }}
                    </h4>
                    <div>
                      <span class="badge badge-secondary me-2">{{ currentCase.ai_recommendation.confidence || 'medium' }} confidence</span>
                      <span :class="['badge', `complexity-${currentCase.complexity}`]">{{ currentCase.complexity }} complexity</span>
                    </div>
                  </div>
                  <p class="mb-0">{{ currentCase.ai_recommendation.clinical_rationale || '' }}</p>
                </div>

                <h6>✅ Key Reasons</h6>
                <ul class="mb-3">
                  <li v-for="(reason, index) in currentCase.ai_recommendation.primary_reasons" :key="index">
                    {{ reason }}
                  </li>
                </ul>

                <div v-if="currentCase.ai_recommendation.information_gaps?.length">
                  <h6>❓ Information Gaps</h6>
                  <ul class="mb-3 text-warning">
                    <li v-for="(gap, index) in currentCase.ai_recommendation.information_gaps" :key="index">
                      {{ gap }}
                    </li>
                  </ul>
                </div>

                <div v-if="currentCase.ai_recommendation.guideline_alignment">
                  <h6>📚 Guideline Alignment</h6>
                  <p class="text-muted">{{ currentCase.ai_recommendation.guideline_alignment }}</p>
                </div>
              </div>
              <div v-else class="text-center text-muted py-5">
                <div style="font-size: 3rem;">💡</div>
                <p class="mt-3">Process case to get AI recommendation</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="currentCase.status !== 'pending'" class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              ✉️ Decision & Letters
            </div>
            <div class="card-body">
              <form @submit.prevent="handleSubmitDecision">
                <div class="row mb-4">
                  <div class="col-12">
                    <h5>Final Decision</h5>
                    <div class="btn-group">
                      <input type="radio" class="btn-check" id="approve" value="approve" v-model="formData.final_decision">
                      <label class="btn-outline-success" for="approve">✅ Approve</label>

                      <input type="radio" class="btn-check" id="deny" value="deny" v-model="formData.final_decision">
                      <label class="btn-outline-danger" for="deny">❌ Deny</label>

                      <input type="radio" class="btn-check" id="pend" value="pend" v-model="formData.final_decision">
                      <label class="btn-outline-warning" for="pend">⏸️ Pend</label>
                    </div>
                  </div>
                </div>

                <div class="row mb-4">
                  <div class="col-12">
                    <label class="form-label">Decision Notes (Optional)</label>
                    <textarea
                      class="form-control"
                      v-model="formData.decision_notes"
                      rows="2"
                      placeholder="Add any notes about this decision..."
                    ></textarea>
                  </div>
                </div>

                <ul class="nav-pills">
                  <li>
                    <button
                      type="button"
                      :class="{ active: activeLetterTab === 'provider' }"
                      @click="activeLetterTab = 'provider'"
                    >
                      👨‍⚕️ Provider Letter
                    </button>
                  </li>
                  <li>
                    <button
                      type="button"
                      :class="{ active: activeLetterTab === 'member' }"
                      @click="activeLetterTab = 'member'"
                    >
                      👤 Member Letter
                    </button>
                  </li>
                </ul>

                <div class="tab-content">
                  <div :class="['tab-pane', { active: activeLetterTab === 'provider' }]">
                    <textarea
                      class="form-control letter-textarea"
                      v-model="formData.provider_letter"
                      placeholder="Provider letter will be generated by AI..."
                    ></textarea>
                  </div>
                  <div :class="['tab-pane', { active: activeLetterTab === 'member' }]">
                    <textarea
                      class="form-control letter-textarea"
                      v-model="formData.member_letter"
                      placeholder="Member letter will be generated by AI..."
                    ></textarea>
                  </div>
                </div>

                <div class="mt-4 d-flex justify-content-between">
                  <router-link to="/" class="btn btn-outline-secondary">
                    ⬅️ Back to Cases
                  </router-link>
                  <button
                    type="submit"
                    class="btn btn-primary btn-lg"
                    :disabled="!formData.final_decision || loading"
                  >
                    ✅ {{ currentCase.status === 'decided' ? 'Update Decision' : 'Finalize Decision' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.case-header h3 {
  margin-bottom: 0.5rem;
}

.row {
  display: flex;
  flex-wrap: wrap;
  margin: -0.5rem;
}

.col-4 {
  flex: 0 0 33.333%;
  padding: 0.5rem;
}

.col-8 {
  flex: 0 0 66.666%;
  padding: 0.5rem;
}

.col-md-4 {
  flex: 0 0 100%;
  padding: 0.5rem;
}

@media (min-width: 768px) {
  .col-md-4 {
    flex: 0 0 33.333%;
  }
}
</style>
