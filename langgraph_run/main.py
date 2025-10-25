"""
Main entry point for the audio processing and compliance analysis system.
"""

import os
import json
import argparse
from typing import Optional
from pathlib import Path

from .workflow import AudioProcessingWorkflow, create_workflow
from .llm_clients import LLMConfig, LLMProvider, LLMClientFactory, get_default_client


def setup_environment():
    """Set up environment variables and configuration."""
    # Load environment variables from .env file if it exists
    try:
        from dotenv import load_dotenv

        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    except ImportError:
        pass  # python-dotenv not installed


def validate_audio_file(file_path: str) -> bool:
    """
    Validate that the audio file exists and has supported format.

    Args:
        file_path: Path to the audio file

    Returns:
        True if file is valid, False otherwise
    """
    if not os.path.exists(file_path):
        print(f"Error: Audio file not found: {file_path}")
        return False

    # Check file extension
    supported_formats = [".wav", ".mp3", ".m4a", ".flac", ".ogg"]
    file_ext = Path(file_path).suffix.lower()

    if file_ext not in supported_formats:
        print(f"Warning: Unsupported file format: {file_ext}")
        print(f"Supported formats: {', '.join(supported_formats)}")
        # Continue anyway as the transcription service might support it

    return True


def save_results(results: dict, output_path: Optional[str] = None) -> str:
    """
    Save processing results to a JSON file.

    Args:
        results: Processing results dictionary
        output_path: Optional custom output path

    Returns:
        Path to the saved results file
    """
    if not output_path:
        # Generate default output filename
        timestamp = (
            results.get("processing_timestamp", "").replace(":", "-").replace(".", "-")
        )
        audio_file = Path(results.get("audio_file", "unknown")).stem
        output_path = f"results_{audio_file}_{timestamp}.json"

    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save results
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    return str(output_path)


def print_summary(results: dict):
    """Print a summary of the processing results."""
    print("\n" + "=" * 60)
    print("AUDIO PROCESSING RESULTS SUMMARY")
    print("=" * 60)

    # Basic info
    audio_file = results.get("audio_file", "Unknown")
    processing_time = results.get("processing_duration", 0)
    print(f"Audio File: {audio_file}")
    print(
        f"Processing Time: {processing_time:.2f} seconds"
        if processing_time
        else "Processing Time: Unknown"
    )

    # Transcription summary
    transcription = results.get("transcription", {})
    if transcription:
        speaker_turns = transcription.get("speaker_turns", [])
        duration = transcription.get("total_duration", "Unknown")
        print(f"Transcript: {len(speaker_turns)} speaker turns, {duration} duration")

    # Summary
    summary = results.get("summary", {})
    if summary:
        participant_count = summary.get("participant_count", 0)
        key_topics_count = len(summary.get("key_topics", []))
        print(
            f"Summary: {participant_count} participants, {key_topics_count} key topics"
        )

    # Sentiment
    sentiment = results.get("sentiment_analysis", {})
    if sentiment:
        overall_sentiment = sentiment.get("overall_sentiment", "Unknown")
        sentiment_score = sentiment.get("sentiment_score", 0)
        print(f"Sentiment: {overall_sentiment} (score: {sentiment_score:.2f})")

    # Compliance
    compliance = results.get("compliance_results", {})
    if compliance:
        overall_risk = compliance.get("overall_risk_assessment", "Unknown")
        print(f"Compliance Risk: {overall_risk}")

        # Individual regulation results
        regulations = ["regbi", "regdd", "miranda", "elderly_abuse"]
        for reg in regulations:
            reg_result = compliance.get(reg, {})
            if reg_result:
                reg_compliance = reg_result.get("overall_compliance", False)
                reg_risk = reg_result.get("risk_level", "Unknown")
                status = "✓ PASS" if reg_compliance else "✗ FAIL"
                print(f"  {reg.upper()}: {status} ({reg_risk} risk)")

    # Errors
    errors = results.get("errors", [])
    if errors:
        print(f"\nWarnings/Errors: {len(errors)}")
        for error in errors:
            print(f"  - {error}")

    print("=" * 60)


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Process audio files for compliance analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m langgraph_run.main /path/to/audio.wav
  python -m langgraph_run.main /path/to/audio.wav --output results.json
  python -m langgraph_run.main /path/to/audio.wav --provider vertex_ai --project my-project
        """,
    )

    parser.add_argument("audio_file", help="Path to the audio file to process")

    parser.add_argument(
        "--output", "-o", help="Output file path for results (JSON format)"
    )

    parser.add_argument(
        "--provider",
        choices=["vertex_ai", "openai", "anthropic"],
        default="vertex_ai",
        help="LLM provider to use (default: vertex_ai)",
    )

    parser.add_argument("--project", help="Google Cloud project ID (for Vertex AI)")

    parser.add_argument(
        "--location",
        default="us-central1",
        help="Google Cloud location (for Vertex AI, default: us-central1)",
    )

    parser.add_argument(
        "--model", help="Model name to use (default depends on provider)"
    )

    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress summary output"
    )

    args = parser.parse_args()

    # Setup environment
    setup_environment()

    # Validate audio file
    if not validate_audio_file(args.audio_file):
        return 1

    try:
        # Create LLM configuration
        if args.provider == "vertex_ai":
            config = LLMConfig(
                provider=LLMProvider.VERTEX_AI,
                model_name=args.model or "gemini-1.5-pro",
                project_id=args.project or os.getenv("GOOGLE_CLOUD_PROJECT"),
                location=args.location,
            )
        elif args.provider == "openai":
            config = LLMConfig(
                provider=LLMProvider.OPENAI,
                model_name=args.model or "gpt-4",
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        elif args.provider == "anthropic":
            config = LLMConfig(
                provider=LLMProvider.ANTHROPIC,
                model_name=args.model or "claude-3-sonnet-20240229",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
        else:
            print(f"Error: Unsupported provider: {args.provider}")
            return 1

        # Create client and workflow
        client = LLMClientFactory.create_client(config)
        workflow = create_workflow(client)

        # Process audio file
        print(f"Processing audio file: {args.audio_file}")
        print(f"Using {args.provider} provider...")

        results = workflow.process_audio_file(args.audio_file)

        # Save results
        output_path = save_results(results, args.output)
        print(f"\nResults saved to: {output_path}")

        # Print summary unless quiet mode
        if not args.quiet:
            print_summary(results)

        return 0

    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


def demo():
    """Run a demonstration with mock data."""
    print("Running Audio Processing Demo")
    print("=" * 40)

    # Setup environment
    setup_environment()

    # Create workflow with default settings
    try:
        workflow = create_workflow()

        # Use a mock audio file path for demo
        demo_audio_path = "/demo/sample_call.wav"

        print(f"Processing demo audio: {demo_audio_path}")
        print(workflow.get_workflow_visualization())

        # Process the demo file (will use mock data)
        results = workflow.process_audio_file(demo_audio_path)

        # Save and display results
        output_path = save_results(results, "demo_results.json")
        print(f"\nDemo results saved to: {output_path}")
        print_summary(results)

    except Exception as e:
        print(f"Demo failed: {str(e)}")
        print("This is expected if dependencies are not installed.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == "demo"):
        demo()
    else:
        sys.exit(main())
