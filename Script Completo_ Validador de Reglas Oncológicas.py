
#!/usr/bin/env python3
"""
Validador de Reglas de Negocio Oncológicas
==========================================
Valida compliance con protocolos de cáncer de mama usando SHACL + SPARQL

Uso:
    python3 oncology_validator.py --patient BC-2025-001
    python3 oncology_validator.py --all
    python3 oncology_validator.py --report
"""

import json
import sys
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# ========================================
# TIPOS Y ENUMS
# ========================================

class RuleSeverity(Enum):
    """Niveles de severidad de reglas"""
    CRITICAL = "🔴 CRITICAL"
    HIGH = "🟠 HIGH"
    MEDIUM = "🟡 MEDIUM"
    LOW = "🟢 LOW"
    INFO = "ℹ️  INFO"

class RuleStatus(Enum):
    """Estados de reglas"""
    COMPLIANT = "✅ COMPLIANT"
    WARNING = "⚠️  WARNING"
    VIOLATION = "❌ VIOLATION"

@dataclass
class RuleResult:
    """Resultado de validación de una regla"""
    rule_name: str
    rule_id: str
    status: RuleStatus
    severity: RuleSeverity
    message: str
    action: Optional[str] = None
    details: Optional[Dict] = None
    affected_field: Optional[str] = None

# ========================================
# DATOS DE PACIENTES (Simulado)
# ========================================

PATIENTS_DB = {
    "BC-2025-001": {
        "mrn": "BC-2025-001",
        "name": "María García",
        "age": 55,
        "gender": "female",
        "diagnosis": {
            "code": "254837009",
            "name": "Invasive Ductal Carcinoma",
            "stage": "IIA",
            "status": "active",
            "date": "2025-08-15"
        },
        "observations": {
            "er_status": {"value": "Positive", "date": "2025-10-28"},
            "pr_status": {"value": "Positive", "date": "2025-10-28"},
            "her2_status": {"value": "negative", "date": "2025-10-28"},
            "ki67": {"value": "25%", "date": "2025-10-28"},
            "brca1": {"value": "Present", "date": "2025-10-28"},
            "grade": {"value": "III", "date": "2025-10-28"}
        },
        "medications": [
            {
                "name": "Tamoxifen",
                "dose": "20 mg",
                "frequency": "once daily",
                "start_date": "2025-10-28",
                "end_date": "2026-10-28"
            },
            {
                "name": "Fluconazole",
                "dose": "200 mg",
                "frequency": "daily",
                "start_date": "2025-10-20",
                "reason": "fungal infection"
            }
        ],
        "consultations": [
            {"type": "genetic_counseling", "date": "2025-10-20"}
        ],
        "imaging": []
    },
    
    "BC-2025-042": {
        "mrn": "BC-2025-042",
        "name": "Patricia López",
        "age": 48,
        "gender": "female",
        "diagnosis": {
            "code": "254837009",
            "name": "Invasive Ductal Carcinoma",
            "stage": "IIIB",
            "status": "active",
            "date": "2025-09-01"
        },
        "observations": {
            "er_status": {"value": "Positive", "date": "2025-10-15"},
            "pr_status": {"value": "Positive", "date": "2025-10-15"},
            "her2_status": {"value": "3+", "date": "2025-10-15"},
            "brca1": {"value": "Present", "date": "2025-10-15"},
        },
        "medications": [
            # ❌ FALTA terapia hormonal
            # ❌ FALTA Herceptin
        ],
        "consultations": [
            # ❌ FALTA genetic counseling
        ],
        "imaging": []
    },
    
    "BC-2025-089": {
        "mrn": "BC-2025-089",
        "name": "Carmen Sánchez",
        "age": 38,
        "gender": "female",
        "diagnosis": {
            "code": "254837009",
            "name": "Invasive Ductal Carcinoma",
            "stage": "II",
            "status": "active",
            "date": "2025-07-10"
        },
        "observations": {
            "er_status": {"value": "Positive", "date": "2025-10-10"},
            "pr_status": {"value": "Negative", "date": "2025-10-10"},
            "her2_status": {"value": "negative", "date": "2025-10-10"},
        },
        "medications": [],  # ❌ SIN TERAPIA
        "consultations": [
            {"type": "fertility_preservation", "date": "2025-08-01"}
        ],
        "imaging": []
    },
    
    "BC-2025-156": {
        "mrn": "BC-2025-156",
        "name": "Rosa Martínez",
        "age": 62,
        "gender": "female",
        "diagnosis": {
            "code": "254837009",
            "name": "Metastatic Breast Cancer",
            "stage": "IV",
            "status": "active",
            "metastatic_sites": ["bones", "liver"],
            "date": "2025-05-20"
        },
        "observations": {
            "her2_status": {"value": "3+", "date": "2025-10-01"},
        },
        "medications": [
            {
                "name": "Paclitaxel",
                "dose": "80 mg/m2",
                "frequency": "weekly",
                "start_date": "2025-09-01"
            }
            # ❌ FALTA Herceptin para HER2+
        ],
        "consultations": [],
        "imaging": [
            {"type": "CT", "date": "2025-10-20"},
            # ❌ FALTA PET-CT
            # ❌ FALTA Bone Scan
        ]
    }
}

# ========================================
# VALIDADOR DE REGLAS ONCOLÓGICAS
# ========================================

class OncologyRulesValidator:
    """Validador de reglas de negocio oncológicas"""
    
    def __init__(self):
        self.rules = self._define_rules()
        self.patients = PATIENTS_DB
    
    def _define_rules(self) -> List[Dict]:
        """Definir todas las reglas de validación"""
        return [
            {
                "id": "R001",
                "name": "ER+ → Hormone Therapy Mandatory",
                "description": "If Estrogen Receptor positive, hormone therapy MUST be prescribed",
                "severity": RuleSeverity.CRITICAL,
                "check_func": self._check_er_positive_therapy
            },
            {
                "id": "R002",
                "name": "HER2+ → Herceptin Mandatory",
                "description": "If HER2 3+, Trastuzumab (Herceptin) MUST be prescribed",
                "severity": RuleSeverity.CRITICAL,
                "check_func": self._check_her2_herceptin
            },
            {
                "id": "R003",
                "name": "BRCA+ → Genetic Counseling Required",
                "description": "If BRCA1/BRCA2 mutation detected, genetic counseling MANDATORY",
                "severity": RuleSeverity.HIGH,
                "check_func": self._check_brca_counseling
            },
            {
                "id": "R004",
                "name": "Young Patient → Fertility Discussion",
                "description": "Age < 40 with breast cancer SHOULD discuss fertility preservation",
                "severity": RuleSeverity.MEDIUM,
                "check_func": self._check_fertility_young
            },
            {
                "id": "R005",
                "name": "Tamoxifen Interaction Check",
                "description": "Tamoxifen + CYP3A4 inhibitors = DANGEROUS interaction",
                "severity": RuleSeverity.HIGH,
                "check_func": self._check_tamoxifen_interactions
            },
            {
                "id": "R006",
                "name": "Anthracycline → Cardiac Monitoring",
                "description": "Patients on Anthracycline MUST have cardiac monitoring (ECHO/EF)",
                "severity": RuleSeverity.HIGH,
                "check_func": self._check_anthracycline_monitoring
            },
            {
                "id": "R007",
                "name": "Adjuvant Therapy Duration",
                "description": "Tamoxifen adjuvant should be minimum 5 years (or until 10 years)",
                "severity": RuleSeverity.MEDIUM,
                "check_func": self._check_adjuvant_duration
            },
            {
                "id": "R008",
                "name": "Metastatic → Complete Staging",
                "description": "Stage IV MUST have PET-CT, Bone Scan, Liver Imaging",
                "severity": RuleSeverity.CRITICAL,
                "check_func": self._check_metastatic_staging
            },
            {
                "id": "R009",
                "name": "Stage III+ → Pathology Report",
                "description": "Stage III or higher MUST have complete pathology report",
                "severity": RuleSeverity.HIGH,
                "check_func": self._check_pathology_report
            },
            {
                "id": "R010",
                "name": "PR+ Positive → Hormone Response Expected",
                "description": "PR+ patients typically respond better to hormone therapy",
                "severity": RuleSeverity.LOW,
                "check_func": self._check_pr_status
            },
        ]
    
    # ====== IMPLEMENTACIÓN DE REGLAS ======
    
    def _check_er_positive_therapy(self, patient: Dict) -> RuleResult:
        """REGLA 1: ER+ → Debe tener terapia hormonal"""
        er_status = patient['observations'].get('er_status', {}).get('value', 'unknown')
        medications = [m['name'] for m in patient['medications']]
        
        hormone_therapies = ['Tamoxifen', 'Letrozole', 'Anastrozole', 'Exemestane', 'Fulvestrant']
        has_hormone_therapy = any(drug in medications for drug in hormone_therapies)
        
        if er_status.lower() == 'positive':
            if not has_hormone_therapy:
                return RuleResult(
                    rule_name="ER+ → Hormone Therapy",
                    rule_id="R001",
                    status=RuleStatus.VIOLATION,
                    severity=RuleSeverity.CRITICAL,
                    message=f"Patient ER+ but NO hormone therapy prescribed",
                    action="MUST prescribe: Tamoxifen (premenopausal) or Aromatase Inhibitor (postmenopausal)",
                    affected_field="medications",
                    details={
                        "er_status": er_status,
                        "prescribed_therapies": medications or "NONE"
                    }
                )
            else:
                therapy = next(d for d in medications if d in hormone_therapies)
                return RuleResult(
                    rule_name="ER+ → Hormone Therapy",
                    rule_id="R001",
                    status=RuleStatus.COMPLIANT,
                    severity=RuleSeverity.CRITICAL,
                    message=f"✓ ER+ patient correctly prescribed {therapy}",
                    details={"therapy": therapy}
                )
        
        return RuleResult(
            rule_name="ER+ → Hormone Therapy",
            rule_id="R001",
            status=RuleStatus.COMPLIANT,
            severity=RuleSeverity.LOW,
            message="N/A: Patient is ER-negative"
        )
    
    def _check_her2_herceptin(self, patient: Dict) -> RuleResult:
        """REGLA 2: HER2+ → Debe tener Herceptin"""
        her2_status = patient['observations'].get('her2_status', {}).get('value', 'unknown')
        medications = [m['name'] for m in patient['medications']]
        
        if her2_status == '3+':
            if 'Herceptin' not in medications and 'Trastuzumab' not in medications:
                return RuleResult(
                    rule_name="HER2+ → Herceptin",
                    rule_id="R002",
                    status=RuleStatus.VIOLATION,
                    severity=RuleSeverity.CRITICAL,
                    message=f"Patient HER2 3+ but NO Herceptin (Trastuzumab) prescribed",
                    action="MUST start Herceptin immediately - consider HER2-directed therapy",
                    affected_field="medications",
                    details={"her2_status": "3+ (positive)"}
                )
            else:
                return RuleResult(
                    rule_name="HER2+ → Herceptin",
                    rule_id="R002",
                    status=RuleStatus.COMPLIANT,
                    severity=RuleSeverity.CRITICAL,
                    message="✓ HER2+ patient correctly prescribed Herceptin"
                )
        
        return RuleResult(
            rule_name="HER2+ → Herceptin",
            rule_id="R002",
            status=RuleStatus.COMPLIANT,
            severity=RuleSeverity.LOW,
            message="N/A: Patient is HER2-negative or unknown"
        )
    
    def _check_brca_counseling(self, patient: Dict) -> RuleResult:
        """REGLA 3: BRCA+ → Debe tener genetic counseling"""
        brca_status = patient['observations'].get('brca1', {}).get('value', 'unknown')
        has_counseling = any(
            c['type'] == 'genetic_counseling' 
            for c in patient.get('consultations', [])
        )
        
        if brca_status.lower() == 'present':
            if not has_counseling:
                return RuleResult(
                    rule_name="BRCA+ → Genetic Counseling",
                    rule_id="R003",
                    status=RuleStatus.VIOLATION,
                    severity=RuleSeverity.HIGH,
                    message="Patient BRCA+ but NO genetic counseling documented",
                    action="MUST refer to genetic counselor - family counseling recommended",
                    affected_field="consultations"
                )
            else:
                return RuleResult(
                    rule_name="BRCA+ → Genetic Counseling",
                    rule_id="R003",
                    status=RuleStatus.COMPLIANT,
                    severity=RuleSeverity.HIGH,
                    message="✓ Genetic counseling documented for BRCA+ patient"
                )
        
        return RuleResult(
            rule_name="BRCA+ → Genetic Counseling",
            rule_id="R003",
            status=RuleStatus.COMPLIANT,
            severity=RuleSeverity.LOW,
            message="N/A: Patient BRCA-negative"
        )
    
    def _check_fertility_young(self, patient: Dict) -> RuleResult:
        """REGLA 4: Edad < 40 → Considerar fertility preservation"""
        age = patient['age']
        has_fertility_discussion = any(
            c['type'] == 'fertility_preservation'
            for c in patient.get('consultations', [])
        )
        
        if age < 40:
            if not has_fertility_discussion:
                return RuleResult(
                    rule_name="Young Patient Fertility",
                    rule_id="R004",
                    status=RuleStatus.WARNING,
                    severity=RuleSeverity.MEDIUM