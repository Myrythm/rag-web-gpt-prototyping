from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from backend.utils.config import settings


# Simple greetings that don't need LLM classification (instant response)
SIMPLE_GREETINGS = {
    # Indonesian
    "halo", "hai", "hi", "hey", "hello", "hallo",
    "selamat pagi", "selamat siang", "selamat sore", "selamat malam",
    "pagi", "siang", "sore", "malam",
    "terima kasih", "terimakasih", "makasih", "thanks", "thank you", "thx",
    "ok", "oke", "okay", "sip", "siap", "baik",
    "bye", "bye bye", "dadah", "sampai jumpa",
    "hehe", "haha", "wkwk", "lol",
    # English
    "good morning", "good afternoon", "good evening", "good night",
}


def is_simple_greeting(query: str) -> bool:
    """Check if query is a simple greeting without LLM."""
    normalized = query.lower().strip().rstrip("!?.,:;")
    return normalized in SIMPLE_GREETINGS or len(normalized) <= 3


# Pre-defined instant responses for simple greetings
INSTANT_RESPONSES = {
    "halo": "Halo! Ada yang bisa saya bantu terkait data reimbursement?",
    "hai": "Hai! Silakan tanyakan tentang data reimburse.",
    "hi": "Hi! Ada yang bisa saya bantu?",
    "hello": "Hello! Silakan tanyakan tentang reimbursement.",
    "terima kasih": "Sama-sama! Senang bisa membantu.",
    "terimakasih": "Sama-sama! Ada yang lain yang bisa saya bantu?",
    "makasih": "Sama-sama! 😊",
    "thanks": "You're welcome!",
    "ok": "Baik, ada pertanyaan lain tentang reimbursement?",
    "oke": "Siap! Ada yang lain?",
    "bye": "Sampai jumpa! 👋",
}


def get_instant_response(query: str) -> str:
    """Get instant response for simple greetings."""
    normalized = query.lower().strip().rstrip("!?.,:;")
    return INSTANT_RESPONSES.get(normalized, "Halo! Ada yang bisa saya bantu terkait reimbursement?")


# Initialize a fast, cheap model for classification
_classifier_llm = None

def get_classifier_llm():
    global _classifier_llm
    if _classifier_llm is None:
        _classifier_llm = ChatOpenAI(
            model="gpt-4.1-nano", 
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY,
            max_tokens=50
        )
    return _classifier_llm


CLASSIFICATION_PROMPT = ChatPromptTemplate.from_template("""
Classify this query into one of two categories:

1. "RAG" - Query is about reimbursement data, expenses, claims, or needs document retrieval
   Examples: "reimburse Angga", "data bulan Agustus", "total pengeluaran", "klaim transport"
   
2. "CHAT" - Query is a greeting, thanks, or general chat NOT about reimbursement
   Examples: "halo", "terima kasih", "ok", "selamat pagi", "bye"

Query: "{query}"

Respond with ONLY one word: either "RAG" or "CHAT"
""")


async def classify_query(query: str) -> str:
    """
    Classify query using LLM.
    
    Returns:
        "RAG" if query needs document retrieval
        "CHAT" if query is just greeting/thanks/etc
    """
    try:
        llm = get_classifier_llm()
        chain = CLASSIFICATION_PROMPT | llm
        result = await chain.ainvoke({"query": query})
        classification = result.content.strip().upper()
        
        # Validate response
        if classification in ["RAG", "CHAT"]:
            return classification
        return "RAG"  # Default to RAG if unclear
        
    except Exception as e:
        print(f"Classification error: {e}")
        return "RAG"  # Default to RAG on error


def is_reimbursement_related(query: str) -> bool:
    """
    Synchronous wrapper - use classify_query for async code.
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return True
        result = loop.run_until_complete(classify_query(query))
        return result == "RAG"
    except:
        return True


async def is_reimbursement_related_async(query: str) -> bool:
    """Check if query needs RAG - with fast-path for simple greetings."""
    # Fast path: simple greetings don't need RAG
    if is_simple_greeting(query):
        return False
    
    # Otherwise use LLM classification
    result = await classify_query(query)
    return result == "RAG"


# Pre-defined responses for non-RAG queries
CHAT_RESPONSES = {
      "default": "Saya adalah asisten khusus untuk data reimbursement. Silakan tanyakan tentang data reimburse karyawan."
}


async def get_chat_response(query: str) -> str:
    try:
        llm = get_classifier_llm()
        prompt = ChatPromptTemplate.from_template("""
        Kamu adalah asisten ramah untuk sistem reimbursement.
        User mengirim pesan yang BUKAN tentang data reimbursement (sapaan/ucapan terima kasih/dll).

        Balas dengan singkat dan ramah dalam Bahasa Indonesia.
        Jika relevan, ingatkan bahwa kamu bisa membantu untuk data reimbursement.

        Pesan user: "{query}"

        Balasan singkat (1-2 kalimat):
""")
        chain = prompt | llm
        result = await chain.ainvoke({"query": query})
        return result.content.strip()
        
    except Exception as e:
        print(f"Chat response error: {e}")
        return CHAT_RESPONSES["default"]


async def get_non_rag_response(query: str) -> str:
    try:
        logger.info(f"Chat response: {await get_chat_response(query)}")
        return await get_chat_response(query)
    except Exception as e:
        logger.error(f"Failed to get chat response: {e}")
        return CHAT_RESPONSES["default"]
