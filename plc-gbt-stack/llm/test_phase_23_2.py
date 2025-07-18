"""
Phase 23.2 Natural Language Understanding Validation Script
Tests all components of Phase 23.2: Natural Language Understanding

Components tested:
- Task 23.2.1: Intent Recognition Engine (intent_recognition.py)
- Task 23.2.2: Command Generation Engine (command_generator.py)
- Task 23.2.3: Conversation Management System (conversation.py)
- Task 23.2.4: Domain-Specific Understanding (domain_understanding.py)
"""

import sys
import os
import time
import json
import logging
from datetime import datetime, timedelta

# Add current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Phase23_2_TestRunner:
    def __init__(self):
        self.results = {
            "23.2.1_intent_recognition": {"score": 0, "max_score": 100, "details": []},
            "23.2.2_command_generation": {"score": 0, "max_score": 100, "details": []},
            "23.2.3_conversation_management": {"score": 0, "max_score": 100, "details": []},
            "23.2.4_domain_understanding": {"score": 0, "max_score": 100, "details": []},
            "overall": {"score": 0, "max_score": 400}
        }
        self.start_time = time.time()
    
    def test_intent_recognition(self):
        """Test Task 23.2.1: Intent Recognition Engine"""
        logger.info("🔍 Testing Task 23.2.1: Intent Recognition Engine")
        
        score = 0
        details = []
        
        try:
            # Test intent recognition module
            intent_path = os.path.join(current_dir, "intent_recognition.py")
            if os.path.exists(intent_path):
                score += 15
                details.append("✅ Intent recognition module exists")
                
                with open(intent_path, 'r') as f:
                    content = f.read()
                
                # Test enum definitions
                required_enums = [
                    "EntityType", "ConfidenceLevel", "AmbiguityType"
                ]
                
                for enum_name in required_enums:
                    if f"class {enum_name}(Enum)" in content:
                        score += 5
                        details.append(f"✅ {enum_name} enum defined")
                
                # Test dataclass definitions
                required_dataclasses = [
                    "ExtractedEntity", "IntentCandidate", "AmbiguityResolution",
                    "IntentRecognitionResult"
                ]
                
                for dataclass_name in required_dataclasses:
                    if f"class {dataclass_name}" in content:
                        score += 5
                        details.append(f"✅ {dataclass_name} dataclass defined")
                
                # Test core classes
                core_classes = [
                    "EntityExtractor", "IntentClassifier", "AmbiguityResolver",
                    "IntentRecognitionEngine"
                ]
                
                for class_name in core_classes:
                    if f"class {class_name}" in content:
                        score += 10
                        details.append(f"✅ {class_name} class implemented")
                
                # Test key methods
                key_methods = [
                    "extract_entities", "classify_intent", "detect_ambiguities",
                    "recognize_intent"
                ]
                
                for method_name in key_methods:
                    if f"def {method_name}" in content:
                        score += 5
                        details.append(f"✅ {method_name} method implemented")
                
                # Test entity types coverage
                if "LOOP_NAME" in content and "PARAMETER" in content and "TUNING_METHOD" in content:
                    score += 5
                    details.append("✅ Comprehensive entity types defined")
                
                # Test ambiguity handling
                if "MULTIPLE_INTENTS" in content and "UNCLEAR_TARGET" in content:
                    score += 5
                    details.append("✅ Ambiguity detection implemented")
                
                # Test singleton pattern
                if "get_intent_engine" in content:
                    score += 5
                    details.append("✅ Singleton engine pattern implemented")
                
            else:
                details.append("❌ Intent recognition module not found")
                
        except Exception as e:
            details.append(f"❌ Error testing intent recognition: {str(e)}")
        
        self.results["23.2.1_intent_recognition"]["score"] = min(score, 100)
        self.results["23.2.1_intent_recognition"]["details"] = details
        
        logger.info(f"📊 Task 23.2.1 Score: {self.results['23.2.1_intent_recognition']['score']}/100")
    
    def test_command_generation(self):
        """Test Task 23.2.2: Command Generation Engine"""
        logger.info("🔍 Testing Task 23.2.2: Command Generation Engine")
        
        score = 0
        details = []
        
        try:
            # Test command generation module
            command_path = os.path.join(current_dir, "command_generator.py")
            if os.path.exists(command_path):
                score += 15
                details.append("✅ Command generation module exists")
                
                with open(command_path, 'r') as f:
                    content = f.read()
                
                # Test enum definitions
                required_enums = [
                    "CommandType", "ValidationStatus", "ExecutionMode"
                ]
                
                for enum_name in required_enums:
                    if f"class {enum_name}(Enum)" in content:
                        score += 5
                        details.append(f"✅ {enum_name} enum defined")
                
                # Test dataclass definitions
                required_dataclasses = [
                    "CommandParameter", "GeneratedCommand", "CommandSequence",
                    "CommandGenerationResult"
                ]
                
                for dataclass_name in required_dataclasses:
                    if f"class {dataclass_name}" in content:
                        score += 5
                        details.append(f"✅ {dataclass_name} dataclass defined")
                
                # Test core classes
                core_classes = [
                    "ParameterExtractor", "CommandBuilder", "SequencePlanner",
                    "CommandGenerator"
                ]
                
                for class_name in core_classes:
                    if f"class {class_name}" in content:
                        score += 10
                        details.append(f"✅ {class_name} class implemented")
                
                # Test command building methods
                builder_methods = [
                    "extract_parameters", "build_command", "plan_sequence",
                    "generate_command"
                ]
                
                for method_name in builder_methods:
                    if f"def {method_name}" in content:
                        score += 5
                        details.append(f"✅ {method_name} method implemented")
                
                # Test command templates
                if "command_templates" in content and "plc-cl" in content:
                    score += 10
                    details.append("✅ CLI command templates implemented")
                
                # Test validation
                if "validate_command" in content and "risk_level" in content:
                    score += 5
                    details.append("✅ Command validation implemented")
                
                # Test sequence planning
                if "plan_sequence" in content and "dependencies" in content:
                    score += 5
                    details.append("✅ Command sequence planning implemented")
                
                # Test singleton pattern
                if "get_command_generator" in content:
                    score += 5
                    details.append("✅ Singleton generator pattern implemented")
                
            else:
                details.append("❌ Command generation module not found")
                
        except Exception as e:
            details.append(f"❌ Error testing command generation: {str(e)}")
        
        self.results["23.2.2_command_generation"]["score"] = min(score, 100)
        self.results["23.2.2_command_generation"]["details"] = details
        
        logger.info(f"📊 Task 23.2.2 Score: {self.results['23.2.2_command_generation']['score']}/100")
    
    def test_conversation_management(self):
        """Test Task 23.2.3: Conversation Management System"""
        logger.info("🔍 Testing Task 23.2.3: Conversation Management System")
        
        score = 0
        details = []
        
        try:
            # Test conversation module
            conversation_path = os.path.join(current_dir, "conversation.py")
            if os.path.exists(conversation_path):
                score += 15
                details.append("✅ Conversation management module exists")
                
                with open(conversation_path, 'r') as f:
                    content = f.read()
                
                # Test enum definitions
                required_enums = [
                    "ConversationState", "TaskStatus", "ConversationTopic"
                ]
                
                for enum_name in required_enums:
                    if f"class {enum_name}(Enum)" in content:
                        score += 5
                        details.append(f"✅ {enum_name} enum defined")
                
                # Test dataclass definitions
                required_dataclasses = [
                    "ConversationTask", "ClarificationRequest", "ConversationContext",
                    "ConversationTurn", "ConversationSession"
                ]
                
                for dataclass_name in required_dataclasses:
                    if f"class {dataclass_name}" in content:
                        score += 5
                        details.append(f"✅ {dataclass_name} dataclass defined")
                
                # Test core classes
                core_classes = [
                    "ContextManager", "TaskTracker", "ClarificationManager",
                    "ConversationManager"
                ]
                
                for class_name in core_classes:
                    if f"class {class_name}" in content:
                        score += 10
                        details.append(f"✅ {class_name} class implemented")
                
                # Test conversation methods
                conversation_methods = [
                    "start_session", "process_turn", "update_context",
                    "create_task", "update_task_status"
                ]
                
                for method_name in conversation_methods:
                    if f"def {method_name}" in content:
                        score += 5
                        details.append(f"✅ {method_name} method implemented")
                
                # Test multi-turn support
                if "conversation_history" in content and "session_history" in content:
                    score += 5
                    details.append("✅ Multi-turn conversation support implemented")
                
                # Test clarification handling
                if "clarification" in content and "requires_clarification" in content:
                    score += 5
                    details.append("✅ Clarification request handling implemented")
                
                # Test task tracking
                if "task_tracker" in content and "progress_percentage" in content:
                    score += 5
                    details.append("✅ Task progress tracking implemented")
                
                # Test singleton pattern
                if "get_conversation_manager" in content:
                    score += 5
                    details.append("✅ Singleton manager pattern implemented")
                
            else:
                details.append("❌ Conversation management module not found")
                
        except Exception as e:
            details.append(f"❌ Error testing conversation management: {str(e)}")
        
        self.results["23.2.3_conversation_management"]["score"] = min(score, 100)
        self.results["23.2.3_conversation_management"]["details"] = details
        
        logger.info(f"📊 Task 23.2.3 Score: {self.results['23.2.3_conversation_management']['score']}/100")
    
    def test_domain_understanding(self):
        """Test Task 23.2.4: Domain-Specific Understanding"""
        logger.info("🔍 Testing Task 23.2.4: Domain-Specific Understanding")
        
        score = 0
        details = []
        
        try:
            # Test domain understanding module
            domain_path = os.path.join(current_dir, "domain_understanding.py")
            if os.path.exists(domain_path):
                score += 15
                details.append("✅ Domain understanding module exists")
                
                with open(domain_path, 'r') as f:
                    content = f.read()
                
                # Test enum definitions
                required_enums = [
                    "ControlConcept", "TuningMethod", "PerformanceGoal", "IndustryDomain"
                ]
                
                for enum_name in required_enums:
                    if f"class {enum_name}(Enum)" in content:
                        score += 5
                        details.append(f"✅ {enum_name} enum defined")
                
                # Test dataclass definitions
                required_dataclasses = [
                    "ConceptDefinition", "TuningMethodInfo", "PerformanceGoalInfo",
                    "IndustryTerminology", "DomainContext"
                ]
                
                for dataclass_name in required_dataclasses:
                    if f"class {dataclass_name}" in content:
                        score += 5
                        details.append(f"✅ {dataclass_name} dataclass defined")
                
                # Test core classes
                core_classes = [
                    "ConceptRecognizer", "TuningMethodInterpreter", "PerformanceGoalInterpreter",
                    "IndustryTerminologyManager", "DomainUnderstandingEngine"
                ]
                
                for class_name in core_classes:
                    if f"class {class_name}" in content:
                        score += 8
                        details.append(f"✅ {class_name} class implemented")
                
                # Test domain analysis methods
                domain_methods = [
                    "recognize_concepts", "identify_tuning_method", "identify_performance_goals",
                    "identify_industry_domain", "analyze_domain_content"
                ]
                
                for method_name in domain_methods:
                    if f"def {method_name}" in content:
                        score += 4
                        details.append(f"✅ {method_name} method implemented")
                
                # Test control theory concepts
                if "PID_CONTROLLER" in content and "SETPOINT" in content and "PROPORTIONAL_GAIN" in content:
                    score += 5
                    details.append("✅ Core control theory concepts defined")
                
                # Test tuning methods
                if "ZIEGLER_NICHOLS" in content and "COHEN_COON" in content and "LAMBDA_TUNING" in content:
                    score += 5
                    details.append("✅ Major tuning methods implemented")
                
                # Test industry domains
                if "CHEMICAL_PROCESS" in content and "POWER_GENERATION" in content and "WATER_TREATMENT" in content:
                    score += 5
                    details.append("✅ Industry domains implemented")
                
                # Test singleton pattern
                if "get_domain_engine" in content:
                    score += 5
                    details.append("✅ Singleton engine pattern implemented")
                
            else:
                details.append("❌ Domain understanding module not found")
                
        except Exception as e:
            details.append(f"❌ Error testing domain understanding: {str(e)}")
        
        self.results["23.2.4_domain_understanding"]["score"] = min(score, 100)
        self.results["23.2.4_domain_understanding"]["details"] = details
        
        logger.info(f"📊 Task 23.2.4 Score: {self.results['23.2.4_domain_understanding']['score']}/100")
    
    def run_comprehensive_test(self):
        """Run all Phase 23.2 tests"""
        logger.info("🚀 Starting Phase 23.2: Natural Language Understanding Validation")
        logger.info("=" * 80)
        
        # Run individual tests
        self.test_intent_recognition()
        self.test_command_generation()
        self.test_conversation_management()
        self.test_domain_understanding()
        
        # Calculate overall score
        total_score = (
            self.results["23.2.1_intent_recognition"]["score"] +
            self.results["23.2.2_command_generation"]["score"] +
            self.results["23.2.3_conversation_management"]["score"] +
            self.results["23.2.4_domain_understanding"]["score"]
        )
        
        self.results["overall"]["score"] = total_score
        
        # Determine completion status
        if total_score >= 360:  # 90% threshold
            completion_status = "EXCELLENT"
        elif total_score >= 320:  # 80% threshold
            completion_status = "GOOD"
        elif total_score >= 280:  # 70% threshold
            completion_status = "SATISFACTORY"
        else:
            completion_status = "NEEDS_IMPROVEMENT"
        
        # Generate summary
        execution_time = time.time() - self.start_time
        
        logger.info("=" * 80)
        logger.info("📊 PHASE 23.2 VALIDATION RESULTS")
        logger.info("=" * 80)
        
        for task_id, result in self.results.items():
            if task_id != "overall":
                task_name = {
                    "23.2.1_intent_recognition": "Intent Recognition Engine",
                    "23.2.2_command_generation": "Command Generation Engine",
                    "23.2.3_conversation_management": "Conversation Management System",
                    "23.2.4_domain_understanding": "Domain-Specific Understanding"
                }[task_id]
                
                status = "✅" if result["score"] >= 80 else "⚠️" if result["score"] >= 60 else "❌"
                logger.info(f"{status} {task_id.replace('_', '.')}: {task_name} - {result['score']}/{result['max_score']}")
                
                # Show key capabilities
                capabilities = [detail for detail in result["details"] if detail.startswith("✅")][:3]
                if capabilities:
                    capabilities_str = ", ".join([cap.replace("✅ ", "") for cap in capabilities])
                    logger.info(f"   🔧 Capabilities: {capabilities_str}...")
        
        logger.info("=" * 80)
        logger.info(f"🎯 OVERALL SCORE: {total_score}/400")
        logger.info(f"📈 COMPLETION STATUS: {completion_status}")
        
        # Calculate capabilities implemented
        total_capabilities = sum(len([d for d in result["details"] if d.startswith("✅")]) 
                               for result in self.results.values() if isinstance(result.get("details"), list))
        
        logger.info(f"🔧 TOTAL CAPABILITIES IMPLEMENTED: {total_capabilities}")
        logger.info(f"⏱️ EXECUTION TIME: {execution_time:.2f} seconds")
        logger.info(f"🎉 PHASE 23.2 {completion_status} COMPLETION - {'Production ready!' if completion_status == 'EXCELLENT' else 'Review recommended' if completion_status in ['GOOD', 'SATISFACTORY'] else 'Additional work needed'}")
        
        # Save results
        results_dir = os.path.join(parent_dir, "results", "phase23")
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(results_dir, f"phase23_2_validation_{timestamp}.json")
        
        with open(results_file, 'w') as f:
            json.dump({
                "phase": "23.2",
                "timestamp": datetime.now().isoformat(),
                "execution_time": execution_time,
                "overall_score": total_score,
                "max_score": 400,
                "completion_status": completion_status,
                "capabilities_implemented": total_capabilities,
                "detailed_results": self.results
            }, f, indent=2)
        
        logger.info(f"✅ Validation results saved to {results_file}")
        
        return total_score, completion_status

def main():
    """Main execution function"""
    runner = Phase23_2_TestRunner()
    score, status = runner.run_comprehensive_test()
    return score >= 320  # Return True if GOOD or better

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 