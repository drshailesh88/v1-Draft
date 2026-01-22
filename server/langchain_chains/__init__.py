"""
LangChain RAG Chain Module
Handles RAG (Retrieval-Augmented Generation) for answering questions about documents.
"""

from core.openai_client import chat_completion
from typing import List, Optional


SYSTEM_PROMPT = """You are a helpful research assistant specializing in academic papers and scientific documents.

Your role is to:
1. Answer questions accurately based ONLY on the provided document context
2. Always cite the specific page numbers when referencing information
3. Be precise and scholarly in your responses
4. If the answer is not found in the context, clearly state that

When citing sources, use the format: (Page X) or [Page X] inline with your response.

Important guidelines:
- Only use information from the provided context
- Do not make up or assume information not present in the context
- If multiple pages contain relevant information, cite all of them
- Maintain academic tone and precision"""


USER_PROMPT_TEMPLATE = """Based on the following excerpts from the document, please answer the user's question.

=== DOCUMENT CONTEXT ===
{context}
=== END CONTEXT ===

User Question: {query}

Please provide a comprehensive answer based solely on the information in the document context above. Include page number citations for any information you reference."""


class RagChain:
    """RAG (Retrieval-Augmented Generation) chain for answering questions about documents"""

    def __init__(self, model: str = "gpt-4", temperature: float = 0.3):
        """
        Initialize RAG chain.

        Args:
            model: OpenAI model to use for generation
            temperature: Temperature for response generation (lower = more focused)
        """
        self.model = model
        self.temperature = temperature

    async def generate_answer(
        self,
        query: str,
        relevant_chunks: List[dict],
        include_sources: bool = True
    ) -> str:
        """
        Generate answer using relevant document chunks.

        Args:
            query: User's question
            relevant_chunks: List of relevant document chunks with content and page_number
            include_sources: Whether to include source citations

        Returns:
            Generated answer string
        """
        if not relevant_chunks:
            return "I couldn't find any relevant information in the document to answer your question. Please try rephrasing your question or ensure the document contains information about this topic."

        # Build context from chunks
        context = self._build_context(relevant_chunks)

        # Create messages for chat completion
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": USER_PROMPT_TEMPLATE.format(
                    context=context,
                    query=query
                )
            }
        ]

        # Generate answer
        answer = await chat_completion(
            messages,
            model=self.model,
            temperature=self.temperature
        )

        return answer

    async def generate_answer_with_sources(
        self,
        query: str,
        relevant_chunks: List[dict]
    ) -> dict:
        """
        Generate answer with explicit source tracking.

        Args:
            query: User's question
            relevant_chunks: List of relevant document chunks

        Returns:
            Dict with 'answer' and 'sources' (list of page numbers)
        """
        answer = await self.generate_answer(query, relevant_chunks)

        # Extract unique page numbers from chunks
        sources = list(set(
            chunk.get("page_number", 0)
            for chunk in relevant_chunks
            if chunk.get("page_number")
        ))
        sources.sort()

        return {
            "answer": answer,
            "sources": sources,
            "chunk_count": len(relevant_chunks)
        }

    def _build_context(self, chunks: List[dict]) -> str:
        """
        Build context string from chunks with page annotations.

        Args:
            chunks: List of document chunks

        Returns:
            Formatted context string
        """
        context_parts = []

        for i, chunk in enumerate(chunks, 1):
            page_num = chunk.get("page_number", "N/A")
            content = chunk.get("content", "")
            similarity = chunk.get("similarity", None)

            # Format each chunk with clear page reference
            header = f"[Excerpt {i} - Page {page_num}]"
            if similarity is not None:
                header += f" (relevance: {similarity:.2f})"

            context_parts.append(f"{header}\n{content}")

        return "\n\n---\n\n".join(context_parts)


class ConversationalRagChain(RagChain):
    """Extended RAG chain with conversation history support"""

    def __init__(self, model: str = "gpt-4", temperature: float = 0.3):
        super().__init__(model, temperature)
        self.conversation_history: List[dict] = []

    async def chat(
        self,
        query: str,
        relevant_chunks: List[dict],
        max_history: int = 5
    ) -> str:
        """
        Generate answer with conversation context.

        Args:
            query: User's question
            relevant_chunks: List of relevant document chunks
            max_history: Maximum conversation turns to include

        Returns:
            Generated answer string
        """
        context = self._build_context(relevant_chunks)

        # Build messages with history
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add recent conversation history
        for turn in self.conversation_history[-max_history * 2:]:
            messages.append(turn)

        # Add current query with context
        messages.append({
            "role": "user",
            "content": USER_PROMPT_TEMPLATE.format(
                context=context,
                query=query
            )
        })

        # Generate answer
        answer = await chat_completion(
            messages,
            model=self.model,
            temperature=self.temperature
        )

        # Update history
        self.conversation_history.append({"role": "user", "content": query})
        self.conversation_history.append({"role": "assistant", "content": answer})

        return answer

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []


# Default RAG chain instance
rag_chain = RagChain()

# Conversational RAG chain instance
conversational_rag_chain = ConversationalRagChain()
