"""
Simple test script for RAG pipeline

Tests the complete flow:
1. Settings loading
2. Vector store connectivity
3. RAG agent initialization
4. Query processing
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from config.settings import Settings
from rag.agent import RAGAgent
from ingestion.vectorstore import VectorStore


def test_settings():
    """Test settings loading"""
    logger.info("Testing settings loading...")

    try:
        settings = Settings()
        logger.info(f"✅ Settings loaded successfully")
        logger.info(f"   - LLM Provider: {settings.llm_provider}")
        logger.info(f"   - LLM Model: {settings.llm_model}")
        logger.info(f"   - Vector Store: {settings.vector_store_type}")
        logger.info(f"   - Collection: {settings.vector_store_collection}")
        logger.info(f"   - Vault Path: {settings.obsidian_vault_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Settings loading failed: {e}")
        return False


def test_vector_store():
    """Test vector store connectivity"""
    logger.info("Testing vector store connectivity...")

    try:
        settings = Settings()
        vector_store = VectorStore(settings)

        # Get collection info
        info = vector_store.get_collection_info()
        logger.info(f"✅ Vector store connected successfully")
        logger.info(f"   - Collection: {info.get('name')}")
        logger.info(f"   - Points count: {info.get('points_count', 0)}")
        logger.info(f"   - Status: {info.get('status')}")

        return True
    except Exception as e:
        logger.error(f"❌ Vector store connection failed: {e}")
        return False


def test_rag_agent():
    """Test RAG agent initialization"""
    logger.info("Testing RAG agent initialization...")

    try:
        settings = Settings()
        agent = RAGAgent(settings)

        logger.info(f"✅ RAG agent initialized successfully")
        logger.info(f"   - Provider: {settings.llm_provider}")
        logger.info(f"   - Model: {settings.llm_model}")
        logger.info(f"   - Citations enabled: {settings.enable_citations}")

        return agent
    except Exception as e:
        logger.error(f"❌ RAG agent initialization failed: {e}")
        return None


def test_query(agent: RAGAgent, test_query: str = "Hello, can you help me?"):
    """Test query processing"""
    logger.info(f"Testing query processing with: '{test_query}'")

    try:
        response = agent.query(test_query)

        logger.info(f"✅ Query processed successfully")
        logger.info(f"   - Answer: {response['answer'][:100]}...")
        logger.info(f"   - Context found: {response.get('context_found', False)}")
        logger.info(f"   - Sources: {response.get('num_sources', 0)}")

        return True
    except Exception as e:
        logger.error(f"❌ Query processing failed: {e}")
        logger.exception(e)
        return False


def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("🧠 MNEME RAG PIPELINE TEST")
    logger.info("=" * 60)

    # Test 1: Settings
    if not test_settings():
        logger.error("Settings test failed. Stopping tests.")
        sys.exit(1)

    logger.info("")

    # Test 2: Vector Store
    if not test_vector_store():
        logger.error("Vector store test failed. Stopping tests.")
        sys.exit(1)

    logger.info("")

    # Test 3: RAG Agent
    agent = test_rag_agent()
    if not agent:
        logger.error("RAG agent test failed. Stopping tests.")
        sys.exit(1)

    logger.info("")

    # Test 4: Query Processing
    if not test_query(agent):
        logger.error("Query test failed.")
        sys.exit(1)

    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ ALL TESTS PASSED!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Run ingestion: mneme-ingest --vault-path /path/to/vault")
    logger.info("2. Start API server: mneme-serve")
    logger.info("3. Visit http://localhost:8000/docs for API documentation")


if __name__ == "__main__":
    main()
