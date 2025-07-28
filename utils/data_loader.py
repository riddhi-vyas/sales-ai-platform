"""Data loading utilities for mock HockeyStack data and knowledge base."""

import json
import os
from typing import List, Dict, Any
from pathlib import Path

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class DataLoader:
    """Handles loading of mock data and knowledge base files."""
    
    def __init__(self):
        self.mock_data_path = Path(settings.mock_data_path)
        self.knowledge_base_path = Path(settings.knowledge_base_path)
    
    def load_mock_accounts(self) -> List[Dict[str, Any]]:
        """Load mock HockeyStack account data."""
        try:
            with open(self.mock_data_path, 'r') as f:
                accounts = json.load(f)
            
            logger.info(
                "Loaded mock account data",
                total_accounts=len(accounts),
                path=str(self.mock_data_path)
            )
            return accounts
            
        except FileNotFoundError:
            logger.error(f"Mock data file not found: {self.mock_data_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing mock data JSON: {e}")
            return []
    
    def get_high_intent_accounts(self, threshold: int = None) -> List[Dict[str, Any]]:
        """Get accounts above the intent threshold that haven't been processed."""
        threshold = threshold or settings.high_intent_threshold
        accounts = self.load_mock_accounts()
        
        high_intent = [
            account for account in accounts
            if account.get('intent_score', 0) >= threshold 
            and not account.get('processed', False)
        ]
        
        logger.info(
            "Filtered high-intent accounts",
            total_accounts=len(accounts),
            high_intent_count=len(high_intent),
            threshold=threshold
        )
        
        return high_intent
    
    def mark_account_processed(self, account_id: str) -> bool:
        """Mark an account as processed in the mock data."""
        try:
            accounts = self.load_mock_accounts()
            
            for account in accounts:
                if account.get('account_id') == account_id:
                    account['processed'] = True
                    break
            else:
                logger.warning(f"Account not found: {account_id}")
                return False
            
            # Write back to file
            with open(self.mock_data_path, 'w') as f:
                json.dump(accounts, f, indent=2)
            
            logger.success(f"Marked account as processed: {account_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error marking account as processed: {e}")
            return False
    
    def load_knowledge_base_files(self) -> Dict[str, str]:
        """Load all knowledge base text files."""
        knowledge_files = {}
        
        if not self.knowledge_base_path.exists():
            logger.warning(f"Knowledge base directory not found: {self.knowledge_base_path}")
            return knowledge_files
        
        try:
            for file_path in self.knowledge_base_path.glob("*.txt"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    knowledge_files[file_path.stem] = content
                    
                logger.info(f"Loaded knowledge file: {file_path.name}")
            
            logger.success(
                "Knowledge base loaded",
                total_files=len(knowledge_files),
                files=list(knowledge_files.keys())
            )
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
        
        return knowledge_files
    
    def get_account_by_id(self, account_id: str) -> Dict[str, Any]:
        """Get a specific account by ID."""
        accounts = self.load_mock_accounts()
        
        for account in accounts:
            if account.get('account_id') == account_id:
                return account
        
        logger.warning(f"Account not found: {account_id}")
        return {}


# Global data loader instance
data_loader = DataLoader() 