import unittest
import json
import time
from unittest.mock import patch
from app import app

class TestIntegration(unittest.TestCase):
    """Integration tests for JetSet AI"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
    
    def test_full_conversation_flow(self):
        """Test complete conversation flow"""
        conversation_id = 'integration_test_001'
        
        # Step 1: Health check
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Send initial message (mocked)
        with patch('app.call_claude_with_mcp') as mock_claude:
            with patch('app.reformat_to_structured_json') as mock_reformat:
                mock_claude.return_value = {
                    'success': True,
                    'response': 'I found some flights for you!',
                    'error': None
                }
                
                mock_reformat.return_value = {
                    'flights': [{'id': '1', 'airline': 'Test Air', 'price': 300}],
                    'summary': {'totalResults': 1, 'cheapestPrice': 300}
                }
                
                response = self.client.post('/api/chat',
                    data=json.dumps({
                        'message': 'Find flights from NYC to LAX tomorrow',
                        'conversation_id': conversation_id
                    }),
                    content_type='application/json'
                )
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertIn('response', data)
                self.assertIn('flight_data', data)
        
        # Step 3: Check progress
        response = self.client.get('/api/progress')
        self.assertEqual(response.status_code, 200)
        
        # Step 4: Reset conversation
        response = self.client.post('/api/reset',
            data=json.dumps({'conversation_id': conversation_id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_multiple_conversations(self):
        """Test handling multiple conversations"""
        with patch('app.call_claude_with_mcp') as mock_claude:
            with patch('app.reformat_to_structured_json') as mock_reformat:
                mock_claude.return_value = {
                    'success': True,
                    'response': 'Response',
                    'error': None
                }
                mock_reformat.return_value = None
                
                # Conversation 1
                response1 = self.client.post('/api/chat',
                    data=json.dumps({
                        'message': 'Find flights to Paris',
                        'conversation_id': 'conv1'
                    }),
                    content_type='application/json'
                )
                self.assertEqual(response1.status_code, 200)
                
                # Conversation 2
                response2 = self.client.post('/api/chat',
                    data=json.dumps({
                        'message': 'Find flights to Tokyo',
                        'conversation_id': 'conv2'
                    }),
                    content_type='application/json'
                )
                self.assertEqual(response2.status_code, 200)
                
                # Both should succeed independently
                data1 = json.loads(response1.data)
                data2 = json.loads(response2.data)
                self.assertEqual(data1['conversation_id'], 'conv1')
                self.assertEqual(data2['conversation_id'], 'conv2')
    
    def test_error_recovery(self):
        """Test error handling and recovery"""
        with patch('app.call_claude_with_mcp') as mock_claude:
            # First request fails
            mock_claude.return_value = {
                'success': False,
                'response': None,
                'error': 'Timeout'
            }
            
            response = self.client.post('/api/chat',
                data=json.dumps({
                    'message': 'Find flights',
                    'conversation_id': 'error_test'
                }),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 500)
            
            # Second request succeeds
            with patch('app.reformat_to_structured_json') as mock_reformat:
                mock_claude.return_value = {
                    'success': True,
                    'response': 'Success',
                    'error': None
                }
                mock_reformat.return_value = None
                
                response = self.client.post('/api/chat',
                    data=json.dumps({
                        'message': 'Find flights again',
                        'conversation_id': 'error_test'
                    }),
                    content_type='application/json'
                )
                self.assertEqual(response.status_code, 200)
    
    def test_progress_monitoring_integration(self):
        """Test progress monitoring during chat"""
        with patch('app.call_claude_with_mcp') as mock_claude:
            with patch('app.reformat_to_structured_json') as mock_reformat:
                mock_claude.return_value = {
                    'success': True,
                    'response': 'Processing...',
                    'error': None
                }
                mock_reformat.return_value = None
                
                # Start a chat request
                response = self.client.post('/api/chat',
                    data=json.dumps({
                        'message': 'Find flights',
                        'conversation_id': 'progress_test'
                    }),
                    content_type='application/json'
                )
                self.assertEqual(response.status_code, 200)
                
                # Check progress endpoint
                progress_response = self.client.get('/api/progress')
                self.assertEqual(progress_response.status_code, 200)
                progress_data = json.loads(progress_response.data)
                self.assertIn('status', progress_data)
                self.assertIn('progress', progress_data)

if __name__ == '__main__':
    unittest.main()