#!/usr/bin/env python3
"""
The Proactive GTM Opportunity Agent (Hunter)

Main entry point for the autonomous AI agent that identifies high-intent accounts
and delivers actionable opportunity briefs to sales teams.
"""

import asyncio
import signal
import sys
from datetime import datetime, timedelta
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Temporal imports
from temporalio.client import Client, WorkflowFailureError
from temporalio.worker import Worker

# Local imports
from config.settings import settings
from utils.logger import get_logger
from utils.data_loader import data_loader
from workflows.opportunity_workflow import OpportunityProcessingWorkflow, HealthCheckWorkflow
from activities.rag_analyzer import analyze_account_with_rag
from activities.slack_poster import post_to_slack, send_slack_test

# Initialize
logger = get_logger(__name__)
console = Console()
app = typer.Typer(help="The Proactive GTM Opportunity Agent")

# Global state
running = True
temporal_client: Optional[Client] = None


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global running
    running = False
    console.print("\n[yellow]Shutting down gracefully...[/yellow]")


class GTMAgent:
    """Main agent orchestrator."""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.worker: Optional[Worker] = None
        
    async def initialize(self):
        """Initialize Temporal client and worker."""
        try:
            # Connect to Temporal
            self.client = await Client.connect(settings.temporal_host)
            logger.success(f"Connected to Temporal at {settings.temporal_host}")
            
            # Create worker
            self.worker = Worker(
                self.client,
                task_queue="gtm-opportunity-queue",
                workflows=[OpportunityProcessingWorkflow, HealthCheckWorkflow],
                activities=[analyze_account_with_rag, post_to_slack, send_slack_test]
            )
            
            logger.success("Temporal worker created successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Temporal: {e}")
            raise
    
    async def start_worker(self):
        """Start the Temporal worker."""
        if not self.worker:
            await self.initialize()
        
        logger.info("Starting Temporal worker...")
        await self.worker.run()
    
    async def process_high_intent_accounts(self):
        """Main loop to process high-intent accounts."""
        if not self.client:
            await self.initialize()
        
        logger.info(f"Starting account monitoring (checking every {settings.poll_interval_seconds}s)")
        
        processed_count = 0
        
        while running:
            try:
                # Get high-intent accounts
                high_intent_accounts = data_loader.get_high_intent_accounts()
                
                if not high_intent_accounts:
                    logger.info("No new high-intent accounts found")
                    await asyncio.sleep(settings.poll_interval_seconds)
                    continue
                
                # Process each account
                for account in high_intent_accounts:
                    if not running:
                        break
                    
                    account_id = account.get('account_id')
                    company_name = account.get('company_name')
                    
                    logger.info(f"Processing high-intent account: {company_name}")
                    
                    try:
                        # Start workflow
                        workflow_id = f"opportunity-{account_id}-{int(datetime.now().timestamp())}"
                        
                        handle = await self.client.start_workflow(
                            OpportunityProcessingWorkflow.run,
                            account,
                            id=workflow_id,
                            task_queue="gtm-opportunity-queue",
                            execution_timeout=timedelta(minutes=10)
                        )
                        
                        logger.info(f"Started workflow {workflow_id} for {company_name}")
                        
                        # Wait for workflow to complete
                        result = await handle.result()
                        
                        if result.get('status') == 'completed':
                            logger.success(f"Successfully processed {company_name}")
                            data_loader.mark_account_processed(account_id)
                            processed_count += 1
                        else:
                            logger.error(f"Workflow failed for {company_name}: {result.get('error')}")
                    
                    except WorkflowFailureError as e:
                        logger.error(f"Workflow execution failed for {company_name}: {e}")
                    except Exception as e:
                        logger.error(f"Error processing {company_name}: {e}")
                
                # Brief pause before next check
                await asyncio.sleep(settings.poll_interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(settings.poll_interval_seconds)
        
        logger.info(f"Agent stopped. Processed {processed_count} opportunities.")
    
    async def run_health_check(self):
        """Run system health check."""
        if not self.client:
            await self.initialize()
        
        logger.info("Running system health check...")
        
        try:
            workflow_id = f"health-check-{int(datetime.now().timestamp())}"
            
            handle = await self.client.start_workflow(
                HealthCheckWorkflow.run,
                "System health check",
                id=workflow_id,
                task_queue="gtm-opportunity-queue",
                execution_timeout=timedelta(minutes=2)
            )
            
            result = await handle.result()
            
            if result.get('status') == 'healthy':
                logger.success("✅ System health check passed")
                return True
            else:
                logger.error(f"❌ System health check failed: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return False


def display_banner():
    """Display startup banner."""
    banner = Panel.fit(
        "[bold blue]🎯 The Proactive GTM Opportunity Agent (Hunter)[/bold blue]\n\n"
        "[dim]Autonomous AI agent for sales opportunity intelligence[/dim]\n"
        "[dim]Powered by Temporal + LlamaIndex + Arcade + Datadog[/dim]",
        border_style="blue"
    )
    console.print(banner)


def display_status():
    """Display current configuration status."""
    table = Table(title="Configuration Status", show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Details", style="dim")
    
    # Check configurations
    configs = [
        ("Temporal", "✅ Configured" if settings.temporal_host else "❌ Missing", settings.temporal_host),
        ("LLM", "✅ Claude" if settings.anthropic_api_key else "🔧 Ollama Local", "API Key Set" if settings.anthropic_api_key else "localhost:11434"),
        ("Arcade", "✅ Configured" if settings.arcade_api_key else "🔧 Mock Mode", "API Key Set" if settings.arcade_api_key else "Development Mode"),
        ("Datadog", "✅ Configured" if settings.dd_api_key else "⚠️ Optional", "Monitoring Enabled" if settings.dd_api_key else "Disabled"),
        ("Slack Channel", "✅ Set", settings.slack_channel),
        ("Intent Threshold", "✅ Set", f"{settings.high_intent_threshold}/100"),
    ]
    
    for component, status, details in configs:
        table.add_row(component, status, details)
    
    console.print(table)


@app.command()
def run(
    worker_only: bool = typer.Option(False, "--worker-only", help="Run only the Temporal worker"),
    health_check: bool = typer.Option(False, "--health-check", help="Run health check and exit")
):
    """Run the GTM Opportunity Agent."""
    
    display_banner()
    display_status()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    agent = GTMAgent()
    
    async def main():
        if health_check:
            success = await agent.run_health_check()
            sys.exit(0 if success else 1)
        
        if worker_only:
            logger.info("Starting in worker-only mode")
            await agent.start_worker()
        else:
            logger.info("Starting full agent (worker + monitor)")
            # Run worker and account processor concurrently
            await asyncio.gather(
                agent.start_worker(),
                agent.process_high_intent_accounts()
            )
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Agent stopped by user[/yellow]")
    except Exception as e:
        logger.error(f"Agent crashed: {e}")
        sys.exit(1)


@app.command()
def test_slack():
    """Test Slack integration."""
    
    async def test():
        agent = GTMAgent()
        await agent.run_health_check()
    
    asyncio.run(test())


@app.command()
def show_accounts():
    """Show current high-intent accounts."""
    
    accounts = data_loader.get_high_intent_accounts()
    
    if not accounts:
        console.print("[yellow]No high-intent accounts found[/yellow]")
        return
    
    table = Table(title="High-Intent Accounts", show_header=True, header_style="bold magenta")
    table.add_column("Company", style="cyan", no_wrap=True)
    table.add_column("Industry", style="green")
    table.add_column("Intent Score", justify="right", style="red")
    table.add_column("Signals", style="dim")
    table.add_column("Processed", justify="center")
    
    for account in accounts:
        signals = len(account.get('intent_signals', []))
        processed = "✅" if account.get('processed') else "⏳"
        
        table.add_row(
            account.get('company_name', 'Unknown'),
            account.get('industry', 'Unknown'),
            f"{account.get('intent_score', 0)}/100",
            f"{signals} signals",
            processed
        )
    
    console.print(table)


@app.command()
def reset_data():
    """Reset all accounts to unprocessed state."""
    
    accounts = data_loader.load_mock_accounts()
    for account in accounts:
        account['processed'] = False
    
    import json
    with open(settings.mock_data_path, 'w') as f:
        json.dump(accounts, f, indent=2)
    
    console.print("[green]✅ All accounts reset to unprocessed state[/green]")


if __name__ == "__main__":
    app() 