from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os


load_dotenv()
llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="deepseek-r1-distill-llama-70b")


if __name__ == "__main__":
    response = llm.invoke("What are the two most important ingradient in samosa? ")
    print(response.content)