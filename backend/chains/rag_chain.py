from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from backend.chains.retriever_chroma import get_retriever
from backend.utils.config import settings
from operator import itemgetter

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def get_rag_chain_streaming():
    retriever = get_retriever()
    llm = ChatOpenAI(
        model="gpt-4.1-mini", 
        temperature=0.7, 
        openai_api_key=settings.OPENAI_API_KEY,
        streaming=True
    )

    template = """
    You are an intelligent assistant specialized in reimbursement queries.

    QUESTION TYPE DETECTION (DO THIS FIRST):
    
    Type A - DISCOVERY QUESTION (asking WHO exists):
    - Keywords: "siapa saja", "daftar nama", "list nama", "ada siapa", "who all"
    - Example: "siapa saja yang mengajukan reimburse?"
    - Action: Extract ALL unique names from CONTEXT and list them
    - DO NOT ask for period - just list the names you found in context
    
    Type B - SPECIFIC DATA QUESTION (asking for details):
    - User asks for specific person's data OR specific period's data
    - Example: "reimburse Angga November", "total reimburse bulan ini"
    - Action: Follow the WHO + WHEN logic below
    
    ---
    
    FOR TYPE B QUESTIONS ONLY:
    
    STEP 1: Extract information from CHAT HISTORY
    - Look for WHO (name) mentioned in previous messages
    - Look for WHEN (period/month/year) mentioned in previous messages
    
    STEP 2: Combine with CURRENT QUESTION
    - If current question only mentions period, but name was in history → use BOTH
    - If current question only mentions name, but period was in history → use BOTH
    
    STEP 3: Check completeness
    - You need BOTH: WHO (specific name OR "all") AND WHEN (period)
    - If BOTH are known → Show the data
    - If still missing one → Ask politely for the missing info
    
    ---
    
    OTHER RULES:
    - Use CONTEXT as source of truth for actual data
    - Format with Markdown (use tables for data)
    - Be concise and friendly
    - Reject any question that is not related to reimbursement
    - When listing names, also mention what periods/months are available for each

    ---

    Context:
    {context}

    This is the chat history, you can use it to remember the previous conversation:
    {chat_history}

    Current Question from User:
    {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    rag_chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain_from_docs, retriever
