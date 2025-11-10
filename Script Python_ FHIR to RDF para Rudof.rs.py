
#!/usr/bin/env python3
"""
FHIR to RDF Converter para RudoLF
================================
Convierte datos FHIR JSON desde Epic/Cerner a RDF Turtle
Entrada: JSON FHIR Bundle
Salida: Turtle file listo para importar en RudoLF

Uso:
    python3 fhir_to_rdf.py input.json output.ttl
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

class FHIRtoRDFConverter:
    """Convertidor de FHIR JSON a RDF Turtle"""
    
    def __init__(self):
        self.prefixes = {
            "ex": "http://example.org/",
            "fhir": "http://hl7.org/fhir/",
            "snomed": "http://snomed.info/id/",
            "icd10": "http://hl7.org/fhir/sid/icd-10-cm/",
            "loinc": "http://loinc.org/",
            "mesh": "http://id.nlm.nih.gov/mesh/",
            "umls": "https://identifiers.org/umls:",
            "hgnc": "https://identifiers.org/hgnc:",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        }
        self.turtle_lines = []
        self.triples = {}
    
    def add_prefixes(self):
        """Agregar declaraciones PREFIX"""
        for prefix, uri in self.prefixes.items():
            self.turtle_lines.append(f"@prefix {prefix}: <{uri}> .")
        self.turtle_lines.append("")
    
    def add_triple(self, subject: str, predicate: str, obj: str, 
                   is_literal: bool = False, datatype: Optional[str] = None):
        """Agregar triple RDF"""
        if is_literal and datatype:
            triple = f'    {predicate} "{obj}"^^{datatype} ;'
        elif is_literal:
            triple = f'    {predicate} "{obj}" ;'
        else:
            triple = f'    {predicate} {obj} ;'
        
        if subject not in self.triples:
            self.triples[subject] = []
        self.triples[subject].append((predicate, obj, triple))
    
    def write_triples(self):
        """Escribir triples acumulados a Turtle"""
        for subject, predicates in self.triples.items():
            self.turtle_lines.append(f"{subject}")
            
            for i, (pred, obj, line) in enumerate(predicates):
                if i == len(predicates) - 1:
                    self.turtle_lines.append(line.rstrip(';') + " .")
                else:
                    self.turtle_lines.append(line)
            self.turtle_lines.append("")
    
    def get_age_from_birthdate(self, birthdate: str) -> int:
        """Calcular edad desde fecha de nacimiento"""
        try:
            birth_year = int(birthdate.split("-")[0])
            return datetime.now().year - birth_year
        except:
            return None
    
    def convert_patient(self, patient_resource: Dict):
        """Convertir FHIR Patient a RDF"""
        patient_id = patient_resource.get("id")
        patient_uri = f"ex:Patient_{patient_id}"
        
        # Tipos
        self.add_triple(patient_uri, "rdf:type", "fhir:Patient")
        self.add_triple(patient_uri, "rdf:type", "ex:Patient")
        
        # MRN (Medical Record Number)
        for identifier in patient_resource.get("identifier", []):
            mrn = identifier.get("value")
            if mrn:
                self.add_triple(patient_uri, "ex:hasMRN", mrn, 
                              is_literal=True, datatype="xsd:string")
        
        # Nombre
        for name in patient_resource.get("name", []):
            given = " ".join(name.get("given", []))
            family = name.get("family", "")
            full_name = f"{given} {family}".strip()
            self.add_triple(patient_uri, "ex:hasName", full_name, 
                          is_literal=True, datatype="xsd:string")
        
        # Fecha de nacimiento y edad
        if "birthDate" in patient_resource:
            birthdate = patient_resource["birthDate"]
            self.add_triple(patient_uri, "ex:hasBirthDate", birthdate, 
                          is_literal=True, datatype="xsd:date")
            
            age = self.get_age_from_birthdate(birthdate)
            if age:
                self.add_triple(patient_uri, "ex:hasAge", str(age), 
                              is_literal=True, datatype="xsd:integer")
        
        # Género
        if "gender" in patient_resource:
            gender = patient_resource["gender"]
            self.add_triple(patient_uri, "ex:hasGender", gender, 
                          is_literal=True, datatype="xsd:string")
        
        # País (desde extensión)
        for address in patient_resource.get("address", []):
            country = address.get("country")
            if country:
                self.add_triple(patient_uri, "ex:hasCountry", country, 
                              is_literal=True, datatype="xsd:string")
        
        self.turtle_lines.append(f"# ========================================")
        self.turtle_lines.append(f"# PACIENTE: {full_name if 'full_name' in locals() else patient_id}")
        self.turtle_lines.append(f"# ========================================")
        
        return patient_uri
    
    def convert_condition(self, condition_resource: Dict, patient_uri: str):
        """Convertir FHIR Condition a RDF"""
        condition_id = condition_resource.get("id")
        condition_uri = f"ex:Condition_{condition_id}"
        
        # Tipos
        self.add_triple(condition_uri, "rdf:type", "fhir:Condition")
        self.add_triple(condition_uri, "rdf:type", "ex:Condition")
        
        # Si es cáncer de mama
        is_breast_cancer = False
        
        # Códigos (SNOMED, ICD-10)
        for coding in condition_resource.get("code", {}).get("coding", []):
            system = coding.get("system", "")
            code = coding.get("code", "")
            display = coding.get("display", "")
            
            if "snomed" in system.lower():
                if code == "254837009":  # Breast cancer
                    is_breast_cancer = True
                self.add_triple(condition_uri, "ex:hasCode", f"snomed:{code}")
            elif "icd-10" in system.lower():
                if code.startswith("C50"):  # Breast cancer ICD-10
                    is_breast_cancer = True
                self.add_triple(condition_uri, "ex:hasCode", f"icd10:{code}")
            
            if display:
                self.add_triple(condition_uri, "rdfs:label", display, 
                              is_literal=True)
        
        # Estado clínico
        for status_coding in condition_resource.get("clinicalStatus", {}).get("coding", []):
            status = status_coding.get("code")
            if status:
                self.add_triple(condition_uri, "ex:hasStatus", status, 
                              is_literal=True, datatype="xsd:string")
        
        # Marcar como BreastCancerDisease si aplica
        if is_breast_cancer:
            self.add_triple(condition_uri, "rdf:type", "ex:BreastCancerDisease")
        
        # Relacionar con paciente
        self.add_triple(patient_uri, "ex:hasCondition", condition_uri)
        
        self.turtle_lines.append(f"# ========================================")
        self.turtle_lines.append(f"# CONDICIÓN: {condition_id}")
        self.turtle_lines.append(f"# ========================================")
        
        return condition_uri
    
    def convert_observation(self, observation_resource: Dict, patient_uri: str):
        """Convertir FHIR Observation a RDF"""
        obs_id = observation_resource.get("id")
        obs_uri = f"ex:Observation_{obs_id}"
        
        # Tipos
        self.add_triple(obs_uri, "rdf:type", "fhir:Observation")
        self.add_triple(obs_uri, "rdf:type", "ex:LabObservation")
        
        # Nombre de la observación
        for coding in observation_resource.get("code", {}).get("coding", []):
            display = coding.get("display", "")
            if display:
                self.add_triple(obs_uri, "ex:hasName", display, 
                              is_literal=True, datatype="xsd:string")
                self.add_triple(obs_uri, "rdfs:label", display, 
                              is_literal=True)
        
        # Valor (CodeableConcept)
        if "valueCodeableConcept" in observation_resource:
            for coding in observation_resource["valueCodeableConcept"].get("coding", []):
                value = coding.get("display", "")
                if value:
                    self.add_triple(obs_uri, "ex:hasValue", value, 
                                  is_literal=True, datatype="xsd:string")
        
        # Valor (Quantity)
        elif "valueQuantity" in observation_resource:
            value = observation_resource["valueQuantity"].get("value")
            unit = observation_resource["valueQuantity"].get("unit")
            if value:
                self.add_triple(obs_uri, "ex:hasValue", str(value), 
                              is_literal=True, datatype="xsd:decimal")
            if unit:
                self.add_triple(obs_uri, "ex:hasUnit", unit, 
                              is_literal=True, datatype="xsd:string")
        
        # Fecha
        if "issued" in observation_resource:
            issued = observation_resource["issued"]
            self.add_triple(obs_uri, "ex:hasDate", issued, 
                          is_literal=True, datatype="xsd:dateTime")
        
        # Relacionar con paciente
        self.add_triple(patient_uri, "ex:hasObservation", obs_uri)
        
        self.turtle_lines.append(f"# ========================================")
        self.turtle_lines.append(f"# OBSERVACIÓN: {obs_id}")
        self.turtle_lines.append(f"# ========================================")
        
        return obs_uri
    
    def convert_medication(self, medication_resource: Dict, patient_uri: str):
        """Convertir FHIR MedicationStatement a RDF"""
        med_id = medication_resource.get("id")
        med_uri = f"ex:Medication_{med_id}"
        
        # Tipos
        self.add_triple(med_uri, "rdf:type", "fhir:MedicationStatement")
        self.add_triple(med_uri, "rdf:type", "ex:Therapy")
        
        # Nombre del medicamento
        for coding in medication_resource.get("medicationCodeableConcept", {}).get("coding", []):
            display = coding.get("display", "")
            if display:
                self.add_triple(med_uri, "rdfs:label", display, 
                              is_literal=True)
                self.add_triple(med_uri, "ex:hasName", display, 
                              is_literal=True, datatype="xsd:string")
        
        # Dosis
        for dosage in medication_resource.get("dosage", []):
            text = dosage.get("text", "")
            if text:
                self.add_triple(med_uri, "ex:hasDose", text, 
                              is_literal=True, datatype="xsd:string")
        
        # Fecha efectiva
        if "effectivePeriod" in medication_resource:
            start = medication_resource["effectivePeriod"].get("start")
            end = medication_resource["effectivePeriod"].get("end")
            if start:
                self.add_triple(med_uri, "ex:startDate", start, 
                              is_literal=True, datatype="xsd:date")
            if end:
                self.add_triple(med_uri, "ex:endDate", end, 
                              is_literal=True, datatype="xsd:date")
        
        # Relacionar con paciente
        self.add_triple(patient_uri, "ex:treatedWith", med_uri)
        
        self.turtle_lines.append(f"# ========================================")
        self.turtle_lines.append(f"# MEDICACIÓN: {med_id}")
        self.turtle_lines.append(f"# ========================================")
        
        return med_uri
    
    def convert_bundle(self, fhir_bundle: Dict) -> str:
        """Convertir FHIR Bundle completo a RDF"""
        # Agregar prefijos
        self.add_prefixes()
        
        self.turtle_lines.append("# ========================================")
        self.turtle_lines.append("# RDF GENERADO DESDE FHIR")
        self.turtle_lines.append(f"# Generado: {datetime.now().isoformat()}")
        self.turtle_lines.append("# ========================================")
        self.turtle_lines.append("")
        
        patient_uri = None
        
        # Procesar entries del bundle
        for entry in fhir_bundle.get("entry", []):
            resource = entry.get("resource", {})
            resource_type = resource.get("resourceType")
            
            try:
                if resource_type == "Patient":
                    patient_uri = self.convert_patient(resource)
                elif resource_type == "Condition" and patient_uri:
                    self.convert_condition(resource, patient_uri)
                elif resource_type == "Observation" and patient_uri:
                    self.convert_observation(resource, patient_uri)
                elif resource_type == "MedicationStatement" and patient_uri:
                    self.convert_medication(resource, patient_uri)
            except Exception as e:
                print(f"⚠️  Error procesando {resource_type}: {e}", file=sys.stderr)
                continue
        
        # Escribir todos los triples
        self.write_triples()
        
        return "\n".join(self.turtle_lines)


def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python3 fhir_to_rdf.py <input.json> [output.ttl]")
        print("")
        print("Ejemplos:")
        print("  python3 fhir_to_rdf.py patient.json patient.ttl")
        print("  python3 fhir_to_rdf.py bundle.json > output.ttl")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        # Leer JSON FHIR
        with open(input_file, 'r', encoding='utf-8') as f:
            fhir_bundle = json.load(f)
        
        # Convertir a RDF
        converter = FHIRtoRDFConverter()
        rdf_turtle = converter.convert_bundle(fhir_bundle)
        
        # Escribir salida
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(rdf_turtle)
            print(f"✅ RDF exportado a: {output_file}")
        else:
            print(rdf_turtle)
        
        print(f"✅ Conversión completada exitosamente")
        print(f"📊 Triples generados: {len(converter.triples)}")
        
    except FileNotFoundError:
        print(f"❌ Error: Archivo no encontrado: {input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: JSON inválido en: {input_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
