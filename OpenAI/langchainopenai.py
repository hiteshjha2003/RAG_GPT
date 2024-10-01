from langchain.chat_models import ChatOpenAI
import os
import openai

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']


#Account for depreciation of LLM Models
current_date = datetime.datetime.now().date()

#Define the date model should be set up to gpt-3.5-turbo
target_date = datetime.date(2024, 6, 12)

if current_date >target_date:
    llm_model = "gpt-3.5-turbo"
else:
    llm_model = "gpt-4"
    
    
#To control the randomness and creativity  of the generated text by llm , use temperature =0.0

chat = ChatOpenAI(
    temperature = 0.0,
    model = llm_model
    
)
