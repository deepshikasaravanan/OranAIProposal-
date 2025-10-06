"""
RAG (Retrieval Augmented Generation) System for Proposal Bot
Provides semantic document search, knowledge retrieval, and context-aware generation
"""

import os
import json
import pickle
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime
import logging

# Vector embedding imports
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    HAS_VECTOR_LIBS = True
except ImportError:
    HAS_VECTOR_LIBS = False

# Additional ML imports
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import sent_tokenize, word_tokenize
    HAS_NLP_LIBS = True
except ImportError:
    HAS_NLP_LIBS = False

@dataclass
class DocumentChunk:
    """Represents a chunk of document content with metadata"""
    id: str
    content: str
    source_file: str
    chunk_index: int
    section: str
    page_number: Optional[int]
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    keywords: List[str] = None

@dataclass
class SearchResult:
    """Represents a search result with relevance scoring"""
    chunk: DocumentChunk
    relevance_score: float
    context_snippet: str
    highlight_positions: List[Tuple[int, int]]

class RAGKnowledgeBase:
    """Knowledge base for storing and retrieving document chunks"""
    
    def __init__(self, storage_path: str = "rag_storage"):
        self.storage_path = storage_path
        self.chunks: List[DocumentChunk] = []
        self.index_built = False
        
        # Initialize vector storage
        self.vector_index = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        
        # Load pre-trained models if available
        if HAS_VECTOR_LIBS:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.vector_dim = 384  # Dimension for all-MiniLM-L6-v2
            except Exception:
                self.embedding_model = None
                self.vector_dim = 0
        else:
            self.embedding_model = None
            self.vector_dim = 0
        
        # Create storage directory
        os.makedirs(storage_path, exist_ok=True)
        
        # Load existing knowledge base
        self._load_knowledge_base()
    
    def add_document(self, file_path: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> List[str]:
        """Add a document to the knowledge base by chunking and indexing it"""
        if metadata is None:
            metadata = {}
        
        # Generate document chunks
        chunks = self._chunk_document(content, file_path, metadata)
        
        # Add chunks to knowledge base
        chunk_ids = []
        for chunk in chunks:
            # Generate embeddings if model available
            if self.embedding_model:
                try:
                    chunk.embedding = self.embedding_model.encode(chunk.content)
                except Exception as e:
                    logging.warning(f"Failed to generate embedding for chunk {chunk.id}: {e}")
            
            # Extract keywords
            chunk.keywords = self._extract_keywords(chunk.content)
            
            self.chunks.append(chunk)
            chunk_ids.append(chunk.id)
        
        # Mark index for rebuild
        self.index_built = False
        
        # Save updated knowledge base
        self._save_knowledge_base()
        
        return chunk_ids
    
    def search(self, query: str, top_k: int = 5, search_type: str = "hybrid") -> List[SearchResult]:
        """Search the knowledge base using various methods"""
        if not self.chunks:
            return []
        
        # Rebuild index if needed
        if not self.index_built:
            self._build_indexes()
        
        results = []
        
        if search_type == "semantic" and self.embedding_model:
            results = self._semantic_search(query, top_k)
        elif search_type == "keyword":
            results = self._keyword_search(query, top_k)
        elif search_type == "hybrid":
            # Combine semantic and keyword search
            semantic_results = self._semantic_search(query, top_k) if self.embedding_model else []
            keyword_results = self._keyword_search(query, top_k)
            results = self._combine_search_results(semantic_results, keyword_results, top_k)
        else:
            # Fallback to simple text matching
            results = self._simple_text_search(query, top_k)
        
        return results
    
    def get_context_for_generation(self, query: str, max_context_length: int = 2000) -> str:
        """Get relevant context for RAG generation"""
        search_results = self.search(query, top_k=10, search_type="hybrid")
        
        context_parts = []
        current_length = 0
        
        for result in search_results:
            chunk_text = f"[Source: {result.chunk.source_file}]\n{result.chunk.content}\n"
            
            if current_length + len(chunk_text) > max_context_length:
                break
            
            context_parts.append(chunk_text)
            current_length += len(chunk_text)
        
        return "\n---\n".join(context_parts)
    
    def _chunk_document(self, content: str, file_path: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Split document into semantic chunks"""
        chunks = []
        
        # Simple sentence-based chunking with overlap
        sentences = self._split_into_sentences(content)
        
        chunk_size = 3  # Number of sentences per chunk
        overlap = 1     # Sentence overlap between chunks
        
        for i in range(0, len(sentences), chunk_size - overlap):
            chunk_sentences = sentences[i:i + chunk_size]
            chunk_content = " ".join(chunk_sentences)
            
            if len(chunk_content.strip()) < 50:  # Skip very short chunks
                continue
            
            chunk_id = self._generate_chunk_id(file_path, i)
            
            chunk = DocumentChunk(
                id=chunk_id,
                content=chunk_content,
                source_file=os.path.basename(file_path),
                chunk_index=i,
                section=metadata.get('section', 'Unknown'),
                page_number=metadata.get('page_number'),
                metadata=metadata.copy()
            )
            
            chunks.append(chunk)
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        if HAS_NLP_LIBS:
            try:
                return sent_tokenize(text)
            except Exception:
                pass
        
        # Fallback to simple splitting
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        if HAS_NLP_LIBS:
            try:
                # Download stopwords if not available
                try:
                    stop_words = set(stopwords.words('english'))
                except:
                    nltk.download('stopwords', quiet=True)
                    stop_words = set(stopwords.words('english'))
                
                # Tokenize and filter
                words = word_tokenize(text.lower())
                keywords = [word for word in words 
                           if word.isalpha() and word not in stop_words and len(word) > 3]
                
                return list(set(keywords))[:20]  # Return top 20 unique keywords
            except Exception:
                pass
        
        # Fallback to simple word extraction
        import re
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        return list(set(words))[:20]
    
    def _semantic_search(self, query: str, top_k: int) -> List[SearchResult]:
        """Perform semantic search using embeddings"""
        if not self.embedding_model or self.vector_index is None:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Ensure query embedding is the right shape and type
            if len(query_embedding.shape) == 1:
                query_embedding = query_embedding.reshape(1, -1)
            query_embedding = query_embedding.astype('float32')
            
            # Normalize query embedding for cosine similarity
            import faiss
            faiss.normalize_L2(query_embedding)
            
            # Search vector index
            scores, indices = self.vector_index.search(
                query_embedding, 
                min(top_k, len(self.chunks))
            )
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and idx < len(self.chunks):  # Check for valid index
                    chunk = self.chunks[idx]
                    result = SearchResult(
                        chunk=chunk,
                        relevance_score=float(score),
                        context_snippet=self._create_context_snippet(chunk.content, query),
                        highlight_positions=self._find_highlight_positions(chunk.content, query)
                    )
                    results.append(result)
            
            return results
        except Exception as e:
            logging.error(f"Semantic search failed: {e}")
            return []
    
    def _keyword_search(self, query: str, top_k: int) -> List[SearchResult]:
        """Perform keyword-based search using TF-IDF"""
        if not self.tfidf_vectorizer or self.tfidf_matrix is None:
            return []
        
        try:
            # Transform query
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            
            # Get top results
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                similarity_score = float(similarities[idx])
                if similarity_score > 0:  # Only include relevant results
                    chunk = self.chunks[idx]
                    result = SearchResult(
                        chunk=chunk,
                        relevance_score=similarity_score,
                        context_snippet=self._create_context_snippet(chunk.content, query),
                        highlight_positions=self._find_highlight_positions(chunk.content, query)
                    )
                    results.append(result)
            
            return results
        except Exception as e:
            logging.error(f"Keyword search failed: {e}")
            return []
    
    def _simple_text_search(self, query: str, top_k: int) -> List[SearchResult]:
        """Simple text matching search as fallback"""
        query_words = set(query.lower().split())
        results = []
        
        for chunk in self.chunks:
            chunk_words = set(chunk.content.lower().split())
            common_words = query_words.intersection(chunk_words)
            
            if common_words:
                relevance_score = len(common_words) / len(query_words)
                result = SearchResult(
                    chunk=chunk,
                    relevance_score=relevance_score,
                    context_snippet=self._create_context_snippet(chunk.content, query),
                    highlight_positions=self._find_highlight_positions(chunk.content, query)
                )
                results.append(result)
        
        # Sort by relevance and return top_k
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:top_k]
    
    def _combine_search_results(self, semantic_results: List[SearchResult], 
                               keyword_results: List[SearchResult], top_k: int) -> List[SearchResult]:
        """Combine semantic and keyword search results"""
        # Create a dict to merge results by chunk ID
        combined = {}
        
        # Add semantic results with weight
        for result in semantic_results:
            combined[result.chunk.id] = result
            combined[result.chunk.id].relevance_score *= 0.7  # Weight semantic higher
        
        # Add keyword results with weight
        for result in keyword_results:
            if result.chunk.id in combined:
                # Average the scores if chunk exists in both
                combined[result.chunk.id].relevance_score = (
                    combined[result.chunk.id].relevance_score + result.relevance_score * 0.3
                ) / 2
            else:
                result.relevance_score *= 0.3  # Weight keyword lower
                combined[result.chunk.id] = result
        
        # Sort by combined relevance score
        results = list(combined.values())
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results[:top_k]
    
    def _create_context_snippet(self, content: str, query: str, max_length: int = 200) -> str:
        """Create a context snippet highlighting query terms"""
        query_words = query.lower().split()
        content_lower = content.lower()
        
        # Find best position to center snippet
        best_pos = 0
        max_matches = 0
        
        for i in range(len(content) - max_length):
            snippet = content_lower[i:i + max_length]
            matches = sum(word in snippet for word in query_words)
            if matches > max_matches:
                max_matches = matches
                best_pos = i
        
        snippet = content[best_pos:best_pos + max_length]
        if best_pos > 0:
            snippet = "..." + snippet
        if best_pos + max_length < len(content):
            snippet = snippet + "..."
        
        return snippet
    
    def _find_highlight_positions(self, content: str, query: str) -> List[Tuple[int, int]]:
        """Find positions of query terms in content for highlighting"""
        positions = []
        query_words = query.lower().split()
        content_lower = content.lower()
        
        for word in query_words:
            start = 0
            while True:
                pos = content_lower.find(word, start)
                if pos == -1:
                    break
                positions.append((pos, pos + len(word)))
                start = pos + 1
        
        return positions
    
    def _build_indexes(self):
        """Build search indexes"""
        if not self.chunks:
            return
        
        # Build vector index
        if self.embedding_model and HAS_VECTOR_LIBS:
            try:
                embeddings = []
                for chunk in self.chunks:
                    if chunk.embedding is not None:
                        embeddings.append(chunk.embedding)
                    else:
                        # Generate embedding if missing
                        embedding = self.embedding_model.encode(chunk.content)
                        chunk.embedding = embedding
                        embeddings.append(embedding)
                
                if embeddings:
                    embeddings_array = np.array(embeddings).astype('float32')
                    self.vector_index = faiss.IndexFlatIP(self.vector_dim)  # Inner product index
                    faiss.normalize_L2(embeddings_array)  # Normalize for cosine similarity
                    self.vector_index.add(embeddings_array)
            except Exception as e:
                logging.error(f"Failed to build vector index: {e}")
        
        # Build TF-IDF index
        if HAS_NLP_LIBS:
            try:
                documents = [chunk.content for chunk in self.chunks]
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
            except Exception as e:
                logging.error(f"Failed to build TF-IDF index: {e}")
        
        self.index_built = True
    
    def _generate_chunk_id(self, file_path: str, chunk_index: int) -> str:
        """Generate unique chunk ID"""
        content = f"{file_path}_{chunk_index}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _save_knowledge_base(self):
        """Save knowledge base to disk"""
        try:
            # Save chunks metadata (without embeddings)
            chunks_data = []
            for chunk in self.chunks:
                chunk_data = {
                    'id': chunk.id,
                    'content': chunk.content,
                    'source_file': chunk.source_file,
                    'chunk_index': chunk.chunk_index,
                    'section': chunk.section,
                    'page_number': chunk.page_number,
                    'metadata': chunk.metadata,
                    'keywords': chunk.keywords
                }
                chunks_data.append(chunk_data)
            
            # Save to JSON
            with open(os.path.join(self.storage_path, 'chunks.json'), 'w') as f:
                json.dump(chunks_data, f, indent=2)
            
            # Save embeddings separately
            if self.chunks and self.chunks[0].embedding is not None:
                embeddings = np.array([chunk.embedding for chunk in self.chunks])
                np.save(os.path.join(self.storage_path, 'embeddings.npy'), embeddings)
            
        except Exception as e:
            logging.error(f"Failed to save knowledge base: {e}")
    
    def _load_knowledge_base(self):
        """Load knowledge base from disk"""
        try:
            chunks_path = os.path.join(self.storage_path, 'chunks.json')
            embeddings_path = os.path.join(self.storage_path, 'embeddings.npy')
            
            if os.path.exists(chunks_path):
                with open(chunks_path, 'r') as f:
                    chunks_data = json.load(f)
                
                # Load embeddings if available
                embeddings = None
                if os.path.exists(embeddings_path):
                    embeddings = np.load(embeddings_path)
                
                # Recreate chunks
                self.chunks = []
                for i, chunk_data in enumerate(chunks_data):
                    chunk = DocumentChunk(
                        id=chunk_data['id'],
                        content=chunk_data['content'],
                        source_file=chunk_data['source_file'],
                        chunk_index=chunk_data['chunk_index'],
                        section=chunk_data['section'],
                        page_number=chunk_data.get('page_number'),
                        metadata=chunk_data.get('metadata', {}),
                        keywords=chunk_data.get('keywords', [])
                    )
                    
                    # Add embedding if available
                    if embeddings is not None and i < len(embeddings):
                        chunk.embedding = embeddings[i]
                    
                    self.chunks.append(chunk)
                
                logging.info(f"Loaded {len(self.chunks)} chunks from knowledge base")
        
        except Exception as e:
            logging.warning(f"Failed to load knowledge base: {e}")

class RAGProposalGenerator:
    """RAG-enhanced proposal generator"""
    
    def __init__(self, knowledge_base: RAGKnowledgeBase):
        self.knowledge_base = knowledge_base
    
    def generate_section_with_context(self, section_title: str, requirements: List[str], 
                                     query: str, max_context_length: int = 1500) -> Dict[str, Any]:
        """Generate proposal section using RAG context"""
        # Get relevant context from knowledge base
        context = self.knowledge_base.get_context_for_generation(query, max_context_length)
        
        # Search for specific requirement-related content
        requirement_context = ""
        for req in requirements[:5]:  # Limit to first 5 requirements
            req_results = self.knowledge_base.search(req, top_k=2, search_type="hybrid")
            for result in req_results:
                requirement_context += f"Requirement: {req}\nRelevant Content: {result.chunk.content}\n\n"
        
        # Combine contexts
        full_context = f"General Context:\n{context}\n\nRequirement-Specific Context:\n{requirement_context}"
        
        return {
            "section_title": section_title,
            "context_used": full_context,
            "context_length": len(full_context),
            "sources_referenced": len(self.knowledge_base.search(query, top_k=10)),
            "generation_ready": True,
            "prompt_template": self._create_generation_prompt(section_title, requirements, full_context)
        }
    
    def _create_generation_prompt(self, section_title: str, requirements: List[str], context: str) -> str:
        """Create a prompt for AI generation with RAG context"""
        return f"""You are writing a proposal section for "{section_title}".

REQUIREMENTS TO ADDRESS:
{chr(10).join(f"- {req}" for req in requirements)}

RELEVANT CONTEXT FROM KNOWLEDGE BASE:
{context}

Please write a comprehensive, compliant proposal section that:
1. Addresses all listed requirements
2. Uses information from the provided context
3. Maintains federal contracting language and tone
4. Includes specific citations to source materials
5. Provides concrete implementation details

Section Content:"""

# Initialize global RAG system
rag_system = RAGKnowledgeBase()

# Function to initialize RAG with project documents
def initialize_rag_knowledge_base():
    """Initialize RAG knowledge base with existing project documents"""
    
    # Add example documents to knowledge base
    examples_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples")
    
    if os.path.exists(examples_dir):
        for filename in os.listdir(examples_dir):
            if filename.endswith(('.md', '.txt', '.yaml', '.json')):
                file_path = os.path.join(examples_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    metadata = {
                        'document_type': filename.split('.')[-1],
                        'category': 'example',
                        'added_date': datetime.now().isoformat()
                    }
                    
                    rag_system.add_document(file_path, content, metadata)
                    print(f"Added {filename} to RAG knowledge base")
                    
                except Exception as e:
                    print(f"Failed to add {filename}: {e}")
    
    # Add prompts to knowledge base
    prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
    
    if os.path.exists(prompts_dir):
        for filename in os.listdir(prompts_dir):
            if filename.endswith('.md'):
                file_path = os.path.join(prompts_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    metadata = {
                        'document_type': 'prompt',
                        'category': 'guidance',
                        'added_date': datetime.now().isoformat()
                    }
                    
                    rag_system.add_document(file_path, content, metadata)
                    print(f"Added {filename} to RAG knowledge base")
                    
                except Exception as e:
                    print(f"Failed to add {filename}: {e}")

# Export main components
__all__ = [
    'RAGKnowledgeBase',
    'RAGProposalGenerator', 
    'DocumentChunk',
    'SearchResult',
    'rag_system',
    'initialize_rag_knowledge_base'
]