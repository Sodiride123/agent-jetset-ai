import unittest
import tempfile
import os
from pathlib import Path
from log_monitor import ClaudeLogMonitor

class TestLogMonitor(unittest.TestCase):
    """Unit tests for Claude log monitoring"""
    
    def setUp(self):
        """Set up test environment"""
        self.monitor = ClaudeLogMonitor("test-workspace")
        self.temp_dir = tempfile.mkdtemp()
    
    def test_parse_tool_use(self):
        """Test parsing tool use log entries"""
        line = "2024-02-08 10:00:00 - Tool: Search_Flights"
        result = self.monitor.parse_log_entry(line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'tool_use')
        self.assertEqual(result['tool'], 'Search_Flights')
        self.assertIn('timestamp', result)
    
    def test_parse_mcp_call(self):
        """Test parsing MCP call log entries"""
        line = "2024-02-08 10:00:00 - MCP call to booking_com"
        result = self.monitor.parse_log_entry(line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'mcp_call')
        self.assertEqual(result['service'], 'booking_com')
    
    def test_parse_flight_search(self):
        """Test parsing flight search log entries"""
        line = "2024-02-08 10:00:00 - Flight Search initiated"
        result = self.monitor.parse_log_entry(line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'flight_search')
    
    def test_parse_completion(self):
        """Test parsing completion log entries"""
        line = "2024-02-08 10:00:00 - Task completed successfully"
        result = self.monitor.parse_log_entry(line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'completion')
    
    def test_parse_irrelevant_line(self):
        """Test parsing irrelevant log entries"""
        line = "2024-02-08 10:00:00 - Some random log message"
        result = self.monitor.parse_log_entry(line)
        
        self.assertIsNone(result)
    
    def test_get_current_status_idle(self):
        """Test status when no updates"""
        status = self.monitor.get_current_status()
        
        self.assertEqual(status['status'], 'idle')
        self.assertIn('message', status)
        self.assertEqual(status['progress'], 0)
    
    def test_find_latest_log_no_directory(self):
        """Test finding log when directory doesn't exist"""
        monitor = ClaudeLogMonitor("nonexistent-workspace")
        result = monitor.find_latest_log()
        
        self.assertIsNone(result)
    
    def test_get_progress_updates_no_log(self):
        """Test getting updates when no log file exists"""
        updates = self.monitor.get_progress_updates()
        
        self.assertIsInstance(updates, list)
        self.assertEqual(len(updates), 0)

if __name__ == '__main__':
    unittest.main()