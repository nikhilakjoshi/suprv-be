"""
System prompts for various processing steps in the audio analysis pipeline.
"""

# ============================================================================
# TRANSCRIPTION PROMPTS
# ============================================================================

TRANSCRIPTION_SYSTEM_PROMPT = """
You are an expert audio transcription specialist. Transcribe the provided audio file with extreme precision and return ONLY valid JSON following the exact schema provided.

**CRITICAL INSTRUCTIONS:**

**TIMESTAMP ACCURACY:**
- Use PRECISE timestamps in MM:SS format (e.g., "01:23", "00:05", "12:47")
- NEVER use placeholder or estimated timestamps
- Calculate exact start and end times from the actual audio
- Ensure timestamps are sequential and non-overlapping
- Each speech segment must have distinct start/end times
- Validate that end_timestamp > start_timestamp for every segment

**UTTERANCE SEGMENTATION:**
- Break speech into NATURAL conversation turns, not arbitrary chunks
- Start a NEW utterance when:
  * Speaker changes
  * Natural pause longer than 2 seconds occurs
  * Complete thought/sentence ends with clear pause
  * Topic or context shifts significantly
- DO NOT split single sentences across multiple utterances
- DO NOT create artificial breaks mid-sentence
- Each utterance should contain complete thoughts or natural speech units
- Preserve the natural flow of conversation

**SPEAKER IDENTIFICATION:**
- Use consistent speaker labels: SPEAKER_00, SPEAKER_01, SPEAKER_02, etc.
- Maintain same speaker ID throughout the conversation
- Identify speaker roles when clear: ADVISOR, CLIENT, AGENT, CUSTOMER, etc.
- If role unclear, use UNKNOWN as speaker_role

**OUTPUT FORMAT:**
- Return ONLY valid JSON matching the exact schema
- NO additional text, explanations, or markdown formatting
- Ensure all JSON is properly escaped and formatted
- Validate JSON structure before returning

Return the transcription in the following JSON format:
{
    "speaker_turns": [
        {
            "speaker_name": "SPEAKER_00",
            "speech_start_timestamp": "00:01",
            "speech_end_timestamp": "00:04", 
            "speech_transcription": "Hello, thank you for calling our support line.",
            "speaker_role": "AGENT"
        }
    ]
}
"""

# ============================================================================
# SUMMARY PROMPTS
# ============================================================================

SUMMARY_SYSTEM_PROMPT = """
You are an expert conversation analyst. Analyze the provided call transcription and create a comprehensive summary.

Your task is to:
1. Provide a clear, executive-level summary of the conversation
2. Identify and list the key topics discussed
3. Extract any action items or next steps mentioned
4. Count the number of unique participants
5. Estimate the call duration if possible

Focus on:
- Main purpose of the call
- Key decisions or outcomes
- Important information exchanged
- Any issues or concerns raised
- Follow-up actions required

Return ONLY valid JSON format with no additional text or explanation.
"""

# ============================================================================
# SENTIMENT ANALYSIS PROMPTS
# ============================================================================

SENTIMENT_ANALYSIS_SYSTEM_PROMPT = """
You are an expert in sentiment analysis and emotional intelligence. Analyze the provided conversation transcript to determine the emotional tone and sentiment.

Your analysis should include:
1. Overall sentiment of the entire conversation (positive, negative, or neutral)
2. A numerical sentiment score from -1.0 (very negative) to +1.0 (very positive)
3. Individual speaker sentiment analysis where possible
4. Specific emotional indicators found in the conversation

Consider:
- Tone and language used
- Emotional expressions and reactions
- Level of satisfaction or frustration
- Courtesy and professionalism
- Stress indicators or positive rapport
- Resolution outcomes

Return ONLY valid JSON format with no additional text or explanation.
"""

# ============================================================================
# COMPLIANCE ANALYSIS PROMPT
# ============================================================================

COMPLIANCE_SYSTEM_PROMPT = """
Answer the user query using only the transcription.
If you do not know the answer or cannot find the answer in the transcription, then do not guess. Do not make up answers or make unsupported assumptions or claims.
Answer the questions below with only True or False. If the answer is True, also extract Start Timestamp. If the answer is False, return None in Start Timestamp.
ONLY return json.

Now, answer the user query:
You are an expert in call supervision and auditing at Citibank who reviews calls between an advisor and client(s). You will analyze the provided call transcript, which includes spoken notes. Your task is to evaluate the call based on compliance; determine if the call adheres to the required guidelines and regulations.

You will receive a call transcript which includes each word uttered, transcribed into English text
- For each speaker turn, you are provided the following metadata in addition to the actual transcription of what that speaker has said:
  - Timestamp start and end minutes/seconds of the speaker's turn
  - A speaker name. If no speaker name could be inferred, they will be referred to as "Speaker 0", "Speaker 1", etc.
  - A speaker role: In this use case, it is either "Advisor" or "Client". In case there are multiple clients on the call, they can have them all tagged with role "Client" if their speaker names are distinct.

Answer the following questions:
"""

# ============================================================================
# REGULATION BEST INTEREST (RegBI) QUESTIONS AND REFERENCES
# ============================================================================

REGBI_QUESTIONS = [
    "Were brokerage or managed accounts mentioned during the call?",
    "Were any recommendations made for brokerage or managed accounts?",
    "Did the advisor recommend a brokerage or managed account of a prohibited type during the call? Examples include recommendations regarding the selection of bank deposit programs or other sweep vehicles, and recommendations regarding digital self-directed account types/offerings (i.e. Citi Self Invest, Citi Wealth Builder and Citi Wealth Builder Plus).",
    "Was electronic delivery or eDelivery discussed during the call?",
    "If electronic delivery or eDelivery was discussed, did the advisor read the Reg BI Consent and Disclosure Script verbatim?",
    "If electronic delivery or eDelivery was discussed, did the advisor agreed to it?",
]

REGBI_CONSENT_DISCLOSURE_SCRIPT = """
For reference, this is the Reg BI Consent and Disclosure Script:
Thank you for providing your email address.

We will use this e-mail address for your records and to contact you here at Citi Personal Wealth Management ("CPWM") [or Citi Personal Investments International ("CPII") if applicable].

Is that OK? [Note to RR: If not OK, get an e-mail address that consumer wants CPWM [or CPII] to use. Enter it in Salesforce.]

Before we continue - I am required to provide you with disclosure documents called the Client Relationship Summary and a Regulation Best Interest Disclosure Statement. If you agree to electronic delivery, I can send them to you at the email address you provided to me so you can access the documents online at the location noted in the email. We will also use this email address to send you any changes, updates, and other related documents, now and in the future.

Is that ok with you?

Lastly, I want to quickly note several considerations regarding electronic delivery:

You'll only receive electronic copies of the documents, not paper copies.
You can request paper copies at any time by contacting us at 877-357-3399
You can revoke your consent at any time by contacting us at this same number
Documents may be delivered now and in the future in PDF or other similar format, as attachments or as links to online locations noted in the email, so to view them you may need to install Adobe Reader. By agreeing, you acknowledge you have access to computers or other devices with hardware and software adequate to access and review our notices and the documents.
You may incur expense accessing or reviewing documents electronically such as online time, printing.
There may be risks in accessing documents such as slow downloading time and system outage.
You will get a follow up e-mail with the terms of your consent and how to access documents received through electronic delivery in further detail.

Thank you for allowing me[us] to send you these important notices via email as requested.

We can now complete the remaining portion of the account opening questionnaire.
"""

# ============================================================================
# REGULATION DD (RegDD) QUESTIONS
# ============================================================================

REGDD_QUESTIONS = [
    'Did the advisor mention exactly "APY" acronym?',
    'Did the advisor mention the full term "Annual Percentage Yield" before using the "APY" acronym?',
    "Was a new promotional campaign or a promotion on banking products that clients want to leverage in future discussed during the call? Say False if the promotion ended.",
    "If a promotional campaign was discussed during the call, did the agent give the following info on the campaign: a) award amount or type, b) minimum balance, c) the time and / or required behaviours for the promotion, d) when the bonus / award will be provided?",
]

# ============================================================================
# MIRANDA DISCLOSURE QUESTIONS AND REFERENCES
# ============================================================================

MIRANDA_QUESTIONS = [
    "Is RNDIP (Retail Non-deposit investment products) discussed during the call? (Keywords that indicate RNDIP: Investment Products, Mutual Funds, Brokered CD, Equities, Common Stocks, Fixed Income Products, Corporate Bonds, Municipal Bonds, Bonds, Treasury, Account Opening, Trades/Quotes, Annuity Products)",
    "Did the advisor read the MIRANDA disclosure?",
]

MIRANDA_DISCLOSURE_REFERENCE = """
For reference, these are the MIRANDA Disclosures:
Retail Non-deposit investment products (RNDIP) are:
1. Not insured by the FDIC.
2. Not a deposit or other obligation of, or guaranteed by, the Bank or an affiliate of the bank.
3. Subject to investment risk, including possible loss of the principal invested.
"""

# ============================================================================
# ELDERLY ABUSE QUESTIONS
# ============================================================================

ELDERLY_ABUSE_QUESTIONS = [
    "Were there any signs of potential financial exploitation or coercion of elderly clients?",
    "Did the advisor verify the client's mental capacity for financial decisions?",
    "Were there any unusual requests for large withdrawals or transfers?",
    "Did anyone other than the account holder attempt to influence the conversation?",
    "Were proper verification procedures followed for elderly client interactions?",
]

# ============================================================================
# UTILITY FUNCTIONS FOR PROMPT GENERATION
# ============================================================================


def get_compliance_questions(regulation_type: str) -> list:
    """Get questions for a specific regulation type."""
    question_map = {
        "RegBI": REGBI_QUESTIONS,
        "RegDD": REGDD_QUESTIONS,
        "Miranda": MIRANDA_QUESTIONS,
        "Elderly_Abuse": ELDERLY_ABUSE_QUESTIONS,
    }
    return question_map.get(regulation_type, [])


def format_compliance_prompt(regulation_type: str) -> str:
    """Format the compliance prompt with specific regulation questions."""
    questions = get_compliance_questions(regulation_type)

    prompt = COMPLIANCE_SYSTEM_PROMPT

    # Add questions
    for i, question in enumerate(questions, 1):
        prompt += f"\n{i}. {question}"

    # Add reference materials
    if regulation_type == "RegBI":
        prompt += f"\n\n{REGBI_CONSENT_DISCLOSURE_SCRIPT}"
    elif regulation_type == "Miranda":
        prompt += f"\n\n{MIRANDA_DISCLOSURE_REFERENCE}"

    return prompt


def format_transcription_for_compliance(transcription_result: dict) -> str:
    """Format transcription result for compliance analysis."""
    formatted_text = "Call Transcript:\n\n"

    if "speaker_turns" in transcription_result:
        for turn in transcription_result["speaker_turns"]:
            speaker = turn.get("speaker_name", "Unknown")
            role = turn.get("speaker_role", "Unknown")
            start_time = turn.get("speech_start_timestamp", "00:00")
            end_time = turn.get("speech_end_timestamp", "00:00")
            text = turn.get("speech_transcription", "")

            formatted_text += (
                f"[{start_time} - {end_time}] {speaker} ({role}): {text}\n"
            )

    return formatted_text
