import json
import pandas as pd
from huggingface_hub import InferenceClient
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
import json
import time
from dotenv import load_dotenv
import os
import torch
# from llama import Dialog, Llama
# from typing import List, Optional

# Load the environment variables from the .env file
load_dotenv()

# Access your environment variables
HF_KEY = os.getenv('HF_KEY')

# If no pipeline is provided, the bot will default to Meta Llama 3 8B accessed via HF API
def load_bot(system_prompt, pipe = None, max_new_tokens=512, temperature = None, top_p = None, seed = None):
    """Load an appropriate bot instance and pass sampling params through.

    Args:
        system_prompt (str): the system prompt text
        pipe: None for remote HF API, 'deepseek' for together/deepseek provider, or a local pipeline object
        max_new_tokens (int): max tokens for generation (used for local bots)
        temperature (float|None): sampling temperature
        top_p (float|None): nucleus sampling parameter
        seed (int|None): optional seed for reproducible sampling

    Returns:
        bot instance
    """
    if pipe == 'deepseek':
        bot = Deepseek_Bot(system_prompt, temperature=temperature, top_p=top_p, seed=seed, max_new_tokens=max_new_tokens)
    elif pipe is not None:
        bot = Local_Bot(system_prompt, pipe, max_new_tokens=max_new_tokens, temperature=temperature if temperature is not None else 0.01, top_p=top_p if top_p is not None else 0, seed=seed)
    else:
        bot = API_Bot(system_prompt, model="meta-llama/Meta-Llama-3-8B-Instruct", temperature=temperature, top_p=top_p, seed=seed, max_new_tokens=max_new_tokens)

    return bot


# Class representing an LLM chat bot
class API_Bot():
    def __init__(self, system_prompt, model="meta-llama/Meta-Llama-3-8B-Instruct", temperature=None, top_p=None, seed=None, max_new_tokens=512):
        self.system_prompt = system_prompt
        self.client = InferenceClient(api_key=HF_KEY)
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.seed = seed
        self.max_new_tokens = max_new_tokens

        # Start the conversation with the system prompt
        self.messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
    
    # Prompt the chat bot (both the prompt and response get added to message history)
    def prompt(self, content):
        self.add_to_prompt('user', content)
        response = self.infer()
        self.add_to_prompt('assistant', response)
        return response

    # Add a message to the prompt
    def add_to_prompt(self, role, content):
        self.messages.append({
            "role": role,
            "content": content
        })

    # Infer the response
    def infer(self):
        # Build kwargs for the inference client based on what was provided
        call_kwargs = {
            "model": self.model,
            "messages": self.messages,
            "max_tokens": self.max_new_tokens
        }
        if self.temperature is not None:
            call_kwargs["temperature"] = self.temperature
        if self.top_p is not None:
            call_kwargs["top_p"] = self.top_p
        if self.seed is not None:
            call_kwargs["seed"] = self.seed

        response = self.client.chat.completions.create(**call_kwargs)

        return response.choices[0].message.content
    
    def get_full_chat(self):
        messages = []
        for message in self.messages:
            messages.append(f"{message['role']}: {message['content']}")
        return messages

# Class representing an LLM chat bot
class Local_Bot():
    def __init__(self, system_prompt, pipe, max_new_tokens=512, temperature = 0.01, top_p = 0, seed=None):
        self.system_prompt = system_prompt
        self.pipe = pipe
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.seed = seed

        # Start the conversation with the system prompt
        self.messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
    
    # Prompt the chat bot (both the prompt and response get added to message history)
    def prompt(self, content):
        self.add_to_prompt('user', content)
        response = self.infer()
        self.add_to_prompt('assistant', response)
        return response

    # Add a message to the prompt
    def add_to_prompt(self, role, content):
        self.messages.append({
            "role": role,
            "content": content
        })

    # Infer the response locally using the provided inference logic
    def infer(self):
        # Prepare kwargs for the pipeline call
        pipe_kwargs = {
            "max_new_tokens": self.max_new_tokens,
            "pad_token_id": self.pipe.tokenizer.eos_token_id,
            "temperature": self.temperature,
            "top_p": self.top_p,
        }

        # Decide whether to sample
        do_sample = False
        if (self.temperature is not None and self.temperature > 0) or (self.top_p is not None and self.top_p > 0):
            do_sample = True

        # If a seed is provided, create a torch.Generator for reproducible sampling
        if self.seed is not None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            try:
                gen = torch.Generator(device=device).manual_seed(int(self.seed))
                outputs = self.pipe(self.messages, do_sample=do_sample, generator=gen, **pipe_kwargs)
            except Exception:
                # Fallback to CPU generator if CUDA generator creation fails
                gen = torch.Generator(device='cpu').manual_seed(int(self.seed))
                outputs = self.pipe(self.messages, do_sample=do_sample, generator=gen, **pipe_kwargs)
        else:
            outputs = self.pipe(self.messages, do_sample=do_sample, **pipe_kwargs)

        response = outputs[0]["generated_text"][-1]
        response_text = response['content']

        return response_text
    
    def get_full_chat(self):
        messages = []
        for message in self.messages:
            messages.append(f"{message['role']}: {message['content']}")
        return messages
    
# Class representing an LLM chat bot
class Deepseek_Bot():
    def __init__(self, system_prompt, temperature=None, top_p=None, seed=None, max_new_tokens=2000):
        self.system_prompt = system_prompt
        self.client = client = InferenceClient(
            provider="together",
            api_key=HF_KEY
        )
        self.model = "deepseek-ai/DeepSeek-V3"
        self.temperature = temperature
        self.top_p = top_p
        self.seed = seed
        self.max_new_tokens = max_new_tokens
        # Start the conversation with the system prompt
        self.messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
    
    # Prompt the chat bot (both the prompt and response get added to message history)
    def prompt(self, content):
        self.add_to_prompt('user', content)
        response = self.infer()
        self.add_to_prompt('assistant', response)
        return response

    # Add a message to the prompt
    def add_to_prompt(self, role, content):
        self.messages.append({
            "role": role,
            "content": content
        })

    # Infer the response
    def infer(self):
        call_kwargs = {"model": self.model, "messages": self.messages, "max_tokens": self.max_new_tokens}
        if self.temperature is not None:
            call_kwargs["temperature"] = self.temperature
        if self.top_p is not None:
            call_kwargs["top_p"] = self.top_p
        if self.seed is not None:
            call_kwargs["seed"] = self.seed

        response = self.client.chat.completions.create(**call_kwargs)

        return response.choices[0].message.content
    
    def get_full_chat(self):
        messages = []
        for message in self.messages:
            messages.append(f"{message['role']}: {message['content']}")
        return messages

# Class representing an LLM chat bot
class DeepseekDirect_Bot():
    def __init__(self, system_prompt, temperature=None, top_p=None, seed=None, max_new_tokens=2000):
        self.system_prompt = system_prompt
        self.client = client = InferenceClient(
            provider="together",
            api_key=HF_KEY
        )
        self.model = "deepseek-ai/DeepSeek-R1"
        self.temperature = temperature
        self.top_p = top_p
        self.seed = seed
        self.max_new_tokens = max_new_tokens
        # Start the conversation with the system prompt
        self.messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
    
    # Prompt the chat bot (both the prompt and response get added to message history)
    def prompt(self, content):
        self.add_to_prompt('user', content)
        response = self.infer()
        self.add_to_prompt('assistant', response)
        return response

    # Add a message to the prompt
    def add_to_prompt(self, role, content):
        self.messages.append({
            "role": role,
            "content": content
        })

    # Infer the response
    def infer(self):
        call_kwargs = {"model": self.model, "messages": self.messages, "max_tokens": self.max_new_tokens}
        if self.temperature is not None:
            call_kwargs["temperature"] = self.temperature
        if self.top_p is not None:
            call_kwargs["top_p"] = self.top_p
        if self.seed is not None:
            call_kwargs["seed"] = self.seed

        response = self.client.chat.completions.create(**call_kwargs)

        return response.choices[0].message.content
    
    def get_full_chat(self):
        messages = []
        for message in self.messages:
            messages.append(f"{message['role']}: {message['content']}")
        return messages


# Function to load model and tokenizer
# Models are loaded from the ./local_models folder if they are already downloaded
# Models are downloaded and saved in the ./local_models folder if they are not already downloaded
def load_pipe(model_checkpoint="meta-llama/Meta-Llama-3-8B-Instruct", local_dir="./local_models", quantization_config=None, save=False):
    if model_checkpoint == None:
        return None

    # If HF_KEY is present, set HUGGINGFACE_HUB_TOKEN so transformers/huggingface_hub can authenticate
    if HF_KEY:
        os.environ.setdefault('HUGGINGFACE_HUB_TOKEN', HF_KEY)
    
    torch.cuda.empty_cache()

    # prefer float16 on CUDA devices (works on most NVIDIA consumer GPUs); otherwise keep bfloat16
    dtype = torch.bfloat16
    if torch.cuda.is_available():
        dtype = torch.float16

    # Check if the model and tokenizer are already stored locally
    model_directory = local_dir + '/' + model_checkpoint
    if not os.path.exists(model_directory):
        print('downloading model...')
        # Download and save the model and tokenizer locally
        tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

        # Load model with correct qunatization settings
        if quantization_config == '8bit':
            quantization_config = BitsAndBytesConfig(load_in_8bit=True)
            model = AutoModelForCausalLM.from_pretrained(model_checkpoint, device_map="auto", trust_remote_code=True, quantization_config=quantization_config)
        
        elif quantization_config == '4bit':
            quantization_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
            model = AutoModelForCausalLM.from_pretrained(model_checkpoint, device_map="auto", trust_remote_code=True, quantization_config=quantization_config)
        
        else:
            # use the chosen dtype variable for consistency
            model = AutoModelForCausalLM.from_pretrained(model_checkpoint, device_map="auto", torch_dtype=dtype)
        
        # Save model and tokenizer locally
        if save:
            print('saving model...')
            # Save them locally for future use
            tokenizer.save_pretrained(model_directory)
            model.save_pretrained(model_directory)

        # Load the model and tokenizer
        print('loading model...')
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            model_kwargs={"dtype": torch.bfloat16},
            device_map="auto",
            )
    else:

        # Load the model and tokenizer
        print('loading model...')
        pipe = pipeline(
            "text-generation",
            model=model_directory,
            model_kwargs={"dtype": torch.bfloat16},
            device_map="auto",
            )

    return pipe

# Function to load model and tokenizer locally
def load_from_snellius(directory):

    print(f'Loading model from {directory}...')
    pipe = pipeline(
        "text-generation",
        model=directory,
        model_kwargs={"dtype": torch.bfloat16},
        device_map="auto",
        )

    return pipe
