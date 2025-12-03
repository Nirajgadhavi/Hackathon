from typing import List, Dict, Any

def evaluate_criteria(case_data: dict, policy: dict) -> List[Dict]:
    criteria = policy.get('criteria', [])
    evaluations = []
    
    for criterion in criteria:
        evaluation = {
            'id': criterion['id'],
            'description': criterion['description'],
            'type': criterion['type'],
            'required': criterion.get('required', True),
            'status': 'unknown',
            'evidence': '',
            'details': ''
        }
        
        if criterion['type'] == 'stage':
            evaluation = evaluate_stage_criterion(case_data, criterion, evaluation)
        elif criterion['type'] == 'biomarker':
            evaluation = evaluate_biomarker_criterion(case_data, criterion, evaluation)
        elif criterion['type'] == 'prior_therapy':
            evaluation = evaluate_prior_therapy_criterion(case_data, criterion, evaluation)
        elif criterion['type'] == 'clinical':
            evaluation = evaluate_clinical_criterion(case_data, criterion, evaluation)
        
        evaluations.append(evaluation)
    
    return evaluations


def evaluate_stage_criterion(case_data: dict, criterion: dict, evaluation: dict) -> dict:
    disease_stage = case_data.get('disease_stage', {})
    stage = disease_stage.get('stage', '').lower()
    
    criterion_desc = criterion['description'].lower()
    
    if 'stage iv' in criterion_desc or 'stage 4' in criterion_desc or 'metastatic' in criterion_desc:
        if 'stage iv' in stage or 'stage 4' in stage or 'metastatic' in stage:
            evaluation['status'] = 'met'
            evaluation['evidence'] = f"Patient has {disease_stage.get('stage', 'Stage IV')}"
            if disease_stage.get('metastatic_sites'):
                evaluation['details'] = f"Metastatic sites: {', '.join(disease_stage['metastatic_sites'])}"
        elif stage:
            evaluation['status'] = 'unmet'
            evaluation['evidence'] = f"Patient stage is {disease_stage.get('stage')}, not Stage IV/metastatic"
        else:
            evaluation['status'] = 'unknown'
            evaluation['evidence'] = "Disease stage not documented"
    
    elif 'stage iii' in criterion_desc or 'stage 3' in criterion_desc:
        if 'stage iii' in stage or 'stage 3' in stage or 'stage iv' in stage or 'stage 4' in stage:
            evaluation['status'] = 'met'
            evaluation['evidence'] = f"Patient has {disease_stage.get('stage', 'Stage III+')}"
        elif stage:
            evaluation['status'] = 'unmet'
            evaluation['evidence'] = f"Patient stage is {disease_stage.get('stage')}"
        else:
            evaluation['status'] = 'unknown'
            evaluation['evidence'] = "Disease stage not documented"
    
    return evaluation


def evaluate_biomarker_criterion(case_data: dict, criterion: dict, evaluation: dict) -> dict:
    biomarkers = case_data.get('biomarkers', {})
    criterion_desc = criterion['description'].lower()
    
    if 'pd-l1' in criterion_desc or 'pdl1' in criterion_desc:
        pd_l1 = biomarkers.get('pd_l1', {})
        status = pd_l1.get('status', '').lower()
        value = pd_l1.get('value', '')
        
        if status == 'pending' or 'pending' in str(value).lower():
            evaluation['status'] = 'unknown'
            evaluation['evidence'] = "PD-L1 testing is pending"
            return evaluation
        
        if '>= 50%' in criterion_desc or '>=50%' in criterion_desc or 'tps >= 50' in criterion_desc:
            try:
                numeric_value = float(str(value).replace('%', '').strip())
                if numeric_value >= 50:
                    evaluation['status'] = 'met'
                    evaluation['evidence'] = f"PD-L1 TPS is {value} (>= 50% required)"
                else:
                    evaluation['status'] = 'unmet'
                    evaluation['evidence'] = f"PD-L1 TPS is {value} (< 50% required threshold)"
            except:
                if status == 'positive' or 'high' in status:
                    evaluation['status'] = 'met'
                    evaluation['evidence'] = f"PD-L1 status: {status}"
                elif status == 'negative' or 'low' in status:
                    evaluation['status'] = 'unmet'
                    evaluation['evidence'] = f"PD-L1 status: {status}"
                else:
                    evaluation['status'] = 'unknown'
                    evaluation['evidence'] = "PD-L1 level not clearly documented"
        else:
            if status in ['positive', 'detected']:
                evaluation['status'] = 'met'
                evaluation['evidence'] = f"PD-L1 {status}: {value}" if value else f"PD-L1 {status}"
            elif status in ['negative', 'not detected']:
                evaluation['status'] = 'unmet'
                evaluation['evidence'] = f"PD-L1 {status}"
            elif status == 'not tested':
                evaluation['status'] = 'unknown'
                evaluation['evidence'] = "PD-L1 not tested"
            else:
                evaluation['status'] = 'unknown'
                evaluation['evidence'] = "PD-L1 status unclear"
    
    elif 'egfr' in criterion_desc:
        egfr = biomarkers.get('egfr', {})
        status = egfr.get('status', '').lower()
        mutation = egfr.get('mutation', '')
        
        if status == 'pending':
            evaluation['status'] = 'unknown'
            evaluation['evidence'] = "EGFR testing is pending"
        elif 'no egfr' in criterion_desc or 'egfr negative' in criterion_desc or 'no' in criterion_desc:
            if status in ['wild type', 'negative', 'not detected', 'no mutations']:
                evaluation['status'] = 'met'
                evaluation['evidence'] = f"EGFR: {status} (no mutations detected)"
            elif status in ['mutated', 'positive', 'detected'] or mutation:
                evaluation['status'] = 'unmet'
                evaluation['evidence'] = f"EGFR mutation detected: {mutation or status}"
            elif status == 'not tested':
                evaluation['status'] = 'unknown'
                evaluation['evidence'] = "EGFR not tested"
            else:
                evaluation['status'] = 'unknown'
                evaluation['evidence'] = "EGFR status unclear"
        else:
            if status in ['mutated', 'positive', 'detected'] or mutation:
                evaluation['status'] = 'met'
                evaluation['evidence'] = f"EGFR mutation: {mutation or 'detected'}"
            else:
                evaluation['status'] = 'unmet'
                evaluation['evidence'] = f"EGFR: {status}"
    
    elif 'alk' in criterion_desc:
        alk = biomarkers.get('alk', {})
        status = alk.get('status', '').lower()
        
        if status == 'pending':
            evaluation['status'] = 'unknown'
            evaluation['evidence'] = "ALK testing is pending"
        elif 'no alk' in criterion_desc or 'alk negative' in criterion_desc or 'no' in criterion_desc:
            if status in ['negative', 'not detected', 'no rearrangement']:
                evaluation['status'] = 'met'
                evaluation['evidence'] = f"ALK: {status} (no rearrangement)"
            elif status in ['positive', 'detected', 'rearranged']:
                evaluation['status'] = 'unmet'
                evaluation['evidence'] = f"ALK rearrangement detected"
            elif status == 'not tested':
                evaluation['status'] = 'unknown'
                evaluation['evidence'] = "ALK not tested"
            else:
                evaluation['status'] = 'unknown'
                evaluation['evidence'] = "ALK status unclear"
    
    elif 'braf' in criterion_desc:
        other_markers = biomarkers.get('other_markers', [])
        braf_result = None
        for marker in other_markers:
            if 'braf' in marker.get('name', '').lower():
                braf_result = marker.get('result', '').lower()
                break
        
        if braf_result:
            if 'determined' in criterion_desc.lower():
                evaluation['status'] = 'met'
                evaluation['evidence'] = f"BRAF status determined: {braf_result}"
            elif 'negative' in criterion_desc or 'wild type' in criterion_desc:
                if 'wild type' in braf_result or 'negative' in braf_result:
                    evaluation['status'] = 'met'
                    evaluation['evidence'] = f"BRAF: {braf_result}"
                else:
                    evaluation['status'] = 'unmet'
                    evaluation['evidence'] = f"BRAF mutation detected: {braf_result}"
        else:
            if 'determined' in criterion_desc.lower():
                evaluation['status'] = 'unknown'
                evaluation['evidence'] = "BRAF status not documented"
    
    return evaluation


def evaluate_prior_therapy_criterion(case_data: dict, criterion: dict, evaluation: dict) -> dict:
    prior_therapy = case_data.get('prior_therapy', {})
    has_prior = prior_therapy.get('has_prior_systemic', False)
    treatments = prior_therapy.get('treatments', [])
    
    criterion_desc = criterion['description'].lower()
    
    if 'no prior' in criterion_desc or 'first-line' in criterion_desc or 'first line' in criterion_desc:
        if not has_prior or len(treatments) == 0 or all('no prior' in t.lower() for t in treatments):
            evaluation['status'] = 'met'
            evaluation['evidence'] = "No prior systemic therapy documented"
        else:
            evaluation['status'] = 'unmet'
            evaluation['evidence'] = f"Prior treatments: {', '.join(treatments)}"
    else:
        if has_prior and len(treatments) > 0:
            evaluation['status'] = 'met'
            evaluation['evidence'] = f"Prior treatments: {', '.join(treatments)}"
        else:
            evaluation['status'] = 'unmet'
            evaluation['evidence'] = "No prior therapy documented"
    
    return evaluation


def evaluate_clinical_criterion(case_data: dict, criterion: dict, evaluation: dict) -> dict:
    criterion_desc = criterion['description'].lower()
    
    if 'ecog' in criterion_desc or 'performance status' in criterion_desc:
        perf_status = case_data.get('performance_status', {})
        ecog = perf_status.get('ecog', '')
        
        try:
            ecog_value = int(str(ecog).strip())
            
            if 'ecog 0-1' in criterion_desc or 'ecog performance status 0-1' in criterion_desc:
                if ecog_value <= 1:
                    evaluation['status'] = 'met'
                    evaluation['evidence'] = f"ECOG Performance Status: {ecog_value}"
                else:
                    evaluation['status'] = 'unmet'
                    evaluation['evidence'] = f"ECOG {ecog_value} exceeds 0-1 requirement"
            elif 'ecog 0-2' in criterion_desc or 'ecog performance status 0-2' in criterion_desc:
                if ecog_value <= 2:
                    evaluation['status'] = 'met'
                    evaluation['evidence'] = f"ECOG Performance Status: {ecog_value}"
                else:
                    evaluation['status'] = 'unmet'
                    evaluation['evidence'] = f"ECOG {ecog_value} exceeds 0-2 requirement"
        except:
            evaluation['status'] = 'unknown'
            evaluation['evidence'] = "ECOG Performance Status not clearly documented"
    
    elif 'brain metastases' in criterion_desc or 'brain metastasis' in criterion_desc:
        disease_stage = case_data.get('disease_stage', {})
        metastatic_sites = disease_stage.get('metastatic_sites', [])
        
        has_brain_mets = any('brain' in site.lower() for site in metastatic_sites)
        
        if 'no active brain' in criterion_desc:
            if not has_brain_mets:
                evaluation['status'] = 'met'
                evaluation['evidence'] = "No brain metastases documented"
            else:
                evaluation['status'] = 'unknown'
                evaluation['evidence'] = "Brain metastases present - stability status needs verification"
        else:
            if has_brain_mets:
                evaluation['status'] = 'met'
                evaluation['evidence'] = "Brain metastases documented"
            else:
                evaluation['status'] = 'unmet'
                evaluation['evidence'] = "No brain metastases documented"
    
    return evaluation


def calculate_complexity(criteria_evaluations: list) -> str:
    required_criteria = [c for c in criteria_evaluations if c.get('required', True)]
    
    unknown_count = sum(1 for c in required_criteria if c['status'] == 'unknown')
    unmet_count = sum(1 for c in required_criteria if c['status'] == 'unmet')
    
    if unknown_count > 0 or unmet_count > 0:
        return 'high'
    return 'low'


def get_triage_summary(criteria_evaluations: list) -> dict:
    total = len(criteria_evaluations)
    met = sum(1 for c in criteria_evaluations if c['status'] == 'met')
    unmet = sum(1 for c in criteria_evaluations if c['status'] == 'unmet')
    unknown = sum(1 for c in criteria_evaluations if c['status'] == 'unknown')
    
    required = [c for c in criteria_evaluations if c.get('required', True)]
    required_met = sum(1 for c in required if c['status'] == 'met')
    required_total = len(required)
    
    return {
        'total_criteria': total,
        'met': met,
        'unmet': unmet,
        'unknown': unknown,
        'required_criteria': required_total,
        'required_met': required_met,
        'all_required_met': required_met == required_total and all(c['status'] == 'met' for c in required),
        'has_unmet_required': any(c['status'] == 'unmet' for c in required),
        'has_unknown_required': any(c['status'] == 'unknown' for c in required)
    }
