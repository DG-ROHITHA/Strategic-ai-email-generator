"""Streamlit UI for Strategic Agentic AI Email Assistant."""

import re
from pathlib import Path

import streamlit as st

from src.config import create_gemini_llm, load_config
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
    st.sidebar.write("Set your Gemini API key and model options.")

    generation_mode = st.sidebar.selectbox(
        "Generation Mode",
        [
            "Gemini AI",
            "Local Fallback Rules (free)",
        ],
        index=0,
    )

    if not Path(".env").exists():
        st.sidebar.warning("No .env file found. .env.example is only a template and is not loaded.")

    gemini_api_key = ""
    gemini_model = config.gemini_model

    if generation_mode == "Gemini AI":
        gemini_api_key = st.sidebar.text_input(
            "Gemini API Key",
            type="password",
            value=config.gemini_api_key,
            help="Store this in .env as GEMINI_API_KEY.",
        )
        gemini_model = st.sidebar.text_input("Gemini Model", value=config.gemini_model)

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
        "gemini_api_key": gemini_api_key,
        "gemini_model": gemini_model,
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
    gemini_api_key: str,
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
    if require_api_key and not gemini_api_key.strip():
        errors.append("Gemini API Key is required.")
    return errors


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
    gemini_api_key = settings["gemini_api_key"]
    gemini_model = settings["gemini_model"]
    temperature = settings["temperature"]

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
        gemini_api_key=gemini_api_key,
        require_api_key=generation_mode == "Gemini AI",
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
        with st.spinner("Running multi-agent workflow with Gemini..."):
            llm = create_gemini_llm(
                api_key=gemini_api_key.strip(),
                model_name=gemini_model.strip() or "gemini-2.0-flash",
                temperature=temperature,
            )

            orchestrator = EmailAssistantOrchestrator(llm)
            result = orchestrator.run(request)

        render_output(result)

    except Exception as exc:
        error_text = str(exc)
        lowered_error = error_text.lower()

        if "invalid" in lowered_error and "api" in lowered_error:
            st.error("Invalid Gemini API key. Please check your GEMINI_API_KEY.")
        elif "quota" in lowered_error or "limit" in lowered_error or "exceeded" in lowered_error:
            st.error("API quota exceeded for this Gemini key/account.")
            st.info("Switch Generation Mode to Local Fallback Rules (free).")
        else:
            st.error(f"Failed to generate email: {error_text}")
            st.info("Check your Gemini API key, model name, and internet connectivity.")


if __name__ == "__main__":
    main()
