import os
import openai
import datetime
from dotenv import load_dotenv , find_dotenv
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.retrievers import ParentDocumentRetriever
from PyPDF2 import PdfReader
## Text Splitting & Docloader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.storage import InMemoryStore
from langchain.document_loaders import TextLoader
from langchain.embeddings import HuggingFaceBgeEmbeddings
# from langchain.embeddings.openai import OpenAIEmbeddings
# embeddings = OpenAIEmbeddings()
import glob
from langchain.document_loaders import PyPDFLoader
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI


_ = load_dotenv(find_dotenv())

openai.api_key = os.environ["OPENAI_API_KEY"]

model_name = "BAAI/bge-small-en-v1.5"
encode_kwargs = {'normalize_embeddings': True} # set True to compute cosine similarity

bge_embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    # model_kwargs={'device': 'cuda'},
    encode_kwargs=encode_kwargs
)

# directory = "D://LangChain//data"

# # Iterate through each file in the directory
# for filename in os.listdir(directory):
#     if filename.endswith(".pdf"):
#         file_path = os.path.join(directory, filename)
#         print(f"Reading {file_path}...")
#         with open(file_path, "rb") as file:
#             reader = PdfReader(file)
#             docs = []
#             for i, page in enumerate(reader.pages, start=1):
#                 docs.append(Document(page_content=page.extract_text(), metadata={'page': i}))

# print("DOCS", docs)



# Get all PDF files and its contents
all_pdf = glob.glob("D://LangChain//data//*.pdf")

docs = []
for pdf_file in all_pdf:
    loader = PyPDFLoader(pdf_file)
    pages = loader.load_and_split()
    docs.extend(pages)
    

print("LENGTH OF THE DOCS", len(docs))




# Retrieving full documents rather than chunks
# In this mode, we want to retrieve the full documents.

# This is good to use if you initial full docs 
# aren't too big themselves and you aren't going to return many of them

# This text splitter is used to create the child documents
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)


# The vectorstore to use to index the child chunks
vectorstore = Chroma(
    collection_name="full_documents",
    embedding_function=bge_embeddings  #OpenAIEmbeddings()
)

# The storage layer for the parent documents
store = InMemoryStore()

full_doc_retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
)

full_doc_retriever.add_documents(docs, ids=None)

# our
list(store.yield_keys())

sub_docs = vectorstore.similarity_search("what is Deep Learning", k=2)

print("Length of the Sub Docs",len(sub_docs))


print(sub_docs[0].page_content)

retrieved_docs = full_doc_retriever.get_relevant_documents("what is Deep Learning")

print("Length of the Retrieved DOCS",len(retrieved_docs[0].page_content))

retrieved_docs[0].page_content



# Retrieving larger chunks
# Sometimes, the full documents can be too big to want to retrieve them as is. 
# In that case, what we really want to do is to first split the raw documents 
# into larger chunks, and then split it into smaller chunks.
# We then index the smaller chunks, but on retrieval we retrieve the larger 
# chunks (but still not the full documents).


# This text splitter is used to create the parent documents - The big chunks
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)

# This text splitter is used to create the child documents - The small chunks
# It should create documents smaller than the parent
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

# The vectorstore to use to index the child chunks
vectorstore = Chroma(collection_name="split_parents", embedding_function=bge_embeddings) #OpenAIEmbeddings()

# The storage layer for the parent documents
store = InMemoryStore()



big_chunks_retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)

big_chunks_retriever.add_documents(docs)

len(list(store.yield_keys()))


sub_docs = vectorstore.similarity_search("what is Deep Learning")

print(sub_docs[0].page_content)


retrieved_docs = big_chunks_retriever.get_relevant_documents("what is Deep Learning")


print(len(retrieved_docs))

print(len(retrieved_docs[0].page_content))


print(retrieved_docs[0].page_content)


print(retrieved_docs[1].page_content)




qa = RetrievalQA.from_chain_type(llm=OpenAI(),
                                 chain_type="stuff",
                                 retriever=big_chunks_retriever)



query = input("Enter Your Query:\n")
res = qa.run(query)
print(res)
