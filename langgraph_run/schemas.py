"""
Data models and schemas for the audio processing pipeline.
"""

from typing import Dict, List, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class SpeakerTurn(BaseModel):
    """Model for individual speaker turns in transcription."""

    speaker_name: str = Field(
        ..., description="Name/ID of the speaker (e.g., SPEAKER_00)"
    )
    speech_start_timestamp: str = Field(
        ..., description="Start timestamp in MM:SS format"
    )
    speech_end_timestamp: str = Field(..., description="End timestamp in MM:SS format")
    speech_transcription: str = Field(..., description="Transcribed text for this turn")
    speaker_role: str = Field(
        ..., description="Role of the speaker (ADVISOR, CLIENT, etc.)"
    )


class TranscriptionResult(BaseModel):
    """Model for complete transcription results."""

    speaker_turns: List[SpeakerTurn] = Field(..., description="List of speaker turns")
    total_duration: Optional[str] = Field(None, description="Total audio duration")
    confidence_score: Optional[float] = Field(
        None, description="Overall transcription confidence"
    )


class SummaryResult(BaseModel):
    """Model for transcription summary."""

    executive_summary: str = Field(
        ..., description="Brief executive summary of the conversation"
    )
    key_topics: List[str] = Field(..., description="Main topics discussed")
    action_items: List[str] = Field(
        default_factory=list, description="Action items identified"
    )
    participant_count: int = Field(..., description="Number of participants")
    call_duration: Optional[str] = Field(None, description="Duration of the call")


class SentimentAnalysis(BaseModel):
    """Model for sentiment analysis results."""

    overall_sentiment: Literal["positive", "negative", "neutral"] = Field(
        ..., description="Overall conversation sentiment"
    )
    sentiment_score: float = Field(
        ...,
        ge=-1.0,
        le=1.0,
        description="Sentiment score from -1 (negative) to 1 (positive)",
    )
    speaker_sentiments: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Individual speaker sentiment analysis"
    )
    emotional_indicators: List[str] = Field(
        default_factory=list, description="Detected emotional indicators"
    )


class ComplianceFinding(BaseModel):
    """Model for individual compliance findings."""

    rational: str = Field(..., description="Rationale for the finding")
    answer: Literal["True", "False"] = Field(..., description="Compliance check result")
    start_timestamp: Optional[str] = Field(
        None, description="Timestamp where issue was found"
    )


class ComplianceResult(BaseModel):
    """Model for compliance check results."""

    regulation_type: str = Field(
        ..., description="Type of regulation (RegBI, RegDD, MIRANDA, Elderly_Abuse)"
    )
    findings: List[ComplianceFinding] = Field(
        ..., description="List of compliance findings"
    )
    overall_compliance: bool = Field(..., description="Overall compliance status")
    risk_level: Literal["low", "medium", "high"] = Field(
        ..., description="Risk level assessment"
    )


class AllComplianceResults(BaseModel):
    """Model for all compliance check results."""

    regbi: ComplianceResult = Field(..., description="RegBI compliance results")
    regdd: ComplianceResult = Field(..., description="RegDD compliance results")
    miranda: ComplianceResult = Field(..., description="MIRANDA compliance results")
    elderly_abuse: ComplianceResult = Field(
        ..., description="Elderly abuse compliance results"
    )
    overall_risk_assessment: Literal["low", "medium", "high"] = Field(
        ..., description="Overall risk assessment"
    )


class ProcessingResult(BaseModel):
    """Model for complete processing pipeline result."""

    audio_file: str = Field(..., description="Original audio file path")
    processing_timestamp: datetime = Field(
        default_factory=datetime.now, description="When processing was completed"
    )
    transcription: TranscriptionResult = Field(..., description="Transcription results")
    summary: SummaryResult = Field(..., description="Summary results")
    sentiment_analysis: SentimentAnalysis = Field(
        ..., description="Sentiment analysis results"
    )
    compliance_results: AllComplianceResults = Field(
        ..., description="All compliance check results"
    )
    processing_duration: Optional[float] = Field(
        None, description="Total processing time in seconds"
    )


# Schema definitions for LLM responses
TRANSCRIPTION_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "speaker_turns": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "speaker_name": {"type": "string"},
                    "speech_start_timestamp": {"type": "string"},
                    "speech_end_timestamp": {"type": "string"},
                    "speech_transcription": {"type": "string"},
                    "speaker_role": {"type": "string"},
                },
                "required": [
                    "speaker_name",
                    "speech_start_timestamp",
                    "speech_end_timestamp",
                    "speech_transcription",
                    "speaker_role",
                ],
            },
        }
    },
    "required": ["speaker_turns"],
}

SUMMARY_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "executive_summary": {"type": "string"},
        "key_topics": {"type": "array", "items": {"type": "string"}},
        "action_items": {"type": "array", "items": {"type": "string"}},
        "participant_count": {"type": "integer"},
        "call_duration": {"type": "string"},
    },
    "required": ["executive_summary", "key_topics", "participant_count"],
}

SENTIMENT_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "overall_sentiment": {
            "type": "string",
            "enum": ["positive", "negative", "neutral"],
        },
        "sentiment_score": {"type": "number", "minimum": -1.0, "maximum": 1.0},
        "speaker_sentiments": {"type": "object"},
        "emotional_indicators": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["overall_sentiment", "sentiment_score"],
}

COMPLIANCE_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "rational": {"type": "string"},
                    "answer": {"type": "string", "enum": ["True", "False"]},
                    "start_timestamp": {"type": "string"},
                },
                "required": ["rational", "answer"],
            },
        }
    },
    "required": ["findings"],
}
