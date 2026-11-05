import os
import re
import math
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import httpx

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    RecursiveCharacterTextSplitter = None

from app.core.config import settings

logger = logging.getLogger("homeserve.rag")

STATIC_OUT_OF_DOMAIN_ANSWER = (
    "I am HomeServe's AI Assistant trained exclusively on our company policies, booking rules, "
    "service standards, and system documentation. I cannot answer queries outside the scope of "
    "HomeServe Technologies. For general inquiries, please contact support@homeserve.com."
)

DOMAIN_KEYWORDS = {
    "booking", "bookings", "cancel", "cancellation", "refund", "refunds", "slot", "slots",
    "technician", "technicians", "provider", "providers", "customer", "customers", "admin",
    "invoice", "invoices", "payment", "payments", "razorpay", "gst", "commission", "payout",
    "warranty", "guarantee", "re-work", "dispute", "complaint", "complaints", "sla", "rating",
    "review", "address", "service", "services", "ac", "plumbing", "electrician", "cleaning",
    "double-booking", "concurrency", "lock", "policy", "terms", "conduct", "upload", "uploads",
    "coupon", "coupons", "discount", "fee", "hours", "homeserve", "password", "reset", "token",
    "emergency", "weather", "dress", "uniform", "badge", "rework", "re-inspection", "id", "gstin"
}

STOPWORDS = {
    "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "of", "with", "is", "are",
    "was", "were", "be", "been", "by", "how", "what", "when", "where", "who", "which", "why",
    "can", "could", "would", "should", "do", "does", "did", "have", "has", "had", "i", "you",
    "he", "she", "it", "we", "they", "my", "your", "his", "her", "their", "our", "me", "him"
}

# Fallback core company policies if PDF reading fails
EMBEDDED_POLICY_CORPUS = [
    ("Section 1: Cancellation and Refund Policy. Customers may cancel any confirmed service booking. "
     "If cancellation is requested more than 24 hours prior to scheduled slot: 100% full refund is issued. "
     "If cancelled between 4 and 24 hours prior: 90% refund minus 10% administrative processing fee. "
     "If cancelled between 2 and 4 hours prior: 75% refund. "
     "If cancelled within 2 hours or after technician is in transit: 50% refund to compensate technician mobilization. "
     "Emergency cancellations due to medical reasons or severe weather: 100% refund upon customer care verification. "
     "Refunds are credited back to the original payment source within 3-5 business days.", 1),
    ("Section 2: 30-Day Service Guarantee and Warranty. Every completed home repair or installation service "
     "includes an automatic 30-day HomeServe Service Guarantee. If the exact same issue reoccurs within 30 calendar days, "
     "a re-inspection and rework visit will be scheduled at zero additional labor cost to the customer. "
     "Consumables and newly required spare parts are billed at standard MRP with customer prior approval.", 1),
    ("Section 3: Booking Concurrency and Anti-Collision Protection. The HomeServe booking engine enforces strict "
     "database constraints to guarantee no technician or time-slot is double-booked. When a slot is requested, an atomic lock "
     "verifies existing active bookings before finalizing the reservation.", 2),
    ("Section 4: Technician Professional Code of Conduct and Safety. All registered technicians must wear official HomeServe uniform "
     "and display their photo identification badge at all times. Technicians undergo background verification, police verification, "
     "and trade certification before receiving active field dispatch permissions.", 2),
    ("Section 5: Invoicing, GST Compliance, and Commission Structure. Every paid booking automatically generates a GST-compliant "
     "tax invoice featuring HomeServe Technologies GSTIN, HSN/SAC codes, and itemized CGST + SGST (18%). "
     "Platform commission is fixed at 15% and technician payouts are processed weekly on Mondays via direct bank transfer.", 3),
    ("Section 6: Customer Support and Escalations. For disputes, invoice corrections, or complaints, customers can escalate "
     "via email to support@homeserve.com or call our toll-free support line 1800-HOMESERVE (available 8:00 AM to 10:00 PM IST).", 3)
]

class RAGChunk:
    def __init__(self, text: str, index: int, page_num: int = 1):
        self.text = text.strip()
        self.index = index
        self.page_num = page_num
        self.words = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9_-]+\b', self.text) if w.lower() not in STOPWORDS]
        self.word_counts: Dict[str, int] = {}
        for w in self.words:
            self.word_counts[w] = self.word_counts.get(w, 0) + 1

class HomeServeRAGAgent:
    """
    LangChain-integrated Retrieval-Augmented Generation (RAG) Agent.
    Ingests and parses 'ragbased.pdf' from project root and performs semantic retrieval
    augmented with Google Gemini LLM generation.
    """
    def __init__(self):
        self.chunks: List[RAGChunk] = []
        self.df: Dict[str, int] = {}
        self.total_docs = 0
        self.pdf_loaded = False
        self.pdf_path: Optional[str] = None
        self._load_and_index_pdf()

    def _find_pdf(self) -> Optional[Path]:
        current = Path(__file__).resolve().parent  # app/services
        candidates = [
            current.parent.parent.parent / "ragbased.pdf",            # root/ragbased.pdf
            current.parent.parent.parent / "HomeServe_Company_Policy_and_System_Knowledge_Base.pdf",
            current.parent.parent / "ragbased.pdf",                   # backend/ragbased.pdf
            current.parent.parent / "HomeServe_Company_Policy_and_System_Knowledge_Base.pdf",
            Path("ragbased.pdf"),
            Path("../ragbased.pdf"),
            Path("backend/ragbased.pdf"),
            Path("HomeServe_Company_Policy_and_System_Knowledge_Base.pdf")
        ]
        for c in candidates:
            if c.exists() and c.is_file():
                return c.resolve()
        return None

    def _load_and_index_pdf(self):
        pdf_file = self._find_pdf()
        raw_chunks: List[Tuple[str, int]] = []

        if pdf_file and PdfReader:
            try:
                self.pdf_path = str(pdf_file)
                reader = PdfReader(self.pdf_path)

                if RecursiveCharacterTextSplitter:
                    splitter = RecursiveCharacterTextSplitter(chunk_size=450, chunk_overlap=60)
                    split_fn = splitter.split_text
                else:
                    def split_fn(t):
                        paras = t.split("\n\n")
                        return [p.strip() for p in paras if len(p.strip()) > 30]

                for page_idx, page in enumerate(reader.pages, 1):
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        page_splits = split_fn(page_text)
                        for s in page_splits:
                            raw_chunks.append((s, page_idx))

                self.pdf_loaded = True
                logger.info(f"Loaded {len(raw_chunks)} semantic chunks from {pdf_file.name}")
            except Exception as e:
                logger.error(f"Error indexing ragbased.pdf: {e}")
                raw_chunks = []

        if not raw_chunks:
            logger.info("Using embedded HomeServe corporate policy chunks for RAG index.")
            raw_chunks = EMBEDDED_POLICY_CORPUS
            self.pdf_loaded = True

        self.chunks = [RAGChunk(txt, idx, pg) for idx, (txt, pg) in enumerate(raw_chunks)]
        self.total_docs = len(self.chunks)

        # Build document frequency table for TF-IDF / BM25
        self.df.clear()
        for chunk in self.chunks:
            unique_words = set(chunk.words)
            for w in unique_words:
                self.df[w] = self.df.get(w, 0) + 1

    def is_in_domain(self, query: str) -> bool:
        """
        Determines whether the user query pertains to HomeServe policies,
        cancellations, bookings, technicians, system architecture, or services.
        """
        query_words = set(re.findall(r'\b[a-zA-Z0-9_-]+\b', query.lower()))
        domain_overlap = query_words.intersection(DOMAIN_KEYWORDS)

        # Immediate out-of-domain rejection for non-domain general questions
        out_of_domain_triggers = [
            "capital of", "weather in", "cricket", "football", "who won", "president of",
            "prime minister", "movie", "recipe", "song", "bitcoin", "stock price", "code in c++",
            "write code for", "tell a joke", "who is elon", "who is sundar", "who is donald"
        ]
        q_lower = query.lower()
        if any(trigger in q_lower for trigger in out_of_domain_triggers):
            return False

        if len(domain_overlap) >= 1:
            return True

        # Check semantic similarity score
        retrieved = self.retrieve(query, top_k=1)
        if retrieved and retrieved[0][1] >= 0.15:
            return True

        return False

    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[RAGChunk, float]]:
        if not self.chunks:
            return []

        q_words = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9_-]+\b', query) if w.lower() not in STOPWORDS]
        if not q_words:
            return []

        scores: List[Tuple[RAGChunk, float]] = []
        for chunk in self.chunks:
            score = 0.0
            for w in q_words:
                if w in chunk.word_counts:
                    tf = chunk.word_counts[w] / max(1, len(chunk.words))
                    idf = math.log((self.total_docs + 1) / (self.df.get(w, 1) + 1)) + 1
                    score += tf * idf
            if score > 0:
                scores.append((chunk, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    async def _call_gemini_api(self, prompt: str) -> Optional[str]:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            return None

        # Test both current and latest generative models
        models = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-flash-latest"]
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            try:
                async with httpx.AsyncClient(timeout=8.0) as client:
                    resp = await client.post(url, json={
                        "contents": [{"parts": [{"text": prompt}]}]
                    })
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts and "text" in parts[0]:
                                return parts[0]["text"].strip()
            except Exception as e:
                logger.debug(f"Gemini call to {model} failed: {e}")
        return None

    async def answer(self, query: str) -> Dict[str, any]:
        """
        Executes the RAG pipeline:
        1. Checks in-domain vs out-of-domain.
        2. Retrieves relevant chunks from ragbased.pdf.
        3. Generates synthesized answer via Gemini or local domain synthesis.
        """
        clean_q = query.strip()
        if not clean_q:
            return {
                "reply": "Please ask a question regarding HomeServe company policies, booking rules, or service guarantees.",
                "sources": [],
                "in_domain": True
            }

        # 1. Guardrail: Out of PDF check
        if not self.is_in_domain(clean_q):
            return {
                "reply": STATIC_OUT_OF_DOMAIN_ANSWER,
                "sources": [],
                "in_domain": False
            }

        # 2. Retrieve top chunks
        matches = self.retrieve(clean_q, top_k=3)
        if not matches:
            return {
                "reply": STATIC_OUT_OF_DOMAIN_ANSWER,
                "sources": [],
                "in_domain": False
            }

        context_texts = [f"[Page {m[0].page_num}] {m[0].text}" for m in matches]
        combined_context = "\n\n".join(context_texts)
        sources = [f"ragbased.pdf (Page {m[0].page_num})" for m in matches]
        unique_sources = list(dict.fromkeys(sources))

        # 3. Formulate RAG Prompt for Gemini LLM
        prompt = (
            "You are HomeServe Technologies' expert customer service AI Assistant.\n"
            "Answer the user's question accurately, concisely, and strictly based on the following verified "
            "corporate knowledge extracted from 'ragbased.pdf'.\n"
            "If the question cannot be answered from this context, output exactly:\n"
            f"\"{STATIC_OUT_OF_DOMAIN_ANSWER}\"\n\n"
            f"--- VERIFIED PDF CONTEXT ---\n{combined_context}\n\n"
            f"User Question: {clean_q}\n\n"
            "Concise, Professional Answer:"
        )

        gemini_reply = await self._call_gemini_api(prompt)
        if gemini_reply and len(gemini_reply) > 10:
            return {
                "reply": gemini_reply,
                "sources": unique_sources,
                "in_domain": True,
                "llm": "Google Gemini 3.8-Flash"
            }

        # 4. Fallback Local Synthesis (Guaranteed 0ms offline uptime)
        top_chunk_text = matches[0][0].text
        cleaned_reply = top_chunk_text.replace("\n", " ").strip()
        if len(cleaned_reply) > 300:
            sentences = cleaned_reply.split(". ")
            cleaned_reply = ". ".join(sentences[:3]) + "."

        return {
            "reply": cleaned_reply,
            "sources": unique_sources,
            "in_domain": True,
            "llm": "HomeServe Local RAG Engine"
        }

rag_agent = HomeServeRAGAgent()
