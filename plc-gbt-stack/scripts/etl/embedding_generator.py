#!/usr/bin/env python3
"""
OpenAI Embedding Generator
Phase 3 Day 2: Embedding Generation Pipeline
Version: 1.0.0

This module handles embedding generation using OpenAI's text-embedding-3-large model:
- Batch processing for efficiency
- Error handling and retries
- Caching to avoid duplicate API calls
- Progress tracking for large datasets
"""

import os
import time
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import pickle

import openai
from openai import OpenAI
import numpy as np
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class EmbeddingGenerator:
    """Generates embeddings using OpenAI's API."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "text-embedding-3-large",
        dimensions: int = 3072,
        cache_dir: Optional[Path] = None
    ):
        """
        Initialize embedding generator.
        
        Args:
            api_key: OpenAI API key (uses env var if not provided)
            model: Embedding model to use
            dimensions: Embedding dimensions (3072 for large, 1536 for small)
            cache_dir: Directory for caching embeddings
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("No OpenAI API key found - will use mock embeddings")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
            
        self.model = model
        self.dimensions = dimensions
        self.cache_dir = cache_dir or Path("./embedding_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Track API usage
        self.api_calls = 0
        self.tokens_used = 0
        
    def generate_embedding(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            use_cache: Whether to use cached embeddings
            
        Returns:
            Embedding vector
        """
        if not text:
            return [0.0] * self.dimensions
            
        # Check cache
        if use_cache:
            cached = self._get_cached_embedding(text)
            if cached is not None:
                logger.debug("Using cached embedding", text_preview=text[:50])
                return cached
                
        # Generate embedding
        if self.client:
            embedding = self._call_openai_api([text])[0]
        else:
            # Mock embedding for testing
            embedding = self._generate_mock_embedding(text)
            
        # Cache the result
        if use_cache:
            self._cache_embedding(text, embedding)
            
        return embedding
        
    def generate_embeddings_batch(
        self, 
        texts: List[str], 
        batch_size: int = 100,
        use_cache: bool = True,
        show_progress: bool = True
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts per API call
            use_cache: Whether to use cached embeddings
            show_progress: Whether to show progress
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        # Check cache first
        if use_cache:
            for i, text in enumerate(texts):
                cached = self._get_cached_embedding(text)
                if cached is not None:
                    embeddings.append(cached)
                else:
                    embeddings.append(None)
                    uncached_texts.append(text)
                    uncached_indices.append(i)
                    
            logger.info(
                f"Found {len(texts) - len(uncached_texts)} cached embeddings, "
                f"need to generate {len(uncached_texts)} new ones"
            )
        else:
            uncached_texts = texts
            uncached_indices = list(range(len(texts)))
            embeddings = [None] * len(texts)
            
        # Generate embeddings for uncached texts
        if uncached_texts:
            if self.client:
                # Process in batches
                for i in range(0, len(uncached_texts), batch_size):
                    batch = uncached_texts[i:i + batch_size]
                    
                    if show_progress:
                        progress = (i + len(batch)) / len(uncached_texts) * 100
                        logger.info(f"Generating embeddings: {progress:.1f}% complete")
                        
                    batch_embeddings = self._call_openai_api(batch)
                    
                    # Update results and cache
                    for j, (text, embedding) in enumerate(zip(batch, batch_embeddings)):
                        idx = uncached_indices[i + j]
                        embeddings[idx] = embedding
                        if use_cache:
                            self._cache_embedding(text, embedding)
                            
            else:
                # Generate mock embeddings
                for i, text in enumerate(uncached_texts):
                    idx = uncached_indices[i]
                    embedding = self._generate_mock_embedding(text)
                    embeddings[idx] = embedding
                    if use_cache:
                        self._cache_embedding(text, embedding)
                        
        return embeddings
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60)
    )
    def _call_openai_api(self, texts: List[str]) -> List[List[float]]:
        """
        Call OpenAI API with retry logic.
        
        Args:
            texts: Texts to embed
            
        Returns:
            List of embeddings
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts,
                dimensions=self.dimensions
            )
            
            self.api_calls += 1
            self.tokens_used += response.usage.total_tokens
            
            embeddings = [data.embedding for data in response.data]
            
            logger.debug(
                f"Generated {len(embeddings)} embeddings, "
                f"used {response.usage.total_tokens} tokens"
            )
            
            return embeddings
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
            
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Generate deterministic mock embedding for testing."""
        # Use hash to ensure same text gets same embedding
        text_hash = hashlib.md5(text.encode()).hexdigest()
        seed = int(text_hash[:8], 16)
        np.random.seed(seed)
        
        # Generate normalized random vector
        embedding = np.random.randn(self.dimensions)
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding.tolist()
        
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        return f"{self.model}_{self.dimensions}_{text_hash}"
        
    def _get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Retrieve embedding from cache."""
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cached embedding: {str(e)}")
                
        return None
        
    def _cache_embedding(self, text: str, embedding: List[float]):
        """Save embedding to cache."""
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(embedding, f)
        except Exception as e:
            logger.warning(f"Failed to cache embedding: {str(e)}")
            
    def embed_plc_component(self, component: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate embedding for a PLC component.
        
        Args:
            component: PLC component data
            
        Returns:
            Component with embedding added
        """
        # Create text representation
        text_parts = []
        
        # Add component type and name
        component_type = component.get('type', 'Unknown')
        name = component.get('name', 'Unnamed')
        text_parts.append(f"{component_type}: {name}")
        
        # Add description if available
        if component.get('description'):
            text_parts.append(f"Description: {component['description']}")
            
        # Add type-specific information
        if component_type == 'Routine':
            if component.get('language'):
                text_parts.append(f"Language: {component['language']}")
            if component.get('rung_count'):
                text_parts.append(f"Rungs: {component['rung_count']}")
                
        elif component_type == 'AOI':
            if component.get('revision'):
                text_parts.append(f"Revision: {component['revision']}")
            if component.get('parameters'):
                text_parts.append(f"Parameters: {component['parameters']}")
                
        elif component_type == 'UDT':
            if component.get('size'):
                text_parts.append(f"Size: {component['size']} bytes")
            if component.get('members'):
                text_parts.append(f"Members: {component['members']}")
                
        # Generate embedding
        text = " | ".join(text_parts)
        embedding = self.generate_embedding(text)
        
        # Add to component
        component['embedding'] = embedding
        component['embedding_text'] = text
        component['embedding_model'] = self.model
        component['embedding_dimensions'] = self.dimensions
        
        return component
        
    def embed_document_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate embedding for a document chunk.
        
        Args:
            chunk: Document chunk data
            
        Returns:
            Chunk with embedding added
        """
        text = chunk.get('text', '')
        
        # Add metadata context if available
        metadata = chunk.get('metadata', {})
        if metadata.get('source_document'):
            text = f"Document: {metadata['source_document']} | {text}"
            
        # Generate embedding
        embedding = self.generate_embedding(text)
        
        # Add to chunk
        chunk['embedding'] = embedding
        chunk['embedding_model'] = self.model
        chunk['embedding_dimensions'] = self.dimensions
        
        return chunk
        
    def embed_qa_pair(self, qa: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate embedding for a Q&A pair.
        
        Args:
            qa: Q&A pair data
            
        Returns:
            Q&A pair with embedding added
        """
        # Combine question and answer for embedding
        question = qa.get('question', '')
        answer = qa.get('answer', '')
        text = f"Q: {question} A: {answer}"
        
        # Generate embedding
        embedding = self.generate_embedding(text)
        
        # Add to Q&A pair
        qa['embedding'] = embedding
        qa['embedding_model'] = self.model
        qa['embedding_dimensions'] = self.dimensions
        
        return qa
        
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics."""
        return {
            'api_calls': self.api_calls,
            'tokens_used': self.tokens_used,
            'estimated_cost': self._estimate_cost(),
            'cache_size': len(list(self.cache_dir.glob("*.pkl")))
        }
        
    def _estimate_cost(self) -> float:
        """Estimate API cost based on usage."""
        # Pricing for text-embedding-3-large (as of 2024)
        cost_per_1k_tokens = 0.00013
        return (self.tokens_used / 1000) * cost_per_1k_tokens


def main():
    """Main execution for testing."""
    generator = EmbeddingGenerator()
    
    # Test single embedding
    test_text = "This is a test of the MotorControl_AOI for motor speed control"
    embedding = generator.generate_embedding(test_text)
    
    print("\n" + "="*60)
    print("EMBEDDING GENERATOR TEST")
    print("="*60)
    
    print(f"\nTest text: {test_text}")
    print(f"Embedding dimensions: {len(embedding)}")
    print(f"Embedding preview: {embedding[:5]}...")
    
    # Test batch embeddings
    test_texts = [
        "PLCProgram: TestController with firmware version 35.00",
        "Routine: MainRoutine using Ladder Logic with 2 rungs",
        "AOI: MotorControl_AOI for speed control and monitoring",
        "UDT: MotorData_UDT with 20 bytes containing speed and status"
    ]
    
    print("\n\nBatch embedding test:")
    embeddings = generator.generate_embeddings_batch(test_texts)
    
    for text, embedding in zip(test_texts, embeddings):
        print(f"\nText: {text[:50]}...")
        print(f"Embedding: {embedding[:3]}...")
        
    # Test PLC component embedding
    test_component = {
        'type': 'AOI',
        'name': 'MotorControl_AOI',
        'description': 'Motor control Add-On Instruction for speed control',
        'revision': '1.0',
        'parameters': 'Start, Stop, SpeedSetpoint, MotorData'
    }
    
    print("\n\nPLC component embedding test:")
    embedded_component = generator.embed_plc_component(test_component)
    print(f"Component: {embedded_component['name']}")
    print(f"Embedding text: {embedded_component['embedding_text']}")
    print(f"Embedding generated: {'embedding' in embedded_component}")
    
    # Show usage stats
    stats = generator.get_usage_stats()
    print(f"\n\nUsage Statistics:")
    print(f"API calls: {stats['api_calls']}")
    print(f"Tokens used: {stats['tokens_used']}")
    print(f"Estimated cost: ${stats['estimated_cost']:.4f}")
    print(f"Cached embeddings: {stats['cache_size']}")


if __name__ == "__main__":
    main() 