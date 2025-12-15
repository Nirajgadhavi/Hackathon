<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCasesStore } from '@/stores/cases'
import { useMetricsStore } from '@/stores/metrics'

const router = useRouter()
const casesStore = useCasesStore()
const metricsStore = useMetricsStore()

onMounted(async () => {
  await Promise.all([
    casesStore.fetchCases(),
    metricsStore.fetchMetrics()
  ])
})

const metrics = computed(() => metricsStore.metrics)
const cases = computed(() => casesStore.cases)

function navigateToCase(caseId: string) {
  router.push(`/case/${caseId}`)
}

function getRecommendationClass(recommendation: string | undefined) {
  if (!recommendation) return ''
  switch (recommendation) {
    case 'approve': return 'badge-success'
    case 'deny': return 'badge-danger'
    case 'pend': return 'badge-warning'
    default: return ''
  }
}

function getStatusIcon(status: string) {
  switch (status) {
    case 'pending': return '🕐'
    case 'processed': return '🤖'
    case 'decided': return '✅'
    default: return ''
  }
}
</script>

<template>
  <div>
    <div class="page-header mb-4">
      <h2>📊 Prior Authorization Dashboard</h2>
      <p class="text-muted">AI-powered clinical co-pilot for specialty drug prior authorization review</p>
    </div>

    <div class="row mb-4" v-if="metrics">
      <div class="col-md-3">
        <div class="card metric-card">
          <div class="metric-value">{{ metrics.total_cases }}</div>
          <div class="metric-label">Total Cases</div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card metric-card">
          <div class="metric-value text-warning">{{ metrics.pending_cases }}</div>
          <div class="metric-label">Pending Review</div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card metric-card">
          <div class="metric-value text-info">{{ metrics.processed_cases }}</div>
          <div class="metric-label">AI Processed</div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card metric-card">
          <div class="metric-value text-success">{{ metrics.decided_cases }}</div>
          <div class="metric-label">Decisions Made</div>
        </div>
      </div>
    </div>

    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <span>📁 Prior Authorization Cases</span>
            <span class="badge badge-primary">{{ cases.length }} cases</span>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>Case ID</th>
                    <th>Title</th>
                    <th>Drug</th>
                    <th>Indication</th>
                    <th>Status</th>
                    <th>Complexity</th>
                    <th>AI Recommendation</th>
                    <th>Final Decision</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="caseItem in cases" :key="caseItem.id" @click="navigateToCase(caseItem.id)" style="cursor: pointer;">
                    <td><strong>{{ caseItem.id }}</strong></td>
                    <td>{{ caseItem.title?.substring(0, 50) }}{{ caseItem.title?.length > 50 ? '...' : '' }}</td>
                    <td>{{ caseItem.drug_name || 'N/A' }}</td>
                    <td>{{ caseItem.indication || 'N/A' }}</td>
                    <td>
                      <span :class="['status-badge', `status-${caseItem.status}`]">
                        {{ getStatusIcon(caseItem.status) }} {{ caseItem.status }}
                      </span>
                    </td>
                    <td>
                      <span v-if="caseItem.complexity" :class="['badge', `complexity-${caseItem.complexity}`]">
                        {{ caseItem.complexity }}
                      </span>
                      <span v-else class="text-muted">-</span>
                    </td>
                    <td>
                      <span v-if="caseItem.ai_recommendation" :class="['badge', getRecommendationClass(caseItem.ai_recommendation.recommendation)]">
                        {{ caseItem.ai_recommendation.recommendation?.toUpperCase() }}
                      </span>
                      <span v-else class="text-muted">-</span>
                    </td>
                    <td>
                      <span v-if="caseItem.final_decision" :class="['badge', getRecommendationClass(caseItem.final_decision)]">
                        {{ caseItem.final_decision?.toUpperCase() }}
                      </span>
                      <span v-else class="text-muted">Awaiting</span>
                    </td>
                    <td>
                      <button class="btn btn-sm btn-outline-primary" @click.stop="navigateToCase(caseItem.id)">
                        👁️ View
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            ℹ️ About This Demo
          </div>
          <div class="card-body">
            <h6>AI-Transformed Prior Authorization</h6>
            <p class="text-muted">This demo showcases how AI can transform the specialty drug PA process:</p>
            <ul class="text-muted">
              <li>Auto-summarizes PA requests (diagnosis, labs, biomarkers)</li>
              <li>Evaluates policy criteria automatically</li>
              <li>Generates recommendations with clinical rationale</li>
              <li>Drafts provider and member letters</li>
              <li>Reduces review time from 25-40 min to 6-10 min</li>
            </ul>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            📈 Expected Impact
          </div>
          <div class="card-body">
            <table class="impact-table">
              <tbody>
                <tr>
                  <td>PA Turnaround Time</td>
                  <td class="text-end"><span class="text-success">55-70% faster</span></td>
                </tr>
                <tr>
                  <td>MD Review Time</td>
                  <td class="text-end"><span class="text-success">70-78% reduction</span></td>
                </tr>
                <tr>
                  <td>SLA Compliance</td>
                  <td class="text-end"><span class="text-success">97-99%</span></td>
                </tr>
                <tr>
                  <td>Appeals Rate</td>
                  <td class="text-end"><span class="text-success">30-45% lower</span></td>
                </tr>
                <tr>
                  <td>Therapy Drop-offs</td>
                  <td class="text-end"><span class="text-success">3-4x better</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header h2 {
  margin-bottom: 0.5rem;
}

.impact-table {
  width: 100%;
}

.impact-table td {
  padding: 0.5rem 0;
  border-bottom: 1px solid #dee2e6;
}

.impact-table tr:last-child td {
  border-bottom: none;
}
</style>
