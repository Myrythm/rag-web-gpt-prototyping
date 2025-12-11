from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from backend.utils.config import settings


def get_rewriter_llm():
    return ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0,
        openai_api_key=settings.OPENAI_API_KEY
    )


async def rewrite_query_with_context(query: str, chat_history: str) -> str:   
    # If no history, return as-is
    if not chat_history or not chat_history.strip():
        return query
    
    # Short queries likely need context from history
    if len(query.split()) > 5:
        return query
    
    try:
        llm = get_rewriter_llm()
        
        prompt = ChatPromptTemplate.from_template("""
        You are a query rewriter for a reimbursement search system.

        Your task: Combine the user's SHORT/AMBIGUOUS query with relevant context from chat history 
        to create a COMPLETE search query.

        RULES:
        1. Extract relevant entities from history: names (Ancika, Angga, etc), periods (November, 2025, etc)
        2. Combine with the current query to make it searchable
        3. Keep it concise - just the key search terms
        4. Output ONLY the rewritten query, nothing else
        5. If the query is already complete, return it as-is

        ---
        Chat History:
        {chat_history}

        Current Query: "{query}"

        Rewritten Query (for search):""")
        
        chain = prompt | llm
        result = await chain.ainvoke({
            "query": query,
            "chat_history": chat_history
        })
        
        rewritten = result.content.strip().strip('"').strip("'")
        
        # Fallback to original if rewrite is empty or too short
        if not rewritten or len(rewritten) < 3:
            return query
            
        return rewritten
        
    except Exception as e:
        print(f"Query rewrite error: {e}")
        return query
