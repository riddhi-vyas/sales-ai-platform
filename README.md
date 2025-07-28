# The Proactive GTM Opportunity Agent (Hunter) 🎯

An autonomous AI agent that proactively identifies high-intent accounts and delivers actionable opportunity briefs to sales teams, transforming raw data into revenue-generating actions.

## 🚀 Quick Demo

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Start Temporal server**: `temporal server start-dev`
3. **Run the agent**: `python main.py`
4. **Watch it work**: Monitor in Datadog dashboard + check Slack for opportunity briefs

## 🏗️ Architecture

```
HockeyStack Data → Temporal Workflow → LlamaIndex RAG → Arcade → Slack
     (Trigger)      (Orchestration)    (Analysis)     (Action)  (Output)
```

### Components
- **Trigger**: Mock HockeyStack data polling for high-intent signals
- **Orchestration**: Temporal workflows for durable, fault-tolerant execution
- **Analysis**: LlamaIndex RAG with sales playbooks knowledge base
- **Action**: Arcade-powered secure Slack integration
- **Observability**: Datadog monitoring and tracing

## 🛠️ Technology Stack

- **Temporal**: Durable workflow orchestration
- **LlamaIndex**: RAG-powered account analysis
- **Arcade**: Secure API integrations
- **Datadog**: System monitoring and observability
- **Claude/Ollama**: LLM for intelligent analysis

## 📁 Project Structure

```
gtm_agent/
├── workflows/          # Temporal workflow definitions
├── activities/         # Individual workflow activities
├── data/              # Mock data and knowledge base
├── config/            # Configuration files
├── utils/             # Helper utilities
└── main.py           # Entry point
```

## 🔧 Setup Instructions

### 1. Environment Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start Temporal development server
temporal server start-dev
```

### 2. Configure Services
- **Arcade**: Set up Slack integration in dashboard
- **Datadog**: Configure monitoring (14-day free trial)
- **LLM**: Either use Claude API or install Ollama locally

### 3. Run the Agent
```bash
python main.py
```

## 🎯 Key Features

- **Event-Driven**: Triggered by high-intent account signals
- **Durable**: Temporal ensures reliable execution even with failures
- **Intelligent**: RAG-powered analysis with sales playbooks
- **Actionable**: Direct Slack integration for immediate team alerts
- **Observable**: Full monitoring and tracing capabilities

## 🎯 Demo Flow

1. Agent detects high-intent account (multiple pricing page visits)
2. Temporal workflow triggers with account data
3. LlamaIndex analyzes account against sales playbooks
4. Opportunity brief generated with actionable insights
5. Arcade posts structured brief to sales team Slack
6. Datadog shows real-time execution metrics

## 📊 Sample Output

**Opportunity Brief for Acme Corp**
- **Intent Score**: 85/100
- **Key Signals**: 5 pricing page visits, 2 executives engaged
- **Recommended Approach**: Enterprise security play
- **Next Action**: Schedule demo with CISO within 48hrs
- **Sales Play**: Use Security ROI calculator, mention SOC2 compliance

## 🚀 Built for Scale

This isn't just a demo - it's enterprise-ready:
- Durable execution handles failures gracefully
- Horizontal scaling with Temporal
- Secure integrations via Arcade
- Production monitoring with Datadog 