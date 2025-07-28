"""Temporal workflow for processing high-intent opportunities."""

from datetime import timedelta
from typing import Dict, Any

from temporalio import workflow
from temporalio.common import RetryPolicy

# Import activities
from activities.rag_analyzer import analyze_account_with_rag
from activities.slack_poster import post_to_slack
from utils.logger import get_logger

logger = get_logger(__name__)


@workflow.defn
class OpportunityProcessingWorkflow:
    """Durable workflow for processing high-intent accounts."""
    
    @workflow.run
    async def run(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main workflow execution."""
        
        company_name = account_data.get('company_name', 'Unknown Company')
        workflow.logger.info(f"Starting opportunity workflow for {company_name}")
        
        try:
            # Activity 1: Analyze account with RAG
            workflow.logger.info("Step 1: Analyzing account with RAG")
            analysis_result = await workflow.execute_activity(
                analyze_account_with_rag,
                account_data,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10),
                    maximum_attempts=3,
                    non_retryable_error_types=["ValueError"]
                )
            )
            
            # Activity 2: Post to Slack via Arcade
            workflow.logger.info("Step 2: Posting opportunity brief to Slack")
            slack_result = await workflow.execute_activity(
                post_to_slack,
                analysis_result,
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=5),
                    maximum_attempts=3
                )
            )
            
            # Combine results
            final_result = {
                "workflow_id": workflow.info().workflow_id,
                "account_data": account_data,
                "analysis_result": analysis_result,
                "slack_result": slack_result,
                "status": "completed",
                "company_name": company_name
            }
            
            workflow.logger.info(f"Workflow completed successfully for {company_name}")
            return final_result
            
        except Exception as e:
            workflow.logger.error(f"Workflow failed for {company_name}: {e}")
            
            # Return failure result
            return {
                "workflow_id": workflow.info().workflow_id,
                "account_data": account_data,
                "status": "failed",
                "error": str(e),
                "company_name": company_name
            }


@workflow.defn  
class HealthCheckWorkflow:
    """Simple workflow to test system health."""
    
    @workflow.run
    async def run(self, test_message: str = "Health check") -> Dict[str, Any]:
        """Run health check workflow."""
        
        workflow.logger.info("Running health check workflow")
        
        try:
            # Import here to avoid circular imports
            from activities.slack_poster import send_slack_test
            
            # Test Slack connectivity
            slack_result = await workflow.execute_activity(
                send_slack_test,
                test_message,
                start_to_close_timeout=timedelta(minutes=1),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=5),
                    maximum_attempts=2
                )
            )
            
            return {
                "status": "healthy",
                "slack_test": slack_result,
                "timestamp": workflow.now()
            }
            
        except Exception as e:
            workflow.logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": workflow.now()
            } 