from pprint import pprint
from langchain_cohere import ChatCohere , CohereRagRetriever
from dotenv import load_dotenv
import os 
# import cohere
load_dotenv()

api_key = os.getenv("COHERE_API_KEY")
# co = cohere.Client(api_key)

user_query = "Who are cohere?"

llm = ChatCohere(cohere_api_key=api_key)

rag = CohereRagRetriever(
    llm=llm,
    connectors = [{"id":"web-search"}]
    
)
docs = rag.get_relevant_documents(user_query)

answer = docs.pop()

print("Relevant Documents")
print(docs)

pprint(f"Question {user_query}")
pprint("Answer")
pprint(answer.page_content)
pprint(answer.metadata["citations"])


