import json
import os
import re
from openai import OpenAI

DEMO_MODE = not os.environ.get("OPENAI_API_KEY")

def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

SYSTEM_PROMPT = """You are a clinical prior authorization co-pilot for a health plan. 
You never make final decisions; you prepare structured summaries, recommendations, and draft letters 
based on policy and evidence. You must always obey the policy JSON when provided, and output valid JSON when asked.

You are highly knowledgeable about:
- Oncology drugs and treatment protocols
- NCCN Guidelines
- Clinical biomarkers and their significance
- Prior authorization criteria and medical necessity determinations

Always be precise, evidence-based, and cite specific clinical data from the case when making assessments."""


def extract_patient_info_demo(pa_text: str) -> dict:
    patient_info = {"name": "N/A", "dob": "N/A", "member_id": "N/A"}
    
    name_match = re.search(r'Patient:\s*([^\n\(]+)', pa_text)
    if name_match:
        patient_info["name"] = name_match.group(1).strip()
    
    dob_match = re.search(r'DOB:\s*(\d{1,2}/\d{1,2}/\d{4})', pa_text)
    if dob_match:
        patient_info["dob"] = dob_match.group(1)
    
    member_match = re.search(r'Member ID:\s*([^\n]+)', pa_text)
    if member_match:
        patient_info["member_id"] = member_match.group(1).strip()
    
    return patient_info


def extract_case_data_demo(pa_text: str) -> dict:
    patient_info = extract_patient_info_demo(pa_text)
    
    diagnosis = {"primary": "N/A", "icd10": "", "histology": ""}
    diag_match = re.search(r'Diagnosis:\s*([^\n]+)', pa_text)
    if diag_match:
        diagnosis["primary"] = diag_match.group(1).strip()
    icd_match = re.search(r'ICD-10:\s*([^\n]+)', pa_text)
    if icd_match:
        diagnosis["icd10"] = icd_match.group(1).strip()
    hist_match = re.search(r'Histology:\s*([^\n]+)', pa_text)
    if hist_match:
        diagnosis["histology"] = hist_match.group(1).strip()
    
    disease_stage = {"stage": "N/A", "tnm": "", "metastatic_sites": []}
    stage_match = re.search(r'Stage[:\s]+(IV|III|II|I)[\s\(]*([^\n\)]*)', pa_text, re.IGNORECASE)
    if stage_match:
        disease_stage["stage"] = f"Stage {stage_match.group(1).upper()}"
        if stage_match.group(2):
            disease_stage["tnm"] = stage_match.group(2).strip()
    
    met_match = re.search(r'[Mm]etastatic sites?:\s*([^\n]+)', pa_text)
    if met_match:
        disease_stage["metastatic_sites"] = [s.strip() for s in met_match.group(1).split(',')]
    
    pd_l1 = {"status": "not tested", "value": "", "test_date": ""}
    pdl1_match = re.search(r'PD-L1[^:]*:\s*(\d+)%', pa_text)
    if pdl1_match:
        value = int(pdl1_match.group(1))
        pd_l1["status"] = "positive" if value > 0 else "negative"
        pd_l1["value"] = f"{value}%"
    elif "pending" in pa_text.lower() and "pd-l1" in pa_text.lower():
        pd_l1["status"] = "pending"
    
    egfr = {"status": "not tested", "mutation": ""}
    if re.search(r'EGFR[:\s]+Wild type', pa_text, re.IGNORECASE):
        egfr["status"] = "wild type"
    elif re.search(r'EGFR[:\s]+(Exon \d+ [^\n,]+)', pa_text, re.IGNORECASE):
        egfr["status"] = "mutated"
        egfr_mut = re.search(r'EGFR[:\s]+(Exon \d+ [^\n,]+)', pa_text, re.IGNORECASE)
        if egfr_mut:
            egfr["mutation"] = egfr_mut.group(1).strip()
    elif "egfr" in pa_text.lower() and "pending" in pa_text.lower():
        egfr["status"] = "pending"
    
    alk = {"status": "not tested"}
    if re.search(r'ALK[:\s]+Negative', pa_text, re.IGNORECASE):
        alk["status"] = "negative"
    elif re.search(r'ALK[:\s]+Positive', pa_text, re.IGNORECASE):
        alk["status"] = "positive"
    
    performance_status = {"ecog": "", "description": ""}
    ecog_match = re.search(r'ECOG[:\s]+(\d)', pa_text)
    if ecog_match:
        performance_status["ecog"] = ecog_match.group(1)
    perf_desc = re.search(r'ECOG[:\s]+\d+\s*[-–]\s*([^\n]+)', pa_text)
    if perf_desc:
        performance_status["description"] = perf_desc.group(1).strip()
    
    prior_therapy = {"has_prior_systemic": False, "treatments": [], "immunotherapy_history": "none"}
    if re.search(r'No prior systemic', pa_text, re.IGNORECASE):
        prior_therapy["has_prior_systemic"] = False
        prior_therapy["treatments"] = ["No prior systemic therapy"]
    elif re.search(r'Prior [Tt]reatments?:', pa_text):
        prior_match = re.search(r'Prior [Tt]reatments?:\s*([^\n]+)', pa_text)
        if prior_match and "no prior" not in prior_match.group(1).lower():
            prior_therapy["has_prior_systemic"] = True
            prior_therapy["treatments"] = [prior_match.group(1).strip()]
    
    comorbidities = []
    comor_match = re.search(r'COMORBIDITIES:\s*([\s\S]*?)(?=RATIONALE|REQUESTING|$)', pa_text)
    if comor_match:
        comor_text = comor_match.group(1)
        comor_lines = [line.strip().strip('-').strip() for line in comor_text.split('\n') if line.strip() and line.strip() != '-']
        comorbidities = [c for c in comor_lines if c and len(c) > 2]
    
    provider = {"name": "", "npi": "", "facility": ""}
    prov_match = re.search(r'Requesting Provider:\s*([^\n]+)', pa_text)
    if prov_match:
        provider["name"] = prov_match.group(1).strip()
    npi_match = re.search(r'NPI:\s*(\d+)', pa_text)
    if npi_match:
        provider["npi"] = npi_match.group(1)
    
    drug = {"name": "", "dose": "", "duration": ""}
    drug_match = re.search(r'MEDICATION REQUESTED:\s*([^\n]+)', pa_text)
    if drug_match:
        drug["name"] = drug_match.group(1).strip()
    req_match = re.search(r'REQUESTING:\s*([^\n]+)', pa_text)
    if req_match:
        drug["duration"] = req_match.group(1).strip()
    
    return {
        "patient_info": patient_info,
        "diagnosis": diagnosis,
        "disease_stage": disease_stage,
        "biomarkers": {
            "pd_l1": pd_l1,
            "egfr": egfr,
            "alk": alk,
            "other_markers": []
        },
        "labs": {
            "wbc": "",
            "hemoglobin": "",
            "platelets": "",
            "creatinine": "",
            "alt": "",
            "ast": "",
            "other": []
        },
        "performance_status": performance_status,
        "prior_therapy": prior_therapy,
        "comorbidities": comorbidities,
        "requesting_provider": provider,
        "drug_requested": drug,
        "_demo_mode": True
    }


def extract_case_data(pa_text: str) -> dict:
    if DEMO_MODE:
        return extract_case_data_demo(pa_text)
    
    prompt = f"""Analyze this prior authorization request and extract structured clinical data.

PA REQUEST TEXT:
{pa_text}

Extract and return a JSON object with these exact fields:
{{
    "patient_info": {{
        "name": "patient name",
        "dob": "date of birth",
        "member_id": "member ID"
    }},
    "diagnosis": {{
        "primary": "primary diagnosis",
        "icd10": "ICD-10 code(s)",
        "histology": "histology type if applicable"
    }},
    "disease_stage": {{
        "stage": "cancer stage (e.g., Stage IV)",
        "tnm": "TNM staging if available",
        "metastatic_sites": ["list of metastatic sites"]
    }},
    "biomarkers": {{
        "pd_l1": {{
            "status": "positive/negative/pending/not tested",
            "value": "TPS percentage if available",
            "test_date": "date of test"
        }},
        "egfr": {{
            "status": "wild type/mutated/pending/not tested",
            "mutation": "specific mutation if detected"
        }},
        "alk": {{
            "status": "positive/negative/pending/not tested"
        }},
        "other_markers": [
            {{"name": "marker name", "result": "result"}}
        ]
    }},
    "labs": {{
        "wbc": "value with unit",
        "hemoglobin": "value with unit", 
        "platelets": "value with unit",
        "creatinine": "value with unit",
        "alt": "value with unit",
        "ast": "value with unit",
        "other": ["other relevant labs"]
    }},
    "performance_status": {{
        "ecog": "ECOG score (0-4)",
        "description": "brief description"
    }},
    "prior_therapy": {{
        "has_prior_systemic": true/false,
        "treatments": ["list of prior treatments"],
        "immunotherapy_history": "description or 'none'"
    }},
    "comorbidities": ["list of comorbidities"],
    "requesting_provider": {{
        "name": "provider name",
        "npi": "NPI number",
        "facility": "facility name"
    }},
    "drug_requested": {{
        "name": "drug name",
        "dose": "dose and frequency",
        "duration": "requested duration"
    }}
}}

Return ONLY valid JSON, no additional text."""

    try:
        client = get_openai_client()
        if not client:
            return extract_case_data_demo(pa_text)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content) if content else {"error": "Empty response"}
    except Exception as e:
        return {"error": str(e)}


def generate_recommendation_demo(case_data: dict, policy: dict, criteria_evaluation: list) -> dict:
    met_count = sum(1 for c in criteria_evaluation if c.get('status') == 'met')
    unmet_count = sum(1 for c in criteria_evaluation if c.get('status') == 'unmet')
    unknown_count = sum(1 for c in criteria_evaluation if c.get('status') == 'unknown')
    required = [c for c in criteria_evaluation if c.get('required', True)]
    required_met = sum(1 for c in required if c.get('status') == 'met')
    required_unmet = sum(1 for c in required if c.get('status') == 'unmet')
    required_unknown = sum(1 for c in required if c.get('status') == 'unknown')
    
    if required_unknown > 0:
        recommendation = "pend"
        confidence = "medium"
        complexity = "high"
        primary_reasons = [
            f"{required_unknown} required criteria cannot be evaluated due to missing information",
            "Additional documentation needed before determination can be made"
        ]
        info_gaps = [c['description'] for c in required if c.get('status') == 'unknown']
        rationale = f"This case requires additional information before a determination can be made. {required_unknown} required policy criteria have unknown status and need clarification."
    elif required_unmet > 0:
        recommendation = "deny"
        confidence = "high"
        complexity = "high"
        unmet_criteria = [c for c in required if c.get('status') == 'unmet']
        primary_reasons = [f"Criterion not met: {c['description']} - {c.get('evidence', '')}" for c in unmet_criteria[:3]]
        info_gaps = []
        rationale = f"This request does not meet {required_unmet} required policy criteria. The clinical evidence documented in the request does not satisfy the coverage requirements."
    else:
        recommendation = "approve"
        confidence = "high"
        complexity = "low"
        primary_reasons = [
            f"All {len(required)} required policy criteria are met",
            "Clinical documentation supports medical necessity",
            "Treatment aligns with current clinical guidelines"
        ]
        info_gaps = []
        rationale = f"Patient meets all required criteria for {policy.get('drug_name', 'the requested medication')}. Clinical evidence demonstrates medical necessity for the requested treatment."
    
    return {
        "recommendation": recommendation,
        "confidence": confidence,
        "complexity": complexity,
        "primary_reasons": primary_reasons,
        "information_gaps": info_gaps,
        "clinical_rationale": rationale,
        "guideline_alignment": f"Recommendation aligns with {policy.get('indication', 'indication')} treatment guidelines.",
        "risk_considerations": [],
        "alternative_options": [],
        "_demo_mode": True
    }


def generate_recommendation(case_data: dict, policy: dict, criteria_evaluation: list, guidelines: list) -> dict:
    if DEMO_MODE:
        return generate_recommendation_demo(case_data, policy, criteria_evaluation)
    
    prompt = f"""Based on the following clinical case data, policy criteria, and guidelines, generate a prior authorization recommendation.

EXTRACTED CASE DATA:
{json.dumps(case_data, indent=2)}

POLICY: {policy['drug_name']} - {policy['indication']}
Policy Description: {policy.get('description', '')}

CRITERIA EVALUATION:
{json.dumps(criteria_evaluation, indent=2)}

CLINICAL GUIDELINES:
{json.dumps(guidelines, indent=2)}

Generate a recommendation JSON with these exact fields:
{{
    "recommendation": "approve" | "deny" | "pend",
    "confidence": "high" | "medium" | "low",
    "complexity": "low" | "high",
    "primary_reasons": [
        "reason 1 with specific clinical evidence",
        "reason 2 with specific clinical evidence"
    ],
    "information_gaps": [
        "missing information 1",
        "missing information 2"
    ],
    "clinical_rationale": "A 2-3 sentence clinical rationale summarizing the key factors in this decision",
    "guideline_alignment": "How this recommendation aligns with NCCN/ICER guidelines",
    "risk_considerations": ["any clinical risks or considerations"],
    "alternative_options": ["alternative treatment options if applicable"]
}}

Decision Logic:
- APPROVE if all required criteria are MET and no critical information is missing
- DENY if any required criterion is clearly NOT MET based on documented evidence  
- PEND if required criteria cannot be evaluated due to missing/pending information

Return ONLY valid JSON."""

    try:
        client = get_openai_client()
        if not client:
            return generate_recommendation_demo(case_data, policy, criteria_evaluation)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content) if content else {"error": "Empty response", "recommendation": "pend"}
    except Exception as e:
        return {"error": str(e), "recommendation": "pend"}


def draft_letters_demo(case_data: dict, policy: dict, recommendation: dict) -> dict:
    rec = recommendation.get('recommendation', 'pend').upper()
    drug_name = policy.get('drug_name', 'the requested medication')
    indication = policy.get('indication', 'the stated indication')
    reasons = recommendation.get('primary_reasons', [])
    reasons_text = '\n'.join([f"  - {r}" for r in reasons]) if reasons else "  - See clinical rationale"
    
    if rec == 'APPROVE':
        provider_letter = f"""PRIOR AUTHORIZATION DETERMINATION

RE: {drug_name} for {indication}

Dear Healthcare Provider,

Following our review of the prior authorization request submitted for the above-referenced medication, we are pleased to inform you that this request has been APPROVED.

DETERMINATION: APPROVED
EFFECTIVE DATE: Upon receipt
AUTHORIZATION PERIOD: Per policy guidelines

CLINICAL RATIONALE:
{reasons_text}

The submitted clinical documentation demonstrates that the patient meets the applicable coverage criteria for {drug_name}. This authorization is valid for the standard treatment duration as outlined in our coverage policy.

Please ensure that all claims are submitted with the appropriate authorization reference number. If you have any questions regarding this determination, please contact our Provider Services line.

Sincerely,
Medical Management Department"""
        
        member_letter = f"""PRIOR AUTHORIZATION DECISION

Dear Member,

We have reviewed your doctor's request for {drug_name} to treat your condition.

DECISION: APPROVED

Good news! Your request has been approved. This means your health plan will cover this medication according to your plan benefits.

WHAT HAPPENS NEXT:
- Your doctor can now prescribe this medication
- Take the prescription to your pharmacy
- Your regular copay or coinsurance will apply

If you have any questions about this decision or your benefits, please call the Member Services number on the back of your ID card.

We wish you the best with your treatment.

Sincerely,
Member Services"""
    
    elif rec == 'DENY':
        provider_letter = f"""PRIOR AUTHORIZATION DETERMINATION

RE: {drug_name} for {indication}

Dear Healthcare Provider,

Following our review of the prior authorization request submitted for the above-referenced medication, we regret to inform you that this request has been DENIED.

DETERMINATION: DENIED
DATE OF DETERMINATION: Current Date

REASONS FOR DENIAL:
{reasons_text}

CLINICAL RATIONALE:
{recommendation.get('clinical_rationale', 'The submitted documentation does not meet the required coverage criteria.')}

APPEAL RIGHTS:
You and/or the member have the right to appeal this decision. To file an appeal, please submit additional clinical documentation addressing the criteria noted above within 180 days of this notice.

If you have questions about this determination or the appeal process, please contact our Provider Services line.

Sincerely,
Medical Management Department"""
        
        member_letter = f"""PRIOR AUTHORIZATION DECISION

Dear Member,

We have reviewed your doctor's request for {drug_name} to treat your condition.

DECISION: NOT APPROVED AT THIS TIME

We understand this may not be the answer you were hoping for. Here's why we made this decision:

The information your doctor sent us did not show that you meet all the requirements for this medication under your health plan.

WHAT YOU CAN DO:
1. Talk to your doctor about other treatment options that may be covered
2. Ask your doctor to send us more information and request another review
3. File an appeal if you disagree with this decision

HOW TO APPEAL:
You have the right to ask us to look at this decision again. Call the Member Services number on your ID card, and we will help you understand your options.

We're here to help. Please don't hesitate to contact us with any questions.

Sincerely,
Member Services"""
    
    else:
        info_gaps = recommendation.get('information_gaps', ['Additional clinical documentation'])
        gaps_text = '\n'.join([f"  - {g}" for g in info_gaps])
        
        provider_letter = f"""PRIOR AUTHORIZATION DETERMINATION

RE: {drug_name} for {indication}

Dear Healthcare Provider,

Following our review of the prior authorization request submitted for the above-referenced medication, we require additional information to complete our determination.

DETERMINATION: PENDED FOR ADDITIONAL INFORMATION
DATE: Current Date

INFORMATION NEEDED:
{gaps_text}

Please submit the requested documentation within 14 days to avoid delays in processing. Once received, we will complete our review and issue a determination.

SUBMISSION INSTRUCTIONS:
Please fax the requested information to our Medical Management department with the case reference number clearly noted.

If you have questions about the requested information, please contact our Provider Services line.

Sincerely,
Medical Management Department"""
        
        member_letter = f"""PRIOR AUTHORIZATION UPDATE

Dear Member,

We are reviewing your doctor's request for {drug_name} to treat your condition.

STATUS: WE NEED MORE INFORMATION

We don't have all the information we need to make a decision yet. We have asked your doctor to send us more details about your treatment.

WHAT HAPPENS NEXT:
- Your doctor will send us the information we requested
- Once we get it, we will finish our review
- We will send you another letter with our decision

You don't need to do anything right now. If you have questions, you can call the Member Services number on your ID card.

Thank you for your patience.

Sincerely,
Member Services"""
    
    return {
        "provider_letter": provider_letter,
        "member_letter": member_letter,
        "_demo_mode": True
    }


def draft_letters(case_data: dict, policy: dict, recommendation: dict) -> dict:
    if DEMO_MODE:
        return draft_letters_demo(case_data, policy, recommendation)
    
    prompt = f"""Generate two letters for this prior authorization decision.

CASE DATA:
{json.dumps(case_data, indent=2)}

POLICY: {policy['drug_name']} - {policy['indication']}

RECOMMENDATION: {json.dumps(recommendation, indent=2)}

Generate a JSON with two letters:
{{
    "provider_letter": "A formal, clinical letter to the requesting provider. Include:
        - Patient identification (use generic 'the patient' for privacy)
        - Decision and effective date
        - Clinical rationale with policy references
        - Specific criteria met or not met
        - If denied/pended: clear explanation of what is needed
        - Appeal rights information
        - Contact information placeholder
        This should be professional, detailed, and reference specific clinical findings.",
    
    "member_letter": "A simplified letter to the member/patient in plain language. Include:
        - Clear statement of the decision
        - Simple explanation of what this means
        - What happens next
        - If denied/pended: what they can do
        - How to get help or ask questions
        - Reassurance and support
        Use 6th-grade reading level, avoid medical jargon."
}}

Format each letter professionally with appropriate sections. Return ONLY valid JSON."""

    try:
        client = get_openai_client()
        if not client:
            return draft_letters_demo(case_data, policy, recommendation)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content) if content else {"error": "Empty response", "provider_letter": "", "member_letter": ""}
    except Exception as e:
        return {
            "error": str(e),
            "provider_letter": "Error generating letter. Please try again.",
            "member_letter": "Error generating letter. Please try again."
        }


def is_demo_mode() -> bool:
    return DEMO_MODE
