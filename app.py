import os
from typing import Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnableParallel
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

load_dotenv()

# OpenRouter Setup
chat_model_config: dict[str, Any] = {
    "model": "google/gemini-2.0-flash-001",  # OpenRouter ka model path
    "base_url": "https://openrouter.ai/api/v1",  # Ye line sab se zaroori ha
    "default_headers": {
        "HTTP-Referer": "http://localhost:3000",  # OpenRouter ki requirement ha
        "X-Title": "LangChain Practice",
    },
}
model = ChatOpenAI(**chat_model_config)

# Step 1: Explain topic

explain_prompt = ChatPromptTemplate.from_messages([
    ("system", "Aap aik expert AI Engineer hain"),
    MessagesPlaceholder(variable_name="history"),
    ("user", "Explain the: {topic}")
])

# Step 2: Summarize

summerize_prompt = ChatPromptTemplate.from_messages([
    ("system", "Aap aik expert AI Engineer hain"),
    MessagesPlaceholder(variable_name="history"),
    ("user", "Summarize this topic in 2 lines:\n{topic}")
])

# Step 3: General chat (memory-aware direct answers)
general_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful AI assistant. Use chat history to answer personal recall questions correctly (name, favorite language, project, etc.). Reply in the language requested by the user.",
    ),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{topic}"),
])

explain_chain = explain_prompt | model | StrOutputParser()
summarize_chain = summerize_prompt | model | StrOutputParser()
general_chain = general_prompt | model | StrOutputParser()

# # Run sequentially (clear and parser-safe)
# explained_text = explain_chain.invoke({"topic": "Docker Containers"})
# response = summarize_chain.invoke({"text": explained_text})
# print(response)

# # Parallel Chains (Ek hi input → multiple outputs)

# parallel_chain = RunnableParallel({
#     "explanation": explain_chain,
#     "summary": summarize_chain
# })

# response = parallel_chain.invoke({
#     "topic": "Vector Databases",
#     "text": "Vector DB explanation"
# })

# print(response)

# Router chain (Input ke basis pe different chains choose karo)
def is_code_topic(info: dict[str, Any]) -> bool:
    topic = str(info.get("topic", "")).lower()
    return "code" in topic


def is_summary_request(info: dict[str, Any]) -> bool:
    topic = str(info.get("topic", "")).lower()
    summary_keywords = ("summarize", "summary", "2 lines", "two lines", "tl;dr")
    return any(keyword in topic for keyword in summary_keywords)


final_chain = RunnableBranch(
    (is_code_topic, explain_chain),
    (is_summary_request, summarize_chain),
    general_chain,
)

# Session-wise in-memory chat history store
store: dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


chat_chain = RunnableWithMessageHistory(
    final_chain,
    get_session_history,
    input_messages_key="topic",
    history_messages_key="history",
)

user_session = input("Enter session id (press Enter for default-session): ").strip()
session_id = user_session if user_session else "default-session"

print(f"Using session: {session_id}")
print("Type your topic/question. Type 'exit' to stop.")
print("Commands: /session, /switch <session_id>")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in {"exit", "quit"}:
        print("Chat ended.")
        break

    if user_input.lower() == "/session":
        print(f"Active session: {session_id}\n")
        continue

    if user_input.lower().startswith("/switch"):
        parts = user_input.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            print("Usage: /switch <session_id>\n")
            continue

        session_id = parts[1].strip()
        get_session_history(session_id)
        print(f"Switched to session: {session_id}\n")
        continue

    result = chat_chain.invoke(
        {"topic": user_input},
        config={"configurable": {"session_id": session_id}},
    )
    print(f"AI: {result}\n")
