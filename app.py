"""Streamlit UI for Strategic Agentic AI Email Assistant."""

import re
from pathlib import Path

import streamlit as st

from src.config import create_llm, create_ollama_llm, load_config
from src.fallback_engine import generate_fallback_result
from src.models import EmailRequest
from src.orchestrator import EmailAssistantOrchestrator
from src.utils import normalize_text

st.set_page_config(
    page_title="Strategic Agentic AI Email Assistant",
    page_icon="M",
    layout="wide",
)


def render_header() -> None:
    """Render the page heading and workflow summary."""

    st.title("Strategic Agentic AI Email Assistant")
    st.caption(
        "Analyze context, choose communication strategy, select tone, generate and review a professional email."
    )


def render_sidebar(config):
    """Render sidebar controls for model configuration."""

    st.sidebar.header("Model Configuration")
    st.sidebar.write("Set your API key and model options.")

    generation_mode = st.sidebar.selectbox(
        "Generation Mode",
        [
            "OpenAI API (paid)",
            "Ollama Local AI (free)",
            "Local Fallback Rules (free)",
        ],
        index=1,
    )

    if not Path(".env").exists():
        st.sidebar.warning("No .env file found. .env.example is only a template and is not loaded.")

    api_key = ""
    base_url = ""
    model_name = config.model_name
    ollama_model = config.ollama_model
    ollama_base_url = config.ollama_base_url

    if generation_mode == "OpenAI API (paid)":
        api_key = st.sidebar.text_input(
            "OpenAI API Key",
            type="password",
            value=config.openai_api_key,
            help="Store this in .env as OPENAI_API_KEY (not in .env.example).",
        )
        base_url = st.sidebar.text_input(
            "OpenAI Base URL (optional)",
            value=config.base_url,
            help="Use this if you are calling an OpenAI-compatible model endpoint.",
        )
        model_name = st.sidebar.text_input("OpenAI Model", value=config.model_name)

    elif generation_mode == "Ollama Local AI (free)":
        st.sidebar.info("No paid API required. Requires Ollama running locally.")
        ollama_model = st.sidebar.text_input("Ollama Model", value=config.ollama_model)
        ollama_base_url = st.sidebar.text_input("Ollama Base URL", value=config.ollama_base_url)

    else:
        st.sidebar.info("Uses built-in rule-based generator. No model server needed.")

    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=float(config.temperature),
        step=0.05,
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Workflow: User Input -> Situation Analysis -> Strategy Selection -> Tone Selection -> "
        "Email Generation -> Email Quality Review -> Final Email"
    )

    return {
        "generation_mode": generation_mode,
        "api_key": api_key,
        "base_url": base_url,
        "model_name": model_name,
        "ollama_model": ollama_model,
        "ollama_base_url": ollama_base_url,
        "temperature": temperature,
    }


def render_input_form() -> tuple:
    """Render the main user input form."""

    with st.form("email_form"):
        email_purpose = st.text_input(
            "Email purpose",
            placeholder="Example: Request a timeline extension for a client project",
        )
        recipient = st.text_input(
            "Recipient",
            placeholder="Example: Sarah Ahmed, Product Manager",
        )
        situation = st.text_area(
            "Describe the situation",
            height=150,
            placeholder="Provide context, constraints, and what outcome you want.",
        )
        tone_preference = st.selectbox(
            "Tone preference",
            [
                "Auto detect",
                "Formal",
                "Friendly",
                "Confident",
                "Empathetic",
                "Concise",
                "Diplomatic",
            ],
        )
        key_points = st.text_area(
            "Key points to include",
            height=120,
            placeholder="Add bullet-like points or must-include details.",
        )

        improve_existing_email = st.checkbox("Improve an existing email draft")
        existing_email = st.text_area(
            "Existing email draft",
            height=180,
            placeholder="Paste your current draft here if you want the AI to improve it.",
            disabled=not improve_existing_email,
        )

        submitted = st.form_submit_button("Generate Email", type="primary")

    return (
        submitted,
        email_purpose,
        recipient,
        situation,
        tone_preference,
        key_points,
        improve_existing_email,
        existing_email,
    )


def validate_inputs(
    email_purpose: str,
    recipient: str,
    situation: str,
    key_points: str,
    improve_existing_email: bool,
    existing_email: str,
    api_key: str,
    require_api_key: bool = True,
) -> list[str]:
    """Collect and return form validation errors."""

    errors = []
    if not email_purpose.strip():
        errors.append("Email purpose is required.")
    if not recipient.strip():
        errors.append("Recipient is required.")
    if not situation.strip():
        errors.append("Situation details are required.")
    if not key_points.strip():
        errors.append("Please add at least one key point.")
    if improve_existing_email and not existing_email.strip():
        errors.append("Improve mode is enabled, so please paste your existing email draft.")
    if require_api_key and not api_key.strip():
        errors.append("OpenAI API Key is required.")
    return errors


def sanitize_api_key(raw_api_key: str) -> tuple[str, bool]:
    """Extract a usable API key from raw user input.

    This handles common copy/paste mistakes such as pasting an entire .env block
    into a single text input.
    """

    raw = raw_api_key.strip().strip("\"").strip("'")
    if not raw:
        return "", False

    normalized = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in normalized.split("\n") if line.strip()]

    def _clean_token(token: str) -> str:
        cleaned = token.strip().strip("\"").strip("'").rstrip(",;")
        if cleaned.lower().startswith("bearer "):
            cleaned = cleaned[7:].strip()
        return cleaned

    # Best-case extraction from OPENAI_API_KEY=<value>
    for line in lines:
        if line.upper().startswith("OPENAI_API_KEY="):
            value = _clean_token(line.split("=", 1)[1])
            return value, value != raw

    # If no explicit variable is found, use first non-variable line
    for line in lines:
        if "=" not in line:
            value = _clean_token(line)
            return value, value != raw

    # Fallback: try to find an sk- style token anywhere in the input
    match = re.search(r"sk-[A-Za-z0-9_-]{20,}", raw)
    if match:
        value = match.group(0)
        return value, value != raw

    return raw, False


def render_output(result) -> None:
    """Render final outputs from the multi-agent workflow."""

    st.success("Email generated successfully.")

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Selected Strategy",
        normalize_text(result.strategy.get("selected_strategy"), "N/A").title(),
    )
    col2.metric(
        "Chosen Tone",
        normalize_text(result.tone.get("chosen_tone"), "N/A").title(),
    )
    col3.metric(
        "Quality Score",
        f"{result.review.get('quality_score', 'N/A')}/10",
    )

    st.subheader("Generated Subject Line")
    st.code(result.final_subject)

    st.subheader("Full Email Draft")
    st.text_area("Final Email", value=result.final_email, height=320)

    st.subheader("Email Quality Review")
    st.write(result.quality_review)

    strengths = result.review.get("strengths", [])
    improvements = result.review.get("improvements", [])

    if strengths:
        st.write("Strengths:")
        for item in strengths:
            st.write(f"- {item}")

    if improvements:
        st.write("Improvement Suggestions:")
        for item in improvements:
            st.write(f"- {item}")

    with st.expander("Show agent outputs"):
        st.write("Intent Agent")
        st.json(result.intent)

        st.write("Situation Analysis Agent")
        st.json(result.situation_analysis)

        st.write("Strategy Selection Agent")
        st.json(result.strategy)

        st.write("Tone Selection Agent")
        st.json(result.tone)

        st.write("Email Generator Agent")
        st.json(result.generated_email)

        st.write("Email Review Agent")
        st.json(result.review)


def main() -> None:
    """Entry point for the Streamlit application."""

    config = load_config()

    render_header()
    settings = render_sidebar(config)
    generation_mode = settings["generation_mode"]
    api_key = settings["api_key"]
    base_url = settings["base_url"]
    model_name = settings["model_name"]
    ollama_model = settings["ollama_model"]
    ollama_base_url = settings["ollama_base_url"]
    temperature = settings["temperature"]

    sanitized_api_key, was_sanitized = sanitize_api_key(api_key)
    if was_sanitized:
        st.sidebar.info("Detected extra text in API key input and extracted the key automatically.")

    (
        submitted,
        email_purpose,
        recipient,
        situation,
        tone_preference,
        key_points,
        improve_existing_email,
        existing_email,
    ) = render_input_form()

    if not submitted:
        return

    errors = validate_inputs(
        email_purpose=email_purpose,
        recipient=recipient,
        situation=situation,
        key_points=key_points,
        improve_existing_email=improve_existing_email,
        existing_email=existing_email,
        api_key=sanitized_api_key,
        require_api_key=generation_mode == "OpenAI API (paid)",
    )

    if errors:
        for error in errors:
            st.error(error)
        return

    request = EmailRequest(
        email_purpose=email_purpose.strip(),
        recipient=recipient.strip(),
        situation=situation.strip(),
        tone_preference=tone_preference.strip().lower(),
        key_points=key_points.strip(),
        improve_existing_email=improve_existing_email,
        existing_email=existing_email.strip(),
    )

    if generation_mode == "Local Fallback Rules (free)":
        with st.spinner("Running local fallback workflow..."):
            result = generate_fallback_result(request)
        st.warning("Using local fallback mode because API calls are disabled.")
        render_output(result)
        return

    try:
        with st.spinner("Running multi-agent workflow..."):
            if generation_mode == "Ollama Local AI (free)":
                llm = create_ollama_llm(
                    model_name=ollama_model.strip() or "llama3.2:3b",
                    temperature=temperature,
                    base_url=ollama_base_url.strip() or "http://localhost:11434",
                )
            else:
                llm = create_llm(
                    api_key=sanitized_api_key.strip(),
                    model_name=model_name.strip(),
                    temperature=temperature,
                    base_url=base_url.strip(),
                )

            orchestrator = EmailAssistantOrchestrator(llm)
            result = orchestrator.run(request)

        render_output(result)

    except Exception as exc:
        error_text = str(exc)
        lowered_error = error_text.lower()

        if "invalid_api_key" in lowered_error or "incorrect api key provided" in lowered_error:
            st.error("Invalid API key. Paste only the API key value, not a full .env block.")
            st.info("Tip: OPENAI_API_KEY should contain only the key string, and OPENAI_MODEL should be set separately.")
        elif "insufficient_quota" in lowered_error or "exceeded your current quota" in lowered_error:
            st.error("API quota exceeded for this key/account.")
            st.info("Switch Generation Mode to Ollama Local AI (free) or Local Fallback Rules (free).")
        elif generation_mode == "Ollama Local AI (free)" and (
            "connection" in lowered_error
            or "refused" in lowered_error
            or "failed to establish" in lowered_error
            or "timed out" in lowered_error
        ):
            st.error("Could not connect to Ollama.")
            st.info("Install/start Ollama, run a model (example: ollama run llama3.2:3b), then try again.")
        else:
            st.error(f"Failed to generate email: {error_text}")
            st.info("Check API key, model name, and internet connectivity.")


if __name__ == "__main__":
    main()
