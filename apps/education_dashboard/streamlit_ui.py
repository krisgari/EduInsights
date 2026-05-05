import streamlit as st
import ast
import pandas as pd
import sys
import os

# Append the root workspace so we can access our new architecture modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from agents.education_analyst.langgraph_a2a import run_a2a_pipeline

#to invoke the vertex ai agents, uncomment the following line
#from hackathon_vertex_agents import run_vertex_app as run_a2a_pipeline


st.set_page_config(page_title="Education Insights AI", page_icon="🎓", layout="wide")

# --- UI Header ---
st.title("🎓 Education Insights Recommender")
st.markdown("""
Welcome to the Multi-Agent **Education Architecture**. 
* **Root Agent:** Identifies intent.
* **Data Agent:** Dynamically writes Google BigQuery SQL.
* **Insights Agent:** Synthesizes policy recommendations from raw math.
""")
st.divider()

# --- Chatbot Interaction ---
query = st.text_input("Enter a Policy Ask:", "Find the top 5 schools with the highest `poverty_1` rate and display their total enrollment.")

if st.button("Generate Policy Insight", type="primary"):
    with st.spinner("🤖 Multi-Agent Orchestration Protocol Executing..."):
        # 1. Trigger the LangGraph A2A Python script!
        result = run_a2a_pipeline(query)
        
        # 2. Layout the Results Beautifully
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("🔵 The Data Agent")
            st.markdown("*Generated Google Cloud SQL:*")
            st.code(result["sql_query"], language="sql")
        
        with col2:
            st.subheader("🟣 The Insights Agent")
            st.success(result["final_insight"])

        st.divider()
        
        # 3. THE "WOW" FACTOR: Autonomous Data Visualization
        st.subheader("📊 Autonomous Data Visualization")
        try:
            # Langchain's SQL Tool returns raw strings that look like arrays of tuples: "[('School', 80), ...]"
            # We use Abstract Syntax Trees to convert the text back into physical Python lists!
            raw_tuples = ast.literal_eval(result["raw_data"])
            
            if isinstance(raw_tuples, list) and len(raw_tuples) > 0:
                # Convert list to Pandas DataFrame
                df = pd.DataFrame(raw_tuples)
                
                # Assuming the Data Agent pulled the School Name as the first column (0),
                # we set the School Name as our Chart X-Axis!
                df.set_index(0, inplace=True)
                
                # If there are multiple numerical columns, Streamlit automatically graphs all of them side-by-side
                st.bar_chart(df, height=400)
            else:
                st.info(f"Raw Database Output: {result['raw_data']}")
        except Exception as e:
            # If the SQL failed (e.g. invalid column name), gracefully display the SQL error message
            st.error(f"Cannot visualize data. Database Output: {result['raw_data']}")
