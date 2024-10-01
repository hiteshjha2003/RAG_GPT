import fireworks.client
import os
import dotenv
import chromadb
import json
from tqdm.auto import tqdm
import pandas as pd
import random

# you can set envs using Colab secrets
dotenv.load_dotenv()

fireworks.client.api_key = os.getenv("FIREWORKS_API_KEY")


def get_completion(prompt, model=None, max_tokens=50):

    fw_model_dir = "accounts/fireworks/models/"

    if model is None:
        model = fw_model_dir + "llama-v2-7b"
    else:
        model = fw_model_dir + model

    completion = fireworks.client.Completion.create(
        model=model,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=0
    )

    return completion.choices[0].text










