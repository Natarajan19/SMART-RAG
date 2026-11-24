
import os
import time

from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from pypdf.errors import PdfReadError

from google import genai


# ==================================================
# 1. CONFIGURATION
# ==================================================

PDF_PATH = "data/sample.pdf"
VECTOR_DB_PATH = "vectorstore_db"
COLLECTION_NAME = "smartrag"

MODEL_NAME = "gemini-3.8-flash"
FALLBACK_MODEL = "gemini-3.5-flash-lite"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
TOP_K = 3


# ==================================================
# 2. LOAD API KEY
# ==================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. Check your .env file."
    )

client = genai.Client(api_key=api_key)


# ==================================================
# 3. LOAD PDF
# ==================================================

print("\nLoading PDF...")

if not os.path.exists(PDF_PATH):
    raise FileNotFoundError(
        f"PDF not found: {PDF_PATH}"
    )

loader = PyPDFLoader(PDF_PATH)
documents = loader.load()

print(
    f"PDF loaded successfully: {len(documents)} pages"
)


# ==================================================
# 4. SPLIT PDF INTO CHUNKS
# ==================================================

print("\nSplitting PDF into chunks...")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)

chunks = text_splitter.split_documents(documents)

print(f"Total chunks created: {len(chunks)}")


# ==================================================
# 5. LOAD EMBEDDING MODEL
# ==================================================

print("\nLoading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding model loaded successfully.")


# ==================================================
# 6. CONNECT TO CHROMADB
# ==================================================

print("\nConnecting to ChromaDB...")

vector_db = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=VECTOR_DB_PATH,
    embedding_function=embeddings
)

existing_data = vector_db.get()

if len(existing_data["ids"]) == 0:

    print("Creating vector embeddings...")

    vector_db.add_documents(chunks)

    print("Documents added to ChromaDB.")

else:

    print(
        f"Existing vector database loaded: "
        f"{len(existing_data['ids'])} vectors"
    )


def index_pdf(pdf_path, document_name):

    try:
        documents = PyPDFLoader(pdf_path).load()
    except PdfReadError as error:
        raise ValueError("This file is not a valid or readable PDF.") from error

    chunks = text_splitter.split_documents(documents)

    if not chunks:
        raise ValueError("The PDF does not contain readable text.")

    for chunk in chunks:
        chunk.metadata["document_name"] = document_name

    existing_ids = vector_db.get()["ids"]
    if existing_ids:
        vector_db.delete(ids=existing_ids)

    vector_db.add_documents(chunks)

    return {"pages": len(documents)}


def get_active_document_name():

    metadata = vector_db.get(limit=1, include=["metadatas"])["metadatas"]

    for item in metadata:
        if item and item.get("document_name"):
            return item["document_name"]

    return None


# ==================================================
# 7. RETRIEVE RELEVANT DOCUMENTS
# ==================================================

def retrieve_documents(question):

    results = vector_db.similarity_search(
        question,
        k=TOP_K
    )

    return results


# ==================================================
# 8. GENERATE ANSWER USING GEMINI
# ==================================================

def generate_answer(prompt):

    models = [
        MODEL_NAME,
        FALLBACK_MODEL
    ]

    for model in models:

        for attempt in range(2):

            try:

                print(f"\nTrying model: {model}")
                print(f"Attempt: {attempt + 1}")

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if response.text:
                    return response.text

                print("Empty response received.")

            except Exception as error:

                print(f"Generation error: {error}")

                error_message = str(error).upper()

                if (
                    "503" in error_message
                    or "UNAVAILABLE" in error_message
                    or "429" in error_message
                ):

                    print("Temporary API issue. Retrying...")

                    time.sleep(3)

                else:

                    print("Non-retryable API error.")
                    break

    return None


# ==================================================
# 9. COMPLETE RAG PIPELINE
# ==================================================

def ask_question(question):

    print("\nSearching relevant information...")

    relevant_docs = retrieve_documents(question)

    if not relevant_docs:

        return {
            "answer": "No relevant information found.",
            "source_pages": []
        }

    # Prepare context

    context_parts = []

    for index, doc in enumerate(
        relevant_docs,
        start=1
    ):

        page_number = doc.metadata.get("page", 0) + 1

        context_parts.append(
            f"Source {index} (Page {page_number}):\n"
            f"{doc.page_content}"
        )

    context = "\n\n".join(context_parts)

    # Prepare prompt

    prompt = f"""
You are SmartRAG, an AI Knowledge Assistant.

Answer the user's question using ONLY the provided context.

Instructions:

1. Do not invent information.
2. If the answer is not available in the context,
   clearly say that the uploaded document does not
   contain enough information.
3. Give beginner-friendly explanations.
4. Use bullet points when useful.
5. Explain technical terms clearly.

CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

    print("\nGenerating answer...")

    answer = generate_answer(prompt)

    if answer is None:

        return None

    # Collect source pages

    source_pages = sorted(
        set(
            doc.metadata.get("page", 0) + 1
            for doc in relevant_docs
        )
    )

    # Return structured response

    return {
        "answer": answer,
        "source_pages": source_pages
    }


# ==================================================
# 10. INTERACTIVE TERMINAL MODE
# ==================================================

if __name__ == "__main__":

    print("\n" + "=" * 55)
    print("SMART RAG - AI KNOWLEDGE ASSISTANT")
    print("=" * 55)

    print("System is ready!")
    print("Ask questions about your uploaded PDF.")
    print("Type 'exit' to stop.")

    while True:

        question = input(
            "\nEnter your question: "
        ).strip()

        if question.lower() in ["exit", "quit"]:

            print("\nThank you for using SmartRAG!")
            break

        if not question:

            print("Please enter a valid question.")
            continue

        result = ask_question(question)

        if result is None:

            print("\nAI service is temporarily unavailable.")
            continue

        print("\n" + "=" * 55)
        print("SMART RAG ANSWER")
        print("=" * 55)

        print(result["answer"])

        print("\nSOURCE PAGES:")

        print(
            ", ".join(
                map(str, result["source_pages"])
            )
        )

        print("=" * 55)
