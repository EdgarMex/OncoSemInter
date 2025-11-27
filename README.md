# OncoSemInter: A Semantic Interoperability Framework for Oncology
Breast Cancer Case Study
<img width="82" height="20" alt="image" src="https://github.com/user-attachments/assets/ac236fd9-5abd-4ba8-ab42-0e8dd848fb22" />

OncoSemInt is a framework prototype of an operational ontology between ontologies for breast cancer, with a system architecture and data flow pipeline based on semantic technologies for integrating existing biomedical ontologies such as NCIt, BCO, OntoBreast, and MAMO—SCR-Onto using RDF data shapes (ShEx and/or SHACL) to validate and achieve semantic interoperability among them, creating a single validated RDF graph, which can be transferred to clinical environments that support interoperability
through HL7-FHIR and SNOMED-CT standards integrated with ShEx/SHACL and connected to HL7 FHIR Foundation. 

The proposal presented, using RDF data shapes (ShEx and/or SHACL) and HL7 FHIR, opens up several lines of future work, both technical and methodological, as well as clinical applications. Work will continue on creating Shapes forms for breast cancer that involve more semantic elements. Transformation of data to RDF from rudof. This will incorporate treatments (lines of therapy, combinations, doses, toxicities) and clinical outcomes (response, survival, adverse events) in greater detail. Integration of additional ontologies (e.g., drugs, signaling pathways, tumor phenotype) and refinement of alignments with standard terminologies (SNOMED CT, LOINC, ATC, etc.). This would involve defining new ShEx and SHACL shapes. Creation of complex SPARQL queries that complement the results of Shacl validations to ensure high data quality in RDF graphs. Automatic inference processes using OWL for obtaining more medical information about a patient. Each layer of the system architecture presents new challenges,
such as the automation of RDF↔FHIR mappings and updating the defined Shacl validation forms. Extension to complementary clinical standards OMOP (Observational Medical Outcomes Partnership) [38], CDM (Common Data Model) [ 38], CDISC (Clinical Data Interchange Standards Consortium), ODM (Operational Data Model). Use of generative artificial intelligence to suggest ontological alignments and information queries in natural language. Generalization of the semantic model so that it can be extended to other types of cancer. These are some lines of future work, but there are still more to mention, and this also shows the complexity involved in
creating an interoperable ecosystem in the field of health.

Ontological Interoperability (OI) is a specific branch of ontological engineering (EO) and the property of an ecosystem in which different systems, applications, or platforms can share and exchange information with common data meaning through shared ontologies in which vocabulary, relationships, and formal concepts are aligned and validated within semantic systems.
 The integration with other ontologies is sought in a coherent way, allowing heterogeneous systems to communicate with each other, perform automatic reasoning on the data, and can be used for different purposes.
 It is important to mention that semantic interoperability can be achieved without including ontologies, even though they are a key element for it.
 OI is contained within the broader concept of semantic operability (SO), In this sense, ontological Interoperability constitutes the ontological layer that enables semantic consistency, inference, interoperability between domains, and data validation through ShEx and Shacl.
ShEx (Shape Expressions) is a language for describing the shape of an RDF graph, developed in collaboration with the W3C \cite{prud2014shape}. It defines constraints on properties, cardinalities, and expected data types. ShEx has been successfully applied in the biomedical domain to validate RDF data structures \cite{osterman2020improving}.
SHACL (Shapes Constraint Language) is the W3C standard for defining constraints on RDF graphs \cite{prud2014shape}. SHACL is more suitable than SHEX for validation in production environments due to its greater flexibility and extensibility \cite{declerck2025assessing}. The SHACL engine can execute constraints on an RDF graph and generate a detailed validation report. Constraints can include custom SPARQL logic, allowing for complex validations.
\cite{staworko2015complexity}.
Case studies demonstrate the effectiveness of SHACL in detecting anomalies in biomedical RDF graphs \cite{shacldatosgob}. SHACL constraints can include custom SPARQL logic, enabling complex validations \cite{hyvonen20248}.
FHIR \cite{sharma2023shape} is the most widely adopted interoperability standard for structuring clinical and oncology data using reusable resources. It supports specialized profiles such as mCODE (Minimal Common Oncology Data Elements) \cite{osterman2020improving} for recording diagnoses, genomics, and treatments.
It facilitates structured representation of heterogeneous clinical data (Patient, Condition, Observation, Medication Statement). It uses RESTful APIs, JSON/XML, and RDF.
 In the healthcare domain, this includes the ability of ontologies to interoperate using standards such as HL7 FHIR and to be represented through RDF graphs in a consistent and computable way.
The relationship between HL7 FHIR, ShEx, and SHACL constitutes an architecture for ensuring the quality of clinical data, where FHIR provides the base semantic model and interoperability profiles, while ShEx and SHACL act as orthogonal validation languages (independence and free combination of language elements) that verify the conformity of FHIR data serialized in RDF, enabling agile iteration with (ShEx) and production auditing with (SHACL) of the data.

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
Support FHIR R5 for serialization of clinical resources.
Offer an OWL (Turtle) skeleton with modules and alignments to SNOMED CT, NCIt, LOINC, RxNorm, and ICD-11.
Include basic DICOM reading and generation of synthetic records (Diego) in JSON and RDF.
Prepare reasoning (OWL reasoners) and SPARQL queries for validations.
Maintain an open structure for future extensions (other breast cancers, biomarkers, treatments).
Repository structure:
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
