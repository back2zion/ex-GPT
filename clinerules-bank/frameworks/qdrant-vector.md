# Qdrant Vector Database Integration Guidelines

## Overview
Comprehensive guidelines for integrating Qdrant vector database in the ex-GPT system, focusing on document embedding, similarity search, and real-time knowledge base management.

## Architecture Configuration

### Qdrant Setup and Configuration
```python
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, CollectionStatus
from qdrant_client.http.models import PointStruct
import uuid
from typing import List, Dict, Any

class QdrantManager:
    def __init__(self, host: str = "localhost", port: int = 6333, api_key: str = None):
        self.client = QdrantClient(
            host=host,
            port=port,
            api_key=api_key,
            timeout=60,
            prefer_grpc=True  # Better performance for large operations
        )
        
    def create_collection(self, collection_name: str, vector_size: int = 1536):
        """Create collection with optimized settings for document search"""
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
                on_disk=True  # Store vectors on disk for large collections
            ),
            optimizers_config={
                "default_segment_number": 2,
                "max_segment_size": 20000,
                "indexing_threshold": 10000
            },
            hnsw_config={
                "m": 16,
                "ef_construct": 100,
                "full_scan_threshold": 10000
            }
        )
```

### Collection Design Patterns

#### Document Collections
- **legal_documents**: Legal regulations and compliance documents
- **technical_reports**: R&D reports and technical documentation
- **policies**: Internal policies and operational procedures
- **news_articles**: Relevant news and external information
- **user_uploads**: User-uploaded documents with permission metadata

#### Metadata Schema
```python
document_metadata = {
    "document_id": str,
    "title": str,
    "document_type": str,  # legal, technical, policy, news, user
    "department": str,
    "access_level": int,   # 1-5 permission levels
    "created_date": str,
    "updated_date": str,
    "file_format": str,    # pdf, hwp, docx, txt
    "language": str,       # ko, en
    "version": str,
    "keywords": List[str],
    "summary": str,
    "chunk_index": int,    # For document chunking
    "total_chunks": int,
    "file_path": str,
    "user_permissions": List[str]  # User IDs with access
}
```

## Embedding and Indexing Strategies

### Document Processing Pipeline
```python
class DocumentProcessor:
    def __init__(self, embedding_model, qdrant_manager):
        self.embedding_model = embedding_model
        self.qdrant = qdrant_manager
        
    def process_document(self, document: Dict, collection_name: str):
        """Process and index document with chunking strategy"""
        chunks = self.chunk_document(document['content'])
        points = []
        
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding = self.embedding_model.encode(chunk['text'])
            
            # Create metadata
            metadata = {
                **document['metadata'],
                'chunk_index': i,
                'total_chunks': len(chunks),
                'chunk_text': chunk['text'][:500],  # Preview
                'chunk_type': chunk['type']  # paragraph, table, header
            }
            
            # Create point for Qdrant
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding.tolist(),
                payload=metadata
            )
            points.append(point)
        
        # Batch upload to Qdrant
        self.qdrant.client.upsert(
            collection_name=collection_name,
            points=points,
            wait=True
        )
```

### Chunking Strategies
- **Semantic Chunking**: Split documents based on semantic boundaries
- **Fixed-Size Chunking**: Consistent chunk sizes with overlap
- **Hierarchical Chunking**: Different granularities for different content types
- **Table-Aware Chunking**: Special handling for tabular data
- **Metadata-Preserving Chunking**: Maintain document structure information

## Search and Retrieval Patterns

### Advanced Search Implementation
```python
class AdvancedSearch:
    def __init__(self, qdrant_manager, reranker_model=None):
        self.qdrant = qdrant_manager
        self.reranker = reranker_model
        
    def hybrid_search(self, query: str, collection_name: str, user_permissions: List[str], top_k: int = 10):
        """Combine vector search with filtering and reranking"""
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)
        
        # Search with permission filtering
        search_results = self.qdrant.client.search(
            collection_name=collection_name,
            query_vector=query_embedding.tolist(),
            query_filter={
                "must": [
                    {
                        "key": "user_permissions",
                        "match": {"any": user_permissions}
                    }
                ]
            },
            limit=top_k * 2,  # Get more results for reranking
            score_threshold=0.7,
            with_payload=True,
            with_vectors=False
        )
        
        # Rerank results if reranker is available
        if self.reranker:
            reranked_results = self.rerank_results(query, search_results)
            return reranked_results[:top_k]
        
        return search_results[:top_k]
        
    def multi_collection_search(self, query: str, collections: List[str], user_permissions: List[str]):
        """Search across multiple collections and merge results"""
        all_results = []
        
        for collection in collections:
            results = self.hybrid_search(query, collection, user_permissions)
            for result in results:
                result.payload['source_collection'] = collection
            all_results.extend(results)
        
        # Sort by relevance score
        all_results.sort(key=lambda x: x.score, reverse=True)
        return all_results
```

### Permission-Based Filtering
```python
def create_permission_filter(user_role: str, department: str, access_level: int):
    """Create Qdrant filter based on user permissions"""
    return {
        "must": [
            {
                "key": "access_level",
                "range": {"lte": access_level}
            }
        ],
        "should": [
            {
                "key": "department",
                "match": {"value": department}
            },
            {
                "key": "document_type",
                "match": {"value": "public"}
            }
        ]
    }
```

## Real-Time Data Management

### Incremental Updates
```python
class IncrementalUpdater:
    def __init__(self, qdrant_manager):
        self.qdrant = qdrant_manager
        
    def update_document(self, document_id: str, updated_content: str, collection_name: str):
        """Update existing document with new content"""
        
        # Remove old document chunks
        self.qdrant.client.delete(
            collection_name=collection_name,
            points_selector={
                "filter": {
                    "must": [
                        {
                            "key": "document_id",
                            "match": {"value": document_id}
                        }
                    ]
                }
            }
        )
        
        # Process and add updated document
        self.process_document(updated_content, collection_name)
        
    def handle_duplicate_detection(self, new_document: Dict, collection_name: str):
        """Detect and handle duplicate documents"""
        
        # Search for similar documents
        similar_docs = self.qdrant.client.search(
            collection_name=collection_name,
            query_vector=new_document['embedding'],
            query_filter={
                "must": [
                    {
                        "key": "title",
                        "match": {"value": new_document['title']}
                    }
                ]
            },
            limit=5,
            score_threshold=0.95
        )
        
        if similar_docs:
            # Handle duplicate based on business logic
            return self.resolve_duplicate(new_document, similar_docs)
        
        return True  # No duplicates found
```

## Performance Optimization

### Indexing Optimization
- **Batch Operations**: Process multiple documents in batches
- **Async Processing**: Use async operations for large-scale updates
- **Memory Management**: Optimize memory usage for large embeddings
- **Disk Storage**: Use on-disk storage for large collections
- **Compression**: Enable vector compression for storage efficiency

### Query Optimization
```python
class QueryOptimizer:
    def __init__(self, qdrant_manager):
        self.qdrant = qdrant_manager
        self.query_cache = {}  # Simple cache implementation
        
    def optimized_search(self, query: str, collection_name: str, cache_duration: int = 300):
        """Implement caching and query optimization"""
        
        # Check cache first
        cache_key = f"{query}:{collection_name}"
        if cache_key in self.query_cache:
            cached_result, timestamp = self.query_cache[cache_key]
            if time.time() - timestamp < cache_duration:
                return cached_result
        
        # Perform search
        results = self.hybrid_search(query, collection_name)
        
        # Cache results
        self.query_cache[cache_key] = (results, time.time())
        
        return results
```

## Monitoring and Maintenance

### Health Monitoring
```python
def monitor_qdrant_health():
    """Monitor Qdrant cluster health and performance"""
    
    # Check collection status
    collections = client.get_collections()
    for collection in collections.collections:
        collection_info = client.get_collection(collection.name)
        
        print(f"Collection: {collection.name}")
        print(f"Vectors count: {collection_info.vectors_count}")
        print(f"Indexed vectors: {collection_info.indexed_vectors_count}")
        print(f"Status: {collection_info.status}")
        
    # Check memory usage
    cluster_info = client.get_cluster_info()
    print(f"Cluster status: {cluster_info}")
```

### Backup and Recovery
- **Regular Snapshots**: Automated collection snapshots
- **Point-in-Time Recovery**: Restore to specific timestamps
- **Cross-Cluster Replication**: Disaster recovery setup
- **Data Validation**: Verify index integrity after operations
- **Performance Metrics**: Monitor query latency and throughput
