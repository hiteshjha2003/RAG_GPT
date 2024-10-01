# Import the LLaMA class from LLaMA.py
from LLaMA import LLaMA

import torch
# Check if CUDA is available
allow_cuda = False  # Set this to True if you want to use GPU
device = 'cuda' if torch.cuda.is_available() and allow_cuda else 'cpu'

# Set up prompts
prompts = [
    "Simply put, the theory of relativity states that ",
    "If Google was an Italian company founded in Milan, it would",
    # Few shot promt
    """Translate English to French:
    
    sea otter => loutre de mer
    peppermint => menthe poivrée
    plush girafe => girafe peluche
    cheese =>""",
    # Zero shot prompt
    """Tell me if the following person is actually Doraemon disguised as human:
    Name: Umar Jamil
    Decision: 
    """
]

# Set up the model
model = LLaMA.build(
    checkpoints_dir='llama-2-7b/',
    tokenizer_path='tokenizer.model',
    load_model=True,
    max_seq_len=1024,
    max_batch_size=len(prompts),
    device=device
)

# Generate text completions
out_tokens, out_texts = (model.text_completion(prompts, max_gen_len=64))

# Print the results
assert len(out_texts) == len(prompts)
for i in range(len(out_texts)):
    print(out_texts[i])
    print('-' * 50)
