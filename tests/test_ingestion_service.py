import unittest
from unittest.mock import MagicMock, patch
from backend.core.ingestion_service import IngestionService

class TestIngestionService(unittest.TestCase):

    @patch('backend.core.ingestion_service.get_user_credentials')
    @patch('backend.core.ingestion_service.build_google_service')
    @patch('backend.core.ingestion_service.SessionLocal')
    @patch('backend.core.ingestion_service.chromadb.PersistentClient')
    @patch('backend.core.ingestion_service.spacy.load')
    @patch('backend.core.ingestion_service.SentenceTransformer')
    @patch('backend.core.ingestion_service.classification_service')
    def test_fetch_and_process_emails(self, mock_classification_service, mock_sentence_transformer, mock_spacy_load, mock_chromadb, mock_session_local, mock_build_google_service, mock_get_user_credentials):
        # Setup mocks
        mock_get_user_credentials.return_value = 'dummy_credentials'
        mock_google_service = MagicMock()
        mock_build_google_service.return_value = mock_google_service
        mock_db_session = MagicMock()
        mock_session_local.return_value = mock_db_session
        mock_chroma_client = MagicMock()
        mock_chromadb.return_value = mock_chroma_client
        mock_collection = MagicMock()
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        # Mock Gmail API response
        mock_google_service.users().messages().list().execute.return_value = {
            'messages': [{'id': 'test_email_id'}]
        }
        mock_google_service.users().messages().get().execute.return_value = {
            'id': 'test_email_id',
            'threadId': 'test_thread_id',
            'snippet': 'Test snippet',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'From', 'value': 'test@example.com'},
                    {'name': 'Date', 'value': 'Mon, 1 Jan 2024 00:00:00 +0000'}
                ],
                'parts': [
                    {'mimeType': 'text/plain', 'body': {'data': 'VGVzdCBib2R5'}}
                ]
            }
        }

        # Mock classification service response
        mock_classification_service.classify_email.return_value = {
            'category': 'General',
            'company': None,
            'status': None
        }

        # Mock the database query to simulate that the email doesn't exist yet
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Instantiate and run the service
        ingestion_service = IngestionService()
        # We also need to mock the get_latest_email_date method to return None
        ingestion_service.get_latest_email_date = MagicMock(return_value=None)
        ingestion_service.fetch_and_process_emails(limit=1)

        # Assertions
        mock_db_session.add.assert_called_once()
        mock_collection.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
