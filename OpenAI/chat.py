from langchain_cohere import ChatCohere
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os 
# import cohere
load_dotenv()

api_key = os.getenv("COHERE_API_KEY")
# co = cohere.Client(api_key)


llm = ChatCohere(cohere_api_key=api_key)

inputs = input("Enter Your Query")
message = [HumanMessage(content=inputs)]

print(llm.invoke(message).content)

