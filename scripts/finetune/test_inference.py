#!/usr/bin/env python3
"""
Test inference with the fine-tuned LoRA adapter.
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import argparse


MODEL_MAP = {
    "1b": "unsloth/llama3.2-1b-bnb-4bit",
    "3b": "unsloth/llama3.2-3b-bnb-4bit",
}


def load_model(model_size: str = "1b", lora_path: str = "../models/kenyan-gov-lora"):
    """Load model with LoRA adapter."""
    base_model = MODEL_MAP.get(model_size, MODEL_MAP["1b"])

    print(f"Loading {base_model} with LoRA from {lora_path}")

    tokenizer = AutoTokenizer.from_pretrained(base_model)
    tokenizer.pad_token = tokenizer.eos_token

    base = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=BitsAndBytesConfig(load_in_4bit=True),
        device_map="auto",
        low_cpu_mem_usage=True,
    )

    model = PeftModel.from_pretrained(base, lora_path)

    return model, tokenizer


def chat(model, tokenizer, system_prompt: str, user_input: str):
    """Generate a chat response."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]

    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(text, return_tensors="pt").to("cuda")

    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.split("assistant\n")[-1].strip()


def main():
    parser = argparse.ArgumentParser(description="Test fine-tuned model")
    parser.add_argument("--model-size", type=str, default="1b", choices=["1b", "3b"])
    parser.add_argument("--lora-path", type=str, default="../models/kenyan-gov-lora")
    args = parser.parse_args()

    model, tokenizer = load_model(args.model_size, args.lora_path)

    system = """You are Serikali Yangu, an AI assistant specialized in Kenyan government services. Respond in Swahili or English."""

    print("\n=== Kenyan Gov Assistant (Fine-tuned) ===")
    print("Type 'quit' to exit\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            break

        response = chat(model, tokenizer, system, user_input)
        print(f"Assistant: {response}\n")


if __name__ == "__main__":
    main()
