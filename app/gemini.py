from __future__ import annotations
import os
from typing import List, Tuple
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_INSTRUCTIONS = """
You are a fact-checking assistant.
Classify the claim as TRUE, FALSE, or UNSURE.
Always return a short 'why' and add a direct google search link about the claim.
Give your answers in the following format, keep your reply to within 150 words, do not use markdown format and use 1 pair of * to bold words.
Verdict: 
Why: 
Google Search Link:
"""

def gemini_url_check(claim: str) -> str:
    """
    Checks the whole article using Gemini.
    """
    prompt = f"""{SYSTEM_INSTRUCTIONS}\n
            Claim: {claim}    
            """

    # Make the request
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    # Print the grounded response
    print(response.text)
    return response.text

def gemini_verify_with_evidence(claim: str, evidence: str) -> Tuple[str, float, List[str], str]:
    """
    Claim + (already retrieved) evidence path.
    """
    prompt = (
        f"Claim:\n{claim}\n"
        f"Give me an answer and cite sources or the most relevant URLs from the evidence below.\n"
        f"{evidence}\n\n"
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    # Print the grounded response
    print(response.text)
    return response.text

def gemini_verify_with_search(claim: str) -> Tuple[str, float, List[str], str]:
    """
    Public web path where Gemini is instructed to do its own searching and cite sources.
    """
    prompt = (
        f"{SYSTEM_INSTRUCTIONS}\n"
        f"Search the public web for up-to-date sources to verify the claim.\n"
        f"Claim:\n{claim}"
    )
    # Define the grounding tool
    grounding_tool = types.Tool(
        google_search=types.GoogleSearch()
    )

    # Configure generation settings
    config = types.GenerateContentConfig(
        tools=[grounding_tool]
    )
    # Make the request
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config,
    )

    # Print the grounded response
    print(response.text)
    return response.text