#!/usr/bin/env python3
"""
Test Qdrant Cloud connection
"""

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# Load environment variables
load_dotenv()


def test_qdrant_connection():
    """Test connection to Qdrant Cloud"""

    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    print("🔍 Testing Qdrant Cloud connection...")
    print(f"   URL: {qdrant_url}")
    print(f"   API Key: {'*' * 20}{qdrant_api_key[-10:] if qdrant_api_key else 'NOT SET'}")

    try:
        # Initialize client
        client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            timeout=30,
        )

        # Test connection by getting cluster info
        collections = client.get_collections()

        print("✅ Connection successful!")
        print(f"   Collections found: {len(collections.collections)}")

        for collection in collections.collections:
            print(f"   - {collection.name}: {collection.vectors_count} vectors")

        return True

    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_qdrant_connection()
    exit(0 if success else 1)