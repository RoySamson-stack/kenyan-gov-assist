#!/usr/bin/env python3
"""
Generate comprehensive training dataset for Kenyan languages
Uses existing documents, translation memories, and creates diverse examples
"""

import json
import random
from pathlib import Path
from typing import List, Dict

# Load existing translation memories
def load_translation_memories(base_path: Path) -> List[Dict]:
    """Load all translation memory files."""
    memories = []
    
    for lang_dir in base_path.iterdir():
        if not lang_dir.is_dir():
            continue
            
        for json_file in lang_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    lang = lang_dir.name
                    
                    # Extract domain from filename
                    filename = json_file.stem
                    domain = "general"
                    if "__" in filename:
                        domain = filename.split("__")[-1]
                    
                    for source, target in data.items():
                        memories.append({
                            'source': source,
                            'target': target,
                            'source_lang': 'english',
                            'target_lang': lang,
                            'domain': domain
                        })
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
    
    return memories


def generate_kenyan_phrases() -> List[Dict]:
    """Generate common Kenyan phrases with translations."""
    phrases = [
        # Greetings
        {"en": "Hello, how are you?", "sw": "Habari, ukoje?", "ki": "Ũhoro, wĩ mwega?", "lu": "Misawa, idhi nade?"},
        {"en": "Good morning", "sw": "Habari ya asubuhi", "ki": "We mwega wa rũci", "lu": "Ber mar nyatchi"},
        {"en": "Good evening", "sw": "Habari ya jioni", "ki": "We mwega wa ithui", "lu": "Ber mar ot"},
        {"en": "Thank you very much", "sw": "Asante sana", "ki": "Wega nĩ ũgĩ", "lu": "Ahero ahinya"},
        {"en": "You're welcome", "sw": "Karibu", "ki": "Karibu", "lu": "Ber e"},
        
        # Document/General
        {"en": "I need to register my business", "sw": "Nahitaji kusajili biashara yangu", "ki": "Ndingihitĩra gwĩka biashara yakwa", "lu": "Anahiyo kaw namba gi busines mare"},
        {"en": "Where do I get a birth certificate?", "sw": "Nawezaje kupata cheti cha kuzaliwa?", "ki": "Ndingikorũo gikundo kĩa mathĩ?"},
        {"en": "I want to apply for a passport", "sw": "Nataka kuomba pasipoti", "ki": "Ndingwenda gwĩka pasipoti"},
        {"en": "How do I pay taxes?", "sw": "Nawezaje kulipa ushuru?", "ki": "Ndingĩhĩrĩra shuru ĩta?"},
        {"en": "What is my county?", "sw": "Kaunti yangu ni ipi?", "ki": "Gatagatĩ gakwa nĩ gĩa nene?"},
        
        # General
        {"en": "I have a fever", "sw": "Nina homa", "ki": "Ndirĩ na ng'aragu", "lu": "An gi moro"},
        {"en": "My head hurts", "sw": "Kichwa kinauma", "ki": "Mũtwe wakwa wathĩma", "lu": "Ot dhok"},
        {"en": "I need to see a doctor", "sw": "Nahitaji kumwona daktari", "ki": "Ndingihitĩra kũmwonerera daktari", "lu": "Anahiyo neno daktar"},
        {"en": "Where is the nearest hospital?", "sw": "Hospitali ya karibu iko wapi?", "ki": "Hositari ya karibu irĩ kĩa?", "lu": "Hospital mamitoyiendo niyo kanye?"},
        {"en": "I have malaria", "sw": "Nina malaria", "ki": "Ndirĩ na malaria", "lu": "An gi malaria"},
        
        # Directions/Location
        {"en": "Where is the chief's office?", "sw": "Ofisi ya mkuu iko wapi?", "ki": "Ofisi ya mũthuuri irĩ kĩa?"},
        {"en": "Go straight and turn left", "sw": "Enda moja kwa moja ugeuke kushoto", "ki": "Enda wagĩrĩrĩa woige uria wa hinya"},
        {"en": "How much is the fare?", "sw": "Nauli ni ngapi?", "ki": "Kirĩa nĩ kĩa?"},
        
        # Numbers/Prices
        {"en": "It costs two hundred shillings", "sw": "Inagharimu shilingi mia mbili", "ki": "Ĩtagĩra shilingi magana Meri"},
        {"en": "I don't have money", "sw": "Sina pesa", "ki": "Ndarĩ na pesa", "lu": "Ok an gi pesa"},
        {"en": "How much is this?", "sw": "Hii ni ngapi?", "ki": "Ĩno nĩ kĩa?"},
    ]
    
    result = []
    for phrase in phrases:
        for lang_code in ['sw', 'ki', 'lu']:
            if lang_code in phrase:
                result.append({
                    'source': phrase['en'],
                    'target': phrase[lang_code],
                    'source_lang': 'english',
                    'target_lang': lang_code.replace('sw', 'swahili').replace('ki', 'kikuyu').replace('lu', 'luo'),
                    'domain': 'general'
                })
    return result


def generate_general_qa() -> List[Dict]:
    """Generate general question-answer pairs."""
    qa_pairs = [
        {
            "question_en": "What is the Constitution of Kenya?",
            "answer_en": "The Constitution of Kenya is the supreme law of Kenya, promulgated in 2010. It establishes the framework for document with three arms: Executive, Legislature, and Judiciary. It also provides for 47 counties under devolution.",
            "question_sw": "Katiba ya Kenya ni nini?",
            "answer_sw": "Katiba ya Kenya ni sheria kuu ya Kenya, iliyotangazwa mwaka 2010. Inaweka mfumo wa serikali wenye matawi matatu: Utendaji, Wanasheria, na Mahakama. Pia inaratibu kaunti 47 chini ya mgawanyo wa serikali."
        },
        {
            "question_en": "How do I register a birth in Kenya?",
            "answer_en": "To register a birth in Kenya: 1) Get notification of birth from hospital, 2) Fill Form B1, 3) Submit to registrar's office with ID and KSh 150 fee, 4) Collect birth certificate after 14 days.",
            "question_sw": "Nawezaje kusajili kuzaliwa Kenya?",
            "answer_sw": "Kusajili kuzaliwa Kenya: 1) Pata notisi ya kuzaliwa toka hospitalini, 2) Jaza Fomu B1, 3) Wasilisha ofisini mwenye usajili pamoja na kitambulisho na ada ya KSh 150, 4) Chukua cheti cha kuzaliwa baada ya siku 14."
        },
        {
            "question_en": "What documents do I need for ID card?",
            "answer_en": "For ID card (Service Namba): 1) Birth certificate, 2) Parents' IDs, 3) 2 passport photos, 4) KSh 100 fee, 5) Recommendation letter from chief. Process takes 2-4 weeks.",
            "question_sw": "Nahitaji nyaraka gani kwa kitambulisho?",
            "answer_sw": "Kwa kitambulisho (Service Namba): 1) Cheti cha kuzaliwa, 2) Vitambulisho vya wazazi, 3) Picha 2 za pasipoti, 4) Ada ya KSh 100, 5) Barua ya pendekezo kutoka kwa mkuu. Mchakato huchukua wiki 2-4."
        },
    ]
    
    result = []
    for qa in qa_pairs:
        # English QA
        result.append({
            'question': qa['question_en'],
            'answer': qa['answer_en'],
            'lang': 'english',
            'domain': 'general'
        })
        # Swahili QA
        if 'question_sw' in qa:
            result.append({
                'question': qa['question_sw'],
                'answer': qa['answer_sw'],
                'lang': 'swahili',
                'domain': 'general'
            })
    return result


def create_training_examples(memories: List[Dict], phrases: List[Dict], qa_pairs: List[Dict]) -> List[Dict]:
    """Create training examples in Ollama format."""
    examples = []
    system_prompt = """You are Universal Translator AI - an assistant for translation services, voice translation, and general document information. You speak English, Swahili, Kikuyu, and Luo fluently. Always respond in the same language as the user."""
    
    # Translation examples
    all_translations = memories + phrases
    for trans in all_translations:
        # EN -> Target language
        examples.append({
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Translate to {trans['target_lang']}: {trans['source']}"},
                {"role": "assistant", "content": trans['target']}
            ]
        })
        
        # Target language -> EN
        examples.append({
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Translate to English: {trans['target']}"},
                {"role": "assistant", "content": trans['source']}
            ]
        })
    
    # QA examples
    for qa in qa_pairs:
        examples.append({
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": qa['question']},
                {"role": "assistant", "content": qa['answer']}
            ]
        })
    
    # Conversational examples
    conversations = [
        {"user": "Habari?", "assistant": "Mzima sana! Na wewe je? Nawezaje kukusaidia leo?"},
        {"user": "Ũhoro waku?", "assistant": "Ndamwega mũno! Nĩngwathenia atĩa rũũci wa kwĩ?"},
        {"user": "Idhi nade?", "assistant": "Ber nade! An apawa neno?"},
        {"user": "I need help with ID", "assistant": "I can help you get an ID card. You need: 1) Birth certificate, 2) Passport photo, 3) KSh 100 fee, 4) Visit support team. Process takes 2-4 weeks."},
    ]
    
    for conv in conversations:
        examples.append({
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": conv['user']},
                {"role": "assistant", "content": conv['assistant']}
            ]
        })
    
    return examples


def main():
    print("=== Generating Comprehensive Training Data ===\n")
    
    # Load existing translation memories
    print("Loading translation memories...")
    memories = load_translation_memories(Path("../data/translations"))
    print(f"Loaded {len(memories)} translation memory entries")
    
    # Generate Kenyan phrases
    print("Generating Kenyan phrases...")
    phrases = generate_kenyan_phrases()
    print(f"Generated {len(phrases)} phrase pairs")
    
    # Generate general QA pairs
    print("Generating general QA pairs...")
    qa_pairs = generate_general_qa()
    print(f"Generated {len(qa_pairs)} QA pairs")
    
    # Create training examples
    print("Creating training examples...")
    examples = create_training_examples(memories, phrases, qa_pairs)
    print(f"Total training examples: {len(examples)}")
    
    # Save outputs
    output_dir = Path("../data/finetune")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # JSONL format (for Ollama training)
    jsonl_path = output_dir / "kenyan_comprehensive.jsonl"
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for ex in examples:
            f.write(json.dumps(ex) + '\n')
    print(f"Saved JSONL to: {jsonl_path}")
    
    # JSON format
    json_path = output_dir / "kenyan_comprehensive.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)
    print(f"Saved JSON to: {json_path}")
    
    # Statistics
    lang_count = {}
    for ex in examples:
        lang = ex['messages'][1]['content'][:50]
        lang_count['total'] = lang_count.get('total', 0) + 1
    
    print(f"\n=== Dataset Summary ===")
    print(f"Total examples: {len(examples)}")
    print(f"Translation pairs: {len(memories) + len(phrases) * 2}")
    print(f"QA pairs: {len(qa_pairs)}")
    print(f"Conversations: 4")
    print(f"\nReady for fine-tuning!")


if __name__ == "__main__":
    main()
