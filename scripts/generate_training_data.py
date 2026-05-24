#!/usr/bin/env python3
"""
Create training dataset for Kenyan language model
Generates high-quality training examples for Kenyan languages
"""

import json
import random
from pathlib import Path
from typing import List, Dict

# Kenyan language phrases and translations
KENYAN_PHRASES = {
    "swahili": {
        "greetings": ["Habari?", "Hujambo?", "Shikamoo", "Mambo vipi?"],
        "documents": ["Kitabu cha masomo", "Mwongozo wa mtumiaji", "Nakala ya mafunzo", "Barua rasmi"],
        "general": ["Shule", "Mwalimu", "Kitabu", "Tafsiri ni muhimu"],
        "rights": ["Haki za binadamu", "Haki za kiraia", "Haki ya kupata habari"],
    },
    "kikuyu": {
        "greetings": ["Ũhoro?", "Wĩ mwega?", "Mwega mũno?"],
        "documents": ["Mũrũmĩ wa Kenya", "Mwathani wa Kenya", "Service cia ũmwe"],
        "general": ["Cukuru", "Mwalimu", "Ibuku", "Tafsiri nĩ njega"],
        "rights": ["Thĩna cia mũndũ", "Haki cia thĩ"],
    },
    "luo": {
        "greetings": ["Misawa?", "Idhi nade?", "Ber nade?"],
        "documents": ["Kulo mar Kenya", "Kanungo mar Kenya", "Tugo mag kulo"],
        "general": ["Skul", "Japuonj", "Buk", "Loko dhok ber"],
        "rights": ["Thim mag jaduong'", "Kwongo mag jaduong'"],
    }
}

SYSTEM_PROMPT = """You are Universal Translator AI, an assistant for translation services, voice translation, and general document information. You speak English, Swahili, Kikuyu, Luo, and other Kenyan languages fluently."""


def generate_translation_examples() -> List[Dict]:
    """Generate translation examples between English and Kenyan languages."""
    examples = []
    
    translations = [
        # Swahili translations
        {"en": "Hello, how can I help you?", "sw": "Habari, nawezaje kukusaidia?", "domain": "general"},
        {"en": "You have the right to access translation services", "sw": "Una haki ya kupata huduma za serikali", "domain": "general"},
        {"en": "Where is the nearest hospital?", "sw": "Hospitali ya karibu iko wapi?", "domain": "general"},
        {"en": "I need to register my business", "sw": "Nahitaji kusajili biashara yangu", "domain": "general"},
        {"en": "What documents do I need for ID card?", "sw": "Nahitaji nyaraka gani za kitambulisho?", "domain": "general"},
        
        # Kikuyu translations
        {"en": "Hello, how can I help you?", "ki": "Ũhoro, ndingikwathenia atĩa?", "domain": "general"},
        {"en": "You have the right to access translation services", "ki": "Ũrĩ na thĩna wa kinyita ũtumiki wa mũrũmĩ", "domain": "general"},
        {"en": "Where is the nearest hospital?", "ki": "Hositari ya karibu irĩ kĩa?", "domain": "general"},
        
        # Luo translations
        {"en": "Hello, how can I help you?", "lu": "Misawa, anapawa neno?", "domain": "general"},
        {"en": "You have the right to access translation services", "lu": "Gi thim mochuno kaw gi tugo mag kulo", "domain": "general"},
        {"en": "Where is the nearest hospital?", "lu": "Hospitali mamitoyiendo niyo kanye?", "domain": "general"},
    ]
    
    for trans in translations:
        # English to Kenyan language
        examples.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Translate to {list(trans.keys())[1]}: {trans['en']}"},
                {"role": "assistant", "content": trans.get(list(trans.keys())[1], "")}
            ]
        })
        
        # Kenyan language to English
        target_lang = list(trans.keys())[1]
        examples.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Translate to English: {trans.get(target_lang, '')}"},
                {"role": "assistant", "content": trans['en']}
            ]
        })
    
    return examples


def generate_general_qa_examples() -> List[Dict]:
    """Generate general question-answer examples."""
    examples = []
    
    qa_pairs = [
        {
            "question": "What is the Constitution of Kenya?",
            "answer": "The Constitution of Kenya is the supreme law of Kenya, promulgated in 2010. It establishes the framework for document, outlines users' rights, and provides for devolution with 47 counties."
        },
        {
            "question": "How do I register a business in Kenya?",
            "answer": "To register a business in Kenya, visit support team or use eCitizen portal. You need: 1) Proposed business name, 2) Copy of ID, 3) Passport photo, 4) Registration fee. Registration takes 3-7 days."
        },
        {
            "question": "What are the counties in Kenya?",
            "answer": "Kenya has 47 counties established under the 2010 Constitution. Major counties include Nairobi, Mombasa, Kisumu, Nakuru, Kiambu, and Machakos. Each county has its own document with a Governor and County Assembly."
        },
        {
            "question": "Habari za support team?",
            "answer": "support team ni kituo cha kupata huduma za serikali kwa urahisi. Hapa unaweza pata huduma kama vile: usajili wa biashara, kitambulisho cha taifa, leseni ya gari, na huduma nyingine nyingi za serikali."
        },
        {
            "question": "Ni hatua gani za kupata ID card?",
            "answer": "Hatua za kupata kitambulisho cha taifa Kenya: 1) Nenda support team au ofisi ya Karagita, 2) Lipa ada ya shilingi 100, 3) Toa vyeti vya kuzaliwa na picha, 4) Subiri kwa siku 7-14, 5) Chukua ID yako."
        },
    ]
    
    for qa in qa_pairs:
        examples.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": qa["question"]},
                {"role": "assistant", "content": qa["answer"]}
            ]
        })
    
    return examples


def generate_general_qa_examples() -> List[Dict]:
    """Generate general-related question-answer examples."""
    examples = []
    
    qa_pairs = [
        {
            "question": "What are the symptoms of malaria?",
            "answer": "Malaria symptoms include: 1) High fever, 2) Chills and sweating, 3) Headache, 4) Nausea and vomiting, 5) Body aches. If you experience these symptoms, visit a general facility immediately for testing and treatment."
        },
        {
            "question": "Je, dalili za malaria ni zipi?",
            "answer": "Dalili za malaria ni pamoja na: 1) Homa kubwa, 2) Kupapa na kutoka jasho, 3) Maumivu ya kichwa, 4) Kichefuchefu na kutapika, 5) Maumivu ya mwili. Ukipata dalili hizi, tembelea hospitali mara moja kwa uchunguzi na matibabu."
        },
        {
            "question": "How do I book appointment at MTRH?",
            "answer": "To book appointment at Moi Teaching and Referral Hospital (MTRH), you can: 1) Call +254-53-2033471, 2) Visit the hospital in Eldoret, 3) Use their online booking system if available, 4) Walk in for emergency services."
        },
    ]
    
    for qa in qa_pairs:
        examples.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": qa["question"]},
                {"role": "assistant", "content": qa["answer"]}
            ]
        })
    
    return examples


def generate_conversational_examples() -> List[Dict]:
    """Generate conversational examples in Kenyan languages."""
    examples = []
    
    conversations = [
        {
            "user": "Habari yako?",
            "assistant": "Mzima sana, asante! Na wewe je? Nawezaje kukusaidia leo?"
        },
        {
            "user": "Ũhoro waku?",
            "assistant": "Ndamwega mũno! Nĩngwathenia atĩa rũũci wa kwĩ? Service irĩa wĩhokete?"
        },
        {
            "user": "Misawa? Idhi nade?",
            "assistant": "Ber nade! An apawa neno? Tugo ma kulo gi herani nade?"
        },
        {
            "user": "I need help with ID application",
            "assistant": "I can help you with ID application. You need to: 1) Visit support team, 2) Bring your birth certificate, 3) Have a passport-size photo, 4) Pay KSh 100 fee. The process takes about 2 weeks."
        },
    ]
    
    for conv in conversations:
        examples.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": conv["user"]},
                {"role": "assistant", "content": conv["assistant"]}
            ]
        })
    
    return examples


def main():
    """Generate all training data and save to files."""
    output_dir = Path("../data/finetune")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating training data for Kenyan language model...")
    
    all_examples = []
    
    # Generate different types of examples
    all_examples.extend(generate_translation_examples())
    all_examples.extend(generate_general_qa_examples())
    all_examples.extend(generate_general_qa_examples())
    all_examples.extend(generate_conversational_examples())
    
    print(f"Generated {len(all_examples)} training examples")
    
    # Save as JSONL (for Ollama training)
    jsonl_path = output_dir / "kenyan_training.jsonl"
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for example in all_examples:
            f.write(json.dumps(example) + '\n')
    print(f"Saved to {jsonl_path}")
    
    # Save as JSON (for other training methods)
    json_path = output_dir / "kenyan_training.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_examples, f, indent=2, ensure_ascii=False)
    print(f"Saved to {json_path}")
    
    # Create a text file for Modelfile few-shot examples
    text_path = output_dir / "few_shot_examples.txt"
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write("# Few-shot examples for Kenyan languages\n\n")
        for i, example in enumerate(all_examples[:20], 1):
            f.write(f"## Example {i}\n")
            for msg in example['messages']:
                f.write(f"{msg['role']}: {msg['content']}\n")
            f.write("\n")
    print(f"Saved few-shot examples to {text_path}")
    
    print("\n=== Data Generation Complete! ===")
    print(f"Total examples: {len(all_examples)}")
    print(f"Data directory: {output_dir}")


if __name__ == "__main__":
    main()
