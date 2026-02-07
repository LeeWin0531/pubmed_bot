"""
Configuration module for PubMed Search Tool
Handles environment variables and configuration settings
"""

import os
from typing import Optional


class Config:
    """Configuration management for the application"""
    
    def __init__(self):
        """Initialize configuration from environment variables"""
        self._load_env_file()
    
    def _load_env_file(self):
        """Load environment variables from .env file if it exists"""
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
            except Exception:
                pass  # Silently ignore errors in .env file
    
    @property
    def pubmed_email(self) -> str:
        """Get PubMed email from environment or return default"""
        return os.getenv('PUBMED_EMAIL', os.getenv('USER_EMAIL', 'user@example.com'))
    
    @property
    def pubmed_tool_name(self) -> str:
        """Get PubMed tool name from environment or return default"""
        return os.getenv('PUBMED_TOOL_NAME', 'PubMedSearchTool')
    
    @property
    def pubmed_api_key(self) -> Optional[str]:
        """Get PubMed API key from environment if available"""
        return os.getenv('PUBMED_API_KEY')
    
    @property
    def translation_api_url(self) -> str:
        """获取翻译 API 的 Base URL"""
        return os.getenv('TRANSLATION_API', 'https://api.deepseek.com')

    @property
    def translation_model(self) -> str:
        """获取翻译使用的模型名称"""
        return os.getenv('TRANSLATION_MODEL', 'deepseek-chat')

    @property
    def translation_api_key(self) -> str:
        """获取翻译 API 的 Key"""
        return os.getenv('TRANSLATION_API_KEY')

    @property
    def default_language(self) -> str:
        """Get default language from environment or return 'tr'"""
        return os.getenv('DEFAULT_LANGUAGE', 'tr')
    
    @property
    def max_results_limit(self) -> int:
        """Get maximum results limit from environment or return default"""
        try:
            return int(os.getenv('MAX_RESULTS_LIMIT', '10000'))
        except ValueError:
            return 10000
    
    def get_user_info(self) -> dict:
        """Get user information for display"""
        return {
            'email': self.pubmed_email,
            'tool_name': self.pubmed_tool_name,
            'has_api_key': bool(self.pubmed_api_key),
            'language': self.default_language
        }


# Global configuration instance
config = Config()
