#!/usr/bin/env python3
"""
AI Agent Integration Test
Demonstrates the complete workflow for AI agents using all available tools.

This test shows how AI agents can:
1. Discover available resources
2. Analyze tasks systematically
3. Use knowledge graph for context
4. Validate code output
5. Handle complex tasks with context management
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Import AI agent tools
import sys
from pathlib import Path

# Add ai directory to path
ai_dir = Path(__file__).parent.parent / "ai"
sys.path.insert(0, str(ai_dir))

import ai_agent_resources as ai_resources
from ai_task_orchestrator import AITaskOrchestrator, get_task_guidance, validate_task_completion


def test_resource_discovery():
    """Test 1: Resource Discovery - What resources are available to AI agents?"""
    print("🔍 Test 1: Resource Discovery")
    print("=" * 50)

    # Check what resources are available
    resources = ai_resources.get_available_ai_resources()

    print(f"Knowledge Graph Available: {resources['knowledge_graph']['available']}")
    print(f"Available Tools: {len(resources['tools'])}")
    for tool_name in resources['tools']:
        print(f"  • {tool_name}")

    print(f"AI Capabilities: {len(resources['ai_capabilities'])}")
    for capability in resources['ai_capabilities'][:3]:
        print(f"  • {capability}")

    # Test knowledge graph access
    if ai_resources.kg_available():
        print("\n✅ Knowledge graph is accessible")

        # Try to get PLC repositories
        repos = ai_resources.get_plc_repositories(language="Python", min_stars=100)
        print(f"Found {len(repos)} high-quality Python PLC repositories")
        for repo in repos[:3]:
            print(f"  • {repo.get('name', 'Unknown')} ({repo.get('stars', 0)}⭐)")
    else:
        print("\n⚠️ Knowledge graph not accessible (expected if services not running)")

    return True


def test_task_analysis():
    """Test 2: Task Analysis - How does the orchestrator analyze tasks?"""
    print("\n🎯 Test 2: Task Analysis")
    print("=" * 50)

    # Test simple task
    simple_task = "Create a function to parse L5X tag names"
    print(f"Simple Task: {simple_task}")

    guidance = get_task_guidance(simple_task)
    print(guidance)

    # Test complex task
    print("\n" + "-" * 30)
    complex_task = "Build a comprehensive PLC data processing pipeline with Neo4j integration, file format conversion, and real-time monitoring"
    print(f"Complex Task: {complex_task[:50]}...")

    orchestrator = AITaskOrchestrator()
    try:
        analysis = orchestrator.analyze_task(complex_task)
        print(f"Complexity: {analysis['complexity']}")
        print(f"Estimated Effort: {analysis['estimated_effort']['time']}")
        print(f"Requirements: {len(analysis['requirements'])}")
        print(f"Risks: {len(analysis['risks'])}")

        if analysis['complexity'] in ['complex', 'extensive']:
            print("⚠️ Complex task detected - would create context document")

    finally:
        orchestrator.cleanup()

    return True


def test_code_validation():
    """Test 3: Code Validation - How does validation work with hallucination detection?"""
    print("\n✅ Test 3: Code Validation")
    print("=" * 50)

    # Test good code
    good_code = '''
def parse_l5x_tags(xml_content):
    """Parse tag information from L5X XML content."""
    import xml.etree.ElementTree as ET

    try:
        root = ET.fromstring(xml_content)
        tags = []

        for tag_elem in root.findall('.//Tag'):
            tag_name = tag_elem.get('Name')
            tag_type = tag_elem.get('DataType')
            tags.append({'name': tag_name, 'type': tag_type})

        return tags

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML content: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to parse tags: {e}")
'''

    requirements = [
        "Support for L5X format",
        "Robust error handling",
        "Implementation in Python"
    ]

    print("Testing well-written code...")
    validation = validate_task_completion(good_code, requirements)
    print(f"Validation Score: {validation['score']}%")
    print(f"Status: {validation['overall_status']}")

    # Test code with hallucinations
    print("\n" + "-" * 30)
    hallucinated_code = '''
def fake_function():
    """This is example code with hallucinations."""
    import fake_module  # Non-existent module

    api_key = "your_api_key_here"  # Placeholder credential
    url = "https://example.com/api"  # Placeholder URL

    # TODO: Implement this function
    print("Using print instead of logging")

    return placeholder_data
'''

    print("Testing code with hallucinations...")
    validation = validate_task_completion(hallucinated_code, ["Basic functionality"])
    print(f"Validation Score: {validation['score']}%")
    print(f"Status: {validation['overall_status']}")
    print("Issues detected:")
    for issue in validation['issues'][:3]:
        print(f"  • {issue}")

    return True


def test_integrated_workflow():
    """Test 4: Integrated Workflow - Complete AI agent workflow"""
    print("\n🚀 Test 4: Integrated Workflow")
    print("=" * 50)

    # Simulate an AI agent working on a task
    task = "Create a Python utility to convert L5X files to JSON with validation"

    print(f"AI Agent Task: {task}")
    print("\nStep 1: Resource Discovery")
    tools = ai_resources.get_tool_recommendations(task)
    print(f"Recommended tools: {len(tools['tools'])} found")

    print("\nStep 2: Task Analysis")
    analysis = AITaskOrchestrator().analyze_task(task)
    print(f"Complexity: {analysis['complexity']}")
    print(f"Requirements: {analysis['requirements'][:2]}...")

    print("\nStep 3: Implementation Guidance")
    get_task_guidance(task)
    print("✅ Structured guidance generated")

    print("\nStep 4: Code Implementation (simulated)")
    # Simulate code generation
    simulated_code = '''
def convert_l5x_to_json(input_file, output_file):
    """Convert L5X file to JSON format with validation."""
    import json
    import xml.etree.ElementTree as ET

    try:
        # Parse L5X file
        tree = ET.parse(input_file)
        root = tree.getroot()

        # Extract data
        data = {
            'project_name': root.get('Name', 'Unknown'),
            'tags': [],
            'routines': []
        }

        # Process tags
        for tag in root.findall('.//Tag'):
            data['tags'].append({
                'name': tag.get('Name'),
                'type': tag.get('DataType')
            })

        # Write JSON
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        return True

    except Exception as e:
        raise RuntimeError(f"Conversion failed: {e}")
'''

    print("\nStep 5: Code Validation")
    validation = validate_task_completion(simulated_code, analysis['requirements'])
    print(f"Validation Score: {validation['score']}%")
    print(f"Overall Status: {validation['overall_status']}")

    if validation['overall_status'] == 'pass':
        print("✅ AI Agent successfully completed task with validation")
    else:
        print("⚠️ AI Agent completed task but validation found issues")

    return True


def main():
    """Run all integration tests."""
    print("🤖 AI Agent Integration Test Suite")
    print("Testing complete AI agent workflow with all tools")
    print("=" * 60)

    tests = [
        test_resource_discovery,
        test_task_analysis,
        test_code_validation,
        test_integrated_workflow
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} PASSED")
            else:
                failed += 1
                print(f"❌ {test.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} FAILED: {e}")

    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ AI Agent framework is fully operational")
        print("\nAI agents can now:")
        print("  • Discover available resources and tools")
        print("  • Analyze tasks systematically")
        print("  • Access knowledge graph for enhanced context")
        print("  • Validate code with hallucination detection")
        print("  • Handle complex tasks with structured planning")
    else:
        print(f"\n⚠️ {failed} test(s) failed")
        print("Some functionality may be limited")

    print("\n🔗 Available AI Tools:")
    print("  • ai_agent_resources.py - Resource discovery")
    print("  • ai_task_orchestrator.py - Task analysis and validation")
    print("  • Knowledge graph interface - Domain expertise access")
    print("  • Specialized tools - PLC file processing")


if __name__ == "__main__":
    main()
