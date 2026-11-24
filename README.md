# SMART-RAG
An intelligent **Retrieval-Augmented Generation RAG application that allows users to interact with PDF documents and get context-aware answers using Large Language Models LLMs.

SmartRAG combines semantic search, vector databases, and Google's Gemini AI to retrieve relevant information from uploaded knowledge sources and generate accurate, context-based responses.

Project Overview

SmartRAG is designed to make document interaction easier. Instead of manually searching through lengthy PDF files, users can ask questions in natural language and receive relevant answers along with source page references.

Key Features

- PDF-Based Question Answering: Extract and understand content from PDF documents.
- Retrieval-Augmented Generation: Retrieve relevant document chunks before generating answers.
- Semantic Search: Find relevant information based on meaning rather than exact keyword matching.
- Vector Database: Store and retrieve document embeddings using ChromaDB.
- AI-Powered Responses: Generate answers using Google's Gemini models.
- Source References: Display the PDF page numbers used to generate answers.
- Fallback Model Support: Switch to an alternative Gemini model when the primary model is unavailable.
- Interactive Web Interface: Chat with your documents through a React-based frontend.
- REST API: Connect the frontend and AI backend using FastAPI.

Tech Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Frontend | React.js, Vite, CSS |
| Backend | FastAPI |
| LLM | Google Gemini API |
| Framework | LangChain |
| Embeddings | Hugging Face – all-MiniLM-L6-v2 |
| Vector Database | ChromaDB |
| PDF Processing | PyPDF |
| API Server | Uvicorn |

System Architecture

1. **PDF Loading:** Extract text and page information from PDF documents.
2. **Text Chunking:** Split extracted text into smaller chunks using Recursive Character Text Splitter.
3. **Embedding Generation:** Convert text chunks into numerical vectors using Hugging Face embeddings.
4. **Vector Storage:** Store embeddings in ChromaDB for efficient similarity search.
5. **User Query:** Accept natural-language questions through the React frontend.
6. **Information Retrieval:** Retrieve the most relevant document chunks using semantic similarity search.
7. **Answer Generation:** Pass the retrieved context to Gemini to generate a response.
8. **Source Attribution:** Return the answer along with relevant source page numbers.

Project Structure

```text
SMART-RAG/
│
├── data/
│   └── sample.pdf
│
├── frontend/
│   ├── src/
│   │   ├── app.jsx
│   │   ├── app.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   └── package.json
│
├── main.py
├── api.py
├── requirements.txt
├── .gitignore
└── README.md
