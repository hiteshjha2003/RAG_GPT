import os
import openai
import datetime

from dotenv import load_dotenv , find_dotenv

_ = load_dotenv(find_dotenv())

openai.api_key = os.environ["OPENAI_API_KEY"]



#Account for depreciation of LLM Models
current_date = datetime.datetime.now().date()

#Define the date model should be set up to gpt-3.5-turbo
target_date = datetime.date(2024, 6, 12)

if current_date >target_date:
    llm_model = "gpt-3.5-turbo"
else:
    llm_model = "gpt-4"
    

def get_completion(prompt , model = llm_model):
    messages = [{"role":"user", "content":prompt}]
    response = openai.ChatCompletion.create(
        model = model,
        messages = messages,
        temperature = 0
    )
    return response.choices[0].message["content"]


prompt = "How we can merge two differnt vectorstore into one and can apply RAG on it "

response = get_completion(prompt)

print(response)





