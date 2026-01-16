"""
Pinecone Vector Database Integration
=====================================

Handles embedding generation and vector storage/retrieval for RAG.
"""

import os
from typing import List, Dict, Optional
from pathlib import Path
from pinecone import Pinecone, ServerlessSpec
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class PineconeKnowledgeBase:
    """
    Manages knowledge base with Pinecone vector database.
    Provides semantic search for RAG.
    """
    
    def __init__(
        self,
        index_name: str = "maply-knowledge-base",
        dimension: int = 768,  # Gemini embedding dimension
        metric: str = "cosine"
    ):
        """
        Initialize Pinecone knowledge base.
        
        Args:
            index_name: Name of the Pinecone index
            dimension: Embedding dimension (768 for Gemini)
            metric: Distance metric (cosine, euclidean, dotproduct)
        """
        # Initialize Pinecone
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
        
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric
        
        # Initialize Gemini for embeddings
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.gemini_client = genai.Client(api_key=gemini_key)
        
        # Create or connect to index
        self._setup_index()
        
        print(f"✓ Pinecone knowledge base initialized: {index_name}")
    
    def _setup_index(self):
        """Create Pinecone index if it doesn't exist."""
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            print(f"Creating new Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            print(f"✓ Index created: {self.index_name}")
        else:
            print(f"✓ Connected to existing index: {self.index_name}")
        
        # Connect to index
        self.index = self.pc.Index(self.index_name)
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using Gemini.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding
        """
        try:
            result = self.gemini_client.models.embed_content(
                model="models/text-embedding-004",
                content=text
            )
            return result.embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * self.dimension
    
    def chunk_document(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[Dict[str, str]]:
        """
        Split document into overlapping chunks.
        
        Args:
            text: Document text
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk_text.rfind('.')
                last_newline = chunk_text.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:  # At least 50% of chunk
                    end = start + break_point + 1
                    chunk_text = text[start:end]
            
            chunks.append({
                "text": chunk_text.strip(),
                "start": start,
                "end": end
            })
            
            start = end - overlap
        
        return chunks
    
    def index_knowledge_base(self, kb_path: Path, namespace: str = "default"):
        """
        Index the knowledge base document into Pinecone.
        
        Args:
            kb_path: Path to knowledge base markdown file
            namespace: Pinecone namespace for organization
        """
        print(f"\n📚 Indexing knowledge base: {kb_path.name}")
        
        # Load knowledge base
        with open(kb_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into sections based on headers
        sections = self._split_by_headers(content)
        
        print(f"Found {len(sections)} sections")
        
        # Process each section
        vectors = []
        for i, section in enumerate(sections):
            # Generate embedding
            embedding = self.generate_embedding(section['text'])
            
            # Create vector
            vector = {
                "id": f"{namespace}_{i}",
                "values": embedding,
                "metadata": {
                    "text": section['text'][:1000],  # Store first 1000 chars
                    "full_text": section['text'],
                    "section": section['title'],
                    "type": section['type'],
                    "source": "knowledge_base.md"
                }
            }
            vectors.append(vector)
            
            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(sections)} sections...")
        
        # Upsert to Pinecone
        print(f"Uploading {len(vectors)} vectors to Pinecone...")
        self.index.upsert(vectors=vectors, namespace=namespace)
        
        print(f"✓ Knowledge base indexed successfully!")
        print(f"  Total vectors: {len(vectors)}")
        print(f"  Namespace: {namespace}")
    
    def _split_by_headers(self, content: str) -> List[Dict]:
        """Split markdown content by headers."""
        sections = []
        lines = content.split('\n')
        
        current_section = {
            'title': 'Introduction',
            'type': 'general',
            'text': ''
        }
        
        for line in lines:
            if line.startswith('## '):
                # Save previous section
                if current_section['text'].strip():
                    sections.append(current_section)
                
                # Start new section
                title = line.replace('##', '').strip()
                section_type = self._classify_section(title)
                current_section = {
                    'title': title,
                    'type': section_type,
                    'text': line + '\n'
                }
            else:
                current_section['text'] += line + '\n'
        
        # Add last section
        if current_section['text'].strip():
            sections.append(current_section)
        
        return sections
    
    def _classify_section(self, title: str) -> str:
        """Classify section type based on title."""
        title_lower = title.lower()
        
        if 'risk score' in title_lower:
            return 'risk_score'
        elif 'sentiment' in title_lower:
            return 'sentiment'
        elif 'explainability' in title_lower or 'explainable' in title_lower:
            return 'explainability'
        elif 'technical' in title_lower:
            return 'technical'
        else:
            return 'general'
    
    def search(
        self,
        query: str,
        top_k: int = 3,
        namespace: str = "default",
        filter_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Semantic search in knowledge base.
        
        Args:
            query: Search query
            top_k: Number of results to return
            namespace: Pinecone namespace
            filter_type: Optional filter by section type
            
        Returns:
            List of matching documents with metadata
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        
        # Build filter
        filter_dict = None
        if filter_type:
            filter_dict = {"type": {"$eq": filter_type}}
        
        # Search
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            namespace=namespace,
            include_metadata=True,
            filter=filter_dict
        )
        
        # Format results
        documents = []
        for match in results.matches:
            documents.append({
                "text": match.metadata.get('full_text', match.metadata.get('text', '')),
                "section": match.metadata.get('section', 'Unknown'),
                "type": match.metadata.get('type', 'general'),
                "score": match.score,
                "id": match.id
            })
        
        return documents
    
    def get_stats(self, namespace: str = "default") -> Dict:
        """Get index statistics."""
        stats = self.index.describe_index_stats()
        return {
            "total_vectors": stats.total_vector_count,
            "dimension": stats.dimension,
            "namespaces": dict(stats.namespaces) if stats.namespaces else {}
        }
    
    def delete_namespace(self, namespace: str):
        """Delete all vectors in a namespace."""
        self.index.delete(delete_all=True, namespace=namespace)
        print(f"✓ Deleted namespace: {namespace}")
    
    def delete_index(self):
        """Delete the entire index."""
        self.pc.delete_index(self.index_name)
        print(f"✓ Deleted index: {self.index_name}")


def setup_knowledge_base():
    """
    Setup script to index the knowledge base into Pinecone.
    Run this once to initialize the vector database.
    """
    print("\n" + "="*70)
    print("  Pinecone Knowledge Base Setup")
    print("="*70 + "\n")
    
    try:
        # Initialize Pinecone
        kb = PineconeKnowledgeBase()
        
        # Path to knowledge base
        kb_path = Path(__file__).parent / "knowledge_base.md"
        
        if not kb_path.exists():
            print(f"❌ Knowledge base not found: {kb_path}")
            return
        
        # Index knowledge base
        kb.index_knowledge_base(kb_path)
        
        # Show stats
        print("\n" + "="*70)
        print("  Index Statistics")
        print("="*70)
        stats = kb.get_stats()
        print(f"Total vectors: {stats['total_vectors']}")
        print(f"Dimension: {stats['dimension']}")
        print(f"Namespaces: {stats['namespaces']}")
        
        # Test search
        print("\n" + "="*70)
        print("  Testing Search")
        print("="*70 + "\n")
        
        test_queries = [
            "How does the risk score model work?",
            "Explain sentiment analysis",
            "Why is the system explainable?"
        ]
        
        for query in test_queries:
            print(f"Query: {query}")
            results = kb.search(query, top_k=2)
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['section']} (score: {result['score']:.3f})")
            print()
        
        print("="*70)
        print("✓ Setup complete! Knowledge base is ready for use.")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    setup_knowledge_base()
