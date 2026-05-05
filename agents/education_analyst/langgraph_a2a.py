import os
from langchain_google_vertexai import ChatVertexAI
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from dotenv import load_dotenv

load_dotenv()

# --- 1. A2A State Schema ---
# This is the "Shared Memory" that the 3 agents pass to each other
class AgentState(TypedDict):
    user_query: str
    sql_query: str
    raw_data: str
    final_insight: str


# --- 2. Database Connection Phase ---
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = "hackathon_education"

# We connect Langchain directly to Google's Live Cloud Servers!
# This requires sqlalchemy-bigquery which we just installed.
print("☁️ Connecting to Google Cloud BigQuery Backend...")
db = SQLDatabase.from_uri(f"bigquery://{PROJECT_ID}/{DATASET_ID}")
execute_query_tool = QuerySQLDataBaseTool(db=db)

# --- 3. Initialize The Master LLM Brain ---
llm = ChatVertexAI(
    model_name="gemini-2.5-flash", 
    temperature=0,
    project=PROJECT_ID,
    location="us-central1"
)


# --- 4. Define our 3 Hackathon Agents ---

def root_agent(state: AgentState):
    """The Orchestrator. Interprets the original user intent."""
    print("\n🟢 [Root Agent]: Interpreting intent & assigning task to Data Agent...")
    # In a more advanced architecture, this agent would use an IF/ELSE router
    # to decide *which* specific database or agent to delegate to.
    return {"user_query": state["user_query"]}

def data_agent(state: AgentState):
    """The SQL Engineer. Translates English to BigQuery SQL and executes the Tool."""
    print("🔵 [Data Agent]: Translating thought to BigQuery SQL...")
    
    # 🌟 NEW: Physically grab the live Database Schema from Google Cloud!
    schema = db.get_table_info(table_names=["school_demographics"])
    
    # We explicitly force the LLM to format for BigQuery exclusively
    prompt = f"""You are a Google BigQuery SQL Expert. 
    Write a SQL query for the table `school_demographics` based on this analytical request: {state['user_query']}
    
    CRITICAL DATABASE SCHEMA TO USE:
    {schema}
    
    RULES:
    1. NEVER wrap the output in markdown blockquotes like ```sql. Provide strictly physical text.
    2. Only query the `school_demographics` table using the EXACT column names provided in the schema above.
    """
    
    # Generate the SQL
    sql_query = llm.invoke(prompt).content.strip()
    # Execute the SQL physically in the cloud!
    print(f"   -> Executing SQL Code against Cloud: {sql_query}")
    raw_results = execute_query_tool.invoke(sql_query)
    
    return {"sql_query": sql_query, "raw_data": str(raw_results)}

def insights_agent(state: AgentState):
    """The Public Policy Advisor. Translates raw JSON back to actionable Human Intelligence."""
    print("🟣 [Insights Agent]: Formulating analytical recommendation from raw data payload...")
    
    prompt = f"""You are a highly intelligent Public Policy Advisor.
    User's Original Request: {state['user_query']}
    Raw SQL Response Payload from Data Agent: {state['raw_data']}
    
    Synthesize this raw data into a professional, actionable insight for policymakers or parents.
    Highlight any disparities or specific schools that stand out in the data.
    """
    
    insight = llm.invoke(prompt).content
    return {"final_insight": insight}


# --- 5. Compile the LangGraph A2A Architecture ---
graph_builder = StateGraph(AgentState)

graph_builder.add_node("Root", root_agent)
graph_builder.add_node("Data", data_agent)
graph_builder.add_node("Insights", insights_agent)

# Hardcode the flow of communication
graph_builder.add_edge(START, "Root")
graph_builder.add_edge("Root", "Data")
graph_builder.add_edge("Data", "Insights")
graph_builder.add_edge("Insights", END)

A2A_System = graph_builder.compile()


# --- 6. Expose the Flow for Streamlit UI ---
def run_a2a_pipeline(query: str):
    """Modular function to allow the web frontend to instantly trigger the A2A Engine"""
    return A2A_System.invoke({"user_query": query})


# --- 7. Execute the Project (Local Testing) ---
if __name__ == "__main__":
    print("\n=======================================================")
    print("🎓 EDUCATION INSIGHTS: A2A RECOMMENDER ENGINE")
    print("=======================================================\n")
    
    # This precisely simulates the first bullet point from the Hackathon rules!
    test_query = "Identify the top 5 schools with the highest poverty rate and print their total enrollment to prioritize grant funding."
    print(f"USER: {test_query}")
    
    # Kick off the Agent execution loop!
    result = run_a2a_pipeline(test_query)
    
    print("\n=======================================================")
    print("💡 FINAL RECOMMENDATION (FROM INSIGHTS AGENT)")
    print("=======================================================\n")
    print(result["final_insight"])
