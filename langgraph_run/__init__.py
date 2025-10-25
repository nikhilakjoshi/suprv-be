"""
LangGraph Audio Processing and Compliance Analysis System

This package provides a complete workflow for processing audio files through:
1. Audio transcription with speaker identification
2. Conversation summarization
3. Sentiment analysis
4. Regulatory compliance checks (RegBI, RegDD, MIRANDA, Elderly Abuse)
5. Final JSON result compilation

The system is designed to be modular and supports swappable LLM clients,
with primary support for Google Vertex AI.
"""

__version__ = "1.0.0"
__author__ = "Supervision Backend Team"
__description__ = "Audio processing and compliance analysis workflow using LangGraph"

# Core exports
from .workflow import (
    AudioProcessingWorkflow,
    create_workflow,
    process_audio,
    process_audio_async,
)

from .llm_clients import (
    BaseLLMClient,
    VertexAIClient,
    LLMConfig,
    LLMProvider,
    LLMClientFactory,
    get_default_client,
)

from .schemas import (
    SpeakerTurn,
    TranscriptionResult,
    SummaryResult,
    SentimentAnalysis,
    ComplianceFinding,
    ComplianceResult,
    AllComplianceResults,
    ProcessingResult,
)

from .nodes import (
    AudioTranscriptionNode,
    SummaryGenerationNode,
    SentimentAnalysisNode,
    ComplianceCheckNode,
    ResultsCompilerNode,
)

# Convenience imports
from .main import demo

__all__ = [
    # Main workflow classes
    "AudioProcessingWorkflow",
    "create_workflow",
    "process_audio",
    "process_audio_async",
    # LLM clients
    "BaseLLMClient",
    "VertexAIClient",
    "LLMConfig",
    "LLMProvider",
    "LLMClientFactory",
    "get_default_client",
    # Data models
    "SpeakerTurn",
    "TranscriptionResult",
    "SummaryResult",
    "SentimentAnalysis",
    "ComplianceFinding",
    "ComplianceResult",
    "AllComplianceResults",
    "ProcessingResult",
    # Processing nodes
    "AudioTranscriptionNode",
    "SummaryGenerationNode",
    "SentimentAnalysisNode",
    "ComplianceCheckNode",
    "ResultsCompilerNode",
    # Utilities
    "demo",
]
