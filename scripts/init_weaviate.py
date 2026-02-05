#!/usr/bin/env python3
"""
Initialize Weaviate collections for Callisto.

This script creates the necessary collections (classes) in Weaviate:
1. Document - For storing RAG document chunks with multi-tenancy (per company)
2. ConversationHistory - For storing conversation logs

Run this script once after starting Weaviate for the first time.
"""

import os
import sys
import logging
from typing import Optional

import weaviate
from weaviate.classes.config import Configure, Property, DataType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")


def connect_to_weaviate() -> weaviate.WeaviateClient:
    """Connect to Weaviate instance."""
    try:
        # Extract host from URL
        host = WEAVIATE_URL.replace("http://", "").replace("https://", "").split(":")[0]
        port = int(WEAVIATE_URL.split(":")[-1]) if ":" in WEAVIATE_URL else 8080
        
        logger.info(f"Connecting to Weaviate at {host}:{port}")
        
        # For local/Docker setup
        if host in ["localhost", "127.0.0.1", "weaviate"]:
            client = weaviate.connect_to_local(
                host=host,
                port=port
            )
        else:
            # For custom URLs
            client = weaviate.connect_to_custom(
                http_host=host,
                http_port=port,
                http_secure=False,
                grpc_host=host,
                grpc_port=50051,
                grpc_secure=False
            )
        
        logger.info("✅ Connected to Weaviate successfully")
        return client
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to Weaviate: {e}")
        sys.exit(1)


def create_document_collection(client: weaviate.WeaviateClient) -> None:
    """
    Create the Document collection for RAG with multi-tenancy.
    
    Each company (HPE, Toyota, Microsoft) will be a separate tenant.
    """
    collection_name = "Document"
    
    try:
        # Check if collection already exists
        if client.collections.exists(collection_name):
            logger.warning(f"Collection '{collection_name}' already exists. Skipping creation.")
            return
        
        logger.info(f"Creating collection: {collection_name}")
        
        # Create collection with Ollama vectorizer and multi-tenancy
        client.collections.create(
            name=collection_name,
            
            # Vector configuration with Ollama embeddings
            vector_config=Configure.Vectors.text2vec_ollama(
                api_endpoint=OLLAMA_URL,
                model="nomic-embed-text",
                vectorize_collection_name=False
            ),
            
            # Enable multi-tenancy for per-company isolation
            multi_tenancy_config=Configure.multi_tenancy(enabled=True),
            
            # Properties (fields)
            properties=[
                Property(
                    name="content",
                    data_type=DataType.TEXT,
                    description="The text content of the document chunk"
                ),
                Property(
                    name="source",
                    data_type=DataType.TEXT,
                    description="Source document filename",
                    skip_vectorization=True
                ),
                Property(
                    name="chunk_index",
                    data_type=DataType.INT,
                    description="Index of this chunk in the source document",
                    skip_vectorization=True
                ),
                Property(
                    name="metadata",
                    data_type=DataType.TEXT,
                    description="Additional metadata as JSON string",
                    skip_vectorization=True
                )
            ],
            
            # Inverted index config for keyword search
            inverted_index_config=Configure.inverted_index(
                index_null_state=True,
                index_property_length=True,
                index_timestamps=True
            )
        )
        
        logger.info(f"✅ Created collection: {collection_name}")
        
    except Exception as e:
        logger.error(f"❌ Failed to create collection '{collection_name}': {e}")
        raise


def create_conversation_collection(client: weaviate.WeaviateClient) -> None:
    """
    Create the ConversationHistory collection for storing conversation logs.
    """
    collection_name = "ConversationHistory"
    
    try:
        # Check if collection already exists
        if client.collections.exists(collection_name):
            logger.warning(f"Collection '{collection_name}' already exists. Skipping creation.")
            return
        
        logger.info(f"Creating collection: {collection_name}")
        
        # Create collection without vectorization (we don't need semantic search on conversations)
        client.collections.create(
            name=collection_name,
            
            # No vectorization needed for conversation history
            vector_config=Configure.Vectors.self_provided(),
            
            # Properties
            properties=[
                Property(
                    name="scenario_description",
                    data_type=DataType.TEXT,
                    description="Description of the conversation scenario"
                ),
                Property(
                    name="client_company",
                    data_type=DataType.TEXT,
                    description="Client company name (e.g., Toyota)"
                ),
                Property(
                    name="timestamp",
                    data_type=DataType.DATE,
                    description="When the conversation occurred"
                ),
                Property(
                    name="messages",
                    data_type=DataType.TEXT,
                    description="JSON array of conversation messages"
                ),
                Property(
                    name="agent_configs",
                    data_type=DataType.TEXT,
                    description="JSON array of agent configurations"
                ),
                Property(
                    name="total_turns",
                    data_type=DataType.INT,
                    description="Total number of conversation turns"
                ),
                Property(
                    name="final_sentiment",
                    data_type=DataType.NUMBER,
                    description="Final average sentiment score"
                ),
                Property(
                    name="outcome",
                    data_type=DataType.TEXT,
                    description="Conversation outcome or result"
                )
            ]
        )
        
        logger.info(f"✅ Created collection: {collection_name}")
        
    except Exception as e:
        logger.error(f"❌ Failed to create collection '{collection_name}': {e}")
        raise


def create_tenants(client: weaviate.WeaviateClient) -> None:
    """
    Create initial tenants for the Document collection.
    
    Creates tenants for: HPE, Toyota, Microsoft
    """
    collection_name = "Document"
    companies = ["HPE", "Toyota", "Microsoft"]
    
    try:
        logger.info("Creating tenants for Document collection")
        
        # Get the collection
        collection = client.collections.get(collection_name)
        
        # Create tenants
        from weaviate.classes.tenants import Tenant
        
        tenants = [Tenant(name=company) for company in companies]
        collection.tenants.create(tenants)
        
        logger.info(f"✅ Created tenants: {', '.join(companies)}")
        
    except Exception as e:
        logger.error(f"❌ Failed to create tenants: {e}")
        raise


def verify_setup(client: weaviate.WeaviateClient) -> None:
    """Verify that all collections were created successfully."""
    logger.info("Verifying setup...")
    
    try:
        # List all collections
        collections = client.collections.list_all()
        # In v4, list_all() returns dict with collection names as keys
        collection_names = list(collections.keys())
        
        logger.info(f"Found collections: {', '.join(collection_names)}")
        
        # Check Document collection tenants
        document_collection = client.collections.get("Document")
        tenants_list = document_collection.tenants.get()
        # In v4, tenants_list items can be strings or Tenant objects
        tenant_names = [t if isinstance(t, str) else t.name for t in tenants_list]
        
        logger.info(f"Document collection tenants: {', '.join(tenant_names)}")
        
        logger.info("✅ Setup verification complete")
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


def main():
    """Main function to initialize Weaviate."""
    logger.info("=" * 60)
    logger.info("Initializing Weaviate for Callisto")
    logger.info("=" * 60)
    
    client = None
    
    try:
        # Connect to Weaviate
        client = connect_to_weaviate()
        
        # Create collections
        create_document_collection(client)
        create_conversation_collection(client)
        
        # Create tenants
        create_tenants(client)
        
        # Verify setup
        verify_setup(client)
        
        logger.info("=" * 60)
        logger.info("✅ Weaviate initialization complete!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        sys.exit(1)
        
    finally:
        if client:
            client.close()
            logger.info("Connection closed")


if __name__ == "__main__":
    main()
