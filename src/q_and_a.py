import os
import json
import yaml
from .functions import response_with_citations_schema, conversation_summary_format
from .extraction import extract_articles_and_paragraphs
from pathlib import Path
from openai import OpenAI
from langchain_core.documents import Document
from langchain_chroma.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
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
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    # model_kwargs={"device": "cpu"}
)

vector_store = Chroma(
    embedding_function=embedding,
    collection_name="Personal_Data_Protection_Law_en",
    persist_directory="../chroma_langchain_db",
)

def get_question_summary(question: str, conversation_history: list[str]) -> str:
    """
    Get a summary of the question along with conversation history.

    Args:
        question (str): The input question.
        conversation_history (list[str]): The conversation history.

    Returns:
        str: A summary of the question with conversation history.
    """
    system_prompt = prompts["prompts"]["conversation_history_prompt"]["system_prompt"]
    user_prompt = prompts["prompts"]["conversation_history_prompt"]["user_prompt"]

    # Replace user_prompt placeholders for: user_question, conversation_history
    user_prompt = user_prompt.replace("{{ question }}", question)
    user_prompt = user_prompt.replace("{{ history }}", "\n".join(conversation_history))

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
                    "content": user_prompt
                }
                ],
        # extra_body={"reasoning": {"enabled": True}},
        text = conversation_summary_format
    )

    response_dict = json.loads(response.output_text)
    return response_dict["summary"]

def get_relevant_context(question_summary: str) -> list[dict]:
    """
    Get relevant context snippets based on the question.

    Args:
        question_summary (str): The input question summary (with conversation history).

    Returns:
        list[dict]: A list of relevant context snippets.
    """
    results_search = vector_store.similarity_search(question_summary, k=5)
    mentions = extract_articles_and_paragraphs(question_summary)
    print("Extracted Articles and Paragraphs:")
    print(mentions)
    
    # access the underlying chroma collection
    chroma_collection = vector_store._collection
    updated_results_search = []
    for doc in results_search:
        updated_results_search.append(
            {
                "content": doc.page_content,
                "article number": doc.metadata["article number"],
                "paragraph number": doc.metadata["paragraph number"]
            }
        )

    results_mentions = []
    try:
      for record in mentions["articles"]:
          article = record["article"]
          paragraphs = record["paragraphs"]
          for para in paragraphs:
            res = chroma_collection.get(where={"$and": [{"article number": article}, {"paragraph number": str(para)}]}, include=["documents", "metadatas"])
            for idx, doc in enumerate(res["documents"]):
                results_mentions.append({
                        "content": doc,
                        "article number": res["metadatas"][idx]["article number"],
                        "paragraph number": res["metadatas"][idx]["paragraph number"]
                    }
                )
    except KeyError:
      print("No articles found in the extracted mentions.")
      
    return updated_results_search + results_mentions


def query_response(question: str, conversation_history: list[str], relevant_context: list[dict]) -> dict:
    """
    Query the LLM for an answer based on the question, conversation history, and relevant context.
    
    Args:
        question (str): The input question.
        conversation_history (list[str]): The conversation history.
        relevant_context (list[dict]): The relevant context extracted from documents.

    Returns:
        dict: A dictionary containing the answer and citations.
    """
    system_prompt = prompts["prompts"]["response_with_citations"]["system_prompt"]
    user_prompt = prompts["prompts"]["response_with_citations"]["user_prompt"]

    # Replace user_prompt placeholders for: user_question, conversation_history, relevant_context
    user_prompt = user_prompt.replace("{{ user_question }}", question)
    user_prompt = user_prompt.replace("{{ conversation_history }}", "\n".join(conversation_history))
    user_prompt = user_prompt.replace("{{ relevant_context }}", "\n".join(str(item) for item in relevant_context))

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
                    "content": user_prompt
                }
                ],
        extra_body={"reasoning": {"enabled": True}},
        text = response_with_citations_schema
    )

    response_dict = json.loads(response.output_text)
    return response_dict


if __name__ == "__main__":
    question = "What provisions are made in the personal data protection law for the rights of data subjects regarding access to their personal data? And from Articel 1, and Paragraphs 4, 5 and 6. What can you say? What about paragraph 6 in Article 23"
    # extraction_result = extract_articles_and_paragraphs(question)
    # print(json.dumps(extraction_result, indent=2))
    contexts = get_relevant_context(question)
    print("Relevant Context:")
    for context in contexts:
      print(context)
    print()

    response = query_response(question, [], contexts)
    print("Response:")
    print(json.dumps(response, indent=2))
    