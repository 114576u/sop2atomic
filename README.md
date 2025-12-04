![CI](https://github.com/114576u/sop2atomic/actions/workflows/ci.yml/badge.svg)

# sop2atomic
**Automated SOP Decomposition into Atomic Workflow Actions**  
*A Python framework for transforming Standard Operating Procedures into structured, machine-readable atomic actions using OpenAI models.*

---

## 🔍 Overview

**sop2atomic** is an internal tool designed to streamline the digitisation of operational processes within Reporting Operations.  
It automates the conversion of SOP documents (typically `.docx`) into a structured, atomic-action JSON format aligned with the **Atomic Components Catalogue** used for workflow automation.

This enables:

- Consistent, validated SOP definitions  
- Faster onboarding of new reports  
- Preparation for workflow automation and optimisation  
- Clear traceability between SOP steps and executable tasks  

While currently used as a standalone utility, **sop2atomic** forms a foundational building block for broader process automation efforts.

---

## 🎯 Key Features

- **SOP Parsing**: Extracts structured procedure steps and metadata from `.docx` SOPs.  
- **Atomic Component Mapping**: Uses the Atomic Components Catalogue (`.xlsx`) to map SOP steps into atomic actions.  
- **OpenAI Integration**: Uses models like `gpt-5.1` to interpret SOP steps and produce precise JSON mappings.  
- **JSON Output**: Returns clean, deterministic JSON suitable for automation engines or downstream tooling.  
- **Extensible Architecture**: Modular design allows enhancements such as validation, new output formats, or integration with workflow schedulers.

---
