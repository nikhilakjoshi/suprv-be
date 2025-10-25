"""
LangGraph workflow for audio processing and compliance analysis.
"""

import time
from typing import Dict, Any, Optional
from langgraph.graph import Graph, END

from .nodes import (
    AudioTranscriptionNode,
    SummaryGenerationNode,
    SentimentAnalysisNode,
    ComplianceCheckNode,
    ResultsCompilerNode,
)
from .llm_clients import BaseLLMClient, get_default_client
from .schemas import ProcessingResult


class AudioProcessingWorkflow:
    """Main workflow class for processing audio files through the compliance analysis pipeline."""

    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        """
        Initialize the workflow with optional LLM client.

        Args:
            llm_client: Custom LLM client to use. If None, uses default Vertex AI client.
        """
        self.llm_client = llm_client or get_default_client()
        self.graph = None
        self._build_graph()

    def _build_graph(self):
        """Build the LangGraph workflow."""
        # Initialize nodes
        transcription_node = AudioTranscriptionNode(self.llm_client)
        summary_node = SummaryGenerationNode(self.llm_client)
        sentiment_node = SentimentAnalysisNode(self.llm_client)
        compliance_node = ComplianceCheckNode(self.llm_client)
        results_node = ResultsCompilerNode()

        # Create the graph
        workflow = Graph()

        # Add nodes
        workflow.add_node("transcription", transcription_node.process)
        workflow.add_node("summary", summary_node.process)
        workflow.add_node("sentiment", sentiment_node.process)
        workflow.add_node("compliance", compliance_node.process)
        workflow.add_node("results", results_node.process)

        # Define the workflow edges
        workflow.set_entry_point("transcription")

        # Sequential flow: transcription -> parallel processing -> results
        workflow.add_edge("transcription", "summary")
        workflow.add_edge("transcription", "sentiment")
        workflow.add_edge("transcription", "compliance")

        # All parallel nodes feed into results compilation
        workflow.add_edge("summary", "results")
        workflow.add_edge("sentiment", "results")
        workflow.add_edge("compliance", "results")

        # End after results compilation
        workflow.add_edge("results", END)

        # Compile the graph
        self.graph = workflow.compile()

    def process_audio_file(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Process an audio file through the complete workflow.

        Args:
            audio_file_path: Path to the audio file to process

        Returns:
            Complete processing results as dictionary
        """
        # Initialize workflow state
        initial_state = {
            "audio_file_path": audio_file_path,
            "start_time": time.time(),
            "processing_steps": [],
            "errors": [],
        }

        # Execute the workflow
        final_state = self.graph.invoke(initial_state)

        return final_state.get("results", {})

    async def process_audio_file_async(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Asynchronously process an audio file through the workflow.

        Args:
            audio_file_path: Path to the audio file to process

        Returns:
            Complete processing results as dictionary
        """
        # Initialize workflow state
        initial_state = {
            "audio_file_path": audio_file_path,
            "start_time": time.time(),
            "processing_steps": [],
            "errors": [],
        }

        # Execute the workflow asynchronously
        final_state = await self.graph.ainvoke(initial_state)

        return final_state.get("results", {})

    def get_workflow_visualization(self) -> str:
        """
        Get a text representation of the workflow structure.

        Returns:
            String representation of the workflow graph
        """
        return """
        Audio Processing Workflow:
        
        [Audio File] 
             |
             v
        [Transcription] ─────┬─────┬─────┐
             |              │     │     │
             │              v     v     v
             │         [Summary] [Sentiment] [Compliance]
             │              │     │     │
             │              └─────┼─────┘
             │                    │
             v                    v
        [Results Compilation] ────┘
             |
             v
        [Final Output JSON]
        
        Steps:
        1. Audio transcription with speaker identification
        2. Parallel processing:
           - Summary generation
           - Sentiment analysis 
           - Compliance checks (RegBI, RegDD, MIRANDA, Elderly Abuse)
        3. Results compilation into final JSON output
        """


def create_workflow(
    llm_client: Optional[BaseLLMClient] = None,
) -> AudioProcessingWorkflow:
    """
    Factory function to create a new workflow instance.

    Args:
        llm_client: Optional custom LLM client

    Returns:
        Configured AudioProcessingWorkflow instance
    """
    return AudioProcessingWorkflow(llm_client)


# Convenience functions for quick processing
def process_audio(
    audio_file_path: str, llm_client: Optional[BaseLLMClient] = None
) -> Dict[str, Any]:
    """
    Convenience function to process an audio file with default settings.

    Args:
        audio_file_path: Path to the audio file
        llm_client: Optional custom LLM client

    Returns:
        Processing results dictionary
    """
    workflow = create_workflow(llm_client)
    return workflow.process_audio_file(audio_file_path)


async def process_audio_async(
    audio_file_path: str, llm_client: Optional[BaseLLMClient] = None
) -> Dict[str, Any]:
    """
    Convenience function to asynchronously process an audio file.

    Args:
        audio_file_path: Path to the audio file
        llm_client: Optional custom LLM client

    Returns:
        Processing results dictionary
    """
    workflow = create_workflow(llm_client)
    return await workflow.process_audio_file_async(audio_file_path)


if __name__ == "__main__":
    # Example usage
    workflow = create_workflow()
    print(workflow.get_workflow_visualization())

    # Process a sample audio file (this would normally be a real file)
    sample_audio = "/path/to/sample/audio.wav"
    try:
        results = workflow.process_audio_file(sample_audio)
        print("\nProcessing completed successfully!")
        print(f"Results: {results}")
    except Exception as e:
        print(f"Error processing audio: {e}")
