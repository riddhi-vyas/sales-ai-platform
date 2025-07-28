"""Slack posting activity using Arcade for secure integration."""

from typing import Dict, Any
import json

try:
    import arcade_ai
except ImportError:
    print("Warning: Arcade AI not installed. Run: pip install arcade-ai")
    arcade_ai = None

from temporalio import activity
from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class SlackPoster:
    """Handles posting opportunity briefs to Slack via Arcade."""
    
    def __init__(self):
        self.client = None
        self._initialize_arcade()
    
    def _initialize_arcade(self):
        """Initialize Arcade client."""
        if not arcade_ai or not settings.arcade_api_key:
            logger.warning("Arcade not configured - using mock mode")
            return
        
        try:
            self.client = arcade_ai.Arcade(api_key=settings.arcade_api_key)
            logger.info("Arcade client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Arcade: {e}")
            self.client = None
    
    def post_opportunity_brief(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Post opportunity brief to Slack channel."""
        try:
            company_name = analysis_result.get('company_name', 'Unknown Company')
            
            logger.info(f"Posting opportunity brief for {company_name} to Slack")
            
            # Format the message for Slack
            slack_message = self._format_slack_message(analysis_result)
            
            if self.client and settings.arcade_tool_id:
                # Use Arcade to post to Slack
                result = self._post_via_arcade(slack_message)
            else:
                # Mock posting for demo/development
                result = self._mock_slack_post(slack_message)
            
            logger.success(f"Opportunity brief posted for {company_name}")
            
            return {
                "success": True,
                "company_name": company_name,
                "channel": settings.slack_channel,
                "message_id": result.get('message_id'),
                "timestamp": result.get('timestamp')
            }
            
        except Exception as e:
            logger.error(f"Error posting to Slack: {e}")
            return {
                "success": False,
                "error": str(e),
                "company_name": analysis_result.get('company_name', 'Unknown')
            }
    
    def _format_slack_message(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format analysis result for Slack posting."""
        opportunity_brief = analysis_result.get('opportunity_brief', '')
        company_name = analysis_result.get('company_name', 'Unknown Company')
        intent_score = analysis_result.get('intent_score', 0)
        urgency_level = analysis_result.get('urgency_level', 'MEDIUM')
        
        # Create rich Slack message with blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 New High-Intent Opportunity: {company_name}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": opportunity_brief
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Intent Score:*\n{intent_score}/100"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Urgency:*\n{urgency_level}"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "📞 Schedule Call"
                        },
                        "style": "primary",
                        "url": "https://calendly.com/sales-team"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "📊 View Full Analysis"
                        },
                        "url": "https://crm.company.com/analysis"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✉️ Send Follow-up"
                        }
                    }
                ]
            }
        ]
        
        return {
            "channel": settings.slack_channel,
            "text": f"New opportunity: {company_name} (Intent: {intent_score}/100)",
            "blocks": blocks,
            "unfurl_links": False,
            "unfurl_media": False
        }
    
    def _post_via_arcade(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post message via Arcade Slack integration."""
        try:
            # Execute Slack tool via Arcade
            result = self.client.tools.execute(
                tool_id=settings.arcade_tool_id,
                inputs={
                    "channel": message_data["channel"],
                    "text": message_data["text"],
                    "blocks": json.dumps(message_data["blocks"])
                }
            )
            
            return {
                "success": True,
                "message_id": result.get('id'),
                "timestamp": result.get('ts'),
                "channel": message_data["channel"]
            }
            
        except Exception as e:
            logger.error(f"Error executing Arcade Slack tool: {e}")
            raise
    
    def _mock_slack_post(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock Slack posting for development/demo."""
        logger.info("=== MOCK SLACK POST ===")
        logger.info(f"Channel: {message_data['channel']}")
        logger.info(f"Message: {message_data['text']}")
        
        # Pretty print the opportunity brief from blocks
        if message_data.get('blocks'):
            for block in message_data['blocks']:
                if block.get('type') == 'section' and 'text' in block:
                    text_content = block['text'].get('text', '')
                    if '🎯 **OPPORTUNITY BRIEF' in text_content:
                        # This is our main opportunity brief
                        logger.info("\n" + "="*50)
                        logger.info("OPPORTUNITY BRIEF CONTENT:")
                        logger.info("="*50)
                        # Clean up markdown for console display
                        clean_text = text_content.replace('**', '').replace('🎯 ', '').replace('*', '')
                        logger.info(clean_text)
                        logger.info("="*50)
        
        logger.info("=== END MOCK SLACK POST ===")
        
        return {
            "success": True,
            "message_id": "mock_message_id_123",
            "timestamp": "1640995200.123456",
            "channel": message_data["channel"]
        }
    
    def send_test_message(self, test_message: str) -> Dict[str, Any]:
        """Send a test message to verify Slack integration."""
        test_data = {
            "channel": settings.slack_channel,
            "text": f"🧪 Test message from GTM Agent: {test_message}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Test Message:* {test_message}\n\n✅ Slack integration is working!"
                    }
                }
            ]
        }
        
        if self.client and settings.arcade_tool_id:
            return self._post_via_arcade(test_data)
        else:
            return self._mock_slack_post(test_data)


# Activity functions for Temporal
@activity.defn
async def post_to_slack(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """Temporal activity: Post opportunity brief to Slack."""
    poster = SlackPoster()
    return poster.post_opportunity_brief(analysis_result)


@activity.defn
async def send_slack_test(test_message: str = "System check") -> Dict[str, Any]:
    """Temporal activity: Send test message to Slack."""
    poster = SlackPoster()
    return poster.send_test_message(test_message) 