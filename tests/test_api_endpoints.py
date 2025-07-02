import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.main import app

class TestApiEndpoints(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    @patch('backend.api.search.ingestion_service')
    @patch('backend.api.search.SessionLocal')
    def test_search_endpoint(self, mock_session_local, mock_ingestion_service):
        # Setup mocks
        mock_db_session = MagicMock()
        mock_session_local.return_value = mock_db_session
        mock_collection = MagicMock()
        mock_ingestion_service.collection = mock_collection

        # Mock ChromaDB response
        mock_collection.query.return_value = {
            'ids': [['test_email_id']],
            'documents': [['Test snippet']],
            'distances': [[0.1]]
        }
        # Mock SQLAlchemy response
        mock_email = MagicMock()
        mock_email.id = 'test_email_id'
        mock_email.sender = 'test@example.com'
        mock_email.subject = 'Test Subject'
        mock_email.category = 'General'
        mock_email.attachments = []
        mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_email]

        response = self.client.get("/api/v1/search/?query=test")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['id'], 'test_email_id')

    @patch('backend.api.jobs.SessionLocal')
    def test_jobs_endpoint(self, mock_session_local):
        # Setup mocks
        mock_db_session = MagicMock()
        mock_session_local.return_value = mock_db_session

        # Mock SQLAlchemy response
        mock_email = MagicMock()
        mock_email.id = 'job_email_id'
        mock_email.job_company = 'TestCorp'
        mock_email.subject = 'Job Application'
        mock_email.job_status = 'Applied'
        mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_email]

        response = self.client.get("/api/v1/jobs/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['company'], 'TestCorp')

if __name__ == '__main__':
    unittest.main()
