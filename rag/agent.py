"""
RAG Agent using Datapizza AI

Orchestrates retrieval and generation for question answering.
"""

from typing import List, Dict, Optional, Any
from loguru import logger

from config.settings import Settings
from rag.retriever import Retriever
from rag.prompts import RAGPrompts

# Datapizza AI imports
from datapizza.agents import Agent
from datapizza.clients.openai import OpenAIClient
from datapizza.clients.anthropic import AnthropicClient


class RAGAgent:
    """
    RAG Agent for question answering over knowledge base.

    Uses Datapizza AI for LLM interactions and combines with
    semantic retrieval for context-aware responses.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize RAG agent.

        Args:
            settings: Settings object (will create if not provided)
        """
        self.settings = settings or Settings()

        # Get agent configuration (needed before agent initialization)
        self.enable_citations = self.settings.enable_citations
        self.max_history = self.settings.max_conversation_history

        # Initialize retriever
        self.retriever = Retriever(self.settings)

        # Initialize LLM client
        self.llm_client = self._init_llm_client()

        # Initialize agent
        self.agent = self._init_agent()

        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []

        logger.info(
            f"Initialized RAGAgent: provider={self.settings.llm_provider}, "
            f"model={self.settings.llm_model}"
        )

    def _init_llm_client(self):
        """
        Initialize LLM client based on provider setting.

        Returns:
            LLM client instance
        """
        provider = self.settings.llm_provider

        if provider == "openai":
            if not self.settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")

            client = OpenAIClient(
                api_key=self.settings.openai_api_key,
                model=self.settings.llm_model,
                temperature=self.settings.llm_temperature,
            )
            logger.info(f"Initialized OpenAI client: {self.settings.llm_model}")
            return client

        elif provider == "anthropic":
            if not self.settings.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not set in environment")

            client = AnthropicClient(
                api_key=self.settings.anthropic_api_key,
                model=self.settings.llm_model,
                temperature=self.settings.llm_temperature,
            )
            logger.info(f"Initialized Anthropic client: {self.settings.llm_model}")
            return client

        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def _init_agent(self) -> Agent:
        """
        Initialize Datapizza AI agent.

        Returns:
            Agent instance
        """
        # Get system prompt
        system_prompt = RAGPrompts.get_system_prompt(self.enable_citations)

        # Create agent with client directly
        agent = Agent(
            name="rag_agent",
            client=self.llm_client,
            system_prompt=system_prompt,
        )

        logger.info("Initialized Datapizza AI agent")
        return agent

    def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        include_sources: bool = True,
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG.

        Args:
            question: User's question
            top_k: Number of documents to retrieve (uses settings if not provided)
            include_sources: Whether to include source citations

        Returns:
            Dictionary with answer and optional sources
        """
        logger.info(f"Processing query: {question[:100]}...")

        try:
            # Retrieve relevant context
            retrieval_results = self.retriever.retrieve(
                query=question,
                top_k=top_k,
            )

            # Check if we found any relevant context
            if not retrieval_results:
                logger.warning("No relevant context found for query")
                answer = RAGPrompts.format_no_context_message(question)
                return {
                    "answer": answer,
                    "sources": [],
                    "context_found": False,
                }

            # Format context for LLM
            context = self.retriever.format_context(retrieval_results)

            # Format user message
            if self.conversation_history:
                user_message = RAGPrompts.format_user_message_with_history(
                    query=question,
                    context=context,
                    conversation_history=self.conversation_history,
                )
            else:
                user_message = RAGPrompts.format_user_message(
                    query=question,
                    context=context,
                )

            # Generate response using agent
            logger.debug("Generating response with LLM...")
            response = self.agent.run(user_message)

            # Extract answer from StepResult object
            if hasattr(response, "text"):
                answer = response.text.strip() if response.text else ""
            elif isinstance(response, dict):
                answer = response.get("output", "").strip()
            else:
                answer = str(response).strip()

            # Update conversation history
            self._update_history(question, answer)

            # Get sources if requested
            sources = []
            if include_sources:
                sources = self.retriever.get_sources(retrieval_results)

            logger.info("Successfully generated response")

            return {
                "answer": answer,
                "sources": sources,
                "context_found": True,
                "num_sources": len(sources),
            }

        except Exception as e:
            logger.error(f"Failed to process query: {e}")
            raise

    def chat(
        self,
        message: str,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Chat interface with conversation history.

        Args:
            message: User message
            conversation_id: Optional conversation ID for tracking

        Returns:
            Dictionary with response and metadata
        """
        return self.query(message, include_sources=self.enable_citations)

    def _update_history(self, user_message: str, assistant_message: str):
        """
        Update conversation history.

        Args:
            user_message: User's message
            assistant_message: Assistant's response
        """
        self.conversation_history.append(
            {"role": "user", "content": user_message}
        )
        self.conversation_history.append(
            {"role": "assistant", "content": assistant_message}
        )

        # Trim history if it exceeds max length
        if len(self.conversation_history) > self.max_history * 2:
            # Keep most recent messages (pairs of user/assistant)
            self.conversation_history = self.conversation_history[-(self.max_history * 2):]

        logger.debug(f"Conversation history: {len(self.conversation_history) // 2} turns")

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Cleared conversation history")

    def get_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history.

        Returns:
            List of message dictionaries
        """
        return self.conversation_history.copy()

    def reset(self):
        """Reset agent state (clears history)."""
        self.clear_history()
        logger.info("Reset agent state")
