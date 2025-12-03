from src.models.database import insert_policy, insert_case, init_db, get_all_policies

POLICIES = [
    {
        "id": "POL-ONC-001",
        "drug_name": "Keytruda (Pembrolizumab)",
        "indication": "Non-Small Cell Lung Cancer (NSCLC)",
        "description": "Coverage policy for Keytruda (pembrolizumab) for the treatment of metastatic non-small cell lung cancer with high PD-L1 expression.",
        "criteria": [
            {
                "id": "C1",
                "description": "Patient has histologically or cytologically confirmed metastatic NSCLC (Stage IV)",
                "type": "stage",
                "required": True
            },
            {
                "id": "C2", 
                "description": "Tumor expresses PD-L1 (Tumor Proportion Score >= 50%) as determined by FDA-approved test",
                "type": "biomarker",
                "required": True
            },
            {
                "id": "C3",
                "description": "No EGFR or ALK genomic tumor aberrations present",
                "type": "biomarker",
                "required": True
            },
            {
                "id": "C4",
                "description": "ECOG Performance Status 0-1",
                "type": "clinical",
                "required": True
            },
            {
                "id": "C5",
                "description": "No prior systemic chemotherapy for metastatic NSCLC (first-line treatment)",
                "type": "prior_therapy",
                "required": False
            }
        ],
        "guidelines": [
            {
                "source": "NCCN Guidelines",
                "text": "Pembrolizumab is recommended as first-line therapy for patients with metastatic NSCLC with PD-L1 expression >= 50% and no EGFR/ALK aberrations. The recommendation is Category 1, based on high-level evidence from KEYNOTE-024 and KEYNOTE-042 trials showing significant improvement in overall survival compared to platinum-based chemotherapy."
            },
            {
                "source": "ICER Report",
                "text": "ICER's 2020 assessment found pembrolizumab monotherapy for first-line NSCLC with high PD-L1 expression to be cost-effective at a threshold of $150,000 per QALY. The incremental cost-effectiveness ratio was estimated at $122,000/QALY compared to chemotherapy alone."
            },
            {
                "source": "Internal Clinical Policy",
                "text": "Keytruda is approved for first-line treatment of metastatic NSCLC when: (1) PD-L1 TPS >= 50%, (2) No targetable mutations (EGFR, ALK, ROS1, BRAF, NTRK, MET, RET), (3) Adequate organ function, (4) No active autoimmune disease requiring systemic treatment. Treatment should be administered at 200mg Q3W or 400mg Q6W until disease progression or unacceptable toxicity, up to 24 months."
            }
        ]
    },
    {
        "id": "POL-ONC-002",
        "drug_name": "Opdivo (Nivolumab)",
        "indication": "Advanced Melanoma",
        "description": "Coverage policy for Opdivo (nivolumab) for the treatment of unresectable or metastatic melanoma.",
        "criteria": [
            {
                "id": "C1",
                "description": "Patient has histologically confirmed unresectable Stage III or metastatic Stage IV melanoma",
                "type": "stage",
                "required": True
            },
            {
                "id": "C2",
                "description": "BRAF mutation status has been determined",
                "type": "biomarker",
                "required": True
            },
            {
                "id": "C3",
                "description": "ECOG Performance Status 0-2",
                "type": "clinical",
                "required": True
            },
            {
                "id": "C4",
                "description": "No active brain metastases (treated and stable brain metastases allowed)",
                "type": "clinical",
                "required": True
            }
        ],
        "guidelines": [
            {
                "source": "NCCN Guidelines",
                "text": "Nivolumab is recommended as first-line therapy for unresectable or metastatic melanoma regardless of BRAF status. For BRAF-mutant melanoma, both immunotherapy and targeted therapy are options; immunotherapy preferred for patients with low tumor burden and good performance status."
            },
            {
                "source": "Internal Clinical Policy",
                "text": "Opdivo is approved for first-line or subsequent treatment of unresectable or metastatic melanoma. Dosing: 480mg IV every 4 weeks or 240mg IV every 2 weeks. Treatment continues until disease progression, unacceptable toxicity, or completion of 2 years of therapy."
            }
        ]
    }
]

CASES = [
    {
        "id": "PA-2024-001",
        "title": "Stage IV NSCLC - High PD-L1 - First Line Keytruda",
        "policy_id": "POL-ONC-001",
        "raw_text": """PRIOR AUTHORIZATION REQUEST

Patient: John Smith (DOB: 03/15/1958)
Member ID: MEM-789456123
Date of Request: 11/28/2024
Requesting Provider: Dr. Sarah Chen, MD - Valley Oncology Associates
NPI: 1234567890

MEDICATION REQUESTED: Keytruda (pembrolizumab) 200mg IV every 3 weeks

CLINICAL INFORMATION:

Diagnosis: Metastatic Non-Small Cell Lung Cancer (NSCLC) - Adenocarcinoma
ICD-10: C34.90, C78.00

Disease Stage: Stage IV (T3N2M1a) - diagnosed October 2024
Metastatic sites: Contralateral lung nodules, mediastinal lymph nodes

Histology: Adenocarcinoma confirmed by CT-guided biopsy (10/15/2024)

BIOMARKER TESTING (Foundation Medicine CDx - 10/22/2024):
- PD-L1 TPS: 75% (Positive, High Expression)
- EGFR: Wild type (No mutations detected)
- ALK: Negative (No rearrangement)
- ROS1: Negative
- BRAF: Wild type
- KRAS: G12C mutation detected

LABORATORY VALUES (11/20/2024):
- WBC: 7.2 x10^9/L (Normal)
- Hemoglobin: 12.1 g/dL (Slightly low)
- Platelets: 245 x10^9/L (Normal)
- Creatinine: 0.9 mg/dL (Normal)
- ALT: 28 U/L (Normal)
- AST: 32 U/L (Normal)
- Total Bilirubin: 0.8 mg/dL (Normal)

PERFORMANCE STATUS: ECOG 1 - Restricted in strenuous activity but ambulatory

PRIOR TREATMENTS: 
- No prior systemic therapy for lung cancer
- Former smoker (quit 2019, 30 pack-year history)
- No prior immunotherapy or checkpoint inhibitors

COMORBIDITIES:
- Hypertension (controlled on lisinopril)
- Type 2 Diabetes (controlled, A1C 6.8%)
- No autoimmune conditions
- No history of organ transplant

RATIONALE FOR KEYTRUDA:
Patient meets criteria for first-line pembrolizumab monotherapy per NCCN Guidelines based on high PD-L1 expression (TPS 75%), absence of targetable driver mutations (EGFR, ALK negative), and good performance status. Immunotherapy preferred over chemotherapy given high PD-L1 expression and favorable side effect profile.

REQUESTING: Approval for Keytruda 200mg IV Q3W x 24 months or until progression

Attachments: Pathology report, PD-L1 testing results, CT scan report, Lab results
"""
    },
    {
        "id": "PA-2024-002", 
        "title": "NSCLC - Low PD-L1 - Keytruda Denial Expected",
        "policy_id": "POL-ONC-001",
        "raw_text": """PRIOR AUTHORIZATION REQUEST

Patient: Maria Garcia (DOB: 07/22/1965)
Member ID: MEM-456789012
Date of Request: 11/29/2024
Requesting Provider: Dr. Michael Brown, MD - City Cancer Center
NPI: 9876543210

MEDICATION REQUESTED: Keytruda (pembrolizumab) 200mg IV every 3 weeks

CLINICAL INFORMATION:

Diagnosis: Metastatic Non-Small Cell Lung Cancer (NSCLC) - Squamous Cell Carcinoma
ICD-10: C34.11, C78.01

Disease Stage: Stage IV (T4N3M1b) - diagnosed September 2024
Metastatic sites: Liver, bone (L3 vertebra)

Histology: Squamous cell carcinoma confirmed by bronchoscopic biopsy (09/10/2024)

BIOMARKER TESTING (PD-L1 IHC 22C3 - 09/18/2024):
- PD-L1 TPS: 15% (Low Expression)
- EGFR: Not tested (squamous histology)
- ALK: Not tested (squamous histology)

LABORATORY VALUES (11/25/2024):
- WBC: 11.2 x10^9/L (Elevated)
- Hemoglobin: 10.5 g/dL (Low)
- Platelets: 189 x10^9/L (Normal)
- Creatinine: 1.4 mg/dL (Slightly elevated)
- ALT: 52 U/L (Slightly elevated)
- AST: 48 U/L (Slightly elevated)

PERFORMANCE STATUS: ECOG 2 - Capable of self-care but unable to work

PRIOR TREATMENTS: 
- No prior systemic therapy for lung cancer

COMORBIDITIES:
- COPD (on home oxygen 2L)
- Coronary artery disease (stent placed 2020)
- Chronic kidney disease Stage 3

RATIONALE FOR KEYTRUDA:
Patient has metastatic squamous NSCLC. Requesting pembrolizumab monotherapy.

REQUESTING: Approval for Keytruda 200mg IV Q3W

Attachments: Pathology report, PD-L1 testing results
"""
    },
    {
        "id": "PA-2024-003",
        "title": "NSCLC - Missing Biomarker Data - Pend for Info",
        "policy_id": "POL-ONC-001", 
        "raw_text": """PRIOR AUTHORIZATION REQUEST

Patient: Robert Johnson (DOB: 11/08/1952)
Member ID: MEM-321654987
Date of Request: 11/30/2024
Requesting Provider: Dr. Emily White, MD - Regional Medical Oncology
NPI: 5678901234

MEDICATION REQUESTED: Keytruda (pembrolizumab) 200mg IV every 3 weeks

CLINICAL INFORMATION:

Diagnosis: Non-Small Cell Lung Cancer (NSCLC) - Adenocarcinoma
ICD-10: C34.31

Disease Stage: Stage IV (metastatic to brain) - diagnosed November 2024
Metastatic sites: Multiple brain lesions (treated with SRS 11/15/2024)

Histology: Adenocarcinoma confirmed by CT-guided biopsy (11/05/2024)

BIOMARKER TESTING:
- PD-L1: PENDING - specimen sent to reference lab, results expected in 5-7 days
- EGFR/ALK: Testing ordered but results not yet available
- Next-generation sequencing panel ordered

LABORATORY VALUES (11/28/2024):
- WBC: 6.8 x10^9/L (Normal)
- Hemoglobin: 13.2 g/dL (Normal)
- Platelets: 267 x10^9/L (Normal)
- Creatinine: 1.0 mg/dL (Normal)
- LFTs: Within normal limits

PERFORMANCE STATUS: ECOG 1

PRIOR TREATMENTS: 
- Stereotactic radiosurgery to brain metastases (11/15/2024)
- No prior systemic therapy

COMORBIDITIES:
- Well-controlled hypertension
- No autoimmune conditions

RATIONALE FOR KEYTRUDA:
Patient has newly diagnosed metastatic NSCLC with brain metastases now treated with SRS. Biomarker testing is in progress. Requesting expedited review and conditional approval pending biomarker results to avoid treatment delays.

REQUESTING: Expedited approval for Keytruda pending biomarker confirmation

Attachments: Pathology report, Brain MRI, SRS treatment summary
"""
    },
    {
        "id": "PA-2024-004",
        "title": "Stage IV Melanoma - Opdivo First Line",
        "policy_id": "POL-ONC-002",
        "raw_text": """PRIOR AUTHORIZATION REQUEST

Patient: Angela Williams (DOB: 05/30/1970)
Member ID: MEM-654987321
Date of Request: 12/01/2024
Requesting Provider: Dr. James Lee, MD - Dermatology & Oncology Specialists
NPI: 3456789012

MEDICATION REQUESTED: Opdivo (nivolumab) 480mg IV every 4 weeks

CLINICAL INFORMATION:

Diagnosis: Metastatic Melanoma
ICD-10: C43.9, C78.7

Disease Stage: Stage IV (M1c) - initially diagnosed Stage IIIB in 2023, progressed to Stage IV October 2024
Metastatic sites: Liver (3 lesions), lung nodules

Primary Site: Left upper back, surgically excised in 2023
Histology: Melanoma confirmed by biopsy, Breslow depth 4.2mm, ulcerated

BIOMARKER TESTING (11/15/2024):
- BRAF V600E: Negative (Wild type)
- NRAS: Wild type
- c-KIT: Wild type
- LDH: 285 U/L (Elevated, 1.3x ULN)

IMAGING:
- PET-CT (11/10/2024): Multiple hepatic metastases, bilateral pulmonary nodules, no brain involvement
- Brain MRI (11/12/2024): No evidence of brain metastases

LABORATORY VALUES (11/28/2024):
- WBC: 5.9 x10^9/L (Normal)
- Hemoglobin: 11.8 g/dL (Slightly low)
- Platelets: 198 x10^9/L (Normal)
- Creatinine: 0.8 mg/dL (Normal)
- ALT: 45 U/L (Normal)
- AST: 42 U/L (Normal)
- LDH: 285 U/L (Elevated)

PERFORMANCE STATUS: ECOG 0 - Fully active, no restrictions

PRIOR TREATMENTS:
- Wide local excision with sentinel lymph node biopsy (2023)
- Adjuvant radiation to primary site (2023)
- No prior systemic therapy for melanoma

COMORBIDITIES:
- Hypothyroidism (on levothyroxine)
- No autoimmune conditions
- No active infections

RATIONALE FOR OPDIVO:
Patient has BRAF wild-type metastatic melanoma with visceral disease. Immunotherapy with nivolumab is first-line treatment per NCCN Guidelines. Patient has excellent performance status and no contraindications to checkpoint inhibitor therapy.

REQUESTING: Approval for Opdivo 480mg IV Q4W x 24 months or until progression

Attachments: Pathology report, BRAF mutation testing, PET-CT report, Brain MRI report
"""
    },
    {
        "id": "PA-2024-005",
        "title": "NSCLC with EGFR Mutation - Keytruda Not Appropriate",
        "policy_id": "POL-ONC-001",
        "raw_text": """PRIOR AUTHORIZATION REQUEST

Patient: David Chen (DOB: 02/14/1968)
Member ID: MEM-147258369
Date of Request: 12/02/2024
Requesting Provider: Dr. Lisa Park, MD - University Oncology
NPI: 7890123456

MEDICATION REQUESTED: Keytruda (pembrolizumab) 200mg IV every 3 weeks

CLINICAL INFORMATION:

Diagnosis: Metastatic Non-Small Cell Lung Cancer (NSCLC) - Adenocarcinoma
ICD-10: C34.90, C78.00

Disease Stage: Stage IV (T2N2M1a) - diagnosed October 2024
Metastatic sites: Contralateral lung, pleural effusion

Histology: Adenocarcinoma confirmed by bronchoscopic biopsy (10/08/2024)

BIOMARKER TESTING (Guardant360 - 10/20/2024):
- PD-L1 TPS: 60% (High Expression)
- EGFR: Exon 19 deletion DETECTED
- ALK: Negative
- ROS1: Negative
- BRAF: Wild type

LABORATORY VALUES (11/30/2024):
- WBC: 7.5 x10^9/L (Normal)
- Hemoglobin: 12.8 g/dL (Normal)
- Platelets: 225 x10^9/L (Normal)
- Creatinine: 0.9 mg/dL (Normal)
- LFTs: Within normal limits

PERFORMANCE STATUS: ECOG 1

PRIOR TREATMENTS:
- No prior systemic therapy

COMORBIDITIES:
- None significant

RATIONALE FOR KEYTRUDA:
Patient has metastatic NSCLC with high PD-L1 expression. Requesting first-line immunotherapy.

REQUESTING: Approval for Keytruda 200mg IV Q3W

Attachments: Pathology report, Molecular testing results
"""
    }
]

def seed_database():
    init_db()
    
    existing_policies = get_all_policies()
    if not existing_policies:
        for policy in POLICIES:
            insert_policy(policy)
        print(f"Seeded {len(POLICIES)} policies")
        
        for case in CASES:
            insert_case(case)
        print(f"Seeded {len(CASES)} cases")
    else:
        print("Database already contains data, skipping seed")

if __name__ == "__main__":
    seed_database()
