import os
from dotenv import load_dotenv

load_dotenv()
import vertexai
from vertexai.preview import reasoning_engine
from google.cloud import bigquery

# Initialize Google Cloud global state (required for Vertex AI SDK)
vertexai.init(project=os.getenv("GCP_PROJECT_ID"), location="us-central1")

# ==========================================
# 1. DEFINE NATIVE VERTEX AI TOOLS
# ==========================================
def execute_bigquery_sql(sql_query: str) -> str:
    """
    Executes a Google Standard SQL query against the BigQuery database and returns the raw JSON results.
    This effectively replaces the LangChain SQLDatabase toolkit natively.
    """
    print(f"\n[🔧 NATIVE TOOL TRIGGERED] Executing BigQuery SQL:\n{sql_query}\n")
    client = bigquery.Client(project=os.getenv("GCP_PROJECT_ID"))
    try:
        query_job = client.query(sql_query)
        results = query_job.result()
        
        # Convert physical row results tightly to a string to pass back to the LLM context limits
        output = [dict(row) for row in results]
        
        print(f"[✅ TOOL SUCCESS] Retrieved {len(output)} rows.")
        return str(output)
        
    except Exception as e:
        print(f"[❌ TOOL FAILED] BigQuery Error: {e}")
        return f"Error executing SQL: {e}. Please rewrite the SQL and try again."


# ==========================================
# 2. PROVISION THE VERTEX AI REASONING ENGINE
# ==========================================
# Unlike LangGraph, the native Vertex AI 'Reasoning Engine' automatically handles 
# complex planning, task isolation, error-correction, and tool routing internally behind the scenes!

SYSTEM_PROMPT = f"""You are a master Google Cloud Data Engineer and Public Policy Analyst for a Hackathon.
Your goal is to answer questions about school demographic data by dynamically querying a live Google BigQuery database.

DATABASE SCHEMA:
- Absolute Table ID: `{os.getenv("GCP_PROJECT_ID")}.hackathon_db.school_demographics`
- Verified Columns: `School_Name` (string), `poverty_1` (numeric/float), `enrollment_1` (numeric/int).

INSTRUCTIONS FOR EXECUTION:
1. Translate the user's natural language question into exact Google Standard SQL.
2. Ensure you ONLY query the verified columns provided above.
3. Automatically execute the `execute_bigquery_sql` function tool.
4. Wait for the tool to return the raw JSON numbers string.
5. If the tool fails (returns an Error), read the error message, correct your SQL, and try the tool again!
6. Once you get the raw numbers, synthesize them into a beautifully formatted, professional Public Policy recommendation summarizing your findings. Do not show the raw SQL in the final output.
"""

print("\n🚀 Booting up Vertex AI Native Reasoning Engine...")

# Build the native Agent Framework
education_vertex_agent = reasoning_engine.ReasoningEngine(
    model="gemini-2.5-flash",
    tools=[execute_bigquery_sql],
    system_instruction=SYSTEM_PROMPT
)


# ==========================================
# 3. EXECUTION PROTOCOL
# ==========================================
def run_vertex_app(query: str):
    """Exposes the agent execution for terminal testing or Streamlit integration."""
    print(f"\n=======================================================")
    print(f"USER DEMAND: {query}")
    print(f"=======================================================\n")
    
    # Trigger the autonomous agent Reasoning Loop
    # The agent will independently route to the tool, wait for the SQL response, and generate the final answer.
    response = education_vertex_agent.query(input=query)
    
    print("\n=======================================================")
    print("💡 FINAL RECOMMENDATION (FROM VERTEX REASONING ENGINE)")
    print("=======================================================\n")
    
    # Provide the raw string natively
    if isinstance(response, dict) and "output" in response:
        print(response["output"])
        return response["output"]
    else:
        print(response)
        return response


if __name__ == "__main__":
    # Test Payload
    test_query = "Find the top 5 schools with the highest poverty rate and display their total enrollment to help prioritize state funding."
    run_vertex_app(test_query)
