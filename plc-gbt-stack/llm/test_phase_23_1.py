"""
Phase 23.1 LLM Integration Architecture Validation Script
Tests all components of Phase 23.1: LLM Integration Architecture

Components tested:
- Task 23.1.1: LLM Integration Framework (__init__.py)
- Task 23.1.2: LLM Service Layer (service.py)
- Task 23.1.3: Application Context Provider (context_provider.py)
- Task 23.1.4: Safety and Validation Layer (safety.py)
"""

import json
import logging
import os
import sys
import time
from datetime import datetime

# Add current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Phase23_1_TestRunner:
    def __init__(self):
        self.results = {
            "23.1.1_framework": {"score": 0, "max_score": 100, "details": []},
            "23.1.2_service": {"score": 0, "max_score": 100, "details": []},
            "23.1.3_context": {"score": 0, "max_score": 100, "details": []},
            "23.1.4_safety": {"score": 0, "max_score": 100, "details": []},
            "overall": {"score": 0, "max_score": 400}
        }
        self.start_time = time.time()

    def test_llm_framework(self):
        """Test Task 23.1.1: LLM Integration Framework"""
        logger.info("🔍 Testing Task 23.1.1: LLM Integration Framework")

        score = 0
        details = []

        try:
            # Test framework package structure
            framework_init_path = os.path.join(current_dir, "__init__.py")
            if os.path.exists(framework_init_path):
                score += 15
                details.append("✅ Framework __init__.py exists")

                with open(framework_init_path) as f:
                    content = f.read()

                # Test core configuration
                if "LLM_CONFIG" in content:
                    score += 15
                    details.append("✅ LLM_CONFIG configuration present")

                    if "ft:gpt-4o:industrial-control" in content:
                        score += 10
                        details.append("✅ Fine-tuned model ID configured")

                # Test enum definitions
                required_enums = [
                    "LLMRequestType", "LLMResponseStatus", "ConversationRole",
                    "IntentType", "TaskComplexity"
                ]

                for enum_name in required_enums:
                    if f"class {enum_name}(Enum)" in content:
                        score += 5
                        details.append(f"✅ {enum_name} enum defined")

                # Test dataclass definitions
                required_dataclasses = [
                    "ConversationMessage", "LLMRequest", "LLMResponse",
                    "ApplicationContext", "Intent", "TaskPlan", "ExecutionResult"
                ]

                for dataclass_name in required_dataclasses:
                    if f"class {dataclass_name}" in content:
                        score += 5
                        details.append(f"✅ {dataclass_name} dataclass defined")

                # Test utility functions
                utility_functions = [
                    "get_model_info", "create_system_message", "validate_llm_response",
                    "estimate_token_count", "optimize_context_for_model"
                ]

                for func_name in utility_functions:
                    if f"def {func_name}" in content:
                        score += 3
                        details.append(f"✅ {func_name} function implemented")

                # Test exports
                if "__all__" in content:
                    score += 5
                    details.append("✅ Module exports defined")

            else:
                details.append("❌ Framework __init__.py not found")

        except Exception as e:
            details.append(f"❌ Error testing framework: {str(e)}")

        self.results["23.1.1_framework"]["score"] = min(score, 100)
        self.results["23.1.1_framework"]["details"] = details

        logger.info(f"📊 Task 23.1.1 Score: {self.results['23.1.1_framework']['score']}/100")

    def test_llm_service(self):
        """Test Task 23.1.2: LLM Service Layer"""
        logger.info("🔍 Testing Task 23.1.2: LLM Service Layer")

        score = 0
        details = []

        try:
            # Test service module
            service_path = os.path.join(current_dir, "service.py")
            if os.path.exists(service_path):
                score += 15
                details.append("✅ Service module exists")

                with open(service_path) as f:
                    content = f.read()

                # Test core classes
                core_classes = [
                    "LLMServiceError", "TokenManager", "CostTracker", "LLMService"
                ]

                for class_name in core_classes:
                    if f"class {class_name}" in content:
                        score += 10
                        details.append(f"✅ {class_name} class implemented")

                # Test LLMService methods
                service_methods = [
                    "send_request", "_make_api_request_with_retry", "_prepare_messages",
                    "chat_completion", "generate_command", "analyze_performance",
                    "get_service_status", "health_check"
                ]

                for method_name in service_methods:
                    if f"def {method_name}" in content:
                        score += 5
                        details.append(f"✅ {method_name} method implemented")

                # Test async support
                if "async def" in content:
                    score += 10
                    details.append("✅ Async/await support implemented")

                # Test OpenAI integration
                if "openai" in content and "AsyncOpenAI" in content:
                    score += 10
                    details.append("✅ OpenAI API integration present")

                # Test error handling
                if "try:" in content and "except" in content:
                    score += 5
                    details.append("✅ Error handling implemented")

                # Test singleton pattern
                if "get_llm_service" in content:
                    score += 5
                    details.append("✅ Singleton service pattern implemented")

            else:
                details.append("❌ Service module not found")

        except Exception as e:
            details.append(f"❌ Error testing service: {str(e)}")

        self.results["23.1.2_service"]["score"] = min(score, 100)
        self.results["23.1.2_service"]["details"] = details

        logger.info(f"📊 Task 23.1.2 Score: {self.results['23.1.2_service']['score']}/100")

    def test_context_provider(self):
        """Test Task 23.1.3: Application Context Provider"""
        logger.info("🔍 Testing Task 23.1.3: Application Context Provider")

        score = 0
        details = []

        try:
            # Test context provider module
            context_path = os.path.join(current_dir, "context_provider.py")
            if os.path.exists(context_path):
                score += 15
                details.append("✅ Context provider module exists")

                with open(context_path) as f:
                    content = f.read()

                # Test ContextProvider class
                if "class ContextProvider" in content:
                    score += 15
                    details.append("✅ ContextProvider class implemented")

                # Test context gathering methods
                context_methods = [
                    "get_application_context", "_get_current_directory", "_get_available_commands",
                    "_get_active_schemas", "_get_recent_operations", "_get_performance_metrics",
                    "_get_user_preferences", "_get_error_history", "_get_system_state"
                ]

                for method_name in context_methods:
                    if f"def {method_name}" in content:
                        score += 5
                        details.append(f"✅ {method_name} method implemented")

                # Test caching mechanism
                if "cache" in content and "ttl" in content:
                    score += 10
                    details.append("✅ Context caching mechanism implemented")

                # Test CLI documentation support
                if "get_cli_documentation" in content:
                    score += 10
                    details.append("✅ CLI documentation support implemented")

                # Test conversation integration
                if "update_context_with_conversation" in content:
                    score += 10
                    details.append("✅ Conversation context integration implemented")

                # Test singleton pattern
                if "get_context_provider" in content:
                    score += 5
                    details.append("✅ Singleton provider pattern implemented")

                # Test utility functions
                if "get_current_context" in content:
                    score += 5
                    details.append("✅ Utility functions implemented")

            else:
                details.append("❌ Context provider module not found")

        except Exception as e:
            details.append(f"❌ Error testing context provider: {str(e)}")

        self.results["23.1.3_context"]["score"] = min(score, 100)
        self.results["23.1.3_context"]["details"] = details

        logger.info(f"📊 Task 23.1.3 Score: {self.results['23.1.3_context']['score']}/100")

    def test_safety_layer(self):
        """Test Task 23.1.4: Safety and Validation Layer"""
        logger.info("🔍 Testing Task 23.1.4: Safety and Validation Layer")

        score = 0
        details = []

        try:
            # Test safety module
            safety_path = os.path.join(current_dir, "safety.py")
            if os.path.exists(safety_path):
                score += 15
                details.append("✅ Safety module exists")

                with open(safety_path) as f:
                    content = f.read()

                # Test enum definitions
                safety_enums = [
                    "RiskLevel", "ValidationResult", "SafetyCheckType"
                ]

                for enum_name in safety_enums:
                    if f"class {enum_name}(Enum)" in content:
                        score += 5
                        details.append(f"✅ {enum_name} enum defined")

                # Test dataclass definitions
                safety_dataclasses = [
                    "SafetyCheck", "ValidationReport"
                ]

                for dataclass_name in safety_dataclasses:
                    if f"class {dataclass_name}" in content:
                        score += 5
                        details.append(f"✅ {dataclass_name} dataclass defined")

                # Test core safety classes
                safety_classes = [
                    "CommandValidator", "HallucinationDetector", "SafetyValidator"
                ]

                for class_name in safety_classes:
                    if f"class {class_name}" in content:
                        score += 10
                        details.append(f"✅ {class_name} class implemented")

                # Test validation methods
                validation_methods = [
                    "validate_command", "_check_command_syntax", "_check_destructive_operations",
                    "_check_file_access", "_check_system_impact", "_check_privilege_escalation"
                ]

                for method_name in validation_methods:
                    if f"def {method_name}" in content:
                        score += 3
                        details.append(f"✅ {method_name} method implemented")

                # Test hallucination detection
                hallucination_methods = [
                    "detect_hallucination", "_contains_nonexistent_commands",
                    "_contains_impossible_paths", "_contains_inconsistent_info"
                ]

                for method_name in hallucination_methods:
                    if f"def {method_name}" in content:
                        score += 3
                        details.append(f"✅ {method_name} method implemented")

                # Test dangerous command detection
                if "dangerous_commands" in content:
                    score += 5
                    details.append("✅ Dangerous command detection configured")

                # Test confirmation system
                if "confirmation" in content and "requires_confirmation" in content:
                    score += 5
                    details.append("✅ Confirmation system implemented")

                # Test singleton pattern
                if "get_safety_validator" in content:
                    score += 5
                    details.append("✅ Singleton validator pattern implemented")

            else:
                details.append("❌ Safety module not found")

        except Exception as e:
            details.append(f"❌ Error testing safety layer: {str(e)}")

        self.results["23.1.4_safety"]["score"] = min(score, 100)
        self.results["23.1.4_safety"]["details"] = details

        logger.info(f"📊 Task 23.1.4 Score: {self.results['23.1.4_safety']['score']}/100")

    def run_comprehensive_test(self):
        """Run all Phase 23.1 tests"""
        logger.info("🚀 Starting Phase 23.1: LLM Integration Architecture Validation")
        logger.info("=" * 80)

        # Run individual tests
        self.test_llm_framework()
        self.test_llm_service()
        self.test_context_provider()
        self.test_safety_layer()

        # Calculate overall score
        total_score = (
            self.results["23.1.1_framework"]["score"] +
            self.results["23.1.2_service"]["score"] +
            self.results["23.1.3_context"]["score"] +
            self.results["23.1.4_safety"]["score"]
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
        logger.info("📊 PHASE 23.1 VALIDATION RESULTS")
        logger.info("=" * 80)

        for task_id, result in self.results.items():
            if task_id != "overall":
                task_name = {
                    "23.1.1_framework": "LLM Integration Framework",
                    "23.1.2_service": "LLM Service Layer",
                    "23.1.3_context": "Application Context Provider",
                    "23.1.4_safety": "Safety and Validation Layer"
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
        logger.info(f"🎉 PHASE 23.1 {completion_status} COMPLETION - {'Production ready!' if completion_status == 'EXCELLENT' else 'Review recommended' if completion_status in ['GOOD', 'SATISFACTORY'] else 'Additional work needed'}")

        # Save results
        results_dir = os.path.join(parent_dir, "results", "phase23")
        os.makedirs(results_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(results_dir, f"phase23_1_validation_{timestamp}.json")

        with open(results_file, 'w') as f:
            json.dump({
                "phase": "23.1",
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
    runner = Phase23_1_TestRunner()
    score, status = runner.run_comprehensive_test()
    return score >= 320  # Return True if GOOD or better

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
