# LangGraph Audio Processing & Compliance Analysis System

A comprehensive audio processing pipeline built with LangGraph that transcribes audio files, generates summaries, performs sentiment analysis, and conducts regulatory compliance checks.

## Features

- **Audio Transcription**: Convert audio to text with speaker identification and timestamps
- **Conversation Summarization**: Generate executive summaries and extract key topics
- **Sentiment Analysis**: Analyze emotional tone and speaker sentiments
- **Compliance Checks**: Automated regulatory compliance analysis for:
  - RegBI (Regulation Best Interest)
  - RegDD (Regulation DD)
  - MIRANDA Disclosures
  - Elderly Abuse Detection
- **Swappable LLM Clients**: Support for multiple AI providers (Vertex AI, OpenAI, Anthropic)
- **JSON Output**: Structured results for easy integration

## Architecture

The system uses LangGraph to orchestrate a workflow with the following steps:

```
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
```

## Installation

1. **Clone or copy this directory** to your project
2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Cloud credentials** (for Vertex AI):

   ```bash
   # Option 1: Service Account Key
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"

   # Option 2: gcloud CLI
   gcloud auth application-default login
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Quick Start

### Basic Usage

```python
from langgraph_run import process_audio

# Process an audio file
results = process_audio("/path/to/audio.wav")

# Results contain transcription, summary, sentiment, and compliance data
print(f"Overall sentiment: {results['sentiment_analysis']['overall_sentiment']}")
print(f"Compliance risk: {results['compliance_results']['overall_risk_assessment']}")
```

### Advanced Usage

```python
from langgraph_run import create_workflow, LLMConfig, LLMProvider, LLMClientFactory

# Custom LLM configuration
config = LLMConfig(
    provider=LLMProvider.VERTEX_AI,
    model_name="gemini-1.5-pro",
    project_id="your-gcp-project",
    location="us-central1",
    temperature=0.1
)

# Create custom client and workflow
client = LLMClientFactory.create_client(config)
workflow = create_workflow(client)

# Process audio
results = workflow.process_audio_file("/path/to/audio.wav")
```

### Command Line Usage

```bash
# Basic processing
python -m langgraph_run.main /path/to/audio.wav

# Specify output file
python -m langgraph_run.main /path/to/audio.wav --output results.json

# Use specific provider and model
python -m langgraph_run.main /path/to/audio.wav --provider vertex_ai --project my-project

# Run demo with mock data
python -m langgraph_run.main demo
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Required for Vertex AI
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_LOCATION=us-central1
VERTEX_MODEL_NAME=gemini-1.5-pro

# Optional: Other providers
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
```

### Supported LLM Providers

- **Vertex AI** (Default): Google's managed AI platform
- **OpenAI** (Placeholder): GPT models (implementation ready)
- **Anthropic** (Placeholder): Claude models (implementation ready)

## Output Format

The system generates comprehensive JSON output:

```json
{
  "audio_file": "/path/to/audio.wav",
  "processing_timestamp": "2024-10-24T10:30:00",
  "transcription": {
    "speaker_turns": [
      {
        "speaker_name": "SPEAKER_00",
        "speech_start_timestamp": "00:02",
        "speech_end_timestamp": "00:08",
        "speech_transcription": "Hello, how can I help you?",
        "speaker_role": "ADVISOR"
      }
    ]
  },
  "summary": {
    "executive_summary": "Client consultation regarding...",
    "key_topics": ["Account opening", "Investment options"],
    "action_items": ["Send documents", "Schedule follow-up"],
    "participant_count": 2
  },
  "sentiment_analysis": {
    "overall_sentiment": "positive",
    "sentiment_score": 0.7,
    "emotional_indicators": ["Professional courtesy"]
  },
  "compliance_results": {
    "regbi": {
      "overall_compliance": true,
      "risk_level": "low",
      "findings": [...]
    },
    "regdd": {...},
    "miranda": {...},
    "elderly_abuse": {...},
    "overall_risk_assessment": "low"
  }
}
```

## Compliance Regulations

### RegBI (Regulation Best Interest)

- Brokerage account recommendations
- Electronic delivery disclosures
- Prohibited account types

### RegDD (Regulation DD)

- APY (Annual Percentage Yield) disclosures
- Promotional campaign requirements
- Banking product compliance

### MIRANDA Disclosures

- RNDIP (Retail Non-deposit Investment Products) identification
- Required disclosure statements

### Elderly Abuse Detection

- Financial exploitation indicators
- Mental capacity verification
- Unusual transaction patterns

## Customization

### Adding Custom Nodes

```python
from langgraph_run.nodes import BaseNode

class CustomAnalysisNode(BaseNode):
    def process(self, state):
        # Your custom processing logic
        state["custom_analysis"] = analyze_data(state["transcription"])
        return state

# Integrate into workflow
workflow.add_node("custom", CustomAnalysisNode().process)
workflow.add_edge("transcription", "custom")
```

### Custom LLM Client

```python
from langgraph_run.llm_clients import BaseLLMClient

class CustomLLMClient(BaseLLMClient):
    def generate_text(self, prompt, system_prompt=None):
        # Your custom implementation
        return "Generated response"

    def generate_json(self, prompt, system_prompt=None, schema=None):
        # Your custom implementation
        return {"result": "data"}
```

## File Structure

```
langgraph_run/
├── __init__.py              # Package initialization
├── main.py                  # CLI entry point
├── workflow.py              # Main LangGraph workflow
├── nodes.py                 # Processing nodes
├── llm_clients.py          # LLM client implementations
├── schemas.py              # Data models and schemas
├── prompts.py              # System prompts and templates
├── requirements.txt        # Dependencies
├── .env.example           # Environment configuration template
└── README.md              # This file
```

## Dependencies

- `langgraph>=0.2.0` - Workflow orchestration
- `langchain>=0.3.0` - LLM framework
- `google-cloud-aiplatform>=1.60.0` - Vertex AI client
- `pydantic>=2.0.0` - Data validation
- `python-dotenv>=1.0.0` - Environment configuration

## Error Handling

The system includes comprehensive error handling:

- **Graceful Degradation**: Uses mock data if processing fails
- **Error Logging**: All errors are captured in the results
- **Validation**: Input validation for audio files and configurations
- **Retries**: Built-in retry logic for API calls

## Performance

- **Parallel Processing**: Summary, sentiment, and compliance run concurrently
- **Efficient Prompting**: Optimized prompts for better response quality
- **Caching**: Results can be cached to avoid reprocessing
- **Streaming**: Support for async processing

## License

This project is part of the supervision backend system. Please ensure compliance with your organization's licensing requirements.

## Support

For issues and questions:

1. Check the error logs in the output JSON
2. Verify environment configuration
3. Ensure proper Google Cloud setup for Vertex AI
4. Review audio file format compatibility

## Migration Guide

This directory is designed to be **lift-and-shift** compatible. To move to another project:

1. Copy the entire `langgraph_run` directory
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables in `.env`
4. Set up Google Cloud credentials
5. Start processing: `python -m langgraph_run.main demo`
