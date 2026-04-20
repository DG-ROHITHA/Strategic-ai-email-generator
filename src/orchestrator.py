"""Orchestrates the full multi-agent email workflow."""

import concurrent.futures
from langchain_core.language_models.chat_models import BaseChatModel

from src.agents import (
    EmailGeneratorAgent,
    EmailReviewAgent,
    IntentAgent,
    SituationAnalysisAgent,
    StrategySelectionAgent,
    ToneSelectionAgent,
    OutcomeSimulatorAgent,
)
from src.models import AgentPipelineResult, EmailRequest
from src.utils import normalize_text


class EmailAssistantOrchestrator:
    """Runs all agents in sequence and returns final output."""

    def __init__(self, llm: BaseChatModel) -> None:
        self.intent_agent = IntentAgent(llm)
        self.situation_agent = SituationAnalysisAgent(llm)
        self.strategy_agent = StrategySelectionAgent(llm)
        self.tone_agent = ToneSelectionAgent(llm)
        self.email_generator_agent = EmailGeneratorAgent(llm)
        self.review_agent = EmailReviewAgent(llm)
        self.simulator_agent = OutcomeSimulatorAgent(llm)

    def run(self, request: EmailRequest) -> AgentPipelineResult:
        """Execute the workflow:
        User Input -> Situation Analysis -> Strategy -> Tone -> Generation -> Review -> Simulation.
        """

        intent = self.intent_agent.run(request)
        situation_analysis = self.situation_agent.run(request, intent)
        strategy = self.strategy_agent.run(request, intent, situation_analysis)
        tone = self.tone_agent.run(request, strategy, situation_analysis)

        # Optimize by running generation and review concurrently
        total_runs = (request.num_versions + 1) if request.num_versions > 1 else 1

        versions = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=total_runs + 1) as executor:
            # Kick off all email generation tasks
            generation_futures = [
                executor.submit(
                    self.email_generator_agent.run,
                    request, intent, situation_analysis, strategy, tone
                ) for _ in range(total_runs)
            ]
            
            # Use the first one that completes as our main draft
            as_completed_gen = concurrent.futures.as_completed(generation_futures)
            first_completed = next(as_completed_gen)
            generated_email = first_completed.result()
            
            # Start review immediately on the main draft
            review_future = executor.submit(
                self.review_agent.run, request, generated_email, strategy, tone
            )
            
            # Collect the rest into versions
            for f in as_completed_gen:
                versions.append(f.result().get("email_draft", ""))
                
            # Wait for review to finish
            review = review_future.result()

        final_subject = normalize_text(
            review.get("final_subject_line"),
            normalize_text(generated_email.get("subject_line"), "Professional Update"),
        )
        final_email = normalize_text(
            review.get("final_email"),
            normalize_text(generated_email.get("email_draft"), ""),
        )
        quality_review = normalize_text(
            review.get("quality_review"),
            "The email is ready with professional quality.",
        )

        simulation = self.simulator_agent.run(
            recipient=request.recipient,
            situation=request.situation,
            email_content=final_email
        )

        return AgentPipelineResult(
            intent=intent,
            situation_analysis=situation_analysis,
            strategy=strategy,
            tone=tone,
            generated_email=generated_email,
            review=review,
            final_subject=final_subject,
            final_email=final_email,
            quality_review=quality_review,
            simulation=simulation,
            versions=versions if versions else None
        )
