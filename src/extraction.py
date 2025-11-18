import os
import json
import yaml
from pathlib import Path
from functions import compliance_classifier, scope_classifier_format
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

prompts = yaml.safe_load(Path("prompts.yml").read_text())


client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=OPENROUTER_API_KEY,
)


def extract_articles_and_paragraphs(question: str) -> dict:
    """
    Extract relevant articles and paragraphs from the question.

    Args:
        question (str): The input question.

    Returns:
        dict: A dictionary containing the extracted articles and paragraphs.
    """
    system_prompt = prompts["prompts"]["extractor"]["system_prompt"]
    user_prompt = prompts["prompts"]["extractor"]["user_prompt"]

    response = client.responses.create(
        model="openai/gpt-oss-20b:free",
        input=[
                # Define the system prompt
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt.replace("{{ document_text }}", question)
                }
                ],
        extra_body={"reasoning": {"enabled": True}},
        text = compliance_classifier
    )

    response_dict = json.loads(response.output_text)
    return response_dict


def extract_qa_scope(question: str) -> bool:
    """
    Extract relevant sectors from the question.

    Args:
        question (str): The input question.

    Returns:
        bool: True if the question is within scope, False otherwise.
    """
    system_prompt = prompts["prompts"]["scope_classifier"]["system_prompt"]
    user_prompt = prompts["prompts"]["scope_classifier"]["user_prompt"]

    response = client.responses.create(
        model="openai/gpt-oss-20b:free",
        input=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt.replace("{{ user_input }}", question)
                }
                ],
        extra_body={"reasoning": {"enabled": True}},
        text = scope_classifier_format
    )

    response_dict = json.loads(response.output_text)
    return response_dict["value"]


if __name__ == "__main__":
    question = "What provisions are made in the personal data protection law for the rights of data subjects regarding access to their personal data? And from Articel 1, and Paragraphs 4, 5 and 6. What can you say? What about paragraph 6 in Article 23"
    extraction_result = extract_articles_and_paragraphs(question)
    print(json.dumps(extraction_result, indent=2))
    # print(extract_qa_scope(question))