from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os


load_dotenv()
llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-70b-8192")


if __name__ == "__main__":
    response = llm.invoke("What are the two most important ingradient in samosa? ")
    print(response.content)