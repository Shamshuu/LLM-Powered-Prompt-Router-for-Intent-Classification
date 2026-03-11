# LLM-Powered Prompt Router

A production-ready Python service that intelligently routes user requests to specialized AI personas using a two-step "Classify then Respond" architecture. This avoids monolithic, generic system prompts in favor of focused experts for dramatically improved response quality.

## Features & Architecture

*   **Two-Step LLM Pipeline**:
    *   **Step 1: Classification**: A fast, low-cost API call (via `llama-3.1-8b-instant` on Groq) strictly outputs a JSON object `{"intent": "...", "confidence": 0.0}` representing the user's intent.
    *   **Step 2: Generation**: A second API call uses a highly specialized system prompt (the "expert persona") chosen based on the classification to generate a rich, context-aware answer.
*   **Four Distinct Personas**: Contains tailored system prompts for `code`, `data`, `writing`, and `career` requests.
*   **Robust Error Handling**: Safely parses the LLM JSON output. If the response is malformed, unrecognized, or the LLM fails, it defaults to a fallback `unclear` state.
*   **Clarification State**: If the intent is `unclear` (or the confidence score is too low), the system gracefully asks the user for clarification rather than hallucinating an answer.
*   **Stretch Goals Included**:
    *   **Manual Override**: Users can bypass the classifier entirely by using an `@intent` prefix (e.g., `@code Fix this script...`).
    *   **Confidence Threshold**: Any classified intent with a confidence score below `0.7` is rejected and flagged as `unclear`.

## System Requirements

- Docker and Docker Compose
- (Alternatively) Python 3.11+ and `pip`

## Quick Start (Docker)

1. **Add Your API Key**:
   Create a `.env` file in the root directory by copying the example template:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your real `GROQ_API_KEY`.

2. **Run the Application**:
   Start the application using Docker Compose. A pre-defined test suite of 15 messages will run.
   ```bash
   docker compose up --build
   ```

3. **Check the Logs**:
   All outputs and routing decisions are written locally to `route_log.jsonl` securely.

## Local Evaluation (Without Docker)

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and configure your `GROQ_API_KEY`.
3. Run the evaluation script:
   ```bash
   python main.py
   ```

## Design Decisions

- **prompts.json**: Separating prompts from code makes it trivial for non-engs (e.g., Prompt Engineers, PMs) to tweak the personas without modifying `router.py`.
- **JSON Lines logging**: Writing to `.jsonl` creates machine-readable logs which are perfect for observability stacks (like Datadog, ELK) or fine-tuning datasets later on.
- **Groq Llama 3 models usage**: We utilize `llama-3.1-8b-instant` for routing and `llama-3.3-70b-versatile` for generating responses because intent classification must be exceedingly fast and inexpensive in production.