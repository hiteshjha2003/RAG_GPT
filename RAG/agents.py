from langchain.agents import AgentExecutor
from langchain_cohere.chat_models import ChatCohere
from langchain_cohere.react_multi_hop.agent import create_cohere_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate



internet_search = TavilySearchResults()


llm = ChatCohere()

agent = create_cohere_react_agent(
    llm=llm,
    tools=[internet_search],
    prompt=ChatPromptTemplate.from_template("{question}"),
)

agent_executor = AgentExecutor(agent = agent ,tools = [internet_search], verbose = True)

response = agent_executor.invoke({
    
    "question":"I want to write an essay . Any tips"
})

print(response.get("output"))

print(response.get("citations"))


