"""RAG analyzer activity for intelligent account analysis using LlamaIndex."""

import os
from typing import Dict, Any, List
from datetime import datetime

try:
    from llama_index.core import VectorStoreIndex, Document, ServiceContext
    from llama_index.core.query_engine import RetrieverQueryEngine
    from llama_index.core.retrievers import VectorIndexRetriever
    from llama_index.llms.anthropic import Anthropic
    from llama_index.llms.ollama import Ollama
except ImportError as e:
    print(f"Warning: LlamaIndex not installed properly: {e}")
    print("Run: pip install llama-index llama-index-llms-anthropic llama-index-llms-ollama")

from temporalio import activity
from utils.logger import get_logger
from utils.data_loader import data_loader
from config.settings import settings

logger = get_logger(__name__)


class RAGAnalyzer:
    """RAG-powered analyzer for account intelligence and opportunity briefing."""
    
    def __init__(self):
        self.knowledge_base = None
        self.query_engine = None
        self._initialize_llm()
        self._load_knowledge_base()
    
    def _initialize_llm(self):
        """Initialize the LLM based on configuration."""
        try:
            if settings.anthropic_api_key and not settings.use_local_llm:
                logger.info("Initializing Claude (Anthropic) LLM")
                self.llm = Anthropic(
                    model="claude-3-sonnet-20241022",
                    api_key=settings.anthropic_api_key,
                    max_tokens=4096
                )
            else:
                logger.info("Initializing Ollama local LLM")
                self.llm = Ollama(
                    model="llama3.1:8b",
                    base_url=settings.ollama_base_url,
                    request_timeout=60.0
                )
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            # Fallback to mock responses for demo
            self.llm = None
    
    def _load_knowledge_base(self):
        """Load and index the sales playbooks knowledge base."""
        try:
            knowledge_files = data_loader.load_knowledge_base_files()
            
            if not knowledge_files:
                logger.warning("No knowledge base files found")
                return
            
            # Create documents from knowledge base files
            documents = []
            for filename, content in knowledge_files.items():
                doc = Document(
                    text=content,
                    metadata={"source": filename, "type": "sales_playbook"}
                )
                documents.append(doc)
            
            # Create vector index
            if self.llm:
                service_context = ServiceContext.from_defaults(llm=self.llm)
                self.knowledge_base = VectorStoreIndex.from_documents(
                    documents, 
                    service_context=service_context
                )
            else:
                # Create index without LLM for demo
                self.knowledge_base = VectorStoreIndex.from_documents(documents)
            
            # Create query engine
            retriever = VectorIndexRetriever(
                index=self.knowledge_base,
                similarity_top_k=3
            )
            
            self.query_engine = RetrieverQueryEngine(retriever=retriever)
            
            logger.success(
                "Knowledge base indexed successfully",
                documents_count=len(documents),
                files=list(knowledge_files.keys())
            )
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            self.knowledge_base = None
            self.query_engine = None
    
    def analyze_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze account data and generate opportunity brief."""
        try:
            company_name = account_data.get('company_name', 'Unknown Company')
            industry = account_data.get('industry', 'Unknown Industry')
            intent_score = account_data.get('intent_score', 0)
            intent_signals = account_data.get('intent_signals', [])
            
            logger.info(f"Analyzing account: {company_name}")
            
            # Build context from intent signals
            context = self._build_context(account_data)
            
            # Query knowledge base for relevant sales strategies
            sales_strategy = self._get_sales_strategy(context, industry)
            
            # Generate opportunity brief
            opportunity_brief = self._generate_opportunity_brief(
                account_data, context, sales_strategy
            )
            
            logger.success(f"Analysis completed for {company_name}")
            
            return {
                "account_id": account_data.get('account_id'),
                "company_name": company_name,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "intent_score": intent_score,
                "opportunity_brief": opportunity_brief,
                "recommended_actions": self._get_recommended_actions(account_data, sales_strategy),
                "urgency_level": self._calculate_urgency(intent_signals),
                "sales_strategy": sales_strategy
            }
            
        except Exception as e:
            logger.error(f"Error analyzing account {company_name}: {e}")
            return self._generate_fallback_analysis(account_data)
    
    def _build_context(self, account_data: Dict[str, Any]) -> str:
        """Build context string from account data."""
        context_parts = [
            f"Company: {account_data.get('company_name')}",
            f"Industry: {account_data.get('industry')}",
            f"Employee Count: {account_data.get('employee_count')}",
            f"Revenue: {account_data.get('revenue')}",
            f"Intent Score: {account_data.get('intent_score')}/100"
        ]
        
        # Add intent signals
        intent_signals = account_data.get('intent_signals', [])
        if intent_signals:
            context_parts.append("\nRecent Activities:")
            for signal in intent_signals:
                signal_type = signal.get('type', '').replace('_', ' ').title()
                user_title = signal.get('user_title', 'Unknown Role')
                context_parts.append(f"- {signal_type} by {user_title}")
        
        return "\n".join(context_parts)
    
    def _get_sales_strategy(self, context: str, industry: str) -> Dict[str, Any]:
        """Query knowledge base for relevant sales strategy."""
        if not self.query_engine:
            return self._get_fallback_strategy(industry)
        
        try:
            # Create query based on context
            query = f"""
            Based on this customer profile:
            {context}
            
            What sales strategy should we use? Include:
            1. Best playbook to follow
            2. Key value propositions to emphasize
            3. Recommended next steps
            4. Potential objections to prepare for
            """
            
            response = self.query_engine.query(query)
            
            return {
                "strategy_type": self._determine_strategy_type(industry, context),
                "recommendations": str(response),
                "confidence": 0.85
            }
            
        except Exception as e:
            logger.warning(f"Error querying knowledge base: {e}")
            return self._get_fallback_strategy(industry)
    
    def _determine_strategy_type(self, industry: str, context: str) -> str:
        """Determine which sales strategy type to use."""
        industry_lower = industry.lower()
        context_lower = context.lower()
        
        if 'financial' in industry_lower or 'security' in context_lower:
            return "enterprise_security"
        elif 'saas' in industry_lower or 'startup' in context_lower:
            return "saas_growth"
        elif 'enterprise' in context_lower or 'manufacturing' in industry_lower:
            return "enterprise_digital_transformation"
        else:
            return "general_enterprise"
    
    def _generate_opportunity_brief(self, account_data: Dict[str, Any], 
                                  context: str, sales_strategy: Dict[str, Any]) -> str:
        """Generate structured opportunity brief."""
        company_name = account_data.get('company_name')
        intent_score = account_data.get('intent_score')
        
        # Get key signals summary
        signals_summary = self._summarize_intent_signals(account_data.get('intent_signals', []))
        
        brief = f"""🎯 **OPPORTUNITY BRIEF: {company_name}**

**📊 Intent Analysis**
- Intent Score: {intent_score}/100 ({self._get_intent_label(intent_score)})
- Key Signals: {signals_summary}

**🏢 Company Profile**
- Industry: {account_data.get('industry')}
- Size: {account_data.get('employee_count')} employees
- Revenue: {account_data.get('revenue')}

**🎯 Recommended Approach**
- Strategy Type: {sales_strategy.get('strategy_type', 'general').replace('_', ' ').title()}
- Primary Focus: {self._get_primary_focus(sales_strategy)}

**⚡ Next Actions**
{self._format_next_actions(account_data, sales_strategy)}

**⏰ Urgency Level: {self._calculate_urgency(account_data.get('intent_signals', []))}**
"""
        return brief
    
    def _summarize_intent_signals(self, signals: List[Dict[str, Any]]) -> str:
        """Summarize intent signals into readable format."""
        if not signals:
            return "No recent activity"
        
        signal_counts = {}
        for signal in signals:
            signal_type = signal.get('type', 'unknown').replace('_', ' ').title()
            signal_counts[signal_type] = signal_counts.get(signal_type, 0) + 1
        
        summary_parts = []
        for signal_type, count in signal_counts.items():
            if count > 1:
                summary_parts.append(f"{count}x {signal_type}")
            else:
                summary_parts.append(signal_type)
        
        return ", ".join(summary_parts)
    
    def _get_intent_label(self, score: int) -> str:
        """Get human-readable intent label."""
        if score >= 90:
            return "🔥 VERY HIGH"
        elif score >= 80:
            return "🚨 HIGH"
        elif score >= 70:
            return "📈 MEDIUM-HIGH"
        elif score >= 60:
            return "📊 MEDIUM"
        else:
            return "📋 LOW"
    
    def _get_primary_focus(self, sales_strategy: Dict[str, Any]) -> str:
        """Extract primary focus from sales strategy."""
        strategy_type = sales_strategy.get('strategy_type', '')
        
        focus_map = {
            'enterprise_security': 'Compliance & Security Operations',
            'saas_growth': 'Scaling & Engineering Efficiency',
            'enterprise_digital_transformation': 'Digital Transformation & ROI',
            'general_enterprise': 'Operational Excellence'
        }
        
        return focus_map.get(strategy_type, 'Custom Enterprise Solution')
    
    def _format_next_actions(self, account_data: Dict[str, Any], 
                           sales_strategy: Dict[str, Any]) -> str:
        """Format recommended next actions."""
        actions = [
            "1. 📞 Schedule discovery call within 24 hours",
            "2. 📧 Send relevant case study and ROI calculator",
            "3. 🎯 Prepare industry-specific demo scenario"
        ]
        
        # Add strategy-specific actions
        strategy_type = sales_strategy.get('strategy_type', '')
        if strategy_type == 'enterprise_security':
            actions.append("4. 🔒 Include compliance gap assessment offer")
        elif strategy_type == 'saas_growth':
            actions.append("4. ⚡ Offer 14-day free trial setup")
        elif strategy_type == 'enterprise_digital_transformation':
            actions.append("4. 📊 Schedule executive briefing session")
        
        return "\n".join(actions)
    
    def _calculate_urgency(self, intent_signals: List[Dict[str, Any]]) -> str:
        """Calculate urgency level based on intent signals."""
        if not intent_signals:
            return "LOW"
        
        recent_signals = len([s for s in intent_signals if 'pricing' in s.get('type', '')])
        demo_requests = len([s for s in intent_signals if 'demo' in s.get('type', '')])
        
        if demo_requests > 0 or recent_signals >= 2:
            return "🔴 URGENT (Contact within 24hrs)"
        elif recent_signals > 0:
            return "🟡 HIGH (Contact within 48hrs)"
        else:
            return "🟢 MEDIUM (Contact within 1 week)"
    
    def _get_recommended_actions(self, account_data: Dict[str, Any], 
                               sales_strategy: Dict[str, Any]) -> List[str]:
        """Get structured list of recommended actions."""
        return [
            "Schedule discovery call",
            "Send relevant case studies",
            "Prepare demo environment",
            "Connect with industry references",
            "Develop custom ROI projection"
        ]
    
    def _get_fallback_strategy(self, industry: str) -> Dict[str, Any]:
        """Provide fallback strategy when RAG is not available."""
        return {
            "strategy_type": "general_enterprise",
            "recommendations": f"Follow standard enterprise approach for {industry} industry",
            "confidence": 0.5
        }
    
    def _generate_fallback_analysis(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback analysis when LLM is not available."""
        company_name = account_data.get('company_name', 'Unknown Company')
        
        return {
            "account_id": account_data.get('account_id'),
            "company_name": company_name,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "intent_score": account_data.get('intent_score', 0),
            "opportunity_brief": f"High-intent account {company_name} requires immediate follow-up",
            "recommended_actions": ["Contact within 24 hours", "Send discovery meeting invite"],
            "urgency_level": "HIGH",
            "sales_strategy": {"strategy_type": "general_enterprise", "confidence": 0.5}
        }


# Activity functions for Temporal
@activity.defn
async def analyze_account_with_rag(account_data: Dict[str, Any]) -> Dict[str, Any]:
    """Temporal activity: Analyze account using RAG."""
    analyzer = RAGAnalyzer()
    return analyzer.analyze_account(account_data) 