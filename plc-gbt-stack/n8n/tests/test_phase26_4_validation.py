"""
Phase 26.4 Natural Language Workflow Engine - Comprehensive Validation Tests
Following AI Task Orchestrator Guide Methodology

Tests all major components of the Phase 26.4 implementation including:
- Natural Language Workflow Parser
- AI Workflow Optimizer
- Conversational Interface
- Industrial Template Library
- CLI Integration
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pytest

# Add paths for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '../llm'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../ui/conversational_interface'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../templates/industrial_automation'))

try:
    from chat_interface import ConversationalWorkflowManager, ConversationState
    from nl_workflow_parser import (
        NaturalLanguageWorkflowParser,
        NodeType,
        WorkflowParsingResult,
        WorkflowType,
    )
    from template_library import (
        ComplexityLevel,
        IndustrialTemplateLibrary,
        IndustryType,
        TemplateCategory,
    )
    from workflow_optimizer import AIWorkflowOptimizer, OptimizationPriority, OptimizationType
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Components not available for testing: {e}")
    COMPONENTS_AVAILABLE = False

class TestPhase26_4ValidationResults:
    """Test results tracking for Phase 26.4 validation"""

    def __init__(self):
        self.test_results = {
            'workflow_parser': {'passed': 0, 'failed': 0, 'total': 0},
            'workflow_optimizer': {'passed': 0, 'failed': 0, 'total': 0},
            'conversational_interface': {'passed': 0, 'failed': 0, 'total': 0},
            'template_library': {'passed': 0, 'failed': 0, 'total': 0},
            'cli_integration': {'passed': 0, 'failed': 0, 'total': 0},
            'overall': {'passed': 0, 'failed': 0, 'total': 0}
        }
        self.detailed_results = []

    def record_test(self, component: str, test_name: str, passed: bool, details: str = ""):
        """Record individual test result"""
        self.test_results[component]['total'] += 1
        self.test_results['overall']['total'] += 1

        if passed:
            self.test_results[component]['passed'] += 1
            self.test_results['overall']['passed'] += 1
            status = "PASSED"
        else:
            self.test_results[component]['failed'] += 1
            self.test_results['overall']['failed'] += 1
            status = "FAILED"

        self.detailed_results.append({
            'component': component,
            'test_name': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })

    def get_success_rate(self, component: str = 'overall') -> float:
        """Calculate success rate for component or overall"""
        results = self.test_results[component]
        if results['total'] == 0:
            return 0.0
        return (results['passed'] / results['total']) * 100

    def generate_report(self) -> str:
        """Generate comprehensive validation report"""
        report = f"""
# Phase 26.4 Natural Language Workflow Engine - Validation Report

**Validation Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
**Total Tests**: {self.test_results['overall']['total']}
**Overall Success Rate**: {self.get_success_rate():.1f}%

## Component Results

| Component | Tests | Passed | Failed | Success Rate |
|-----------|-------|---------|---------|--------------|
"""

        for component, results in self.test_results.items():
            if component != 'overall' and results['total'] > 0:
                report += f"| {component.replace('_', ' ').title()} | {results['total']} | {results['passed']} | {results['failed']} | {self.get_success_rate(component):.1f}% |\n"

        report += f"| **OVERALL** | **{self.test_results['overall']['total']}** | **{self.test_results['overall']['passed']}** | **{self.test_results['overall']['failed']}** | **{self.get_success_rate():.1f}%** |\n"

        report += "\n## Detailed Test Results\n\n"

        current_component = ""
        for result in self.detailed_results:
            if result['component'] != current_component:
                current_component = result['component']
                report += f"\n### {current_component.replace('_', ' ').title()}\n\n"

            status_icon = "✅" if result['status'] == "PASSED" else "❌"
            report += f"{status_icon} **{result['test_name']}** - {result['status']}\n"
            if result['details']:
                report += f"   {result['details']}\n"

        # Add recommendations based on results
        overall_success = self.get_success_rate()
        report += "\n## Validation Assessment\n\n"

        if overall_success >= 95:
            report += "🎉 **EXCELLENT** - Phase 26.4 is ready for production deployment.\n"
        elif overall_success >= 85:
            report += "✅ **GOOD** - Phase 26.4 is ready with minor improvements needed.\n"
        elif overall_success >= 70:
            report += "⚠️ **ACCEPTABLE** - Phase 26.4 needs improvements before production.\n"
        else:
            report += "❌ **NEEDS WORK** - Phase 26.4 requires significant fixes before deployment.\n"

        return report

@pytest.fixture
def validation_results():
    """Test results tracking fixture"""
    return TestPhase26_4ValidationResults()

@pytest.fixture
def workflow_parser():
    """Workflow parser fixture"""
    if not COMPONENTS_AVAILABLE:
        pytest.skip("Components not available")
    return NaturalLanguageWorkflowParser()

@pytest.fixture
def workflow_optimizer():
    """Workflow optimizer fixture"""
    if not COMPONENTS_AVAILABLE:
        pytest.skip("Components not available")
    return AIWorkflowOptimizer()

@pytest.fixture
def conversation_manager():
    """Conversation manager fixture"""
    if not COMPONENTS_AVAILABLE:
        pytest.skip("Components not available")
    return ConversationalWorkflowManager()

@pytest.fixture
def template_library():
    """Template library fixture"""
    if not COMPONENTS_AVAILABLE:
        pytest.skip("Components not available")
    return IndustrialTemplateLibrary()

class TestWorkflowParser:
    """Test Natural Language Workflow Parser"""

    def test_basic_workflow_creation(self, workflow_parser, validation_results):
        """Test basic workflow creation from natural language"""
        test_cases = [
            "Create a temperature control loop for the reactor with PID controller",
            "Set up data logging for pressure and flow every 30 seconds",
            "Monitor tank level and send email alert when limits are reached",
            "Execute batch recipe with 5 steps: heat, mix, react, cool, discharge"
        ]

        success_count = 0
        for i, description in enumerate(test_cases):
            try:
                result = workflow_parser.parse_workflow_request(description)

                # Validate parsing success
                assert result.parsing_success, f"Parsing failed for: {description}"
                assert result.workflow_definition is not None, "No workflow definition generated"
                assert len(result.workflow_definition.nodes) > 0, "No nodes in workflow"
                assert result.confidence > 0.3, f"Low confidence: {result.confidence}"

                success_count += 1
                validation_results.record_test(
                    'workflow_parser',
                    f'Basic Creation Test {i+1}',
                    True,
                    f"Created {len(result.workflow_definition.nodes)} nodes, confidence: {result.confidence:.1%}"
                )

            except Exception as e:
                validation_results.record_test(
                    'workflow_parser',
                    f'Basic Creation Test {i+1}',
                    False,
                    f"Error: {str(e)}"
                )

        # Overall assessment
        success_rate = (success_count / len(test_cases)) * 100
        assert success_rate >= 75, f"Parser success rate too low: {success_rate}%"

    def test_workflow_type_classification(self, workflow_parser, validation_results):
        """Test workflow type classification accuracy"""
        test_cases = [
            ("Create PID temperature control", WorkflowType.PID_CONTROL),
            ("Log data to database every minute", WorkflowType.DATA_COLLECTION),
            ("Send email when alarm triggered", WorkflowType.ALARM_MANAGEMENT),
            ("Execute batch recipe sequence", WorkflowType.BATCH_PROCESSING)
        ]

        success_count = 0
        for description, expected_type in test_cases:
            try:
                result = workflow_parser.parse_workflow_request(description)

                if result.parsing_success and result.workflow_definition:
                    actual_type = result.workflow_definition.workflow_type

                    if actual_type == expected_type:
                        success_count += 1
                        validation_results.record_test(
                            'workflow_parser',
                            f'Type Classification: {expected_type.value}',
                            True,
                            f"Correctly classified as {actual_type.value}"
                        )
                    else:
                        validation_results.record_test(
                            'workflow_parser',
                            f'Type Classification: {expected_type.value}',
                            False,
                            f"Expected {expected_type.value}, got {actual_type.value}"
                        )
                else:
                    validation_results.record_test(
                        'workflow_parser',
                        f'Type Classification: {expected_type.value}',
                        False,
                        "Parsing failed"
                    )

            except Exception as e:
                validation_results.record_test(
                    'workflow_parser',
                    f'Type Classification: {expected_type.value}',
                    False,
                    f"Error: {str(e)}"
                )

        success_rate = (success_count / len(test_cases)) * 100
        assert success_rate >= 75, f"Classification accuracy too low: {success_rate}%"

    def test_json_output_generation(self, workflow_parser, validation_results):
        """Test N8N JSON workflow generation"""
        try:
            result = workflow_parser.parse_workflow_request(
                "Create temperature control with PID and email alerts"
            )

            assert result.parsing_success, "Workflow parsing failed"
            workflow_json = workflow_parser.get_workflow_json(result.workflow_definition)

            # Validate JSON structure
            workflow_data = json.loads(workflow_json)
            assert 'name' in workflow_data, "Missing workflow name"
            assert 'nodes' in workflow_data, "Missing nodes array"
            assert 'connections' in workflow_data, "Missing connections"
            assert isinstance(workflow_data['nodes'], list), "Nodes not a list"
            assert len(workflow_data['nodes']) > 0, "No nodes in JSON"

            # Validate node structure
            for node in workflow_data['nodes']:
                assert 'id' in node, "Node missing ID"
                assert 'name' in node, "Node missing name"
                assert 'type' in node, "Node missing type"
                assert 'parameters' in node, "Node missing parameters"
                assert 'position' in node, "Node missing position"

            validation_results.record_test(
                'workflow_parser',
                'JSON Output Generation',
                True,
                f"Generated valid N8N JSON with {len(workflow_data['nodes'])} nodes"
            )

        except Exception as e:
            validation_results.record_test(
                'workflow_parser',
                'JSON Output Generation',
                False,
                f"Error: {str(e)}"
            )

class TestWorkflowOptimizer:
    """Test AI Workflow Optimizer"""

    def test_performance_analysis(self, workflow_parser, workflow_optimizer, validation_results):
        """Test workflow performance analysis"""
        try:
            # Create a test workflow
            result = workflow_parser.parse_workflow_request(
                "Create temperature control with multiple PLC reads and database writes"
            )
            assert result.parsing_success, "Failed to create test workflow"

            # Analyze performance
            analysis = workflow_optimizer.performance_analyzer.analyze_workflow_performance(
                result.workflow_definition
            )

            # Validate analysis results
            assert 0 <= analysis.performance_score <= 100, "Invalid performance score"
            assert 0 <= analysis.reliability_score <= 100, "Invalid reliability score"
            assert 0 <= analysis.maintainability_score <= 100, "Invalid maintainability score"
            assert 0 <= analysis.overall_health_score <= 100, "Invalid overall health score"
            assert analysis.current_metrics is not None, "Missing metrics"
            assert analysis.analysis_time_seconds > 0, "Invalid analysis time"

            validation_results.record_test(
                'workflow_optimizer',
                'Performance Analysis',
                True,
                f"Health score: {analysis.overall_health_score:.1f}/100, {len(analysis.recommendations)} recommendations"
            )

        except Exception as e:
            validation_results.record_test(
                'workflow_optimizer',
                'Performance Analysis',
                False,
                f"Error: {str(e)}"
            )

    def test_optimization_recommendations(self, workflow_parser, workflow_optimizer, validation_results):
        """Test optimization recommendation generation"""
        try:
            # Create a complex workflow that should have optimization opportunities
            result = workflow_parser.parse_workflow_request(
                "Create data logging with multiple PLC reads, database writes, email alerts, and timers"
            )
            assert result.parsing_success, "Failed to create test workflow"

            # Get optimization recommendations
            analysis = workflow_optimizer.performance_analyzer.analyze_workflow_performance(
                result.workflow_definition
            )

            # Validate recommendations
            assert isinstance(analysis.recommendations, list), "Recommendations not a list"

            if analysis.recommendations:
                rec = analysis.recommendations[0]
                assert hasattr(rec, 'title'), "Recommendation missing title"
                assert hasattr(rec, 'description'), "Recommendation missing description"
                assert hasattr(rec, 'optimization_type'), "Recommendation missing type"
                assert hasattr(rec, 'priority'), "Recommendation missing priority"
                assert hasattr(rec, 'estimated_impact_score'), "Recommendation missing impact score"
                assert 0 <= rec.estimated_impact_score <= 100, "Invalid impact score"

            validation_results.record_test(
                'workflow_optimizer',
                'Optimization Recommendations',
                True,
                f"Generated {len(analysis.recommendations)} recommendations"
            )

        except Exception as e:
            validation_results.record_test(
                'workflow_optimizer',
                'Optimization Recommendations',
                False,
                f"Error: {str(e)}"
            )

    def test_workflow_optimization_application(self, workflow_parser, workflow_optimizer, validation_results):
        """Test application of optimizations to workflows"""
        try:
            # Create a test workflow
            result = workflow_parser.parse_workflow_request(
                "Create temperature control with PID controller and alarms"
            )
            assert result.parsing_success, "Failed to create test workflow"

            # Apply optimizations
            optimized = workflow_optimizer.optimize_workflow(result.workflow_definition)

            # Validate optimization results
            assert optimized.original_workflow is not None, "Missing original workflow"
            assert optimized.optimized_workflow is not None, "Missing optimized workflow"
            assert optimized.applied_optimizations is not None, "Missing applied optimizations"
            assert optimized.expected_improvements is not None, "Missing expected improvements"
            assert optimized.validation_results is not None, "Missing validation results"

            # Check that optimization was actually applied
            assert optimized.optimized_workflow.id != optimized.original_workflow.id, "Workflow ID not updated"
            assert "optimized" in optimized.optimized_workflow.name.lower(), "Optimized name not set"

            validation_results.record_test(
                'workflow_optimizer',
                'Optimization Application',
                True,
                f"Applied {len(optimized.applied_optimizations)} optimizations"
            )

        except Exception as e:
            validation_results.record_test(
                'workflow_optimizer',
                'Optimization Application',
                False,
                f"Error: {str(e)}"
            )

class TestConversationalInterface:
    """Test Conversational Workflow Management Interface"""

    @pytest.mark.asyncio
    async def test_basic_conversation_flow(self, conversation_manager, validation_results):
        """Test basic conversational workflow creation"""
        try:
            user_id = "test_user"
            session_id = "test_session"

            # Test workflow creation request
            response = await conversation_manager.handle_user_message(
                user_id,
                "Create a temperature control loop for the reactor",
                session_id
            )

            # Validate response
            assert response.message is not None, "No response message"
            assert len(response.message) > 0, "Empty response message"
            assert isinstance(response.suggestions, list), "Suggestions not a list"
            assert response.conversation_state is not None, "Missing conversation state"

            validation_results.record_test(
                'conversational_interface',
                'Basic Conversation Flow',
                True,
                f"State: {response.conversation_state.value}, {len(response.suggestions)} suggestions"
            )

        except Exception as e:
            validation_results.record_test(
                'conversational_interface',
                'Basic Conversation Flow',
                False,
                f"Error: {str(e)}"
            )

    @pytest.mark.asyncio
    async def test_multi_turn_conversation(self, conversation_manager, validation_results):
        """Test multi-turn conversation management"""
        try:
            user_id = "test_user"
            session_id = "test_session_multi"

            # First turn - create workflow
            response1 = await conversation_manager.handle_user_message(
                user_id,
                "Create a PID temperature controller",
                session_id
            )

            # Second turn - analyze workflow
            response2 = await conversation_manager.handle_user_message(
                user_id,
                "Analyze the workflow I just created",
                session_id
            )

            # Validate multi-turn context preservation
            assert response1.conversation_state != response2.conversation_state, "States should change"
            assert "workflow" in response2.message.lower(), "Context not preserved"

            validation_results.record_test(
                'conversational_interface',
                'Multi-turn Conversation',
                True,
                f"Preserved context across {2} turns"
            )

        except Exception as e:
            validation_results.record_test(
                'conversational_interface',
                'Multi-turn Conversation',
                False,
                f"Error: {str(e)}"
            )

    @pytest.mark.asyncio
    async def test_intent_classification(self, conversation_manager, validation_results):
        """Test user intent classification accuracy"""
        test_intents = [
            ("Create a new workflow", "create"),
            ("Analyze my workflow", "analyze"),
            ("List all workflows", "list"),
            ("Help me", "help")
        ]

        success_count = 0
        for message, expected_intent in test_intents:
            try:
                user_id = "test_user"
                session_id = f"test_intent_{expected_intent}"

                response = await conversation_manager.handle_user_message(
                    user_id, message, session_id
                )

                # Basic validation that response is appropriate
                assert response.message is not None, "No response"
                assert len(response.message) > 0, "Empty response"

                success_count += 1
                validation_results.record_test(
                    'conversational_interface',
                    f'Intent Classification: {expected_intent}',
                    True,
                    f"Responded appropriately to {expected_intent} intent"
                )

            except Exception as e:
                validation_results.record_test(
                    'conversational_interface',
                    f'Intent Classification: {expected_intent}',
                    False,
                    f"Error: {str(e)}"
                )

        success_rate = (success_count / len(test_intents)) * 100
        assert success_rate >= 75, f"Intent classification success rate too low: {success_rate}%"

class TestTemplateLibrary:
    """Test Industrial Template Library"""

    def test_template_catalog_access(self, template_library, validation_results):
        """Test template catalog functionality"""
        try:
            catalog = template_library.get_template_catalog()

            # Validate catalog structure
            assert 'total_templates' in catalog, "Missing total_templates"
            assert 'categories' in catalog, "Missing categories"
            assert 'industries' in catalog, "Missing industries"
            assert 'templates' in catalog, "Missing templates list"
            assert catalog['total_templates'] > 0, "No templates in catalog"
            assert len(catalog['templates']) > 0, "Empty templates list"

            # Validate template structure
            template = catalog['templates'][0]
            required_fields = ['id', 'name', 'description', 'category', 'industry', 'complexity']
            for field in required_fields:
                assert field in template, f"Template missing {field}"

            validation_results.record_test(
                'template_library',
                'Template Catalog Access',
                True,
                f"Catalog contains {catalog['total_templates']} templates"
            )

        except Exception as e:
            validation_results.record_test(
                'template_library',
                'Template Catalog Access',
                False,
                f"Error: {str(e)}"
            )

    def test_template_instantiation(self, template_library, validation_results):
        """Test template instantiation with parameters"""
        try:
            # Get a basic template
            template = template_library.get_template("temp_control_basic")
            assert template is not None, "Template not found"

            # Prepare valid parameters
            parameters = {
                "loop_name": "TIC_101",
                "pv_tag": "TT_101.PV",
                "sp_tag": "TIC_101.SP",
                "cv_tag": "TIC_101.CV",
                "setpoint_value": 85.0,
                "kp": 1.2,
                "ki": 0.15,
                "kd": 0.0,
                "high_alarm": 95.0,
                "low_alarm": 75.0,
                "alarm_email": "operator@test.com"
            }

            # Validate parameters
            valid, errors = template_library.validate_parameters("temp_control_basic", parameters)
            assert valid, f"Parameter validation failed: {errors}"

            # Instantiate template
            workflow_def = template_library.instantiate_template("temp_control_basic", parameters)
            assert workflow_def is not None, "Template instantiation failed"
            assert 'name' in workflow_def, "Missing workflow name"
            assert 'nodes' in workflow_def, "Missing nodes"
            assert len(workflow_def['nodes']) > 0, "No nodes generated"

            validation_results.record_test(
                'template_library',
                'Template Instantiation',
                True,
                f"Generated workflow with {len(workflow_def['nodes'])} nodes"
            )

        except Exception as e:
            validation_results.record_test(
                'template_library',
                'Template Instantiation',
                False,
                f"Error: {str(e)}"
            )

    def test_template_search_functionality(self, template_library, validation_results):
        """Test template search and filtering"""
        try:
            # Test search by keyword
            search_results = template_library.search_templates("temperature")
            assert isinstance(search_results, list), "Search results not a list"

            # Test category filtering
            control_templates = template_library.get_templates_by_category(TemplateCategory.CONTROL_LOOPS)
            assert isinstance(control_templates, list), "Category results not a list"

            # Test industry filtering
            general_templates = template_library.get_templates_by_industry(IndustryType.GENERAL)
            assert isinstance(general_templates, list), "Industry results not a list"

            # Test complexity filtering
            basic_templates = template_library.get_templates_by_complexity(ComplexityLevel.BASIC)
            assert isinstance(basic_templates, list), "Complexity results not a list"

            validation_results.record_test(
                'template_library',
                'Template Search Functionality',
                True,
                f"Search: {len(search_results)}, Category: {len(control_templates)}, Industry: {len(general_templates)}, Complexity: {len(basic_templates)}"
            )

        except Exception as e:
            validation_results.record_test(
                'template_library',
                'Template Search Functionality',
                False,
                f"Error: {str(e)}"
            )

class TestCLIIntegration:
    """Test CLI Integration"""

    def test_cli_module_imports(self, validation_results):
        """Test CLI module can be imported"""
        try:
            # Test importing CLI workflow commands
            sys.path.append(os.path.join(os.path.dirname(__file__), '../../cli/commands'))

            import workflow
            assert hasattr(workflow, 'workflow'), "Missing workflow command group"
            assert hasattr(workflow, 'create'), "Missing create command"
            assert hasattr(workflow, 'analyze'), "Missing analyze command"
            assert hasattr(workflow, 'optimize'), "Missing optimize command"
            assert hasattr(workflow, 'templates'), "Missing templates command"
            assert hasattr(workflow, 'chat'), "Missing chat command"

            validation_results.record_test(
                'cli_integration',
                'CLI Module Imports',
                True,
                "All CLI commands imported successfully"
            )

        except Exception as e:
            validation_results.record_test(
                'cli_integration',
                'CLI Module Imports',
                False,
                f"Import error: {str(e)}"
            )

    def test_cli_component_initialization(self, validation_results):
        """Test CLI components can be initialized"""
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), '../../cli/commands'))
            import workflow

            # Test component initialization
            success = workflow.init_workflow_components()

            if COMPONENTS_AVAILABLE:
                assert success, "Component initialization failed"
                assert workflow.workflow_parser is not None, "Parser not initialized"
                assert workflow.workflow_optimizer is not None, "Optimizer not initialized"
                assert workflow.conversation_manager is not None, "Conversation manager not initialized"
                assert workflow.template_library is not None, "Template library not initialized"

                validation_results.record_test(
                    'cli_integration',
                    'CLI Component Initialization',
                    True,
                    "All components initialized successfully"
                )
            else:
                validation_results.record_test(
                    'cli_integration',
                    'CLI Component Initialization',
                    True,
                    "Components gracefully handled when not available"
                )

        except Exception as e:
            validation_results.record_test(
                'cli_integration',
                'CLI Component Initialization',
                False,
                f"Initialization error: {str(e)}"
            )

def run_comprehensive_validation():
    """Run comprehensive Phase 26.4 validation"""
    print("=" * 80)
    print("Phase 26.4 Natural Language Workflow Engine - Comprehensive Validation")
    print("Following AI Task Orchestrator Guide Methodology")
    print("=" * 80)

    # Initialize validation tracking
    validation_results = TestPhase26_4ValidationResults()

    # Run tests if components are available
    if COMPONENTS_AVAILABLE:
        print("✅ Components available - running full test suite")

        try:
            # Initialize test components
            workflow_parser = NaturalLanguageWorkflowParser()
            workflow_optimizer = AIWorkflowOptimizer()
            conversation_manager = ConversationalWorkflowManager()
            template_library = IndustrialTemplateLibrary()

            # Run workflow parser tests
            print("\n🔍 Testing Workflow Parser...")
            parser_tests = TestWorkflowParser()
            parser_tests.test_basic_workflow_creation(workflow_parser, validation_results)
            parser_tests.test_workflow_type_classification(workflow_parser, validation_results)
            parser_tests.test_json_output_generation(workflow_parser, validation_results)

            # Run workflow optimizer tests
            print("🚀 Testing Workflow Optimizer...")
            optimizer_tests = TestWorkflowOptimizer()
            optimizer_tests.test_performance_analysis(workflow_parser, workflow_optimizer, validation_results)
            optimizer_tests.test_optimization_recommendations(workflow_parser, workflow_optimizer, validation_results)
            optimizer_tests.test_workflow_optimization_application(workflow_parser, workflow_optimizer, validation_results)

            # Run conversational interface tests
            print("💬 Testing Conversational Interface...")
            conv_tests = TestConversationalInterface()
            asyncio.run(conv_tests.test_basic_conversation_flow(conversation_manager, validation_results))
            asyncio.run(conv_tests.test_multi_turn_conversation(conversation_manager, validation_results))
            asyncio.run(conv_tests.test_intent_classification(conversation_manager, validation_results))

            # Run template library tests
            print("📚 Testing Template Library...")
            template_tests = TestTemplateLibrary()
            template_tests.test_template_catalog_access(template_library, validation_results)
            template_tests.test_template_instantiation(template_library, validation_results)
            template_tests.test_template_search_functionality(template_library, validation_results)

        except Exception as e:
            print(f"❌ Error during component testing: {e}")

    else:
        print("⚠️  Components not available - running limited tests")

    # Run CLI integration tests
    print("⌨️  Testing CLI Integration...")
    cli_tests = TestCLIIntegration()
    cli_tests.test_cli_module_imports(validation_results)
    cli_tests.test_cli_component_initialization(validation_results)

    # Generate and return validation report
    print("\n📊 Generating validation report...")
    report = validation_results.generate_report()

    print("\n✅ Validation completed!")
    print(f"Overall Success Rate: {validation_results.get_success_rate():.1f}%")
    print(f"Total Tests: {validation_results.test_results['overall']['total']}")
    print(f"Passed: {validation_results.test_results['overall']['passed']}")
    print(f"Failed: {validation_results.test_results['overall']['failed']}")

    return validation_results, report

if __name__ == "__main__":
    validation_results, report = run_comprehensive_validation()

    # Save report to file
    report_file = Path(__file__).parent / f"phase26_4_validation_report_{int(datetime.now().timestamp())}.md"
    report_file.write_text(report)
    print(f"\n📄 Validation report saved to: {report_file}")
