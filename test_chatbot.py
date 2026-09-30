from chatbot.graph import graph


config = {
    "configurable": {
        "thread_id": "student-1"
    }
}


while True:

    question = input("\nYou: ")

    if question.lower() == "exit":
        break

    result = graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ]
        },
        config=config
    )

    answer = result["messages"][-1]

    print("\nAI:", answer.content)