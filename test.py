import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("Set GEMINI_API_KEY in the environment or .env file.")

llm = ChatGoogleGenerativeAI(
    google_api_key=api_key,
    model="gemini-2.5-flash",
    temperature=0.2,
)

response = llm.invoke("Write a short poem about the beauty of nature.")
print(response)
