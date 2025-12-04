from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.utils.config import settings

def classify_query(query: str) -> bool:
    """
    Classify if a query needs document retrieval (RAG) or can be answered directly.
    Returns True if RAG is needed, False otherwise.
    """
    llm = ChatOpenAI(
        model="gpt-4.1-mini",  
        temperature=0,
        openai_api_key=settings.OPENAI_API_KEY
    )
    
    template = """You are a query classifier. Determine if the user's question requires searching through documents/knowledge base or can be answered with general conversation.

Return ONLY "YES" if the query needs document search (technical questions, specific information, explanations about topics).
Return ONLY "NO" if it's general conversation (greetings, thanks, simple chat, opinions).

Examples:
- "Hello" → NO
- "How are you?" → NO
- "Thanks!" → NO
- "What is Python?" → YES
- "Explain the concept of..." → YES
- "Tell me about [specific topic]" → YES

User query: {query}

Answer (YES or NO):"""
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    try:
        result = chain.invoke({"query": query}).strip().upper()
        return result == "YES"
    except:
        # If classification fails, assume RAG is needed (safer)
        return True
