from langchain.agents import create_agent
from langchain_groq import ChatGroq

from config import GROQ_API_KEY, GROQ_MODEL
from tools.calculator import calculator
from tools.file_reader import read_study_file


def build_agent():
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        raise RuntimeError(
            "GROQ_API_KEY is missing. Create a .env file from .env.example "
            "and add your Groq API key."
        )

    model = ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        temperature=0,
    )

    return create_agent(
        model=model,
        tools=[calculator, read_study_file],
        system_prompt=(
            "You are a helpful study assistant. "
            "For every arithmetic or math question, you MUST call the calculator tool. "
            "Never calculate arithmetic yourself. "
            "Use read_study_file when the user asks about a file in the data folder. "
            "Never claim that you read a file unless the tool returned its contents. "
            "Keep answers clear and beginner-friendly."
        ),
    )
