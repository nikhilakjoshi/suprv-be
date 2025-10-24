"""
Mock LLM call for audio transcription with the expected response schema.
This file demonstrates how to structure the LLM call for transcribing audio files
with speaker identification, timestamps, and role classification.
"""

import json
from typing import Dict, List, Any


def mock_llm_call(audio_file_path: str) -> Dict[str, Any]:
    """
    Mock function simulating an LLM call for audio transcription.

    Args:
        audio_file_path: Path to the audio file to be transcribed

    Returns:
        Dictionary containing the structured transcription response
    """

    # System prompt from the image
    system_prompt = """
    Transcribe the following audio file accurately and return the information described in the following instructions.
    **Instructions:**
    - **Task 1 (Transcript):** Provide a verbatim transcript of the following conversation. Format it with speaker labels (e.g., 'Speaker 1:', 'Speaker 2:').
    - **Task 2 (Summary):** Include the start and end time of every speech in the conversation.
    - **Guidance:** Whenever possible, identify who is speaking in all the transcript, the summary, and labels. For speakers that cannot be identified, use generic labels like 'Speaker 1', 'Speaker 2', etc.
    
    Example of the generated fragment for every speech:
    {
        "speaker_name": "SPEAKER_00",
        "speech_start_timestamp": "00:07",
        "speech_end_timestamp": "00:10",
        "speech_transcription": "I just missed your call there. How can I help?",
        "speaker_role": "ADVISOR"
    }
    """

    # Mock response following the schema from the image
    mock_response = {
        "type": "OBJECT",
        "properties": {
            "speaker_turns": {
                "type": "ARRAY",
                "items": [
                    {
                        "type": "OBJECT",
                        "properties": {
                            "speaker_name": "SPEAKER_00",
                            "speech_start_timestamp": "00:02",
                            "speech_end_timestamp": "00:04",
                            "speech_transcription": "Hello, thank you for calling. How can I assist you today?",
                            "speaker_role": "ADVISOR",
                        },
                    },
                    {
                        "type": "OBJECT",
                        "properties": {
                            "speaker_name": "SPEAKER_01",
                            "speech_start_timestamp": "00:05",
                            "speech_end_timestamp": "00:12",
                            "speech_transcription": "Hi, I'm having some issues with my account and I was wondering if you could help me resolve them.",
                            "speaker_role": "CLIENT",
                        },
                    },
                    {
                        "type": "OBJECT",
                        "properties": {
                            "speaker_name": "SPEAKER_00",
                            "speech_start_timestamp": "00:13",
                            "speech_end_timestamp": "00:18",
                            "speech_transcription": "Of course, I'd be happy to help you with your account issues. Can you please provide me with your account number?",
                            "speaker_role": "ADVISOR",
                        },
                    },
                    {
                        "type": "OBJECT",
                        "properties": {
                            "speaker_name": "SPEAKER_01",
                            "speech_start_timestamp": "00:19",
                            "speech_end_timestamp": "00:23",
                            "speech_transcription": "Sure, my account number is 1234567890.",
                            "speaker_role": "CLIENT",
                        },
                    },
                    {
                        "type": "OBJECT",
                        "properties": {
                            "speaker_name": "SPEAKER_00",
                            "speech_start_timestamp": "00:24",
                            "speech_end_timestamp": "00:30",
                            "speech_transcription": "Thank you. Let me pull up your account information. I can see the issue you're referring to.",
                            "speaker_role": "ADVISOR",
                        },
                    },
                ],
            }
        },
        "required": [
            "speaker_name",
            "speech_start_timestamp",
            "speech_end_timestamp",
            "speech_transcription",
            "speaker_role",
        ],
    }

    return mock_response


def format_transcript_for_display(response: Dict[str, Any]) -> str:
    """
    Format the LLM response into a readable transcript format.

    Args:
        response: The structured response from the LLM

    Returns:
        Formatted transcript string
    """
    transcript_lines = []
    speaker_turns = response["properties"]["speaker_turns"]["items"]

    for turn in speaker_turns:
        if turn["type"] == "OBJECT":
            props = turn["properties"]
            speaker = props["speaker_name"]
            start_time = props["speech_start_timestamp"]
            end_time = props["speech_end_timestamp"]
            text = props["speech_transcription"]
            role = props["speaker_role"]

            transcript_lines.append(
                f"[{start_time} - {end_time}] {speaker} ({role}): {text}"
            )

    return "\n".join(transcript_lines)


def extract_speaker_summary(
    response: Dict[str, Any],
) -> Dict[str, List[Dict[str, str]]]:
    """
    Extract summary information grouped by speaker.

    Args:
        response: The structured response from the LLM

    Returns:
        Dictionary with speaker summaries
    """
    speaker_summary = {}
    speaker_turns = response["properties"]["speaker_turns"]["items"]

    for turn in speaker_turns:
        if turn["type"] == "OBJECT":
            props = turn["properties"]
            speaker = props["speaker_name"]

            if speaker not in speaker_summary:
                speaker_summary[speaker] = []

            speaker_summary[speaker].append(
                {
                    "start_time": props["speech_start_timestamp"],
                    "end_time": props["speech_end_timestamp"],
                    "role": props["speaker_role"],
                    "duration": f"{props['speech_start_timestamp']} - {props['speech_end_timestamp']}",
                }
            )

    return speaker_summary


if __name__ == "__main__":
    # Example usage
    audio_file = "/path/to/audio/file.wav"

    # Mock the LLM call
    print("Making mock LLM call for audio transcription...")
    response = mock_llm_call(audio_file)

    # Display the raw response
    print("\n" + "=" * 50)
    print("RAW LLM RESPONSE:")
    print("=" * 50)
    print(json.dumps(response, indent=2))

    # Display formatted transcript
    print("\n" + "=" * 50)
    print("FORMATTED TRANSCRIPT:")
    print("=" * 50)
    formatted_transcript = format_transcript_for_display(response)
    print(formatted_transcript)

    # Display speaker summary
    print("\n" + "=" * 50)
    print("SPEAKER SUMMARY:")
    print("=" * 50)
    speaker_summary = extract_speaker_summary(response)
    for speaker, turns in speaker_summary.items():
        print(f"\n{speaker}:")
        for turn in turns:
            print(f"  - {turn['duration']} ({turn['role']})")
