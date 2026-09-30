from langchain_chroma import Chroma

from langchain_huggingface import HuggingFaceEmbeddings

from rag.ingest import load_documents, split_documents


VECTORSTORE_PATH = "vectorstore"


def create_vectorstore():

    print("Loading documents...")

    documents = load_documents()

    print("Splitting documents...")

    chunks = split_documents(documents)

    print("Creating embeddings...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Creating vector database...")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_PATH
    )

    return vectorstore


def get_retriever():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = Chroma(
        persist_directory=VECTORSTORE_PATH,
        embedding_function=embeddings
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 4
        }
    )

    return retriever