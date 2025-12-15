<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useMetricsStore } from '@/stores/metrics'

const metricsStore = useMetricsStore()

onMounted(() => {
  metricsStore.fetchMetrics()
})

const metrics = computed(() => metricsStore.metrics)
const decidedCases = computed(() => metricsStore.decidedCases)
const loading = computed(() => metricsStore.loading)

const completionRate = computed(() => {
  if (!metrics.value || metrics.value.total_cases === 0) return 0
  return ((metrics.value.decided_cases / metrics.value.total_cases) * 100).toFixed(1)
})

function getRecommendationClass(recommendation: string | undefined) {
  if (!recommendation) return ''
  switch (recommendation) {
    case 'approve': return 'badge-success'
    case 'deny': return 'badge-danger'
    case 'pend': return 'badge-warning'
    default: return ''
  }
}
</script>

<template>
  <div>
    <div class="page-header mb-4">
      <h2>📈 Performance Metrics</h2>
      <p class="text-muted">Track the impact of AI-assisted prior authorization review</p>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner"></div>
      <p class="mt-3 text-muted">Loading metrics...</p>
    </div>

    <div v-else-if="metrics">
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card metric-card">
            <div class="metric-value">{{ metrics.total_cases }}</div>
            <div class="metric-label">Total Cases</div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card metric-card">
            <div class="metric-value text-success">{{ metrics.decided_cases }}</div>
            <div class="metric-label">Decisions Made</div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card metric-card">
            <div class="metric-value text-info">{{ metrics.avg_turnaround_minutes }}</div>
            <div class="metric-label">Avg Turnaround (min)</div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card metric-card">
            <div class="metric-value" style="color: #0dcaf0;">{{ completionRate }}%</div>
            <div class="metric-label">Completion Rate</div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-md-6">
          <div class="card h-100">
            <div class="card-header">
              🥧 Decision Distribution
            </div>
            <div class="card-body">
              <div v-if="metrics.decisions && Object.keys(metrics.decisions).length" class="row text-center">
                <div class="col-4">
                  <div class="decision-box decision-approve">
                    <h3>{{ metrics.decisions.approve || 0 }}</h3>
                    <small>Approved</small>
                  </div>
                </div>
                <div class="col-4">
                  <div class="decision-box decision-deny">
                    <h3>{{ metrics.decisions.deny || 0 }}</h3>
                    <small>Denied</small>
                  </div>
                </div>
                <div class="col-4">
                  <div class="decision-box decision-pend">
                    <h3>{{ metrics.decisions.pend || 0 }}</h3>
                    <small>Pended</small>
                  </div>
                </div>
              </div>
              <div v-else class="text-center text-muted py-4">
                <div style="font-size: 3rem;">🥧</div>
                <p class="mt-3">No decisions recorded yet</p>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-6">
          <div class="card h-100">
            <div class="card-header">
              🎯 Case Complexity
            </div>
            <div class="card-body">
              <div v-if="metrics.complexity_distribution && Object.keys(metrics.complexity_distribution).length" class="row text-center">
                <div class="col-6">
                  <div class="complexity-box complexity-low-box">
                    <h3>{{ metrics.complexity_distribution.low || 0 }}</h3>
                    <small>Low Complexity</small>
                    <p class="mb-0 mt-2" style="font-size: 0.75rem;">All criteria met</p>
                  </div>
                </div>
                <div class="col-6">
                  <div class="complexity-box complexity-high-box">
                    <h3>{{ metrics.complexity_distribution.high || 0 }}</h3>
                    <small>High Complexity</small>
                    <p class="mb-0 mt-2" style="font-size: 0.75rem;">Requires MD attention</p>
                  </div>
                </div>
              </div>
              <div v-else class="text-center text-muted py-4">
                <div style="font-size: 3rem;">🎯</div>
                <p class="mt-3">Process cases to see complexity distribution</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              📊 Before/After Comparison
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="comparison-table">
                  <thead>
                    <tr>
                      <th>Metric</th>
                      <th class="text-center">Pre-AI (Typical)</th>
                      <th class="text-center">Post-AI (Target)</th>
                      <th class="text-center">Improvement</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>🕐 PA Turnaround Time</td>
                      <td class="text-center">72-120 hrs</td>
                      <td class="text-center text-success">12-24 hrs</td>
                      <td class="text-center"><span class="badge badge-success">55-70% faster</span></td>
                    </tr>
                    <tr>
                      <td>👨‍⚕️ Medical Director Review Time</td>
                      <td class="text-center">25-40 min/case</td>
                      <td class="text-center text-success">6-10 min/case</td>
                      <td class="text-center"><span class="badge badge-success">70-78% reduction</span></td>
                    </tr>
                    <tr>
                      <td>✅ SLA Compliance</td>
                      <td class="text-center">82-88%</td>
                      <td class="text-center text-success">97-99%</td>
                      <td class="text-center"><span class="badge badge-success">>98% adherence</span></td>
                    </tr>
                    <tr>
                      <td>🔄 Appeals Rate</td>
                      <td class="text-center">High</td>
                      <td class="text-center text-success">30-45% lower</td>
                      <td class="text-center"><span class="badge badge-success">Significant reduction</span></td>
                    </tr>
                    <tr>
                      <td>⚠️ Provider Complaints</td>
                      <td class="text-center">Frequent</td>
                      <td class="text-center text-success">Rare/escalation only</td>
                      <td class="text-center"><span class="badge badge-success">40-60% reduction</span></td>
                    </tr>
                    <tr>
                      <td>❤️ Therapy Drop-offs</td>
                      <td class="text-center">12-18%</td>
                      <td class="text-center text-success">&lt;5%</td>
                      <td class="text-center"><span class="badge badge-success">3-4x better</span></td>
                    </tr>
                    <tr>
                      <td>💰 Cost Avoidance</td>
                      <td class="text-center">Minimal</td>
                      <td class="text-center text-success">$1.5-2.5M annually</td>
                      <td class="text-center"><span class="badge badge-success">Significant savings</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="decidedCases.length" class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              📋 Recent Decisions
            </div>
            <div class="card-body p-0">
              <div class="table-responsive">
                <table>
                  <thead>
                    <tr>
                      <th>Case ID</th>
                      <th>Title</th>
                      <th>AI Recommendation</th>
                      <th>Final Decision</th>
                      <th>Complexity</th>
                      <th>Turnaround</th>
                      <th>Decided At</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="caseItem in decidedCases.slice(0, 10)" :key="caseItem.id">
                      <td><router-link :to="`/case/${caseItem.id}`">{{ caseItem.id }}</router-link></td>
                      <td>{{ caseItem.title?.substring(0, 40) }}{{ caseItem.title?.length > 40 ? '...' : '' }}</td>
                      <td>
                        <span v-if="caseItem.ai_recommendation" :class="['badge', getRecommendationClass(caseItem.ai_recommendation.recommendation)]">
                          {{ caseItem.ai_recommendation.recommendation?.toUpperCase() }}
                        </span>
                        <span v-else>-</span>
                      </td>
                      <td>
                        <span :class="['badge', getRecommendationClass(caseItem.final_decision || '')]">
                          {{ caseItem.final_decision?.toUpperCase() }}
                        </span>
                      </td>
                      <td>
                        <span v-if="caseItem.complexity" :class="['badge', `complexity-${caseItem.complexity}`]">
                          {{ caseItem.complexity }}
                        </span>
                        <span v-else>-</span>
                      </td>
                      <td>{{ caseItem.turnaround_minutes || '-' }} min</td>
                      <td>{{ caseItem.decided_at?.substring(0, 16) || '-' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row mt-4">
        <div class="col-12">
          <div class="card bg-light">
            <div class="card-body">
              <h5>💡 Qualitative Gains</h5>
              <div class="row">
                <div class="col-md-6">
                  <ul class="mb-0">
                    <li>Clinically fair and consistent decisions</li>
                    <li>Higher provider trust through transparency</li>
                    <li>Better member outcomes due to faster approvals</li>
                  </ul>
                </div>
                <div class="col-md-6">
                  <ul class="mb-0">
                    <li>Improved audit & compliance defensibility</li>
                    <li>Medical team focuses on clinical value, not admin</li>
                    <li>Reduced burnout for Medical Directors</li>
                  </ul>
                </div>
              </div>
            </div>
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

.col-4 {
  flex: 0 0 33.333%;
  padding: 0.5rem;
}

.col-6 {
  flex: 0 0 50%;
  padding: 0.5rem;
}

.decision-box {
  padding: 1rem;
  border-radius: 0.5rem;
}

.decision-box h3 {
  margin-bottom: 0.5rem;
}

.decision-approve {
  background-color: rgba(25, 135, 84, 0.25);
  color: #198754;
}

.decision-deny {
  background-color: rgba(220, 53, 69, 0.25);
  color: #dc3545;
}

.decision-pend {
  background-color: rgba(255, 193, 7, 0.25);
  color: #856404;
}

.complexity-box {
  padding: 1rem;
  border-radius: 0.5rem;
}

.complexity-box h3 {
  margin-bottom: 0.5rem;
}

.complexity-low-box {
  background-color: rgba(25, 135, 84, 0.25);
  color: #155724;
}

.complexity-high-box {
  background-color: rgba(220, 53, 69, 0.25);
  color: #721c24;
}

.comparison-table {
  width: 100%;
}

.comparison-table th {
  background-color: #f8f9fa;
}
</style>
