# backend/core/classification_service.py

import re
import spacy

class ClassificationService:
    def __init__(self):
        """
        Initializes the classification service with NLP model and predefined rules.
        """
        self.nlp = spacy.load("en_core_web_sm")
        self.general_rules = {
            "Job Application": [
                "application", "applied", "resume", "cv", "interview", "recruiting", 
                "talent acquisition", "we've received your application", "next steps", "coding challenge"
            ],
            "Receipt": ["receipt", "invoice", "order confirmation", "your order", "billing statement"],
            "Newsletter": ["unsubscribe", "view in browser", "newsletter", "daily digest"]
        }
        self.job_status_rules = {
            "Rejected": ["unfortunately", "not been selected", "other candidates", "filled the position"],
            "Interview": ["interview", "coding challenge", "assessment", "next steps"],
            "Offer": ["offer of employment", "job offer"],
            "Applied": ["application received", "we've received your application", "confirming your application"]
        }
        self.common_orgs_to_ignore = ["gmail", "linkedin", "indeed", "glassdoor"]

    def classify_email(self, subject: str, body: str) -> dict:
        """
        Classifies an email and extracts job details if applicable.
        Returns a dictionary with category, company, and status.
        """
        text_to_check = f"{subject.lower()} {body.lower()}"
        
        # Step 1: General Classification
        category = "General"
        for cat, keywords in self.general_rules.items():
            if any(re.search(r'\b' + re.escape(kw) + r'\b', text_to_check) for kw in keywords):
                category = cat
                break

        # Step 2: If it's a job application, extract details
        company = None
        status = None
        if category == "Job Application":
            doc = self.nlp(f"{subject}\n{body[:500]}") # Process subject and first 500 chars of body
            company = self._extract_company_name(doc)
            status = self._determine_job_status(text_to_check)

        return {"category": category, "company": company, "status": status}

    def _determine_job_status(self, text: str) -> str:
        for status, keywords in self.job_status_rules.items():
            if any(re.search(r'\b' + re.escape(kw) + r'\b', text) for kw in keywords):
                return status
        return "Applied" # Default status for a job email

    def _extract_company_name(self, doc) -> str | None:
        for ent in doc.ents:
            if ent.label_ == "ORG" and ent.text.lower() not in self.common_orgs_to_ignore:
                return ent.text
        return None

# Create a single, importable instance of the service
classification_service = ClassificationService()

