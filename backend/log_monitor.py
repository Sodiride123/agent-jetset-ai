import os
import time
import json
import logging
from pathlib import Path
from typing import Optional, Dict, List
import re

logger = logging.getLogger(__name__)

class ClaudeLogMonitor:
    """Monitor Claude Code logs for progress tracking"""
    
    def __init__(self, workspace_name: str = "jetset-ai"):
        self.workspace_name = workspace_name
        self.logs_dir = Path.home() / ".claude" / "projects" / workspace_name
        self.current_log_file = None
        self.last_position = 0
        
    def find_latest_log(self) -> Optional[Path]:
        """Find the most recent log file for this workspace"""
        try:
            if not self.logs_dir.exists():
                logger.warning(f"Logs directory not found: {self.logs_dir}")
                return None
            
            log_files = list(self.logs_dir.glob("*.log"))
            if not log_files:
                logger.warning(f"No log files found in {self.logs_dir}")
                return None
            
            # Get the most recent log file
            latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
            logger.info(f"Found latest log: {latest_log}")
            return latest_log
            
        except Exception as e:
            logger.error(f"Error finding log file: {e}")
            return None
    
    def parse_log_entry(self, line: str) -> Optional[Dict]:
        """Parse a log line and extract relevant information"""
        try:
            # Look for tool usage patterns
            tool_match = re.search(r'Tool:\s*(\w+)', line)
            if tool_match:
                return {
                    'type': 'tool_use',
                    'tool': tool_match.group(1),
                    'timestamp': time.time()
                }
            
            # Look for MCP calls
            mcp_match = re.search(r'MCP.*booking_com', line, re.IGNORECASE)
            if mcp_match:
                return {
                    'type': 'mcp_call',
                    'service': 'booking_com',
                    'timestamp': time.time()
                }
            
            # Look for search patterns
            search_match = re.search(r'Search.*Flight|Flight.*Search', line, re.IGNORECASE)
            if search_match:
                return {
                    'type': 'flight_search',
                    'timestamp': time.time()
                }
            
            # Look for completion patterns
            if 'completed' in line.lower() or 'finished' in line.lower():
                return {
                    'type': 'completion',
                    'timestamp': time.time()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing log line: {e}")
            return None
    
    def get_progress_updates(self) -> List[Dict]:
        """Get new progress updates since last check"""
        updates = []
        
        try:
            # Find or update current log file
            if not self.current_log_file or not self.current_log_file.exists():
                self.current_log_file = self.find_latest_log()
                self.last_position = 0
            
            if not self.current_log_file:
                return updates
            
            # Read new content from log file
            with open(self.current_log_file, 'r') as f:
                f.seek(self.last_position)
                new_lines = f.readlines()
                self.last_position = f.tell()
            
            # Parse new lines
            for line in new_lines:
                parsed = self.parse_log_entry(line)
                if parsed:
                    updates.append(parsed)
            
            return updates
            
        except Exception as e:
            logger.error(f"Error reading log updates: {e}")
            return updates
    
    def get_current_status(self) -> Dict:
        """Get current processing status"""
        try:
            updates = self.get_progress_updates()
            
            if not updates:
                return {
                    'status': 'idle',
                    'message': 'Waiting for activity...',
                    'progress': 0
                }
            
            # Determine status based on latest updates
            latest = updates[-1]
            
            if latest['type'] == 'tool_use':
                return {
                    'status': 'processing',
                    'message': f"Using tool: {latest['tool']}",
                    'progress': 30
                }
            elif latest['type'] == 'mcp_call':
                return {
                    'status': 'searching',
                    'message': 'Searching for flights...',
                    'progress': 50
                }
            elif latest['type'] == 'flight_search':
                return {
                    'status': 'analyzing',
                    'message': 'Analyzing flight results...',
                    'progress': 70
                }
            elif latest['type'] == 'completion':
                return {
                    'status': 'complete',
                    'message': 'Search complete!',
                    'progress': 100
                }
            
            return {
                'status': 'processing',
                'message': 'Processing your request...',
                'progress': 40
            }
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {
                'status': 'error',
                'message': 'Error monitoring progress',
                'progress': 0
            }