
# %pip install --upgrade pip
# %pip install boto3==1.34.55 --force-reinstall --quiet
# %pip install botocore==1.34.55 --force-reinstall --quiet
# %pip install langchain==0.1.10 --force-reinstall --quiet

# restart kernel

from langchain.prompts import PromptTemplate
import boto3
import pprint
from botocore.client import Config
import json
from langchain.llms.bedrock import Bedrock
from langchain.retrievers.bedrock import AmazonKnowledgeBasesRetriever
from langchain.chains import RetrievalQA



pp = pprint.PrettyPrinter(indent=2)
session = boto3.session.Session()
region = session.region_name
bedrock_config = Config(connect_timeout=120, read_timeout=120, retries={'max_attempts': 0})
bedrock_client = boto3.client('bedrock-runtime', region_name = 'mumbai')
bedrock_agent_client = boto3.client("bedrock-agent-runtime",
                              config=bedrock_config, region_name = region)
print(region)


def retrieve(query, kbId, numberOfResults=5):
    return bedrock_agent_client.retrieve(
        retrievalQuery= {
            'text': query
        },
        knowledgeBaseId=kbId,
        retrievalConfiguration= {
            'vectorSearchConfiguration': {
                'numberOfResults': numberOfResults,
                'overrideSearchType': "HYBRID", # optional
            }
        }
    )

query = "What is Amazon doing in the field of generative AI?"
response = retrieve(query, kb_id, 5)
retrievalResults = response['retrievalResults']
pp.pprint(retrievalResults)

# fetch context from the response
def get_contexts(retrievalResults):
    contexts = []
    for retrievedResult in retrievalResults: 
        contexts.append(retrievedResult['content']['text'])
    return contexts
contexts = get_contexts(retrievalResults)
pp.pprint(contexts)

prompt = f"""
Human: You are a financial advisor AI system, and provides answers to questions by using fact based and statistical information when possible. 
Use the following pieces of information to provide a concise answer to the question enclosed in <question> tags. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.
<context>
{contexts}
</context>

<question>
{query}
</question>

The response should be specific and use statistics or numbers when possible.

Assistant:"""


# payload with model paramters
mistral_payload = json.dumps({
    "prompt": prompt,
    "max_tokens":512,
    "temperature":0.5,
    "top_k":50,
    "top_p":0.9
})

modelId = 'mistral.mistral-7b-instruct-v0:2' # change this to use a different version from the model provider
accept = 'application/json'
contentType = 'application/json'
response = bedrock_client.invoke_model(body=mistral_payload, modelId=modelId, accept=accept, contentType=contentType)
response_body = json.loads(response.get('body').read())
response_text = response_body.get('outputs')[0]['text']

pp.pprint(response_text)


model_kwargs_claude = {
    "temperature": 0,
    "top_k": 10,
    "max_tokens_to_sample": 3000
}

llm = Bedrock(model_id="anthropic.claude-v2:1",
              model_kwargs=model_kwargs_claude,
              client = bedrock_client,)

query = "By what percentage did AWS revenue grow year-over-year in 2022?"
retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id=kb_id,
        retrieval_config={"vectorSearchConfiguration": 
                          {"numberOfResults": 4,
                           'overrideSearchType': "SEMANTIC", # optional
                           }
                          },
        # endpoint_url=endpoint_url,
        # region_name=region,
        # credentials_profile_name="<profile_name>",
    )
docs = retriever.get_relevant_documents(
        query=query
    )
pp.pprint(docs)



PROMPT_TEMPLATE = """
Human: You are a financial advisor AI system, and provides answers to questions by using fact based and statistical information when possible. 
Use the following pieces of information to provide a concise answer to the question enclosed in <question> tags. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.
<context>
{context}
</context>

<question>
{question}
</question>

The response should be specific and use statistics or numbers when possible.

Assistant:"""
claude_prompt = PromptTemplate(template=PROMPT_TEMPLATE, 
                               input_variables=["context","question"])

qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": claude_prompt}
)
answer = qa.invoke(query)
pp.pprint(answer)

