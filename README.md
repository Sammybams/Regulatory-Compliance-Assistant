# Regulatory-Compliance-Assistant

The Regulatory-Compliance-Assistant is an LLM-powered system designed to analyze, interpret, and answer questions related to the Personal Data Protection Law (PDPL) with high accuracy and traceability. The core objective of the project is to provide reliable compliance-oriented responses while maintaining a strong connection between answers and the underlying legal text.

## **Context Retrieval Method Overview**

The system retrieves context using a **hybrid approach** that combines metadata filtering with semantic search:

* **1. Section Detection from the User Question**

  * Extracts any referenced **Article** numbers and **Paragraph** numbers directly from the question.
  * Also detects **sector keywords** or relevant legal topics.

* **2. Metadata-Based Retrieval (Deterministic Lookup)**

  * If the question mentions specific sections (e.g., *Article 23 Paragraph 5*), the system queries ChromaDB **using metadata filters** to fetch the exact matching chunks.
  * Ensures precise retrieval of authoritative passages.

* **3. Semantic Search Retrieval (Embedding Similarity)**

  * When no explicit section is mentioned—or to supplement precision—the system performs vector similarity search across the stored embeddings.
  * Provides broader contextual understanding.

* **4. Hybrid Merging**

  * Results from metadata-based lookup and semantic search are combined.

* **5. Final Context Passed to the LLM**

  * This ensures grounded, citation-rich answers aligned with the **Personal Data Protection Law** document.

This structured method ensures the assistant retrieves highly accurate context—even for complex legal queries—while still leveraging semantic understanding where needed.


## Run Streamlit UI (manual chat testing)

Start the Streamlit app:

```bash
streamlit run main.py
```

Open the URL shown in the terminal (usually `http://localhost:8501`) and exercise the chat UI:

* Ask general questions and PDPL questions to check scope classification.
* Ask by article/paragraph (e.g., “Show Article 1 Paragraph 3”).
* Click citation links to open the highlight viewer.

---

## Run FastAPI (endpoint/contract testing)

Start the FastAPI server:

```bash
uvicorn app:app --reload --port 8000
```

Default docs: `http://localhost:8000/docs` (if enabled). Use the following quick curl examples to test endpoints — replace placeholders as needed.
