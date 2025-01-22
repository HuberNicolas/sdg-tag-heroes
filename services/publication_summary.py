from transformers import pipeline
from keybert import KeyBERT

from typing import List, Dict

class SummarizationService:
    """Service for text summarization."""
    def __init__(self, model_name: str = "t5-small"):
        self.summarizer = pipeline("summarization", model=model_name)

    def summarize(self, texts: List[str], max_length: int = 50, min_length: int = 25) -> Dict:
        return {
            f"summary_{i + 1}": self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
            for i, text in enumerate(texts)
        }

class KeywordExtractionService:
    """Service for keyword extraction."""
    def __init__(self):
        self.model = KeyBERT()

    def extract_keywords(self, texts: List[str], top_n: int = 5) -> Dict:
        return {
            f"keywords_{i + 1}": [kw[0] for kw in self.model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=top_n)]
            for i, text in enumerate(texts)
        }


class PublicationSummaryService:
    """Main service to handle publications and their operations."""
    def __init__(self):
        self.summarization_service = SummarizationService()
        self.keyword_extraction_service = KeywordExtractionService()


    def summarize_publications(self, abstracts: List[str]) -> Dict:
        return self.summarization_service.summarize(abstracts)

    def extract_keywords(self, abstracts: List[str]) -> Dict:
        return self.keyword_extraction_service.extract_keywords(abstracts)



# Usage Example:
if __name__ == "__main__":
    abstracts = [
        "Climate change is causing severe weather patterns globally. Research shows that reducing emissions can help mitigate its impact.",
        "AI is revolutionizing many industries, including healthcare, where predictive models are saving lives."
    ]

    service = PublicationSummaryService()

    # Summarize abstracts
    summaries = service.summarize_publications(abstracts)
    print("Summaries:", summaries)

    # Extract keywords
    keywords = service.extract_keywords(abstracts)
    print("Keywords:", keywords)
