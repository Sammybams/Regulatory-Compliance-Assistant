# Handle language classification and translation tasks

import os
import json
import yaml
from pathlib import Path
from .functions import translation_format
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

script_location = Path(__file__).absolute().parent
file_location = script_location / 'prompts.yml'
prompts = yaml.safe_load(file_location.read_text())


client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=OPENROUTER_API_KEY,
)

def arabic_to_english_translation(text: str) -> str:
    """
    Translate Arabic text to English.

    Args:
        text (str): The input Arabic text.

    Returns:
        str: The translated English text.
    """
    system_prompt = prompts["prompts"]["translate_ar_en"]["system_prompt"]
    user_prompt = prompts["prompts"]["translate_ar_en"]["user_prompt"]

    response = client.responses.create(
        model="openai/gpt-oss-20b:free",
        input=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt.replace("{{ arabic_text }}", text)
                }
            ],
        # extra_body={"reasoning": {"enabled": True}},
        text = translation_format
    )

    response_dict = json.loads(response.output_text)
    return response_dict

def english_to_arabic_translation(text: str) -> str:
    """
    Translate English text to Arabic.

    Args:
        text (str): The input English text.

    Returns:
        str: The translated Arabic text.
    """
    system_prompt = prompts["prompts"]["translate_en_ar"]["system_prompt"]
    user_prompt = prompts["prompts"]["translate_en_ar"]["user_prompt"]

    response = client.responses.create(
        model="openai/gpt-oss-20b:free",
        input=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt.replace("{{ english_text }}", text)
                }
            ],
        # extra_body={"reasoning": {"enabled": True}},
        text = translation_format
    )

    response_dict = json.loads(response.output_text)
    return response_dict

if __name__ == "__main__":
    # arabic_text = "ما الأحكام الواردة في قانون حماية البيانات الشخصية بشأن حقوق صاحب البيانات في الوصول إلى بياناته الشخصية؟ بالنظر إلى المادة 1 (الفقرات 4 و5 و6) ما الذي تستخلصه؟ وبالنسبة للفقرة 6 من المادة 23، ماذا تتضمن بالضبط؟"
    # translation = arabic_to_english_translation(arabic_text)

    question = "What provisions are made in the personal data protection law for the rights of data subjects regarding access to their personal data? And from Articel 1, and Paragraphs 4, 5 and 6. What can you say? What about paragraph 6 in Article 23"
    translation = english_to_arabic_translation(question)
    print(translation)


