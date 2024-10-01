import streamlit as st
import requests
from bs4 import BeautifulSoup
from PIL import Image
import io
import os
import glob
from dotenv import load_dotenv, find_dotenv
import openai
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from langchain.chains import RetrievalQAWithSourcesChain
import PyPDF2
from langchain import OpenAI, VectorDBQA


# Load environment variables
_ = load_dotenv(find_dotenv())  # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']

# Function to extract information from a web link
def extract_info_from_link(url):
    response = requests.get(url)
    if response.status_code == 200:
        page_content = response.content
        soup = BeautifulSoup(page_content, 'html.parser')
        return soup.prettify()
    else:
        return f"Failed to retrieve content. Status code: {response.status_code}"

# Function to read PDF file
def read_pdf(file):
    text = ""
    images = []
    pdf = PyPDF2.PdfReader(file)
    num_pages = len(pdf.pages)
    for page_num in range(num_pages):
        page = pdf.pages[page_num]
        text += page.extract_text()
        if '/XObject' in page['/Resources']:
            xObject = page['/Resources']['/XObject'].get_object()
            for obj in xObject:
                if xObject[obj]['/Subtype'] == '/Image':
                    image_data = xObject[obj]
                    size = (image_data['/Width'], image_data['/Height'])
                    color_space = image_data['/ColorSpace']
                    mode = "RGB" if color_space == '/DeviceRGB' else "P"
                    data = image_data.get_data()
                    try:
                        img = Image.frombytes(mode, size, data)
                        images.append(img)
                    except ValueError:
                        st.warning(f"Unable to process image on page {page_num + 1}.")
    return text, images

def create_vector_store_from_pdfs(uploaded_file, question):
    data_folder = "D://LangChain//data"  # Assuming "data" is the folder containing your PDF files
    all_pdf = glob.glob(os.path.join(data_folder, "*.pdf"))
    all_pages = []
    
    for pdf_file in all_pdf:
        loader = PyPDFLoader(pdf_file)
        pages = loader.load_and_split()
        all_pages.extend(pages)
    
    if not all_pages:
        st.error("No documents found in the data folder. Please check.")
        return None
    
    # Split the documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(all_pages)
    
    if not docs:
        st.error("No documents found after splitting. Please check the PDF files.")
        return None
    
    # Create embeddings
    embeddings = OpenAIEmbeddings()
    doc_texts = [doc.page_content for doc in docs]
    doc_embeddings = embeddings.embed_documents(doc_texts)
    
    if not doc_embeddings:
        st.error("Failed to generate embeddings. Please check the OpenAI API key and usage.")
        return None
    
    # Initiate the FAISS Database
    db = FAISS.from_documents(docs, embeddings)
    
    # Perform similarity search
    query = question
    matched_docs = db.similarity_search(query)
    
    answers = []
    for doc in matched_docs:
        answers.append(doc.page_content)  # Directly access the content of matched documents
    
    if not answers:
        return "No answers found."
    else:
        return answers[0]  # Return the first answer or adjust as per your requirement


# Streamlit UI
st.title("GEN AI Application")

# Tab layout
tabs = ["Web Link", "Process PDF File", "Q&A Application", "Process PDF Directory"]
selected_tab = st.radio("Select an option:", tabs)

# Tab 1: Web Link
if selected_tab == "Web Link":
    st.header("Web Link App")
    url = st.text_input("Enter URL here")
    if st.button("Extract Information"):
        if url:
            link_info = extract_info_from_link(url)
            st.text_area("Link Information", value=link_info, height=300)

# Tab 2: Process PDF File
elif selected_tab == "Process PDF File":
    st.header("Process PDF File")
    uploaded_file = st.file_uploader("Upload PDF File", type=["pdf"])
    if uploaded_file:
        text, images = read_pdf(io.BytesIO(uploaded_file.read()))
        st.text_area("File Content", value=text, height=300)
        if images:
            # Display each image with its caption
            for i, img in enumerate(images):
                st.image(img, caption=f"Image {i + 1}")

# Tab 3: Q&A Application
elif selected_tab == "Q&A Application":
    st.header("Q&A Application")
    uploaded_file = st.file_uploader("Upload PDF File", type=["pdf"], key="qa_file")
    question = st.text_input("Ask a question about the file content", "")
    if uploaded_file and question:
        answer = create_vector_store_from_pdfs(uploaded_file, question)
        st.text_area("Answer", value=answer, height=100)

# Tab 4: Process PDF Directory
elif selected_tab == "Process PDF Directory":
    st.header("Process PDF Directory")
    st.text("This feature is not yet implemented.")

