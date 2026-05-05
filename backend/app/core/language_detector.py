"""
Language Detector for Kenyan Languages
Supports: English, Swahili, Kikuyu, Luo, Kamba, Kalenjin, Luhya, Somali, Kisii, Meru
"""
import re
from typing import Optional, Dict, List

# Common words/sentence patterns for each Kenyan language
LANGUAGE_MARKERS = {
    "swahili": {
        "words": ["na", "ya", "wa", "kwa", "ni", "katika", "hii", "hili", "haya", 
                  "serikali", "watu", "huduma", "afya", "kutoka", "kuhusu", "sasa",
                  "hapa", "kila", "wakati", "kazi", "pesa", "shule", "magaribi"],
        "patterns": [r'\bn[ai]\b', r'\bka\b', r'\bwa\b', r'\bya\b']
    },
    "kikuyu": {
        "words": ["ni", "na", "ma", "wa", "cia", "githomo", "mwe", "ratha", "ngai",
                  "nyumba", "mũndũ", "andũ", "kĩrĩa", "gũtiri", "kũrĩa", "thĩ",
                  "mũno", "hanya", "tiga", "kwoguo", "no", "nya"],
        "patterns": [r'\bgũ\w+', r'\bthi\w+', r'\bkĩ\w+', r'\bmũ\w+', r'\bandũ']
    },
    "luo": {
        "words": ["ka", "ni", "to", "kendo", "nade", "bera", "duoko", "chiwon",
                  "ng'ato", "won", "gi", "moro", "adiera", "kik", "wach", "kaka",
                  "neni", "koro", "e", "a", "wuon"],
        "patterns": [r'\bng\'', r'\bchi\w+', r'\bwuon', r'\badiera']
    },
    "kamba": {
        "words": ["na", "ni", "kya", "kwa", "va", "mba", "atu", "ũndũ", "kĩla",
                  "sya", "iyo", "kũ", "kwonza", "yũ", "ũ", "ĩ", "aa", "kya"],
        "patterns": [r'\bũndũ', r'\bkĩla', r'\bkwonza', r'\bmba\b']
    },
    "kalenjin": {
        "words": ["ne", "na", "kmen", "tap", "tow", "kab", "kap", "kog", "chom",
                  "tugul", "murei", "barnot", "mwei", "arap", "chebi", "kips",
                  "lagat", "kipko", "cherui", "kimeli"],
        "patterns": [r'\barap\b', r'\bchebi', r'\bkips', r'\blagat', r'\bkipko']
    },
    "luhya": {
        "words": ["na", "ni", "wa", "kwa", "kuli", "ykhulia", "omwami", "abandu",
                  "akhwi", "kumwami", "oyo", "kuli", "lwa", "mbwa", "sibala",
                  "omukhwa", "abakhwi", "eshiami", "ende"],
        "patterns": [r'\bomwami\b', r'\babandu\b', r'\bakhwi', r'\beshiami']
    },
    "somali": {
        "words": ["wa", "ku", "la", "ka", "marka", "dadka", "ha", "in", "rag",
                  "naag", "carruur", "magac", "wax", "ay", "uu", "iyo", "ane",
                  "kiyo", "ma", "ahaan"],
        "patterns": [r'\bmarka\b', r'\bdadka\b', r'\bcarruur', r'\bmagac']
    },
    "kisii": {
        "words": ["na", "ni", "bo", "go", "kwa", "mo", "no", "ite", "ria", "ama",
                  "bouk", "chinko", "enge", "gete", "kiba", "mongo", "nya", "ora"],
        "patterns": [r'\bbouk', r'\bchinko', r'\bgete', r'\bkiba']
    },
    "meru": {
        "words": ["na", "ni", "wa", "kwa", "ya", "no", "kira", "cia", "mwe",
                  "antu", "nyumba", "mũgwe", "kũrĩa", "thĩ", "mũno", "ara",
                  "kithaka", "kiama", "muguna"],
        "patterns": [r'\bmũgwe\b', r'\bkithaka\b', r'\bkiama', r'\bmuguna']
    },
}


class LanguageDetector:
    """
    Detect Kenyan languages from text input.
    Uses a combination of word frequency analysis and regex patterns.
    """
    
    def __init__(self):
        self.language_markers = LANGUAGE_MARKERS
    
    def detect(
        self, 
        text: str, 
        min_confidence: float = 0.3,
        sample_size: int = 500
    ) -> Dict[str, float]:
        """
        Detect language(s) in text and return confidence scores.
        
        Args:
            text: Text to analyze
            min_confidence: Minimum confidence to include in results
            sample_size: Number of characters to sample from text
            
        Returns:
            Dict with language -> confidence score (0-1)
        """
        if not text or not text.strip():
            return {"english": 1.0}
        
        # Sample text if too long
        text_sample = text[:sample_size].lower() if len(text) > sample_size else text.lower()
        words = re.findall(r'\b\w+\b', text_sample)
        
        if not words:
            return {"english": 1.0}
        
        scores = {}
        
        for lang, markers in self.language_markers.items():
            score = 0.0
            
            # Check for common words
            word_matches = sum(1 for word in words if word in markers["words"])
            word_score = min(word_matches / max(len(words), 1), 1.0)
            
            # Check for patterns
            pattern_matches = sum(
                1 for pattern in markers["patterns"] 
                if re.search(pattern, text_sample)
            )
            pattern_score = min(pattern_matches / 3.0, 1.0)
            
            # Combined score (words weighted more)
            score = (word_score * 0.7) + (pattern_score * 0.3)
            
            if score >= min_confidence:
                scores[lang] = round(score, 3)
        
        # If no strong matches, assume English
        if not scores:
            scores["english"] = 0.8
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: round(v / total, 3) for k, v in scores.items()}
        
        return scores
    
    def detect_primary(self, text: str) -> str:
        """
        Return the most likely language for the text.
        
        Returns:
            Language code string (e.g., 'swahili', 'kikuyu', 'english')
        """
        scores = self.detect(text)
        if not scores:
            return "english"
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def detect_with_fallback(
        self, 
        text: str, 
        filename: Optional[str] = None
    ) -> str:
        """
        Detect language with filename hints and fallback.
        
        Args:
            text: Text to analyze
            filename: Optional filename for hints
            
        Returns:
            Detected language code
        """
        # Check filename for hints
        if filename:
            filename_lower = filename.lower()
            lang_hints = {
                "swahili": ["swahili", "kiswahili", "sw.", "swa"],
                "kikuyu": ["kikuyu", "gikuyu", "kikuy"],
                "luo": ["luo"],
                "kamba": ["kamba", "kikamba"],
                "kalenjin": ["kalenjin", "kipsigis", "nandi"],
                "luhya": ["luhya", "lumii", "maragoli"],
                "somali": ["somali", "somalia"],
                "kisii": ["kisii", "gisii", "kisii"],
                "meru": ["meru", "kimîîru"],
            }
            
            for lang, markers in lang_hints.items():
                if any(marker in filename_lower for marker in markers):
                    return lang
        
        return self.detect_primary(text)
