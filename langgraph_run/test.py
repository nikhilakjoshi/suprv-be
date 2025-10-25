"""
Test script to verify the LangGraph audio processing system.
"""

import json
import sys
from pathlib import Path

# Add the current directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from workflow import create_workflow
    from llm_clients import LLMConfig, LLMProvider
    from main import demo, print_summary

    def test_workflow_creation():
        """Test that the workflow can be created."""
        print("Testing workflow creation...")
        try:
            workflow = create_workflow()
            print("✓ Workflow created successfully")
            return True
        except Exception as e:
            print(f"✗ Workflow creation failed: {e}")
            return False

    def test_workflow_visualization():
        """Test workflow visualization."""
        print("\nTesting workflow visualization...")
        try:
            workflow = create_workflow()
            viz = workflow.get_workflow_visualization()
            print("✓ Workflow visualization generated")
            print(viz)
            return True
        except Exception as e:
            print(f"✗ Workflow visualization failed: {e}")
            return False

    def test_mock_processing():
        """Test processing with mock data."""
        print("\nTesting mock processing...")
        try:
            workflow = create_workflow()
            results = workflow.process_audio_file("/test/mock_audio.wav")

            # Verify results structure
            required_keys = [
                "transcription",
                "summary",
                "sentiment_analysis",
                "compliance_results",
            ]
            for key in required_keys:
                if key not in results:
                    print(f"✗ Missing required key: {key}")
                    return False

            print("✓ Mock processing completed successfully")
            return True
        except Exception as e:
            print(f"✗ Mock processing failed: {e}")
            return False

    def test_results_format():
        """Test that results are properly formatted."""
        print("\nTesting results format...")
        try:
            workflow = create_workflow()
            results = workflow.process_audio_file("/test/mock_audio.wav")

            # Test JSON serialization
            json_str = json.dumps(results, indent=2)
            parsed = json.loads(json_str)

            # Test summary printing
            print_summary(results)

            print("✓ Results format validation passed")
            return True
        except Exception as e:
            print(f"✗ Results format validation failed: {e}")
            return False

    def run_all_tests():
        """Run all tests."""
        print("Running LangGraph Audio Processing Tests")
        print("=" * 50)

        tests = [
            test_workflow_creation,
            test_workflow_visualization,
            test_mock_processing,
            test_results_format,
        ]

        passed = 0
        total = len(tests)

        for test in tests:
            if test():
                passed += 1
            print()

        print("=" * 50)
        print(f"Tests completed: {passed}/{total} passed")

        if passed == total:
            print("✓ All tests passed! System is ready to use.")
            return True
        else:
            print("✗ Some tests failed. Please check the errors above.")
            return False

    if __name__ == "__main__":
        success = run_all_tests()

        if success:
            print("\nRunning demonstration...")
            demo()

        sys.exit(0 if success else 1)

except ImportError as e:
    print(f"Import error: {e}")
    print("This is expected if dependencies are not installed.")
    print("To install dependencies, run: pip install -r requirements.txt")

    # Show what the system would do
    print("\nSystem Overview:")
    print("=" * 40)
    print(
        """
This LangGraph audio processing system would:

1. 🎵 Transcribe audio files with speaker identification
2. 📝 Generate conversation summaries and extract key topics  
3. 😊 Analyze sentiment and emotional indicators
4. 📋 Perform regulatory compliance checks:
   - RegBI (Regulation Best Interest)
   - RegDD (Regulation DD) 
   - MIRANDA Disclosures
   - Elderly Abuse Detection
5. 📊 Compile everything into structured JSON output

The system is designed to be modular and supports:
- Swappable LLM clients (Vertex AI, OpenAI, Anthropic)
- Parallel processing for efficiency
- Comprehensive error handling
- Easy integration with existing systems

To get started:
1. Install dependencies: pip install -r requirements.txt
2. Configure environment: cp .env.example .env (and fill in values)
3. Set up Google Cloud credentials for Vertex AI
4. Run: python -m langgraph_run.main demo
    """
    )

    sys.exit(1)
