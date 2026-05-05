# Education Insights 🎓

An AI-powered analytics platform that bridges the gap between raw government data and actionable public policy decisions.

## 🚀 Project Overview

This project demonstrates an **Agentic 2-Agent (A2A)** architecture built with LangGraph and Google Vertex AI. It transforms static CSV datasets (e.g., school funding, poverty rates) into an interactive, intelligent dashboard that can answer complex policy questions in natural language.

### Key Features

- **Agentic Data Analysis**: Utilizes a **Data Agent** to interpret natural language, write complex BigQuery SQL queries, and fetch live data from Google Cloud.
- **Intelligent Recommendation**: Employs an **Insights Agent** to synthesize raw database results into human-readable recommendations for policymakers.
- **Interactive Dashboard**: Powered by **Streamlit**, providing visualizations and filterable views of the educational data.
- **Live Data Pipeline**: Configured to connect to a custom Google BigQuery dataset, ensuring real-time data processing.

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.9+
- Google Cloud Account
- BigQuery Project with a dataset (e.g., `hackathon_education`)

### 1. Environment Setup
Create and activate a Python virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
Install the necessary Python packages:
```bash
pip install -r requirements.txt
```

### 3. Google Cloud Configuration
Ensure your environment is authenticated with Google Cloud:
```bash
gcloud auth application-default login
```
Verify your Project ID in the `.env` file (or environment variables).

## 📊 Running the Application

Start the Streamlit dashboard:
```bash
streamlit run apps/education_dashboard/streamlit_ui.py
```

Access the application at the local URL provided (usually `http://localhost:8501`).

## ⚙️ Architecture

The system uses a **LangGraph State Graph** to manage the flow of information between agents.

1.  **Root Agent**: Interprets the initial user query and assigns the task.
2.  **Data Agent**: Connects to BigQuery, translates the query into SQL, and executes it against the live database.
3.  **Insights Agent**: Consumes the raw SQL results and generates professional policy recommendations.

### Database Connection
The Data Agent uses `SQLDatabase.from_uri` with a `bigquery://` connection string, requiring the `sqlalchemy-bigquery` package.

## 📂 Project Structure
```
EduInsights/
├── .venv/                # Virtual environment (ignored)
├── apps/                  # Streamlit UI and Visualizations
├── agents/                # AI Agents and LangGraph logic
│   └── education_analyst/ # Core A2A pipeline
├── data/                  # Source CSV data files
└── bigquery_setup.py    # Script to upload data to BigQuery
```

## 🔌 Data Setup

If you need to upload your dataset to BigQuery:
1.  Edit `bigquery_setup.py` with your Project ID and desired Dataset ID.
2.  Run:
    ```bash
    python bigquery_setup.py
    ```

This will create the dataset and table in BigQuery, making the data live for the agents.
