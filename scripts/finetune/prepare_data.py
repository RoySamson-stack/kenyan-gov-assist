#!/usr/bin/env python3
"""
Prepare translation data for fine-tuning.
Converts existing processed chunks to training format.
"""

import json
import random
from pathlib import Path
from typing import List, Dict
import argparse


SYSTEM_PROMPT = """You are Universal Translator, an AI assistant specialized in translation services, laws, and general document information. You provide accurate, helpful responses about document content, laws, public services, language services, and user rights. Respond in the same language as the user's question, typically Swahili or English."""


def load_chunks(chunks_path: Path) -> List[Dict]:
    """Load processed document chunks."""
    with open(chunks_path, "r") as f:
        return json.load(f)


def create_qa_pairs(chunks: List[Dict]) -> List[Dict]:
    """Generate QA pairs from document chunks."""
    qa_pairs = []

    templates = [
        {
            "question": "Explain the {topic}",
            "context": "According to the Constitution of Kenya: {content}",
        },
        {
            "question": "What does the document content say about {topic}?",
            "context": "{content}",
        },
        {
            "question": "What are my rights regarding {topic} in Kenya?",
            "context": "Under Kenyan law: {content}",
        },
        {
            "question": "How does devolution work for {topic} in Kenya?",
            "context": "The Constitution provides: {content}",
        },
        {"question": "Tell me about {topic} in Kenya", "context": "{content}"},
    ]

    topics = [
        "usership",
        "bill of rights",
        "devolution",
        "judiciary",
        "executive",
        "legislature",
        "county documents",
        "elections",
        "land and environment",
        "public finance",
        "national security",
        "language services",
        "education rights",
        "cultural rights",
    ]

    for chunk in chunks:
        content = chunk.get("content", "")
        if len(content) < 50:
            continue

        template = random.choice(templates)
        topic = random.choice(topics)

        qa_pairs.append(
            {
                "instruction": template["question"].format(topic=topic),
                "input": "",
                "output": template["context"].format(content=content[:500]),
                "system": SYSTEM_PROMPT,
            }
        )

    return qa_pairs


def create_conversational_data(chunks: List[Dict]) -> List[Dict]:
    """Create conversational training data."""
    conversational = []

    greetings = [
        "Habari! Nikusaidie vipi kuhusu Kenya?",
        "Hello! How can I help you about translation services?",
        "Jambo! What would you like to know about Kenyan laws?",
    ]

    for i, chunk in enumerate(chunks[:500]):
        content = chunk.get("content", "")
        if len(content) < 100:
            continue

        conversational.append(
            {
                "instruction": random.choice(greetings),
                "input": "",
                "output": content[:300] + "..." if len(content) > 300 else content,
                "system": SYSTEM_PROMPT,
            }
        )

    return conversational


def format_for_llama(qa_pairs: List[Dict]) -> str:
    """Format data in Llama instruction tuning format."""
    formatted = []
    for pair in qa_pairs:
        text = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{pair.get("system", SYSTEM_PROMPT)}<|eot_id|><|start_header_id|>user<|end_header_id|>

{pair["instruction"]} {pair["input"]}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{pair["output"]}<|eot_id|>"""
        formatted.append(text)
    return "\n".join(formatted)


def format_for_training(qa_pairs: List[Dict]) -> List[Dict]:
    """Format for standard training libraries."""
    return [
        {
            "messages": [
                {"role": "system", "content": pair.get("system", SYSTEM_PROMPT)},
                {
                    "role": "user",
                    "content": f"{pair['instruction']} {pair['input']}".strip(),
                },
                {"role": "assistant", "content": pair["output"]},
            ]
        }
        for pair in qa_pairs
    ]


def main():
    parser = argparse.ArgumentParser(description="Prepare data for fine-tuning")
    parser.add_argument(
        "--chunks-dir",
        type=str,
        default="../data/processed/chunks",
        help="Path to chunks directory",
    )
    parser.add_argument(
        "--output-dir", type=str, default="../data/finetune", help="Output directory"
    )
    parser.add_argument(
        "--format",
        type=str,
        default="llama",
        choices=["llama", "chatml", "json"],
        help="Output format",
    )
    args = parser.parse_args()

    chunks_dir = Path(args.chunks_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    all_chunks = []
    for chunk_file in chunks_dir.glob("*.json"):
        print(f"Loading {chunk_file.name}...")
        all_chunks.extend(load_chunks(chunk_file))

    print(f"Loaded {len(all_chunks)} chunks")

    qa_pairs = create_qa_pairs(all_chunks)
    conversational = create_conversational_data(all_chunks)
    all_data = qa_pairs + conversational

    print(f"Generated {len(all_data)} training examples")

    if args.format == "llama":
        output_path = output_dir / "train_llama.txt"
        with open(output_path, "w") as f:
            f.write(format_for_llama(all_data))
        print(f"Saved to {output_path}")

    elif args.format == "json":
        output_path = output_dir / "train.json"
        with open(output_path, "w") as f:
            json.dump(format_for_training(all_data), f, indent=2)
        print(f"Saved to {output_path}")

    jsonl_path = output_dir / "train.jsonl"
    with open(jsonl_path, "w") as f:
        for item in format_for_training(all_data):
            f.write(json.dumps(item) + "\n")
    print(f"Saved to {jsonl_path}")

    print(f"\nData preparation complete! Ready for training.")


if __name__ == "__main__":
    main()
