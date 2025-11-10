# OncoSemInter: A Semantic Interoperability Framework for Oncology
Breast Cancer Case Study
<img width="82" height="20" alt="image" src="https://github.com/user-attachments/assets/ac236fd9-5abd-4ba8-ab42-0e8dd848fb22" />

OncoSemInt is a framework prototype of an operational ontology between ontologies for breast cancer, integrated with BI-RADS and connected to HL7 FHIR Foundation. The goal is to facilitate interoperability between clinical ontologies and digital medical images (DICOM and others), with support for FHIR R5 serialization, DICOM reading, synthetic record generation, reasoning, and SPARQL queries.

Table of Contents
Objective and Scope
Repository Structure
Requirements and Dependencies
Installation and Configuration
Basic Use
Pipelines and Workflows
Contribution
License and Synthetic Data
Implementation Notes and Decisions
Contact
Objective and Scope
Provide an MVP for OntoMamI focused on mammograms and BI-RADS.
Support FHIR R5 for serialization of clinical resources.
Offer an OWL (Turtle) skeleton with modules and alignments to SNOMED CT, NCIt, LOINC, RxNorm, and ICD-11.
Include basic DICOM reading and generation of synthetic records (Diego) in JSON and RDF.
Prepare reasoning (OWL reasoners) and SPARQL queries for validations.
Maintain an open structure for future extensions (other breast cancers, biomarkers, treatments).
Repository structure
owl/

OncoSemInt.ttl: Initial OWL skeleton in Turtle.
namespaces.ttl: Prefixes and base IRIs.
fhir_profiles/

r5/
StructureDefinitions/
BreastCancer-Observation-BI_RADS.json
BreastCancer-Bundle.json
BI_RADS_CategoryCode.json
Breast_ReceptorStatus.json

examples/
BI-RADS4_example.json
Diego_DiagnosticReport.json
diego/

diego_synthetic.json: Synthetic record in FHIR JSON.
diego_synthetic.ttl: Issued in RDF/Turtle.
dicom/

read_dicom_example.py: Base Python script for reading DICOM metadata.
dicom_mapping.md: DICOM → FHIR RDF mapping guide.
reasoning/

shacl/ontobci_profile_shacl.ttl: SHACL shapes for profile validation.
sparql/competencia_base.rq: SPARQL query templates for competition.
rdf_store/

setup_instructions.md: Guide for deploying an RDF store and loading artifacts.
docs/

plan.md: Implementation and progress plan.
decisions.md: Record of design decisions.
.gitignore

README.md (current adapted file)

Requirements and dependencies
Java (for OWL/RDF tools and potential reasoners such as HermiT or Pellet).
Python 3.x (for DICOM scripts and pipelines).
Node.js (optional, for JSON processing utilities and FHIR tooling).
Pydicom/DCMTK (for DICOM reading).
FHIR libraries for testing (e.g., HAPI FHIR if using Java, or fhir.resources for Python).
A compatible RDF store (Virtuoso, Stardog, Blazegraph, or similar) for SPARQL and reasoning.
SHACL validators (pySHACL or OWL SHACL tooling).
Notes: The artifacts in this MVP are designed to run in a Python environment with optional Node for FHIR. It can be adapted to a CI/CD flow in GitHub Actions.

Installation and configuration (proposal)
Environment recommendation
Create a Conda environment (optional) for Python and RDF tools.
Install DICOM and RDF dependencies.
Initial steps

Validate SHACL:
pySHACL orients shapes against RDF/Turtle data.
SPARQL queries:
Use a local SPARQL endpoint or Virtuoso to run competencia_base.rq against diego_synthetic.ttl.
Note on versions

This MVP uses FHIR R5 for profiles and examples. StructureDefinitions are in fhir_profiles/r5/StructureDefinitions/.
Diego examples are available in JSON and RDF/Turtle for interoperability.
Basic usage
OWL and SHACL structure verification

Validate ontology and profile consistency with reasoners (HermiT/Pellet/ELK).
Run SHACL to see that the RDFs comply with the defined shapes.
Artifact generation

DICOM: metadata reading and ImagingStudy/Observation generation.
Diego: FHIR resource generation for a BI-RADS-centered synthetic record.

RDF: TTL conversion of FHIR resources for storage.
Validation and queries

SPARQL: execute queries on generated RDF/Turtle.
SHACL: validate FHIR and RDF structures against OntoMamI definitions.
Contribution
To contribute, follow these basic guidelines:


This project is licensed under MIT. See the License section for more details.
License and synthetic data
License: MIT
