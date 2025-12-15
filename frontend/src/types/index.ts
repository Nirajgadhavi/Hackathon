export interface PatientInfo {
  name: string
  dob: string
  member_id: string
}

export interface Diagnosis {
  primary: string
  icd10: string
  histology: string
}

export interface DiseaseStage {
  stage: string
  tnm: string
  metastatic_sites: string[]
}

export interface Biomarker {
  status: string
  value?: string
  mutation?: string
  test_date?: string
}

export interface Biomarkers {
  pd_l1: Biomarker
  egfr: Biomarker
  alk: Biomarker
  other_markers: { name: string; result: string }[]
}

export interface PerformanceStatus {
  ecog: string
  description: string
}

export interface PriorTherapy {
  has_prior_systemic: boolean
  treatments: string[]
  immunotherapy_history: string
}

export interface ExtractedData {
  patient_info: PatientInfo
  diagnosis: Diagnosis
  disease_stage: DiseaseStage
  biomarkers: Biomarkers
  labs: Record<string, string | string[]>
  performance_status: PerformanceStatus
  prior_therapy: PriorTherapy
  comorbidities: string[]
  requesting_provider: { name: string; npi: string; facility: string }
  drug_requested: { name: string; dose: string; duration: string }
  _demo_mode?: boolean
}

export interface CriterionEvaluation {
  id: string
  description: string
  status: 'met' | 'unmet' | 'unknown'
  required: boolean
  evidence?: string
}

export interface AIRecommendation {
  recommendation: 'approve' | 'deny' | 'pend'
  confidence: 'high' | 'medium' | 'low'
  complexity: 'low' | 'high'
  primary_reasons: string[]
  information_gaps: string[]
  clinical_rationale: string
  guideline_alignment: string
  risk_considerations: string[]
  alternative_options: string[]
  _demo_mode?: boolean
}

export interface Guideline {
  source: string
  text: string
}

export interface Policy {
  id: string
  drug_name: string
  indication: string
  description: string
  criteria: CriterionEvaluation[]
  guidelines: Guideline[]
}

export interface Case {
  id: string
  title: string
  raw_text: string
  policy_id: string
  status: 'pending' | 'processed' | 'decided'
  extracted_data: ExtractedData | null
  criteria_evaluation: CriterionEvaluation[] | null
  ai_recommendation: AIRecommendation | null
  provider_letter: string
  member_letter: string
  final_decision: 'approve' | 'deny' | 'pend' | null
  final_decision_notes: string
  complexity: 'low' | 'high' | null
  created_at: string
  processed_at: string | null
  decided_at: string | null
  turnaround_minutes: number | null
  drug_name: string
  indication: string
  policy_description?: string
  policy_criteria?: CriterionEvaluation[]
  policy_guidelines?: Guideline[]
}

export interface Metrics {
  total_cases: number
  pending_cases: number
  processed_cases: number
  decided_cases: number
  avg_turnaround_minutes: number
  decisions: Record<string, number>
  complexity_distribution: Record<string, number>
}

export interface DemoModeStatus {
  demo_mode: boolean
}
