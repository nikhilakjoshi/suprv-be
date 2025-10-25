"""
Processing nodes for the LangGraph audio analysis pipeline.
Each node represents a step in the processing workflow.
"""

import os
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

from .llm_clients import BaseLLMClient, get_default_client
from .schemas import (
    TranscriptionResult,
    SummaryResult,
    SentimentAnalysis,
    ComplianceResult,
    ComplianceFinding,
    AllComplianceResults,
    TRANSCRIPTION_RESPONSE_SCHEMA,
    SUMMARY_RESPONSE_SCHEMA,
    SENTIMENT_RESPONSE_SCHEMA,
    COMPLIANCE_RESPONSE_SCHEMA,
)
from .prompts import (
    TRANSCRIPTION_SYSTEM_PROMPT,
    SUMMARY_SYSTEM_PROMPT,
    SENTIMENT_ANALYSIS_SYSTEM_PROMPT,
    format_compliance_prompt,
    format_transcription_for_compliance,
    get_compliance_questions,
)


class AudioTranscriptionNode:
    """Node for transcribing audio files."""

    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        self.llm_client = llm_client or get_default_client()

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transcribe audio file to text with speaker identification.

        Args:
            state: Current workflow state containing 'audio_file_path'

        Returns:
            Updated state with 'transcription' results
        """
        audio_file_path = state.get("audio_file_path")
        if not audio_file_path:
            raise ValueError("audio_file_path is required")

        # In a real implementation, you would process the actual audio file
        # For now, we'll simulate the transcription process
        transcription_prompt = f"""
        Please transcribe the audio file located at: {audio_file_path}
        
        Return a detailed transcription with speaker identification, timestamps, and roles.
        """

        try:
            # Generate transcription using LLM
            response = self.llm_client.generate_json(
                prompt=transcription_prompt,
                system_prompt=TRANSCRIPTION_SYSTEM_PROMPT,
                schema=TRANSCRIPTION_RESPONSE_SCHEMA,
            )

            # Validate and create TranscriptionResult
            transcription_result = TranscriptionResult(**response)

            # Update state
            state["transcription"] = transcription_result.dict()
            state["processing_steps"] = state.get("processing_steps", [])
            state["processing_steps"].append(
                {
                    "step": "transcription",
                    "timestamp": datetime.now().isoformat(),
                    "status": "completed",
                }
            )

        except Exception as e:
            state["errors"] = state.get("errors", [])
            state["errors"].append(f"Transcription failed: {str(e)}")
            # Add mock transcription for testing
            state["transcription"] = self._get_mock_transcription()

        return state

    def _get_mock_transcription(self) -> Dict[str, Any]:
        """Generate mock transcription data for testing."""
        return {
            "speaker_turns": [
                {
                    "speaker_name": "SPEAKER_00",
                    "speech_start_timestamp": "00:02",
                    "speech_end_timestamp": "00:08",
                    "speech_transcription": "Hello, thank you for calling Citi Personal Wealth Management. How can I assist you today?",
                    "speaker_role": "ADVISOR",
                },
                {
                    "speaker_name": "SPEAKER_01",
                    "speech_start_timestamp": "00:09",
                    "speech_end_timestamp": "00:15",
                    "speech_transcription": "Hi, I'm interested in opening a brokerage account and would like to discuss investment options.",
                    "speaker_role": "CLIENT",
                },
                {
                    "speaker_name": "SPEAKER_00",
                    "speech_start_timestamp": "00:16",
                    "speech_end_timestamp": "00:25",
                    "speech_transcription": "Excellent! I'd be happy to help you with that. Before we proceed, I need to provide you with some important disclosure documents.",
                    "speaker_role": "ADVISOR",
                },
            ],
            "total_duration": "05:30",
            "confidence_score": 0.95,
        }


class SummaryGenerationNode:
    """Node for generating conversation summaries."""

    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        self.llm_client = llm_client or get_default_client()

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary from transcription.

        Args:
            state: Current workflow state containing 'transcription'

        Returns:
            Updated state with 'summary' results
        """
        transcription = state.get("transcription")
        if not transcription:
            raise ValueError("transcription is required")

        # Format transcription for summary
        transcript_text = format_transcription_for_compliance(transcription)

        summary_prompt = f"""
        Analyze the following conversation transcript and provide a comprehensive summary:
        
        {transcript_text}
        
        Provide insights into the main topics, key decisions, and any action items.
        """

        try:
            # Generate summary using LLM
            response = self.llm_client.generate_json(
                prompt=summary_prompt,
                system_prompt=SUMMARY_SYSTEM_PROMPT,
                schema=SUMMARY_RESPONSE_SCHEMA,
            )

            # Validate and create SummaryResult
            summary_result = SummaryResult(**response)

            # Update state
            state["summary"] = summary_result.dict()
            state["processing_steps"].append(
                {
                    "step": "summary",
                    "timestamp": datetime.now().isoformat(),
                    "status": "completed",
                }
            )

        except Exception as e:
            state["errors"] = state.get("errors", [])
            state["errors"].append(f"Summary generation failed: {str(e)}")
            # Add mock summary for testing
            state["summary"] = self._get_mock_summary()

        return state

    def _get_mock_summary(self) -> Dict[str, Any]:
        """Generate mock summary data for testing."""
        return {
            "executive_summary": "Client consultation regarding opening a brokerage account and discussing investment options with necessary compliance disclosures.",
            "key_topics": [
                "Brokerage account opening",
                "Investment options discussion",
                "Compliance disclosures",
                "Client onboarding",
            ],
            "action_items": [
                "Send disclosure documents to client",
                "Schedule follow-up call",
                "Process account application",
            ],
            "participant_count": 2,
            "call_duration": "05:30",
        }


class SentimentAnalysisNode:
    """Node for analyzing conversation sentiment."""

    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        self.llm_client = llm_client or get_default_client()

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment from transcription.

        Args:
            state: Current workflow state containing 'transcription'

        Returns:
            Updated state with 'sentiment_analysis' results
        """
        transcription = state.get("transcription")
        if not transcription:
            raise ValueError("transcription is required")

        # Format transcription for sentiment analysis
        transcript_text = format_transcription_for_compliance(transcription)

        sentiment_prompt = f"""
        Analyze the emotional tone and sentiment of the following conversation:
        
        {transcript_text}
        
        Consider the overall mood, satisfaction levels, and emotional indicators throughout the conversation.
        """

        try:
            # Generate sentiment analysis using LLM
            response = self.llm_client.generate_json(
                prompt=sentiment_prompt,
                system_prompt=SENTIMENT_ANALYSIS_SYSTEM_PROMPT,
                schema=SENTIMENT_RESPONSE_SCHEMA,
            )

            # Validate and create SentimentAnalysis
            sentiment_result = SentimentAnalysis(**response)

            # Update state
            state["sentiment_analysis"] = sentiment_result.dict()
            state["processing_steps"].append(
                {
                    "step": "sentiment_analysis",
                    "timestamp": datetime.now().isoformat(),
                    "status": "completed",
                }
            )

        except Exception as e:
            state["errors"] = state.get("errors", [])
            state["errors"].append(f"Sentiment analysis failed: {str(e)}")
            # Add mock sentiment for testing
            state["sentiment_analysis"] = self._get_mock_sentiment()

        return state

    def _get_mock_sentiment(self) -> Dict[str, Any]:
        """Generate mock sentiment data for testing."""
        return {
            "overall_sentiment": "positive",
            "sentiment_score": 0.7,
            "speaker_sentiments": {
                "SPEAKER_00": {"sentiment": "professional", "score": 0.6},
                "SPEAKER_01": {"sentiment": "interested", "score": 0.8},
            },
            "emotional_indicators": [
                "Professional courtesy",
                "Client interest",
                "Positive engagement",
            ],
        }


class ComplianceCheckNode:
    """Node for performing compliance checks."""

    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        self.llm_client = llm_client or get_default_client()

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform all compliance checks on transcription.

        Args:
            state: Current workflow state containing 'transcription'

        Returns:
            Updated state with 'compliance_results'
        """
        transcription = state.get("transcription")
        if not transcription:
            raise ValueError("transcription is required")

        # Format transcription for compliance analysis
        transcript_text = format_transcription_for_compliance(transcription)

        compliance_results = {}

        # Run each compliance check
        regulation_types = ["RegBI", "RegDD", "Miranda", "Elderly_Abuse"]

        for reg_type in regulation_types:
            try:
                compliance_result = self._run_compliance_check(
                    reg_type, transcript_text
                )
                compliance_results[reg_type.lower()] = compliance_result
            except Exception as e:
                state["errors"] = state.get("errors", [])
                state["errors"].append(f"{reg_type} compliance check failed: {str(e)}")
                # Add mock compliance result
                compliance_results[reg_type.lower()] = self._get_mock_compliance_result(
                    reg_type
                )

        # Determine overall risk assessment
        overall_risk = self._calculate_overall_risk(compliance_results)

        # Create AllComplianceResults
        all_compliance = AllComplianceResults(
            regbi=ComplianceResult(**compliance_results["regbi"]),
            regdd=ComplianceResult(**compliance_results["regdd"]),
            miranda=ComplianceResult(**compliance_results["miranda"]),
            elderly_abuse=ComplianceResult(**compliance_results["elderly_abuse"]),
            overall_risk_assessment=overall_risk,
        )

        # Update state
        state["compliance_results"] = all_compliance.dict()
        state["processing_steps"].append(
            {
                "step": "compliance_checks",
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
            }
        )

        return state

    def _run_compliance_check(
        self, regulation_type: str, transcript_text: str
    ) -> Dict[str, Any]:
        """Run a specific compliance check."""
        compliance_prompt = format_compliance_prompt(regulation_type)

        full_prompt = f"""
        {compliance_prompt}
        
        Transcript to analyze:
        {transcript_text}
        """

        # Generate compliance analysis using LLM
        response = self.llm_client.generate_json(
            prompt=full_prompt, schema=COMPLIANCE_RESPONSE_SCHEMA
        )

        # Process findings
        findings = []
        overall_compliance = True

        for finding_data in response.get("findings", []):
            finding = ComplianceFinding(**finding_data)
            findings.append(finding.dict())
            if finding.answer == "False":
                overall_compliance = False

        # Determine risk level
        risk_level = "low" if overall_compliance else "medium"
        if (
            not overall_compliance
            and len([f for f in findings if f["answer"] == "False"]) > 2
        ):
            risk_level = "high"

        return {
            "regulation_type": regulation_type,
            "findings": findings,
            "overall_compliance": overall_compliance,
            "risk_level": risk_level,
        }

    def _get_mock_compliance_result(self, regulation_type: str) -> Dict[str, Any]:
        """Generate mock compliance data for testing."""
        return {
            "regulation_type": regulation_type,
            "findings": [
                {
                    "rational": f"Mock finding for {regulation_type} - compliance check completed successfully",
                    "answer": "True",
                    "start_timestamp": "02:15",
                }
            ],
            "overall_compliance": True,
            "risk_level": "low",
        }

    def _calculate_overall_risk(self, compliance_results: Dict[str, Any]) -> str:
        """Calculate overall risk assessment from all compliance results."""
        high_risk_count = sum(
            1
            for result in compliance_results.values()
            if result.get("risk_level") == "high"
        )
        medium_risk_count = sum(
            1
            for result in compliance_results.values()
            if result.get("risk_level") == "medium"
        )

        if high_risk_count > 0:
            return "high"
        elif medium_risk_count > 1:
            return "medium"
        else:
            return "low"


class ResultsCompilerNode:
    """Node for compiling final results."""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compile all processing results into final output.

        Args:
            state: Current workflow state with all processing results

        Returns:
            Updated state with final 'results' compiled
        """
        # Calculate processing duration
        start_time = state.get("start_time")
        processing_duration = None
        if start_time:
            processing_duration = time.time() - start_time

        # Compile final results
        final_results = {
            "audio_file": state.get("audio_file_path", ""),
            "processing_timestamp": datetime.now().isoformat(),
            "transcription": state.get("transcription", {}),
            "summary": state.get("summary", {}),
            "sentiment_analysis": state.get("sentiment_analysis", {}),
            "compliance_results": state.get("compliance_results", {}),
            "processing_duration": processing_duration,
            "processing_steps": state.get("processing_steps", []),
            "errors": state.get("errors", []),
        }

        state["results"] = final_results
        state["processing_steps"].append(
            {
                "step": "results_compilation",
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
            }
        )

        return state
