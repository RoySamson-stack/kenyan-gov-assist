#!/usr/bin/env python3
"""
Merge LoRA weights and export to Ollama format.
"""

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import subprocess


BASE_MODEL = "unsloth/llama3.2-1b-bnb-4bit"
LORA_PATH = "../models/kenyan-gov-lora"
OUTPUT_DIR = "../models/kenyan-gov-merged"


def merge_and_export():
    """Merge LoRA weights and export to Ollama."""
    print("Loading base model and LoRA weights...")

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.pad_token = tokenizer.eos_token

    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=BitsAndBytesConfig(load_in_4bit=True),
        device_map="auto",
        low_cpu_mem_usage=True,
    )

    model = PeftModel.from_pretrained(base_model, LORA_PATH)
    model = model.merge_and_unload()

    print(f"Saving merged model to {OUTPUT_DIR}")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print("\nCreating Ollama Modelfile...")
    modelfile_content = f'''FROM {OUTPUT_DIR}

TEMPLATE """
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{{{{ system }}}}<|eot_id|><|start_header_id|>user<|end_header_id|>

{{{{ .Prompt }}}}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{{{{ .Response }}}}<|eot_id|>
"""

SYSTEM """You are Serikali Yangu, an AI assistant specialized in Kenyan government services, laws, and civic information. You provide accurate, helpful responses about Kenyan constitution, laws, public services, health services, and citizen rights. Respond in the same language as the user's question, typically Swahili or English."""

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
'''

    with open(f"{OUTPUT_DIR}/Modelfile", "w") as f:
        f.write(modelfile_content)

    print(f"Modelfile created at {OUTPUT_DIR}/Modelfile")

    print("\nTo create Ollama model:")
    print(f"  cd {OUTPUT_DIR}")
    print(f"  ollama create kenyan-gov-assist -f Modelfile")

    print("\nTo update your app to use the new model:")
    print("  Set OLLAMA_MODEL=kenyan-gov-assist in your .env file")


if __name__ == "__main__":
    merge_and_export()
