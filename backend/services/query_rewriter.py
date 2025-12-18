from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from backend.utils.config import settings


# Cache the LLM instance
_rewriter_llm = None

def get_rewriter_llm():
    global _rewriter_llm
    if _rewriter_llm is None:
        _rewriter_llm = ChatOpenAI(
            model="gpt-4.1-nano", 
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY,
            max_tokens=100
        )
    return _rewriter_llm


async def rewrite_query_with_context(query: str, chat_history: str) -> str:   
    # FAST PATH: If no history, return query as-is (no LLM needed)
    if not chat_history or not chat_history.strip():
        return query
    
    # Long queries are usually complete, skip rewrite
    if len(query.split()) > 5:
        return query
    
    try:
        llm = get_rewriter_llm()
        
        prompt = ChatPromptTemplate.from_template("""Rewrite this query for search by adding context from history.

        History: {chat_history}

        Query: "{query}"

        Rewritten (just the search terms):""")
        
        chain = prompt | llm
        result = await chain.ainvoke({
            "query": query,
            "chat_history": chat_history[-500:] 
        })
        
        rewritten = result.content.strip().strip('"').strip("'")
        
        # Fallback to original if rewrite is empty or too short
        if not rewritten or len(rewritten) < 3:
            return query
            
        return rewritten
        
    except Exception as e:
        print(f"Query rewrite error: {e}")
        return query

