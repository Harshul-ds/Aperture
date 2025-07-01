# backend/core/classification_service.py

import re

class ClassificationService:
    def __init__(self):
        """
        Initializes the classification service with predefined rules.
        """
        self.rules = {
            "Job Application": [
                "application", "applied", "resume", "cv", "interview",
                "recruiting", "talent acquisition", "we've received your application",
                "next steps", "coding challenge"
            ],
            "Receipt": [
                "receipt", "invoice", "order confirmation", "your order",
                "billing statement", "payment confirmation"
            ],
            "Newsletter": [
                "unsubscribe", "view in browser", "newsletter", "daily digest"
            ]
        }

    def classify_email(self, subject: str, body: str) -> str:
        """
        Classifies an email based on its subject and body content.
        """
        text_to_check = f"{subject.lower()} {body.lower()}"

        for category, keywords in self.rules.items():
            for keyword in keywords:
                # Use regex to match whole words to avoid partial matches (e.g., 'cv' in 'receive')
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_to_check):
                    return category
        
        return "General"

# Create a single, importable instance of the service
classification_service = ClassificationService()
