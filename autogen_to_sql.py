from typing import Dict, List
import autogen
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.sql_agent import SqlAssistantAgent
import pandas as pd
import plotly.express as px
import sqlite3

# Configuration for the database
DB_PATH = "traffic_violations.db"

# SQL Agent configuration
sql_config = {
    "connection_string": f"sqlite:///{DB_PATH}",
    "tables": {
        "traffic_violations": """
            CREATE TABLE IF NOT EXISTS traffic_violations (
                id INTEGER PRIMARY KEY,
                violation_time DATETIME,
                district TEXT,
                violation_type TEXT,
                vehicle_type TEXT,
                plate_number TEXT
            )
        """
    }
}

# Configure the agents
config_list = [
    {
        "model": "gpt-4",
        "api_key": "your_openai_api_key_here"
    }
]

# Create the assistant configurations
llm_config = {
    "config_list": config_list,
    "temperature": 0,
    "timeout": 120,
}

def create_agents():
    # Create the SQL Assistant Agent
    sql_agent = SqlAssistantAgent(
        name="sql_expert",
        system_message="""You are an expert SQL analyst. Your role is to:
1. Convert natural language questions about traffic violations into SQL queries
2. Execute these queries against the traffic violations database
3. Return the results in a clear, understandable format
4. Suggest visualizations when appropriate""",
        llm_config=llm_config,
        sql_config=sql_config,
    )

    # Create the Data Visualization Agent
    viz_agent = RetrieveAssistantAgent(
        name="viz_expert",
        system_message="""You are a data visualization expert. Your role is to:
1. Create appropriate visualizations for the SQL query results
2. Explain trends and patterns in the data
3. Provide clear insights about the traffic violations""",
        llm_config=llm_config,
    )

    return sql_agent, viz_agent

class TrafficViolationAnalyzer:
    def __init__(self):
        self.sql_agent, self.viz_agent = create_agents()
        self.conn = sqlite3.connect(DB_PATH)
        
    async def process_query(self, user_query: str) -> Dict:
        try:
            # Get SQL query from SQL agent
            sql_response = await self.sql_agent.generate_sql(user_query)
            sql_query = sql_response["query"]
            
            # Execute the query
            df = pd.read_sql_query(sql_query, self.conn)
            
            # Create visualization if appropriate
            viz = None
            if len(df) > 0:
                if "district" in df.columns:
                    viz = px.bar(df, x="district", y=df.columns[1], 
                               title=f"Traffic Violations by District")
                elif "violation_type" in df.columns:
                    viz = px.pie(df, names="violation_type", values=df.columns[1],
                               title=f"Distribution of Violation Types")
                
            # Get insights from visualization agent
            insights = await self.viz_agent.generate_insights(df.to_dict(), viz)
            
            return {
                "sql_query": sql_query,
                "data": df.to_dict(),
                "visualization": viz,
                "insights": insights
            }
            
        except Exception as e:
            return {
                "error": str(e)
            }

# Example usage
def main():
    analyzer = TrafficViolationAnalyzer()
    
    # Example query
    query = "How many cars in Baiyun District, Guangzhou ran a red light?"
    result = analyzer.process_query(query)
    
    print(f"Query: {query}")
    print(f"\nSQL Query Generated: {result['sql_query']}")
    print(f"\nResults: {result['data']}")
    if result.get('visualization'):
        print("\nVisualization has been created")
    print(f"\nInsights: {result['insights']}")

if __name__ == "__main__":
    main()
