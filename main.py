from agent import build_agent
from logging_config import get_logger

logger = get_logger()


def final_text(result: dict) -> str:
    messages = result.get("messages", [])

    if not messages:
        return "The agent did not return a message."

    last_message = messages[-1]
    content = getattr(last_message, "content", last_message)

    if isinstance(content, list):
        return "\n".join(
            str(item.get("text", item)) if isinstance(item, dict) else str(item)
            for item in content
        )

    return str(content)


def main():
    print("\n=== Study Assistant Agent ===")
    print("Type 'exit' to stop.\n")

    try:
        agent = build_agent()
        logger.info("APPLICATION STARTED")
    except Exception as error:
        logger.exception("APPLICATION FAILED TO START")
        print(f"Setup error: {error}")
        return

    while True:
        question = input("You: ").strip()

        if question.lower() in {"exit", "quit"}:
            logger.info("APPLICATION CLOSED BY USER")
            print("Goodbye!")
            break

        if not question:
            continue

        # This line must appear in agent.log
        logger.info("USER question=%r", question)

        try:
            result = agent.invoke(
                {"messages": [{"role": "user", "content": question}]}
            )

            answer = final_text(result)

            # This line must appear in agent.log
            logger.info("AGENT final_answer=%r", answer)

            print(f"\nAssistant: {answer}\n")

        except Exception as error:
            logger.exception("AGENT EXECUTION FAILED")
            print(f"\nSomething went wrong: {error}\n")


if __name__ == "__main__":
    main()
