import unittest
import json
from unittest.mock import patch, MagicMock
from app import app

class TestJetSetBackend(unittest.TestCase):
    """Unit tests for JetSet AI backend"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
    
    def test_progress_endpoint(self):
        """Test progress monitoring endpoint"""
        response = self.client.get('/api/progress')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('message', data)
        self.assertIn('progress', data)
    
    def test_monitor_dashboard_info(self):
        """Test monitor dashboard info endpoint"""
        response = self.client.get('/api/monitor')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('dashboard_url', data)
        self.assertEqual(data['dashboard_url'], 'http://localhost:9010')
    
    @patch('app.call_claude_with_mcp')
    @patch('app.reformat_to_structured_json')
    def test_chat_endpoint_success(self, mock_reformat, mock_claude):
        """Test successful chat request"""
        # Mock Claude response
        mock_claude.return_value = {
            'success': True,
            'response': 'Here are some flights for you!',
            'error': None
        }
        
        # Mock JSON reformatting
        mock_reformat.return_value = {
            'flights': [
                {
                    'id': '1',
                    'airline': 'Test Airlines',
                    'price': 500,
                    'currency': 'USD'
                }
            ],
            'summary': {
                'totalResults': 1,
                'cheapestPrice': 500
            }
        }
        
        # Send chat request
        response = self.client.post('/api/chat',
            data=json.dumps({
                'message': 'Find flights from NYC to LAX',
                'conversation_id': 'test123'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertIn('flight_data', data)
        self.assertEqual(data['conversation_id'], 'test123')
    
    @patch('app.call_claude_with_mcp')
    def test_chat_endpoint_error(self, mock_claude):
        """Test chat request with error"""
        # Mock Claude error
        mock_claude.return_value = {
            'success': False,
            'response': None,
            'error': 'Connection timeout'
        }
        
        # Send chat request
        response = self.client.post('/api/chat',
            data=json.dumps({
                'message': 'Find flights',
                'conversation_id': 'test456'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_reset_conversation(self):
        """Test conversation reset"""
        response = self.client.post('/api/reset',
            data=json.dumps({
                'conversation_id': 'test789'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
    
    def test_chat_missing_message(self):
        """Test chat request without message"""
        response = self.client.post('/api/chat',
            data=json.dumps({
                'conversation_id': 'test'
            }),
            content_type='application/json'
        )
        
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 500])

if __name__ == '__main__':
    unittest.main()