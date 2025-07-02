import unittest
from backend.core.classification_service import ClassificationService

class TestClassificationService(unittest.TestCase):

    def setUp(self):
        self.service = ClassificationService()

    def test_classify_as_job_application(self):
        subject = "Your application for Software Engineer"
        body = "Thank you for applying. We have received your resume."
        result = self.service.classify_email(subject, body)
        self.assertEqual(result['category'], 'Job Application')

    def test_classify_as_receipt(self):
        subject = "Your order confirmation #12345"
        body = "Here is your receipt for your recent purchase."
        result = self.service.classify_email(subject, body)
        self.assertEqual(result['category'], 'Receipt')

    def test_classify_as_newsletter(self):
        subject = "Weekly Newsletter"
        body = "If you wish to unsubscribe, please click here."
        result = self.service.classify_email(subject, body)
        self.assertEqual(result['category'], 'Newsletter')

    def test_classify_as_general(self):
        subject = "Hello there"
        body = "Just wanted to say hi."
        result = self.service.classify_email(subject, body)
        self.assertEqual(result['category'], 'General')

    def test_determine_job_status_rejected(self):
        text = "unfortunately we have decided to move forward with other candidates"
        status = self.service._determine_job_status(text)
        self.assertEqual(status, 'Rejected')

    def test_extract_company_name(self):
        doc = self.service.nlp("We are excited to have you interview at Google.")
        company = self.service._extract_company_name(doc)
        self.assertEqual(company, 'Google')

if __name__ == '__main__':
    unittest.main()
