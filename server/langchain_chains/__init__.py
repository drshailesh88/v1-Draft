from core.openai_client import chat_completion
from typing import List

class RagChain:
    """RAG (Retrieval-Augmented Generation) chain for answering questions about documents"""
    
    def __init__(self):
        pass
    
    @staticmethod
    async def generate_answer(query: str, relevant_chunks: List[dict]) -> str:
        """Generate answer using relevant document chunks"""
        
        # Build context from chunks
        context = RagChain._build_context(relevant_chunks)
        
        # Create prompt
        messages = [
            {
                "role": "system",
                "content": """You are a helpful research assistant. Answer questions about academic papers using the provided context. Always cite the page number when referencing information from the document. If the answer is not in the context, say "I don't have enough information from this document to answer that.""""
            },
            {
                "role": "user",
                "content": f"""Use the following context from the document to answer the user's question.

Context:
{context}

Question: {query}

Answer:"""
            }
        ]
        
        # Generate answer
        answer = await chat_completion(messages, temperature=0.7)
        
        return answer
    
    @staticmethod
    def _build_context(chunks: List[dict]) -> str:
        """Build context string from chunks"""
        context_parts = []
        
        for chunk in chunks:
            page_info = f"[Page {chunk.get('page_number', 'N/A')}]"
            context_parts.append(f"{page_info} {chunk.get('content', '')}")
        
        return "\n\n".join(context_parts)

rag_chain = RagChain()
