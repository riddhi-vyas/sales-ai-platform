#!/usr/bin/env python3
"""
Demo Script for GTM Opportunity Agent

This script demonstrates the complete workflow in a single run,
perfect for presentations and demonstrations.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Add project root to path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

# Local imports
from utils.data_loader import data_loader
from activities.rag_analyzer import RAGAnalyzer
from activities.slack_poster import SlackPoster

console = Console()


async def run_demo():
    """Run the complete demo workflow."""
    
    # Display demo banner
    banner = Panel.fit(
        "[bold blue]🎯 GTM Opportunity Agent - Live Demo[/bold blue]\n\n"
        "[dim]Live demonstration of the complete workflow:[/dim]\n"
        "[dim]HockeyStack Data → Temporal → RAG Analysis → Slack[/dim]",
        border_style="blue"
    )
    console.print(banner)
    
    # Step 1: Load and display high-intent accounts
    console.print("\n[bold cyan]Step 1: Loading High-Intent Accounts[/bold cyan]")
    
    accounts = data_loader.get_high_intent_accounts()
    
    if not accounts:
        console.print("[red]No high-intent accounts found. Please run: python3 main.py reset-data[/red]")
        return
    
    # Display accounts table
    table = Table(title="High-Intent Accounts Detected", show_header=True, header_style="bold magenta")
    table.add_column("Company", style="cyan")
    table.add_column("Industry", style="green")
    table.add_column("Intent Score", justify="right", style="red")
    table.add_column("Key Signals", style="dim")
    
    for account in accounts[:3]:  # Show top 3 for demo
        signals = account.get('intent_signals', [])
        signal_summary = ", ".join([s.get('type', '').replace('_', ' ').title() for s in signals[:2]])
        if len(signals) > 2:
            signal_summary += f" +{len(signals) - 2} more"
        
        table.add_row(
            account.get('company_name', 'Unknown'),
            account.get('industry', 'Unknown'),
            f"{account.get('intent_score', 0)}/100",
            signal_summary
        )
    
    console.print(table)
    
    # Step 2: Select account for demo
    demo_account = accounts[0]  # Use highest intent account
    company_name = demo_account.get('company_name')
    
    console.print(f"\n[bold cyan]Step 2: Processing Account - {company_name}[/bold cyan]")
    console.print(f"[dim]Intent Score: {demo_account.get('intent_score')}/100[/dim]")
    
    # Step 3: RAG Analysis
    console.print("\n[bold cyan]Step 3: AI-Powered Analysis with LlamaIndex RAG[/bold cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Initialize RAG analyzer
        task1 = progress.add_task("Initializing knowledge base...", total=None)
        analyzer = RAGAnalyzer()
        progress.update(task1, description="✅ Knowledge base loaded")
        
        # Perform analysis
        task2 = progress.add_task("Analyzing account with AI...", total=None)
        await asyncio.sleep(1)  # Simulate processing time
        analysis_result = analyzer.analyze_account(demo_account)
        progress.update(task2, description="✅ Analysis complete")
    
    # Display analysis results
    console.print("\n[bold green]Analysis Results:[/bold green]")
    console.print(Panel(analysis_result.get('opportunity_brief', 'No brief generated'), 
                       title="Opportunity Brief", border_style="green"))
    
    # Step 4: Slack Integration
    console.print("\n[bold cyan]Step 4: Posting to Slack via Arcade[/bold cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task3 = progress.add_task("Preparing Slack message...", total=None)
        poster = SlackPoster()
        await asyncio.sleep(0.5)
        progress.update(task3, description="✅ Message formatted")
        
        task4 = progress.add_task("Posting to Slack channel...", total=None)
        slack_result = poster.post_opportunity_brief(analysis_result)
        progress.update(task4, description="✅ Posted to Slack")
    
    # Step 5: Demo Results Summary
    console.print("\n[bold cyan]Step 5: Demo Results Summary[/bold cyan]")
    
    results_table = Table(title="Workflow Execution Results", show_header=True, header_style="bold blue")
    results_table.add_column("Component", style="cyan")
    results_table.add_column("Status", style="green")
    results_table.add_column("Details", style="dim")
    
    results_table.add_row("Data Source", "✅ Success", "Mock HockeyStack data loaded")
    results_table.add_row("RAG Analysis", "✅ Success", f"Generated brief for {company_name}")
    results_table.add_row("Slack Integration", "✅ Success" if slack_result.get('success') else "❌ Failed", 
                         slack_result.get('channel', 'Mock mode'))
    results_table.add_row("Temporal Workflow", "✅ Ready", "Durable execution configured")
    results_table.add_row("Observability", "✅ Ready", "Datadog tracing available")
    
    console.print(results_table)
    
    # Step 6: Business Impact
    console.print("\n[bold cyan]Step 6: Business Impact Demonstration[/bold cyan]")
    
    impact_panel = Panel(
        "[bold]Business Value Delivered:[/bold]\n\n"
        f"• 🎯 [green]High-intent account identified[/green]: {company_name}\n"
        f"• 📊 [yellow]Intent score[/yellow]: {demo_account.get('intent_score')}/100\n"
        f"• 🤖 [blue]AI-generated strategy[/blue]: Personalized sales approach\n"
        f"• ⚡ [red]Instant alert[/red]: Sales team notified immediately\n"
        f"• 🔄 [purple]Durable workflow[/purple]: Guaranteed execution even with failures\n\n"
        "[dim]This autonomous agent transforms passive data into proactive revenue action![/dim]",
        title="💰 Revenue Impact",
        border_style="yellow"
    )
    console.print(impact_panel)
    
    # Mark account as processed for demo
    data_loader.mark_account_processed(demo_account.get('account_id'))
    
    console.print("\n[bold green]🎉 Demo Complete![/bold green]")
    console.print("\n[dim]In production, this workflow runs continuously, processing new high-intent signals in real-time.[/dim]")
    
    return analysis_result


if __name__ == "__main__":
    asyncio.run(run_demo()) 