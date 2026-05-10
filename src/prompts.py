"""Prompt templates for all agents in the workflow."""

INTENT_AGENT_PROMPT = """
You are the Intent Agent in an email-writing multi-agent system.
Your task is to detect the user's email purpose and classify intent.

Inputs:
- Email purpose from user: {email_purpose}
- Situation details: {situation}
- Key points: {key_points}

Return only valid JSON, with no markdown:
{{
  "intent": "one short label",
  "purpose_summary": "1-2 sentence summary",
  "confidence": 0,
  "reasoning": "why this intent was selected"
}}
"""


SITUATION_ANALYSIS_PROMPT = """
You are the Situation Analysis Agent.
Your task is to understand context, urgency, relationship dynamics, and risk.

Inputs:
- Intent data: {intent_json}
- Situation details: {situation}
- Key points: {key_points}

Return only valid JSON:
{{
  "situation_summary": "short context summary",
  "urgency_level": "low|medium|high",
  "relationship_context": "relationship and context details",
  "risks": ["risk 1", "risk 2"],
  "recommended_focus": ["focus item 1", "focus item 2"]
}}
"""


STRATEGY_SELECTION_PROMPT = """
You are the Strategy Selection Agent.
Choose the best communication strategy from this fixed list:
- persuasion
- apology
- follow-up
- negotiation
- clarification

Inputs:
- User purpose: {email_purpose}
- Recipient: {recipient}
- Intent data: {intent_json}
- Situation analysis: {situation_json}

Return only valid JSON:
{{
  "selected_strategy": "one of the five allowed strategies",
  "strategy_reason": "why this strategy is best",
  "tactics": ["tactic 1", "tactic 2", "tactic 3"]
}}
"""


TONE_SELECTION_PROMPT = """
You are the Tone Selection Agent.
Pick an appropriate tone for the email.

Inputs:
- User tone preference: {tone_preference}
- Recipient: {recipient}
- Strategy data: {strategy_json}
- Situation analysis: {situation_json}

Rules:
- Respect user preference when possible.
- If preference is auto detect, infer the best professional tone.
- Keep tone aligned with strategy and situation.

Return only valid JSON:
{{
  "chosen_tone": "single tone label",
  "tone_reason": "brief reasoning",
  "tone_rules": ["rule 1", "rule 2", "rule 3"]
}}
"""


EMAIL_GENERATOR_PROMPT = """
You are the Email Generator Agent.
Draft a professional, business-ready email using the provided analysis.

Inputs:
- Recipient: {recipient}
- Intent data: {intent_json}
- Situation analysis: {situation_json}
- Strategy data: {strategy_json}
- Tone guidance: {tone_json}
- User key points: {key_points}
- Drafting style: {drafting_style}
- Improve existing email mode: {improve_existing_email}
- Existing email draft: {existing_email}

Requirements:
- Create a concise and professional subject line.
- Use greeting, clear body paragraphs, and a polite sign-off.
- Keep language professional, clear, and action-oriented.
- Do not invent facts not present in the input.
- If improve_existing_email is true and an existing draft is available, improve that draft.
- ADHERE TO STYLE: If drafting style is 'concise', keep it very short. If 'detailed', provide thorough context. If 'balanced', follow standard professional length.

Return only valid JSON:
{{
  "subject_line": "subject text",
  "email_draft": "full email with line breaks"
}}
"""


EMAIL_REVIEW_PROMPT = """
You are the Email Review Agent.
Review and improve the generated email for quality and professionalism.

Inputs:
- Recipient: {recipient}
- Strategy data: {strategy_json}
- Tone data: {tone_json}
- Subject line: {subject_line}
- Email draft: {email_draft}

Quality checks:
1. Clarity and structure
2. Professionalism
3. Tone consistency
4. Actionability and next steps
5. Grammar and concision

Return only valid JSON:
{{
  "quality_score": 0,
  "quality_review": "short review paragraph",
  "strengths": ["strength 1", "strength 2"],
  "improvements": ["improvement 1", "improvement 2"],
  "final_subject_line": "final subject text",
  "final_email": "final revised email"
}}

If the draft is already strong, keep final_subject_line and final_email mostly unchanged.
"""


OUTCOME_SIMULATOR_PROMPT = """
You are the Outcome Simulator Agent.
Predict how the recipient will react to the provided email.

Inputs:
- Recipient: {recipient}
- Situation: {situation}
- Email Content: {email_content}

Return only valid JSON:
{{
  "predicted_reaction": {{
    "positive": 0,
    "neutral": 0,
    "negative": 0
  }},
  "risk_level": "low|medium|high",
  "risk_reasoning": "why this risk level was chosen",
  "potential_objections": ["objection 1", "objection 2"]
}}
"""


EMAIL_COACH_PROMPT = """
You are the Real-Time Email Coach.
Provide live feedback on the user's current draft.

Inputs:
- Current Draft: {current_draft}
- Recipient: {recipient}
- Intent: {intent}

Provide brief, actionable feedback.
Return only valid JSON:
{{
  "tone_check": "summary of tone",
  "is_too_aggressive": false,
  "suggestions": ["suggestion 1", "suggestion 2"],
  "improved_sentence": "alternative for the most problematic part"
}}
"""

SUGGEST_POINTS_PROMPT = """
You are the Strategic Planning Agent. 
Based on the goal and recipient, suggest 3-5 key points that should be included in the email.

Inputs:
- Email Purpose: {email_purpose}
- Recipient: {recipient}

Return only valid JSON:
{{
  "suggested_points": ["point 1", "point 2", "point 3"],
  "recommended_strategy": "brief strategy hint"
}}
"""


UNIFIED_EMAIL_PROMPT = """
You are a Strategic Agentic AI Email Assistant that performs a COMPLETE multi-step professional email workflow in ONE response.

You will act as ALL of the following roles simultaneously:
1. Intent Agent — detect the user's email purpose and classify intent
2. Situation Analysis Agent — understand context, urgency, relationship dynamics, and risk
3. Strategy Selection Agent — choose the best communication strategy
4. Tone Selection Agent — pick the most appropriate tone
5. Email Generator Agent — draft {num_versions} professional email version(s)
6. Email Review Agent — review and refine the FIRST draft for quality
7. Outcome Simulator Agent — predict how the recipient will react

=== USER INPUTS ===
- Email Purpose: {email_purpose}
- Recipient: {recipient}
- Situation: {situation}
- Key Points: {key_points}
- Tone Preference: {tone_preference} (if "auto detect", infer the best professional tone)
- Drafting Style: {drafting_style} (concise / detailed / balanced)
- Improve Existing Email: {improve_existing_email}
- Existing Email Draft: {existing_email}

=== STRATEGY OPTIONS (pick one) ===
persuasion, apology, follow-up, negotiation, clarification

=== INSTRUCTIONS ===
Think step by step through each role, then produce a SINGLE JSON response with ALL sections below.
- Generate exactly {num_versions} distinct email version(s). The first version is the "main" draft that gets reviewed.
- The review should assess and optionally improve the FIRST version.
- If improve_existing_email is true and an existing draft is provided, improve that draft instead of writing from scratch.
- ADHERE TO STYLE: If drafting style is "concise", keep emails very short. If "detailed", provide thorough context. If "balanced", follow standard professional length.

Return ONLY valid JSON (no markdown, no extra text):
{{
  "intent": {{
    "intent": "one short label",
    "purpose_summary": "1-2 sentence summary",
    "confidence": 85,
    "reasoning": "why this intent was selected"
  }},
  "situation_analysis": {{
    "situation_summary": "short context summary",
    "urgency_level": "low|medium|high",
    "relationship_context": "relationship and context details",
    "risks": ["risk 1", "risk 2"],
    "recommended_focus": ["focus item 1", "focus item 2"]
  }},
  "strategy": {{
    "selected_strategy": "one of the five allowed strategies",
    "strategy_reason": "why this strategy is best",
    "tactics": ["tactic 1", "tactic 2", "tactic 3"]
  }},
  "tone": {{
    "chosen_tone": "single tone label",
    "tone_reason": "brief reasoning",
    "tone_rules": ["rule 1", "rule 2", "rule 3"]
  }},
  "generated_email": {{
    "subject_line": "subject text for version 1",
    "email_draft": "full email body for version 1 with line breaks"
  }},
  "versions": ["full email body for version 2", "full email body for version 3"],
  "review": {{
    "quality_score": 8,
    "quality_review": "short review paragraph",
    "strengths": ["strength 1", "strength 2"],
    "improvements": ["improvement 1", "improvement 2"],
    "final_subject_line": "final refined subject",
    "final_email": "final refined email body"
  }},
  "simulation": {{
    "predicted_reaction": {{
      "positive": 60,
      "neutral": 30,
      "negative": 10
    }},
    "risk_level": "low|medium|high",
    "risk_reasoning": "why this risk level was chosen",
    "potential_objections": ["objection 1", "objection 2"]
  }}
}}
"""
