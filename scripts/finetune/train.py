#!/usr/bin/env python3
"""
QLoRA Fine-tuning script for Translation Assistant.
Trains llama3.2:1b on translation and document data.

Requirements:
    pip install torch bitsandbytes peft transformers accelerate datasets trl scipy
"""

import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    pipeline,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer


BASE_MODEL = "unsloth/llama3.2-1b-bnb-4bit"
OUTPUT_DIR = "../models/kenyan-gov-lora"
DATA_PATH = "../data/finetune/train.jsonl"


def setup_quantization():
    """Configure 4-bit quantization for memory efficiency."""
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )


def load_model_and_tokenizer():
    """Load base model with quantization."""
    print(f"Loading base model: {BASE_MODEL}")

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=setup_quantization(),
        device_map="auto",
        low_cpu_mem_usage=True,
    )

    model = prepare_model_for_kbit_training(model)

    return model, tokenizer


def setup_lora(model):
    """Configure LoRA adapters."""
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    return model


def format_dataset(example):
    """Format dataset for training."""
    messages = example["messages"]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    return {"text": text}


def train():
    """Main training loop."""
    model, tokenizer = load_model_and_tokenizer()
    model = setup_lora(model)

    print("Loading dataset...")
    dataset = load_dataset("json", data_files=DATA_PATH, split="train")

    dataset = dataset.map(
        format_dataset,
        remove_columns=["messages"],
        num_proc=os.cpu_count(),
    )

    train_size = int(0.9 * len(dataset))
    train_dataset = dataset.select(range(train_size))
    eval_dataset = dataset.select(range(train_size, len(dataset)))

    print(f"Training samples: {len(train_dataset)}")
    print(f"Eval samples: {len(eval_dataset)}")

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        optim="paged_adamw_32bit",
        learning_rate=2e-4,
        weight_decay=0.001,
        fp16=True,
        logging_steps=10,
        evaluation_strategy="steps",
        eval_steps=50,
        save_steps=100,
        warmup_steps=10,
        report_to="none",
        ddp_find_unused_parameters=False,
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        args=training_args,
        tokenizer=tokenizer,
        max_seq_length=512,
        dataset_text_field="text",
    )

    print("\nStarting training...")
    trainer.train()

    print(f"\nSaving model to {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)

    print("\nTraining complete!")
    print(f"LoRA adapter saved to: {OUTPUT_DIR}")

    print("\nTo use the model:")
    print(f"  python merge_and_export.py")


if __name__ == "__main__":
    train()
