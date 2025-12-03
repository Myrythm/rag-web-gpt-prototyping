import os
from langsmith import Client
from backend.utils.config import settings

def setup_langsmith():
    """Ensure environment variables are set for LangChain auto-tracing"""
    if settings.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = settings.LANGCHAIN_TRACING_V2
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
        
        try:
            client = Client(api_key=settings.LANGCHAIN_API_KEY)
            try:
                client.read_project(project_name=settings.LANGCHAIN_PROJECT)
            except Exception:
                client.create_project(settings.LANGCHAIN_PROJECT)
        except Exception as e:
            print(f"Warning: Could not initialize LangSmith project: {e}")

def get_client():
    if settings.LANGCHAIN_API_KEY:
        return Client(api_key=settings.LANGCHAIN_API_KEY)
    return None

def get_recent_traces(limit: int = 5):
    client = get_client()
    if not client:
        return []
    
    try:
        runs = client.list_runs(
            project_name=settings.LANGCHAIN_PROJECT,
            execution_order=1,
            limit=limit,
        )
        return [
            {
                "id": str(run.id),
                "name": run.name,
                "start_time": run.start_time.isoformat() if run.start_time else None,
                "latency": run.latency,
                "status": run.status,
            }
            for run in runs
        ]
    except Exception as e:
        if "not found" in str(e).lower() and "project" in str(e).lower():
            return []
        print(f"Error fetching LangSmith traces: {e}")
        return []
