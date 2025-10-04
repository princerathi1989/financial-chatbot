# Add New Financial Agent

Add a new specialized financial agent to the multi-agent chatbot system using LangChain/LangGraph patterns.

## Steps
1. **Define Financial Agent Schema**
   - Add new agent type to `AgentType` enum in `models/schemas.py`
   - Create agent-specific request/response models for financial data
   - Update API documentation with financial use cases

2. **Implement LangChain Agent**
   - Create new agent file in `agents/` directory
   - Use LangChain tools and chains for financial operations
   - Implement proper error handling and logging
   - Add financial data validation

3. **Update LangGraph Workflow**
   - Add agent to LangGraph workflow if using multi-agent orchestration
   - Define agent routing logic for financial queries
   - Implement agent communication patterns
   - Add workflow state management

4. **Update Main Chatbot**
   - Add agent to `MultiAgentChatbot.agents` dictionary
   - Update `determine_agent_type()` method with financial keywords
   - Add processing logic in `process_chat_message()`
   - Integrate with LangSmith for tracing

5. **Financial Agent Types**
   - **Risk Analysis Agent**: Analyze financial risks and compliance
   - **Portfolio Agent**: Portfolio analysis and optimization
   - **Market Research Agent**: Market analysis and research
   - **Regulatory Agent**: Compliance and regulatory reporting
   - **Forecasting Agent**: Financial forecasting and modeling

6. **Testing**
   - Create unit tests for financial agent functionality
   - Test integration with LangChain/LangGraph
   - Verify financial data accuracy
   - Test error handling for financial edge cases

## LangChain Integration Template
```python
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class FinancialAgent:
    def __init__(self, config: Settings):
        self.config = config
        self.llm = ChatOpenAI(model=config.openai_model)
        self.tools = self._create_financial_tools()
        self.agent = self._create_agent()
    
    def _create_financial_tools(self):
        """Create LangChain tools for financial operations."""
        return [
            Tool(
                name="financial_calculator",
                description="Calculate financial ratios and metrics",
                func=self._calculate_financial_metrics
            ),
            Tool(
                name="risk_analyzer",
                description="Analyze financial risks",
                func=self._analyze_risks
            )
        ]
    
    def _create_agent(self):
        """Create LangChain agent with financial tools."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a financial expert assistant..."),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        return create_openai_tools_agent(self.llm, self.tools, prompt)
```
