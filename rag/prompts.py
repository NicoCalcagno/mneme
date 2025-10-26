"""
RAG Agent Prompts

System and user prompts for the RAG agent.
"""

from typing import Dict, List, Any


class RAGPrompts:
    """Prompt templates for RAG agent"""

    SYSTEM_PROMPT = """You are Mneme, an AI assistant specialized in helping users explore and understand their Obsidian knowledge base.

Your capabilities:
- Answer questions based on the user's personal notes and knowledge
- Provide accurate, contextual responses with citations
- Help connect ideas across different notes
- Respect the context and structure of the original notes

Guidelines:
1. **Be accurate**: Base your answers on the provided context from the user's notes
2. **Cite sources**: When referencing specific notes, mention the note title
3. **Be honest**: If the context doesn't contain enough information, say so
4. **Be helpful**: Connect related concepts and provide insights
5. **Respect structure**: Maintain the original formatting, wikilinks, and tags when relevant

When you don't know something or the context doesn't provide enough information, be transparent about it and suggest what additional information might help."""

    SYSTEM_PROMPT_WITH_CITATIONS = """You are Mneme, an AI assistant specialized in helping users explore and understand their Obsidian knowledge base.

Your capabilities:
- Answer questions based on the user's personal notes and knowledge
- Provide accurate, contextual responses with citations
- Help connect ideas across different notes
- Respect the context and structure of the original notes

Guidelines:
1. **Be accurate**: Base your answers on the provided context from the user's notes
2. **Cite sources**: Always cite your sources using [Document N] format (e.g., [Document 1], [Document 2])
3. **Be honest**: If the context doesn't contain enough information, say so
4. **Be helpful**: Connect related concepts and provide insights
5. **Respect structure**: Maintain the original formatting, wikilinks, and tags when relevant

IMPORTANT: When you reference information from the context, always include a citation like [Document N] where N is the document number from the context.

When you don't know something or the context doesn't provide enough information, be transparent about it and suggest what additional information might help."""

    @staticmethod
    def get_system_prompt(enable_citations: bool = True) -> str:
        """
        Get the appropriate system prompt based on settings.

        Args:
            enable_citations: Whether to enable citation requirements

        Returns:
            System prompt string
        """
        if enable_citations:
            return RAGPrompts.SYSTEM_PROMPT_WITH_CITATIONS
        return RAGPrompts.SYSTEM_PROMPT

    @staticmethod
    def format_user_message(query: str, context: str) -> str:
        """
        Format user message with context and query.

        Args:
            query: User's question
            context: Retrieved context from vector store

        Returns:
            Formatted user message
        """
        return f"""Context from your notes:

{context}

---

Question: {query}

Please answer the question based on the context provided above. If the context doesn't contain enough information to answer fully, let me know what's missing."""

    @staticmethod
    def format_user_message_with_history(
        query: str,
        context: str,
        conversation_history: List[Dict[str, str]],
    ) -> str:
        """
        Format user message with context, query, and conversation history.

        Args:
            query: User's question
            context: Retrieved context from vector store
            conversation_history: List of previous messages

        Returns:
            Formatted user message
        """
        # Format conversation history
        history_text = ""
        if conversation_history:
            history_text = "Previous conversation:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_text += f"\n{role.upper()}: {content}\n"
            history_text += "\n---\n\n"

        return f"""{history_text}Context from your notes:

{context}

---

Question: {query}

Please answer the question based on the context provided above and our previous conversation. If the context doesn't contain enough information to answer fully, let me know what's missing."""

    @staticmethod
    def format_no_context_message(query: str) -> str:
        """
        Format message when no relevant context is found.

        Args:
            query: User's question

        Returns:
            Formatted message
        """
        return f"""I couldn't find any relevant information in your notes to answer the question: "{query}"

This could mean:
- The topic hasn't been covered in your notes yet
- The information exists but wasn't retrieved (try rephrasing your question)
- The relevant notes might be in excluded folders

Would you like to rephrase your question or add more context?"""
