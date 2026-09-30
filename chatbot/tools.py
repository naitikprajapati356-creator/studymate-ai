from langchain_core.tools import tool

from rag.retriever import get_retriever


retriever = get_retriever()


@tool
def search_study_material(query: str) -> str:
    """
    Search the uploaded study material and return
    relevant information for answering the user's question.
    """

    documents = retriever.invoke(query)

    if not documents:
        return "No relevant information was found."

    results = []

    for document in documents:

        source = document.metadata.get(
            "source",
            "Unknown"
        )

        page = document.metadata.get(
            "page",
            "Unknown"
        )

        results.append(
            f"""
SOURCE: {source}
PAGE: {page}

CONTENT:
{document.page_content}
"""
        )

    return "\n\n".join(results)

@tool
def calculator(expression: str) -> str:
    """
    Calculate a mathematical expression.

    Example:
    10 * 5 + 20
    """

    try:

        result = eval(
            expression,
            {"__builtins__": {}},
            {}
        )

        return str(result)

    except Exception as e:

        return f"Calculation error: {str(e)}"