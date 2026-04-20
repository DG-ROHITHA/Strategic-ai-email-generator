# Strategic Agentic AI Email Assistant

A complete beginner-friendly Agentic AI project that generates professional emails using a multi-agent workflow built with Streamlit, Python, LangChain, and OpenAI-compatible models.

## Project Goal
Build an AI system that intelligently creates high-quality professional emails by:
- analyzing the situation,
- selecting a communication strategy,
- selecting the right tone,
- generating the draft,
- and self-reviewing quality before returning the final email.

## Agentic Workflow
User Input -> Situation Analysis -> Strategy Selection -> Tone Selection -> Email Generation -> Email Quality Review -> Final Email Output

## Features
- Email purpose detection
- Situation/context analysis
- Strategy selection from:
  - persuasion
  - apology
  - follow-up
  - negotiation
  - clarification
- Tone detection and adjustment
- Professional subject line + email generation
- Email quality self-review with score and suggestions
- Option to improve an existing email draft
- Local fallback mode when API quota is unavailable

## Tech Stack
- Frontend: Streamlit
- Backend: Python
- AI Framework: LangChain
- LLM: OpenAI API or compatible endpoint

## Free Usage Options
- Ollama Local AI (free): Uses a local open-source model, no paid API needed.
- Local Fallback Rules (free): Uses built-in deterministic logic without any model server.

## Folder Structure
```text
Email_Generator/
|-- app.py
|-- requirements.txt
|-- .env.example
|-- README.md
|-- examples/
|   `-- sample_inputs_outputs.md
`-- src/
    |-- __init__.py
    |-- config.py
    |-- models.py
    |-- prompts.py
    |-- utils.py
    |-- orchestrator.py
    `-- agents/
        |-- __init__.py
        |-- base.py
        |-- intent_agent.py
        |-- situation_agent.py
        |-- strategy_agent.py
        |-- tone_agent.py
        |-- email_generator_agent.py
        `-- review_agent.py
```

## Prompt Templates
All agent prompt templates are in:
- src/prompts.py

## How To Run Locally
1. Create and activate a virtual environment.
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
2. Install dependencies.
   ```powershell
   pip install -r requirements.txt
   ```
3. Create environment file.
   ```powershell
   copy .env.example .env
   ```
4. Set your values in .env.
   ```env
   OPENAI_API_KEY=your_key_here
   OPENAI_MODEL=gpt-4o-mini
   OPENAI_TEMPERATURE=0.3
   OPENAI_BASE_URL=
   ```
5. Run the Streamlit app.
   ```powershell
   streamlit run app.py
   ```

## If You See Error 429 (insufficient_quota)
- This means your API account is out of credits or billing is not enabled.
- You can still use the app immediately:
   - In the sidebar, set Generation Mode to "Ollama Local AI (free)" or "Local Fallback Rules (free)".
   - Click Generate Email.
- For full LLM quality, add credits or enable billing for your API account.

## Run With Ollama (No Cost)
1. Install Ollama from the official website.
2. Start a local model:
    ```powershell
    ollama run llama3.2:3b
    ```
3. In the app sidebar:
    - Set Generation Mode to "Ollama Local AI (free)".
    - Set Ollama Model to `llama3.2:3b`.
    - Keep Ollama Base URL as `http://localhost:11434`.
4. Click Generate Email.

## UI Inputs
The app UI lets users:
- Enter email purpose
- Enter recipient
- Describe situation
- Select tone preference
- Add key points
- Enable improve-existing-email mode
- Click Generate Email

## UI Outputs
The app displays:
- Selected communication strategy
- Chosen tone
- Generated subject line
- Full email draft
- Email quality review

## Example Inputs and Outputs
See:
- examples/sample_inputs_outputs.md

## Future Improvements
- Gmail integration for sending drafts directly
- Voice input for hands-free prompt capture
- Meeting transcript to email generation
- Email sentiment detection and adaptative tone tuning

## Notes For Beginners
- Each agent is implemented as its own class so the pipeline is easy to understand.
- The orchestrator in src/orchestrator.py controls the full workflow sequence.
- If model output is not valid JSON, safe fallback defaults are used so the app remains stable.
