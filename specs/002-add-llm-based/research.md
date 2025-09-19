# Phase 0: Research for LLM-based Job Upload Endpoint

## Unknowns/Clarifications
- What is the expected behavior for unsupported file types? (FR-007)
- What should happen if the LLM service is unavailable? (Edge case)
- What level of feedback is required to the user? (FR-008)
- Performance and scale expectations?

## Research Tasks
- Best practices for using Langchain with Gemini for document extraction
- Robust PDF/text parsing for job descriptions
- Error handling and user feedback patterns for LLM-based extraction services
- Mapping LLM output to Pydantic models with optional fields

## Findings

### Langchain + Gemini for Document Extraction
- Decision: Use Langchain's document loaders and Gemini integration for extracting structured data from job description files.
- Rationale: Langchain provides a modular interface for LLMs and document parsing, and Gemini is a state-of-the-art LLM with strong extraction capabilities.
- Alternatives: OpenAI GPT-4, Claude, custom extraction scripts.

### PDF/Text Parsing
- Decision: Use PyPDF2 for PDF parsing and standard file reading for text files.
- Rationale: PyPDF2 is widely used and integrates well with Python backends.
- Alternatives: pdfminer, fitz (PyMuPDF).

### Error Handling & User Feedback
- Decision: Return clear error messages for unsupported file types and LLM service unavailability. Log all errors and provide user feedback via API response.
- Rationale: Improves user experience and debuggability.
- Alternatives: Silent failures, generic error messages.

### Mapping LLM Output to Pydantic Models
- Decision: Use Pydantic's support for optional fields to allow missing data to be set as None.
- Rationale: Ensures robust DB entry even with incomplete extraction.
- Alternatives: Require all fields (not user-friendly).

### Performance & Scale
- Decision: No strict performance/scale requirements specified. Design for moderate usage; revisit if scale increases.
- Rationale: Initial deployment, can optimize later.
- Alternatives: Pre-scaling, async processing.
