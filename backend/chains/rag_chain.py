from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from backend.chains.retriever_chroma import get_retriever
from backend.utils.config import settings

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

from operator import itemgetter

def get_rag_chain():
    retriever = get_retriever()
    # User requested gpt-5-mini, using gpt-4o-mini as the closest valid model.
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0, openai_api_key=settings.OPENAI_API_KEY)

    template = """
    You are an intelligent assistant designed to answer questions using both the provided context and chat history when relevant.

    Your task:
    - Use the **context** primarily to answer accurately.
    - Use the **chat history** only if it adds clarity or continuity to the user’s intent.
    - If the context does not contain enough information, **acknowledge it clearly** and provide a concise, relevant answer based on general knowledge (if allowed).
    - Keep answers **clear, natural, and to the point**.
    - When needed, explain reasoning in a friendly, helpful tone — as if you’re collaborating with the user.
    - if you don't know the answer, just say so.

    ---

    Context:
    {context}

    Chat History:
    {chat_history}

    Question:
    {question}

    """
    prompt = ChatPromptTemplate.from_template(template)

    rag_chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | prompt
        | llm
        | StrOutputParser()
    )

    rag_chain_with_source = RunnableParallel(
        {
            "context": itemgetter("question") | retriever, 
            "question": itemgetter("question"),
            "chat_history": itemgetter("chat_history")
        }
    ).assign(answer=rag_chain_from_docs)

    return rag_chain_with_source

def get_rag_chain_streaming():
    """Get RAG chain configured for streaming responses"""
    retriever = get_retriever()
    # Enable streaming with ChatOpenAI
    llm = ChatOpenAI(
        model="gpt-4.1-mini", 
        temperature=0, 
        openai_api_key=settings.OPENAI_API_KEY,
        streaming=True
    )

    template = """
    You are an intelligent assistant designed to answer questions using both the provided context and chat history when relevant.

    Your task:
    - Use the **context** primarily to answer accurately.
    - Use the **chat history** only if it adds clarity or continuity to the user's intent.
    - If the context does not contain enough information, **acknowledge it clearly** and provide a concise, relevant answer based on general knowledge (if allowed).
    - Keep answers **clear, natural, and to the point**.
    - When needed, explain reasoning in a friendly, helpful tone — as if you're collaborating with the user.
    - if you don't know the answer, just say so.

    ---

    Context:
    {context}

    Chat History:
    {chat_history}

    Question:
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

def get_simple_chat_chain():
    """Get a simple chat chain without RAG for direct conversation"""
    llm = ChatOpenAI(
        model="gpt-4.1-mini", 
        temperature=0.7,  # Slightly higher temperature for natural conversation
        openai_api_key=settings.OPENAI_API_KEY,
        streaming=True
    )

    template = """
    You are a friendly and helpful AI assistant. Answer the user's question naturally and conversationally.
    
    Chat History:
    {chat_history}

    Question:
    {question}

    """
    prompt = ChatPromptTemplate.from_template(template)

    chain = prompt | llm | StrOutputParser()
    
    return chain
