"""
Extracted prompts and schemas from the supervision system images.
Contains system prompts, response schemas, and compliance questions for various regulations.
"""

import json
from typing import Dict, Any

# ============================================================================
# SYSTEM PROMPT - COMPLIANCE ANALYSIS
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
# RESPONSE SCHEMA - COMPLIANCE FINDINGS
# ============================================================================

COMPLIANCE_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "findings": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "rational": {
                        "type": "STRING",
                        "description": "Rational of why the finding violates or doesn't adhere to regulations in the transcription.",
                    },
                    "answer": {
                        "type": "STRING",
                        "description": "Result of the audit question based on the analysis of the transcription. Allowed values are True or False",
                    },
                    "start_timestamp": {
                        "type": "STRING",
                        "description": "Timestamp of the analysis of the transcription",
                    },
                },
            },
        }
    },
    "required": ["findings"],
}

# ============================================================================
# REGULATION BEST INTEREST (RegBI) QUESTIONS
# ============================================================================

REGBI_QUESTIONS = [
    "Were brokerage or managed accounts mentioned during the call?",
    "Were any recommendations made for brokerage or managed accounts?",
    "Did the advisor recommend a brokerage or managed account of a prohibited type during the call? Examples include recommendations regarding the selection of bank deposit programs or other sweep vehicles, and recommendations regarding digital self-directed account types/offerings (i.e. Citi Self Invest, Citi Wealth Builder and Citi Wealth Builder Plus).",
    "Was electronic delivery or eDelivery discussed during the call?",
    "If electronic delivery or eDelivery was discussed, did the advisor read the Reg BI Consent and Disclosure Script verbatim?",
    "If electronic delivery or eDelivery was discussed, did the advisor agreed to it?",
]

# Reference text for Reg BI Consent and Disclosure Script
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
# MIRANDA DISCLOSURE QUESTIONS
# ============================================================================

MIRANDA_QUESTIONS = [
    "Is RNDIP (Retail Non-deposit investment products) discussed during the call? (Keywords that indicate RNDIP: Investment Products, Mutual Funds, Brokered CD, Equities, Common Stocks, Fixed Income Products, Corporate Bonds, Municipal Bonds, Bonds, Treasury, Account Opening, Trades/Quotes, Annuity Products)",
    "Did the advisor read the MIRANDA disclosure?",
]

# Reference text for Miranda Disclosures
MIRANDA_DISCLOSURE_REFERENCE = """
For reference, these are the MIRANDA Disclosures:
Retail Non-deposit investment products (RNDIP) are:
1. Not insured by the FDIC.
2. Not a deposit or other obligation of, or guaranteed by, the Bank or an affiliate of the bank.
3. Subject to investment risk, including possible loss of the principal invested.
"""

# ============================================================================
# ELDERLY ABUSE QUESTIONS (Referenced but not fully visible in images)
# ============================================================================

ELDERLY_ABUSE_QUESTIONS = [
    # Note: Questions not fully visible in the provided images
    # Would need clearer images to extract complete elderly abuse compliance questions
]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def get_all_compliance_questions() -> Dict[str, list]:
    """
    Returns all compliance questions organized by regulation type.

    Returns:
        Dictionary with regulation types as keys and question lists as values
    """
    return {
        "RegBI": REGBI_QUESTIONS,
        "RegDD": REGDD_QUESTIONS,
        "Miranda": MIRANDA_QUESTIONS,
        "Elderly_Abuse": ELDERLY_ABUSE_QUESTIONS,
    }


def format_compliance_prompt(regulation_type: str = "all") -> str:
    """
    Format the complete compliance analysis prompt with specific regulation questions.

    Args:
        regulation_type: Type of regulation to include ("RegBI", "RegDD", "Miranda", "Elderly_Abuse", or "all")

    Returns:
        Formatted prompt string
    """
    prompt = COMPLIANCE_SYSTEM_PROMPT

    if regulation_type == "all":
        questions = []
        all_questions = get_all_compliance_questions()
        for reg_type, reg_questions in all_questions.items():
            if reg_questions:  # Only add if questions exist
                questions.extend(reg_questions)
    else:
        questions = get_all_compliance_questions().get(regulation_type, [])

    # Add questions to prompt
    for i, question in enumerate(questions, 1):
        prompt += f"\n{i}. {question}"

    # Add reference materials based on regulation type
    if regulation_type in ["RegBI", "all"] and REGBI_QUESTIONS:
        prompt += f"\n\n{REGBI_CONSENT_DISCLOSURE_SCRIPT}"

    if regulation_type in ["Miranda", "all"] and MIRANDA_QUESTIONS:
        prompt += f"\n\n{MIRANDA_DISCLOSURE_REFERENCE}"

    return prompt


def create_mock_compliance_response() -> Dict[str, Any]:
    """
    Create a mock compliance analysis response following the expected schema.

    Returns:
        Dictionary matching the compliance response schema
    """
    return {
        "findings": [
            {
                "rational": "The advisor mentioned brokerage accounts at timestamp 02:15 when discussing investment options with the client.",
                "answer": "True",
                "start_timestamp": "02:15",
            },
            {
                "rational": "No mention of APY acronym was found in the transcription during the discussion of savings account rates.",
                "answer": "False",
                "start_timestamp": "None",
            },
            {
                "rational": "The advisor read the complete MIRANDA disclosure verbatim at timestamp 05:42 before discussing investment products.",
                "answer": "True",
                "start_timestamp": "05:42",
            },
        ]
    }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("=== COMPLIANCE SYSTEM COMPONENTS ===\n")

    # Display system prompt
    print("1. COMPLIANCE SYSTEM PROMPT:")
    print("-" * 40)
    print(COMPLIANCE_SYSTEM_PROMPT[:200] + "...")

    # Display response schema
    print("\n2. RESPONSE SCHEMA:")
    print("-" * 40)
    print(json.dumps(COMPLIANCE_RESPONSE_SCHEMA, indent=2))

    # Display all regulation questions
    print("\n3. REGULATION QUESTIONS:")
    print("-" * 40)
    all_questions = get_all_compliance_questions()
    for reg_type, questions in all_questions.items():
        print(f"\n{reg_type.upper()}:")
        for i, question in enumerate(questions, 1):
            print(f"  {i}. {question}")

    # Display formatted prompt example
    print("\n4. FORMATTED REGBI PROMPT EXAMPLE:")
    print("-" * 40)
    regbi_prompt = format_compliance_prompt("RegBI")
    print(regbi_prompt[:300] + "...")

    # Display mock response
    print("\n5. MOCK COMPLIANCE RESPONSE:")
    print("-" * 40)
    mock_response = create_mock_compliance_response()
    print(json.dumps(mock_response, indent=2))
