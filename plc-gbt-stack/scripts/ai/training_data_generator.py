#!/usr/bin/env python3
"""
Training Data Generator for Phase 4 Fine-Tuning
Creates gold standard Q&A pairs for OpenAI fine-tuning

This module:
- Extracts existing Q&A pairs from Neo4j and documents
- Generates new domain-specific Q&A pairs
- Formats data for OpenAI fine-tuning (JSONL)
- Validates and curates training examples
- Creates target 300-1000 high-quality pairs
"""

import json
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
import random

# Database connections
from neo4j import GraphDatabase
from qdrant_client import QdrantClient
import openai

# Internal imports  
import sys
sys.path.append(str(Path(__file__).parent.parent))
from query.knowledge_graph_interface import PLCKnowledgeGraph
from etl.embedding_generator import EmbeddingGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrainingDataGenerator:
    """Generates high-quality training data for PLC domain fine-tuning."""
    
    def __init__(self, 
                 neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_user: str = "neo4j", 
                 neo4j_password: str = "plc-gpt-2024",
                 openai_api_key: Optional[str] = None):
        """Initialize training data generator."""
        
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        
        # Initialize OpenAI for data generation
        if openai_api_key:
            openai.api_key = openai_api_key
        
        self.kg = PLCKnowledgeGraph()
        self.embedding_generator = EmbeddingGenerator()
        
        # Training data categories
        self.categories = {
            "component_identification": "Identifying PLC components and their purposes",
            "configuration_guidance": "How to configure and set up PLC components",
            "troubleshooting": "Diagnosing and fixing PLC issues",
            "best_practices": "Industry best practices and recommendations",
            "safety_procedures": "Safety protocols and requirements",
            "integration_methods": "Connecting and integrating PLC systems",
            "programming_concepts": "PLC programming fundamentals and advanced techniques",
            "hardware_specifications": "Device specifications and compatibility"
        }
        
        self.target_counts = {
            "component_identification": 150,
            "configuration_guidance": 200,
            "troubleshooting": 150,
            "best_practices": 100,
            "safety_procedures": 100,
            "integration_methods": 100,
            "programming_concepts": 150,
            "hardware_specifications": 50
        }
        
    async def generate_complete_training_dataset(self) -> Dict[str, Any]:
        """Generate complete training dataset with target 1000 Q&A pairs."""
        logger.info("Starting complete training dataset generation")
        
        dataset = {
            "metadata": {
                "generated_date": datetime.now().isoformat(),
                "target_total": sum(self.target_counts.values()),
                "categories": self.categories,
                "format": "OpenAI fine-tuning JSONL",
                "model_target": "gpt-4o"
            },
            "training_data": [],
            "validation_data": [],
            "statistics": {}
        }
        
        # Step 1: Extract existing Q&A pairs
        existing_pairs = await self.extract_existing_qa_pairs()
        logger.info(f"Extracted {len(existing_pairs)} existing Q&A pairs")
        
        # Step 2: Generate new Q&A pairs by category
        generated_pairs = []
        for category, count in self.target_counts.items():
            logger.info(f"Generating {count} pairs for category: {category}")
            category_pairs = await self.generate_category_qa_pairs(category, count)
            generated_pairs.extend(category_pairs)
        
        # Step 3: Combine and enhance all pairs
        all_pairs = existing_pairs + generated_pairs
        enhanced_pairs = await self.enhance_qa_pairs(all_pairs)
        
        # Step 4: Split into training/validation (90/10)
        random.shuffle(enhanced_pairs)
        split_index = int(len(enhanced_pairs) * 0.9)
        
        dataset["training_data"] = enhanced_pairs[:split_index]
        dataset["validation_data"] = enhanced_pairs[split_index:]
        
        # Step 5: Generate statistics
        dataset["statistics"] = self.generate_dataset_statistics(enhanced_pairs)
        
        # Step 6: Export to JSONL format
        await self.export_to_jsonl(dataset)
        
        logger.info(f"Complete dataset generated: {len(enhanced_pairs)} total pairs")
        return dataset
    
    async def extract_existing_qa_pairs(self) -> List[Dict[str, Any]]:
        """Extract existing Q&A pairs from knowledge graph."""
        pairs = []
        
        try:
            # Get all Q&A pairs from Neo4j
            with self.kg.driver.session() as session:
                result = session.run("""
                    MATCH (qa:QuestionAnswer)
                    OPTIONAL MATCH (qa)-[:DERIVED_FROM]->(doc:SpecDoc)
                    RETURN qa.question as question,
                           qa.answer as answer,
                           qa.confidence as confidence,
                           qa.source_page as source_page,
                           doc.title as source_document
                    ORDER BY qa.confidence DESC
                """)
                
                for record in result:
                    if record["question"] and record["answer"]:
                        pairs.append({
                            "question": record["question"],
                            "answer": record["answer"],
                            "confidence": record["confidence"] or 0.8,
                            "source": record["source_document"] or "Knowledge Graph",
                            "category": self.classify_qa_category(record["question"], record["answer"]),
                            "enhanced": False
                        })
        
        except Exception as e:
            logger.warning(f"Could not extract from Neo4j: {e}")
        
        return pairs
    
    async def generate_category_qa_pairs(self, category: str, target_count: int) -> List[Dict[str, Any]]:
        """Generate Q&A pairs for specific category using domain knowledge."""
        pairs = []
        
        # Category-specific templates and knowledge
        templates = self.get_category_templates(category)
        domain_knowledge = await self.get_domain_knowledge_for_category(category)
        
        for i in range(target_count):
            try:
                # Generate using templates and domain knowledge
                pair = await self.generate_single_qa_pair(category, templates, domain_knowledge)
                if pair:
                    pairs.append(pair)
                    
                # Add delay to respect API rate limits
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.warning(f"Error generating pair {i} for {category}: {e}")
                continue
        
        return pairs
    
    def get_category_templates(self, category: str) -> Dict[str, List[str]]:
        """Get question/answer templates for each category."""
        templates = {
            "component_identification": {
                "questions": [
                    "What is the purpose of {component}?",
                    "How does {component} function in a PLC system?",
                    "What are the key features of {component}?",
                    "When would you use {component} in automation?",
                    "What are the specifications of {component}?"
                ],
                "contexts": ["AOI", "UDT", "Routine", "Device", "Tag", "Module", "Instruction"]
            },
            "configuration_guidance": {
                "questions": [
                    "How do you configure {component} for {application}?",
                    "What are the steps to set up {component}?",
                    "How do you program {component} in RSLogix 5000?",
                    "What parameters need to be configured for {component}?",
                    "How do you integrate {component} with {system}?"
                ],
                "contexts": ["motor control", "conveyor systems", "safety circuits", "communication", "I/O modules"]
            },
            "troubleshooting": {
                "questions": [
                    "How do you troubleshoot {problem} in {system}?",
                    "What causes {error} and how to fix it?",
                    "Why is {component} not working properly?",
                    "How to diagnose {symptom} in PLC systems?",
                    "What are common issues with {component}?"
                ],
                "contexts": ["communication errors", "I/O faults", "program errors", "hardware failures", "timing issues"]
            },
            "best_practices": {
                "questions": [
                    "What are best practices for {task}?",
                    "How should you structure {component} for maintainability?",
                    "What naming conventions should be used for {element}?",
                    "How to optimize {process} in PLC programming?",
                    "What safety considerations apply to {application}?"
                ],
                "contexts": ["program organization", "tag naming", "routine structure", "documentation", "version control"]
            },
            "safety_procedures": {
                "questions": [
                    "What safety procedures are required for {operation}?",
                    "How do you implement {safety_function}?",
                    "What are the safety requirements for {application}?",
                    "How to ensure {safety_aspect} in PLC systems?",
                    "What happens during {safety_event}?"
                ],
                "contexts": ["emergency stops", "safety interlocks", "fault monitoring", "redundancy", "lockout procedures"]
            },
            "integration_methods": {
                "questions": [
                    "How do you connect {device1} to {device2}?",
                    "What protocol is used for {communication_type}?",
                    "How to integrate {system} with PLC?",
                    "What are the wiring requirements for {connection}?",
                    "How do you configure {network} communication?"
                ],
                "contexts": ["Ethernet/IP", "DeviceNet", "ControlNet", "Serial", "Wireless", "HMI", "SCADA"]
            },
            "programming_concepts": {
                "questions": [
                    "How do you implement {programming_concept}?",
                    "What is the difference between {concept1} and {concept2}?",
                    "When should you use {instruction_type}?",
                    "How to create {structure} in ladder logic?",
                    "What are the advantages of {approach}?"
                ],
                "contexts": ["ladder logic", "function blocks", "structured text", "sequential function charts", "AOIs", "UDTs"]
            },
            "hardware_specifications": {
                "questions": [
                    "What are the specifications of {hardware}?",
                    "What is the maximum {parameter} for {device}?",
                    "How many {units} can {controller} support?",
                    "What are the power requirements for {module}?",
                    "What is the compatibility between {device1} and {device2}?"
                ],
                "contexts": ["CompactLogix", "ControlLogix", "I/O modules", "communication cards", "power supplies"]
            }
        }
        
        return templates.get(category, {"questions": [], "contexts": []})
    
    async def get_domain_knowledge_for_category(self, category: str) -> Dict[str, Any]:
        """Get relevant domain knowledge from knowledge graph for category."""
        knowledge = {"components": [], "relationships": [], "procedures": []}
        
        try:
            with self.kg.driver.session() as session:
                # Get relevant components based on category
                if category == "component_identification":
                    result = session.run("""
                        MATCH (n) WHERE n:AOI OR n:UDT OR n:Device OR n:Routine
                        RETURN labels(n)[0] as type, n.name as name, 
                               coalesce(n.description, '') as description
                        LIMIT 50
                    """)
                    knowledge["components"] = [dict(record) for record in result]
                
                elif category in ["configuration_guidance", "integration_methods"]:
                    result = session.run("""
                        MATCH (d:Device)
                        RETURN d.name as name, d.device_type as type,
                               coalesce(d.description, '') as description
                        LIMIT 30
                    """)
                    knowledge["components"] = [dict(record) for record in result]
                
                elif category == "troubleshooting":
                    result = session.run("""
                        MATCH (qa:QuestionAnswer)
                        WHERE toLower(qa.question) CONTAINS 'error' 
                           OR toLower(qa.question) CONTAINS 'fault'
                           OR toLower(qa.question) CONTAINS 'problem'
                        RETURN qa.question as question, qa.answer as answer
                        LIMIT 20
                    """)
                    knowledge["procedures"] = [dict(record) for record in result]
        
        except Exception as e:
            logger.warning(f"Could not get domain knowledge: {e}")
        
        return knowledge
    
    async def generate_single_qa_pair(self, category: str, templates: Dict, domain_knowledge: Dict) -> Optional[Dict[str, Any]]:
        """Generate a single Q&A pair using templates and domain knowledge."""
        
        # For now, generate using templates (in production, you'd use OpenAI API)
        template_questions = templates.get("questions", [])
        contexts = templates.get("contexts", [])
        
        if not template_questions or not contexts:
            return None
        
        # Select random template and context
        question_template = random.choice(template_questions)
        context = random.choice(contexts)
        
        # Generate question
        if "{component}" in question_template:
            question = question_template.replace("{component}", context)
        elif "{application}" in question_template:
            question = question_template.replace("{application}", context)
        elif "{system}" in question_template:
            question = question_template.replace("{system}", context)
        else:
            question = question_template
        
        # Generate appropriate answer based on category and context
        answer = self.generate_answer_for_context(category, context, question)
        
        return {
            "question": question,
            "answer": answer,
            "confidence": 0.85,
            "source": "Generated",
            "category": category,
            "enhanced": False
        }
    
    def generate_answer_for_context(self, category: str, context: str, question: str) -> str:
        """Generate contextually appropriate answers."""
        
        # Domain-specific answer templates
        answer_templates = {
            "component_identification": {
                "AOI": f"An Add-On Instruction (AOI) named {context} is a reusable code block that encapsulates specific functionality. It can be used across multiple routines and programs to maintain consistency and reduce development time.",
                "UDT": f"A User-Defined Type (UDT) called {context} is a custom data structure that groups related data elements together. It helps organize complex data and ensures consistency across the application.",
                "Device": f"The {context} device is a hardware component in the PLC system that performs specific I/O or communication functions. It must be properly configured in the I/O tree for correct operation.",
                "Routine": f"The {context} routine contains the program logic for a specific function or process. It can be written in ladder logic, function block diagram, or structured text."
            },
            "configuration_guidance": {
                "motor control": f"To configure {context}, first create the motor control AOI with appropriate parameters for speed, direction, and safety interlocks. Configure the I/O mapping in the controller and test the operation in a safe environment.",
                "conveyor systems": f"For {context} configuration, set up the conveyor speed control, direction logic, and safety systems. Ensure proper sensor integration and emergency stop functionality.",
                "safety circuits": f"Configuring {context} requires implementing redundant safety logic, proper diagnostic monitoring, and fail-safe operation modes according to safety standards.",
                "communication": f"To set up {context}, configure the network parameters, device addresses, and communication protocols. Test connectivity and monitor for communication errors."
            },
            "troubleshooting": {
                "communication errors": f"For {context}, check network cables, verify IP addresses, ensure proper routing, and monitor for packet loss. Use diagnostic tools to identify the root cause.",
                "I/O faults": f"When dealing with {context}, check wiring connections, verify module status, examine point configurations, and test individual I/O points.",
                "program errors": f"To resolve {context}, review program logic, check data types, verify tag references, and use online monitoring to identify the problem area."
            }
        }
        
        category_templates = answer_templates.get(category, {})
        return category_templates.get(context, f"This relates to {context} in the context of {category}. Proper implementation requires following industry best practices and manufacturer guidelines.")
    
    def classify_qa_category(self, question: str, answer: str) -> str:
        """Classify Q&A pair into appropriate category."""
        question_lower = question.lower()
        answer_lower = answer.lower()
        
        # Classification keywords
        if any(word in question_lower for word in ["what is", "purpose", "function"]):
            return "component_identification"
        elif any(word in question_lower for word in ["how to", "configure", "setup", "steps"]):
            return "configuration_guidance"
        elif any(word in question_lower for word in ["troubleshoot", "error", "fault", "problem", "fix"]):
            return "troubleshooting"
        elif any(word in question_lower for word in ["best practice", "recommend", "should", "proper"]):
            return "best_practices"
        elif any(word in question_lower for word in ["safety", "emergency", "interlock", "protection"]):
            return "safety_procedures"
        elif any(word in question_lower for word in ["connect", "integrate", "communication", "network"]):
            return "integration_methods"
        elif any(word in question_lower for word in ["program", "logic", "instruction", "ladder"]):
            return "programming_concepts"
        elif any(word in question_lower for word in ["specification", "maximum", "capacity", "power"]):
            return "hardware_specifications"
        else:
            return "component_identification"  # Default category
    
    async def enhance_qa_pairs(self, qa_pairs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance Q&A pairs with additional context and validation."""
        enhanced_pairs = []
        
        for pair in qa_pairs:
            try:
                # Add unique ID
                pair["id"] = str(uuid.uuid4())
                
                # Add metadata
                pair["word_count"] = len(pair["answer"].split())
                pair["created_date"] = datetime.now().isoformat()
                
                # Validate quality
                if self.validate_qa_quality(pair):
                    enhanced_pairs.append(pair)
                else:
                    logger.debug(f"Filtered out low-quality pair: {pair['question'][:50]}...")
                    
            except Exception as e:
                logger.warning(f"Error enhancing pair: {e}")
                continue
        
        return enhanced_pairs
    
    def validate_qa_quality(self, pair: Dict[str, Any]) -> bool:
        """Validate Q&A pair quality."""
        question = pair.get("question", "")
        answer = pair.get("answer", "")
        
        # Basic quality checks
        if len(question) < 10 or len(answer) < 20:
            return False
        
        if len(question) > 500 or len(answer) > 2000:
            return False
        
        # Check for meaningful content
        if question.count("?") != 1:
            return False
        
        # Check confidence threshold
        if pair.get("confidence", 0) < 0.7:
            return False
        
        return True
    
    def generate_dataset_statistics(self, qa_pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive dataset statistics."""
        stats = {
            "total_pairs": len(qa_pairs),
            "category_distribution": {},
            "quality_metrics": {},
            "content_analysis": {}
        }
        
        # Category distribution
        for pair in qa_pairs:
            category = pair.get("category", "unknown")
            stats["category_distribution"][category] = stats["category_distribution"].get(category, 0) + 1
        
        # Quality metrics
        confidences = [pair.get("confidence", 0) for pair in qa_pairs]
        word_counts = [pair.get("word_count", 0) for pair in qa_pairs]
        
        stats["quality_metrics"] = {
            "avg_confidence": sum(confidences) / len(confidences) if confidences else 0,
            "min_confidence": min(confidences) if confidences else 0,
            "max_confidence": max(confidences) if confidences else 0,
            "avg_answer_length": sum(word_counts) / len(word_counts) if word_counts else 0
        }
        
        # Content analysis
        all_text = " ".join([pair.get("question", "") + " " + pair.get("answer", "") for pair in qa_pairs])
        unique_words = len(set(all_text.lower().split()))
        
        stats["content_analysis"] = {
            "total_words": len(all_text.split()),
            "unique_words": unique_words,
            "vocabulary_richness": unique_words / len(all_text.split()) if all_text.split() else 0
        }
        
        return stats
    
    async def export_to_jsonl(self, dataset: Dict[str, Any]) -> None:
        """Export training data to JSONL format for OpenAI fine-tuning."""
        
        # Create output directory
        output_dir = Path("training_data")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export training data
        training_file = output_dir / f"plc_training_{timestamp}.jsonl"
        with open(training_file, 'w') as f:
            for pair in dataset["training_data"]:
                training_example = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a PLC expert assistant. Provide accurate, detailed answers about PLC programming, configuration, and troubleshooting."
                        },
                        {
                            "role": "user", 
                            "content": pair["question"]
                        },
                        {
                            "role": "assistant",
                            "content": pair["answer"]
                        }
                    ]
                }
                f.write(json.dumps(training_example) + "\n")
        
        # Export validation data
        validation_file = output_dir / f"plc_validation_{timestamp}.jsonl"
        with open(validation_file, 'w') as f:
            for pair in dataset["validation_data"]:
                validation_example = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a PLC expert assistant. Provide accurate, detailed answers about PLC programming, configuration, and troubleshooting."
                        },
                        {
                            "role": "user",
                            "content": pair["question"]
                        },
                        {
                            "role": "assistant",
                            "content": pair["answer"]
                        }
                    ]
                }
                f.write(json.dumps(validation_example) + "\n")
        
        # Export metadata
        metadata_file = output_dir / f"dataset_metadata_{timestamp}.json"
        with open(metadata_file, 'w') as f:
            json.dump(dataset["metadata"], f, indent=2)
        
        # Export statistics
        stats_file = output_dir / f"dataset_statistics_{timestamp}.json"
        with open(stats_file, 'w') as f:
            json.dump(dataset["statistics"], f, indent=2)
        
        logger.info(f"Training data exported to:")
        logger.info(f"  Training: {training_file}")
        logger.info(f"  Validation: {validation_file}")
        logger.info(f"  Metadata: {metadata_file}")
        logger.info(f"  Statistics: {stats_file}")


async def main():
    """Main execution for training data generation."""
    generator = TrainingDataGenerator()
    
    try:
        dataset = await generator.generate_complete_training_dataset()
        
        print("\n" + "="*60)
        print("TRAINING DATA GENERATION COMPLETE")
        print("="*60)
        print(f"Total Q&A pairs: {dataset['statistics']['total_pairs']}")
        print(f"Training pairs: {len(dataset['training_data'])}")
        print(f"Validation pairs: {len(dataset['validation_data'])}")
        print("\nCategory Distribution:")
        for category, count in dataset['statistics']['category_distribution'].items():
            print(f"  {category}: {count}")
        
        print(f"\nQuality Metrics:")
        print(f"  Avg Confidence: {dataset['statistics']['quality_metrics']['avg_confidence']:.2f}")
        print(f"  Avg Answer Length: {dataset['statistics']['quality_metrics']['avg_answer_length']:.1f} words")
        
        print("\nFiles exported to training_data/ directory")
        print("Ready for OpenAI fine-tuning!")
        
    except Exception as e:
        logger.error(f"Error generating training data: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 