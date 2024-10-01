from fireworks.client import Fireworks

client = Fireworks(api_key="ZDr9MfQ0toZcjAWIb6Pd9vJzBIYBpgoZXWs7QAOhhbCYzfTl")
response = client.chat.completions.create(
  model="accounts/fireworks/models/llama-v2-7b-chat",
  messages=[{
    "role": "user",
    "content": "Can you  tell me about the vectorstore ?",
  }],
  stream=True,
)
for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")