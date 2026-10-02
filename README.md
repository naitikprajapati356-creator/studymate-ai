# studymate-ai

# studymate-ai

# StudyMate AI Chatbot 🎓✨

A 3D-enhanced, visually stunning RAG-based chatbot that answers your academic questions using your own uploaded notes, textbooks, and PDFs. Built with LangGraph, Groq, and a beautiful Lexend-based dark theme.

## Features

- 🌌 **Immersive 3D Interface** - A floating book with orbiting shapes that follows your cursor.
- 🎨 **Dark "Night Desk" Theme** - Low-glare navy with periwinkle focus and warm amber accents.
- 📝 **RAG-Based Answers** - Chat with your own documents using Groq + Qwen embeddings.
- 🔄 **Stateful Conversations** - Remembers context throughout your session.
- ⚙️ **Production Ready** - Uses LangGraph with explicit state management.

## Setup

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```


3.  **Create Vector Store (First Run):**
    Place your PDF documents in the `data/documents/` directory.
    ```bash
    python rag/ingest.py
    ```

## Running the App

```bash
streamlit run app.py
```

## How It Works

1.  **Ingestion (`rag/ingest.py`):**
    - Loads PDFs from `data/documents/`.
    - Splits them into 1000-char chunks with 200-char overlap.
    - Embeds chunks using `all-MiniLM-L6-v2`.
    - Stores them in `vectorstore/` using Chroma.

2.  **Chat Flow (`chatbot/graph.py`):**
    - **User Input**: Receives your question.
    - **Retrieve**: Finds relevant chunks from the vector store.
    - **Build Prompt**: Combines system instructions, context, and history.
    - **Generate**: Calls the Groq LLM (Qwen).
    - **State Update**: Saves the response to the thread state.

3.  **UI (`app.py`):**
    - Renders a beautiful dark theme using CSS.
    - Includes a 3D floating book animation for visual flair.
    - Manages chat history and session state.
