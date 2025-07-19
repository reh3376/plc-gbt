#!/usr/bin/env python3
"""
Task 23.5.4: Interactive Documentation System
============================================

Comprehensive interactive documentation system with context-aware help,
example-driven learning, and automated tutorial generation.

Features:
- Context-aware help system adapting to user experience
- Example-driven learning with hands-on tutorials
- Interactive assistance with step-by-step guidance
- Automated documentation generation from system knowledge
- Integration with Phase 23.1-23.4 LLM components

Author: PLC-GPT Development Team
Date: June 18, 2025
Task: 23.5.4 - Documentation System
Methodology: AI Task Orchestrator Guide
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
import re

# Rich console imports for interactive documentation
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.text import Text
    from rich.tree import Tree
    from rich.columns import Columns
    from rich.markdown import Markdown
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    logging.warning("Rich library not available - using basic documentation output")

# Import Phase 23 components
try:
    from ...llm.service import LLMService, get_llm_service
    from ...llm.domain_understanding import DomainUnderstandingEngine
    from ...llm import LLMRequest, LLMRequestType, ApplicationContext
except ImportError as e:
    logging.warning(f"Phase 23 components not available: {e}")

# Configure logging
logger = logging.getLogger(__name__)

class UserExperienceLevel(Enum):
    """User experience levels for adaptive documentation"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class DocumentationType(Enum):
    """Types of documentation content"""
    QUICK_START = "quick_start"
    TUTORIAL = "tutorial"
    REFERENCE = "reference"
    TROUBLESHOOTING = "troubleshooting"
    EXAMPLES = "examples"
    API_DOCS = "api_docs"

class InteractionMode(Enum):
    """Documentation interaction modes"""
    GUIDED = "guided"
    SELF_PACED = "self_paced"
    INTERACTIVE = "interactive"
    REFERENCE_ONLY = "reference_only"

@dataclass
class DocumentationContext:
    """Context for documentation generation"""
    user_level: UserExperienceLevel
    current_task: Optional[str] = None
    system_state: Dict[str, Any] = field(default_factory=dict)
    user_history: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TutorialStep:
    """Individual step in a tutorial"""
    step_number: int
    title: str
    description: str
    code_example: Optional[str] = None
    expected_output: Optional[str] = None
    validation: Optional[Callable] = None
    hints: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)

@dataclass
class Tutorial:
    """Complete tutorial structure"""
    tutorial_id: str
    title: str
    description: str
    difficulty_level: UserExperienceLevel
    estimated_time: int  # minutes
    steps: List[TutorialStep]
    learning_objectives: List[str]
    prerequisites: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)

class InteractiveDocumentation:
    """
    Main interactive documentation system
    
    Provides context-aware help, tutorials, examples, and interactive guidance
    for the PLC-GBT Industrial Control System.
    """
    
    def __init__(self):
        """Initialize interactive documentation system"""
        self.console = Console() if RICH_AVAILABLE else None
        
        # Initialize LLM components
        try:
            self.llm_service = get_llm_service()
            self.domain_engine = DomainUnderstandingEngine()
        except Exception as e:
            logger.warning(f"LLM components not available: {e}")
            self.llm_service = None
            self.domain_engine = None
        
        # Load built-in documentation
        self.tutorials: Dict[str, Tutorial] = {}
        self.examples: Dict[str, Dict[str, Any]] = {}
        self.help_topics: Dict[str, Dict[str, Any]] = {}
        
        # User session state
        self.current_context = DocumentationContext(UserExperienceLevel.INTERMEDIATE)
        self.session_history: List[Dict[str, Any]] = []
        
        # Initialize content
        self._initialize_built_in_content()
    
    def _initialize_built_in_content(self):
        """Initialize built-in documentation content"""
        # Load built-in tutorials
        self.tutorials.update({
            "getting_started": Tutorial(
                tutorial_id="getting_started",
                title="Getting Started with PLC-GBT",
                description="Introduction to the Industrial Control AI Assistant",
                difficulty_level=UserExperienceLevel.BEGINNER,
                estimated_time=15,
                learning_objectives=[
                    "Understand PLC-GBT capabilities",
                    "Learn basic chat interface",
                    "Execute first analysis command",
                    "Navigate help system"
                ],
                steps=[
                    TutorialStep(
                        step_number=1,
                        title="Start Chat Session",
                        description="Launch the interactive chat interface",
                        code_example="python -m plc_gbt_stack.ui.chat.chat_interface",
                        hints=["Use rich terminal for best experience", "Type /help for commands"]
                    ),
                    TutorialStep(
                        step_number=2,
                        title="Basic Control Analysis",
                        description="Analyze a temperature control loop",
                        code_example='You: "Analyze temperature control loop TIC-101"',
                        expected_output="AI analysis of the control loop with recommendations"
                    ),
                    TutorialStep(
                        step_number=3,
                        title="Explore Commands",
                        description="Learn available chat commands",
                        code_example="/help",
                        hints=["Try /status to see system information", "Use /history to review conversation"]
                    )
                ]
            ),
            
            "advanced_analysis": Tutorial(
                tutorial_id="advanced_analysis",
                title="Advanced Control Loop Analysis",
                description="Deep dive into advanced analysis capabilities",
                difficulty_level=UserExperienceLevel.ADVANCED,
                estimated_time=45,
                learning_objectives=[
                    "Perform comprehensive loop analysis",
                    "Understand AI recommendations",
                    "Use natural language for complex queries",
                    "Integrate with existing systems"
                ],
                prerequisites=["getting_started"],
                steps=[
                    TutorialStep(
                        step_number=1,
                        title="Multi-Loop Analysis",
                        description="Analyze multiple control loops simultaneously",
                        code_example='You: "Compare performance of TIC-101, FIC-201, and PIC-301"',
                    ),
                    TutorialStep(
                        step_number=2,
                        title="Optimization Recommendations",
                        description="Get AI-powered optimization suggestions",
                        code_example='You: "Optimize distillation column control for maximum efficiency"',
                    )
                ]
            )
        })
        
        # Load built-in examples
        self.examples.update({
            "chat_interface": {
                "title": "Chat Interface Usage",
                "category": "user_interface",
                "difficulty": UserExperienceLevel.BEGINNER,
                "examples": [
                    {
                        "description": "Start a basic chat session",
                        "code": "from plc_gbt_stack.ui.chat import start_chat_session\nawait start_chat_session()",
                        "explanation": "Launches interactive chat with AI assistant"
                    },
                    {
                        "description": "Send programmatic message",
                        "code": "interface = ChatInterface()\nresponse = await interface.send_message('Analyze PID loop')",
                        "explanation": "Send messages programmatically and get responses"
                    }
                ]
            },
            
            "api_usage": {
                "title": "REST API Integration",
                "category": "api",
                "difficulty": UserExperienceLevel.INTERMEDIATE,
                "examples": [
                    {
                        "description": "Send chat request via API",
                        "code": """import requests

response = requests.post("http://localhost:8000/api/v1/chat", 
    json={
        "message": "Analyze temperature control",
        "request_type": "analysis"
    },
    headers={"Authorization": "Bearer your_token"}
)""",
                        "explanation": "Use REST API for chat interaction"
                    }
                ]
            }
        })
        
        # Load built-in help topics
        self.help_topics.update({
            "chat_commands": {
                "title": "Chat Commands Reference",
                "content": {
                    "/help": "Show available commands and examples",
                    "/quit": "Exit the chat session",
                    "/clear": "Clear the screen",
                    "/history": "Show conversation history",
                    "/save": "Save conversation to file",
                    "/status": "Show system status"
                },
                "category": "reference"
            },
            
            "natural_language": {
                "title": "Natural Language Examples",
                "content": {
                    "Analysis": [
                        "Analyze the temperature control loop TIC-101",
                        "What's causing oscillation in my control loop?",
                        "Compare performance of loops TIC-101 and TIC-102"
                    ],
                    "Configuration": [
                        "Create a new PID controller schema",
                        "Set up cascade control for the distillation column",
                        "Configure feedforward control for the reactor"
                    ],
                    "Optimization": [
                        "Optimize the control system for better performance",
                        "Suggest tuning improvements for loop FIC-201",
                        "How can I reduce oscillations in this loop?"
                    ]
                },
                "category": "examples"
            }
        })
    
    async def start_interactive_help(self, context: Optional[DocumentationContext] = None) -> None:
        """Start interactive documentation session"""
        if context:
            self.current_context = context
        
        self._display_welcome()
        
        while True:
            try:
                choice = await self._get_main_menu_choice()
                
                if choice == "1":
                    await self._show_quick_start()
                elif choice == "2":
                    await self._browse_tutorials()
                elif choice == "3":
                    await self._search_help()
                elif choice == "4":
                    await self._show_examples()
                elif choice == "5":
                    await self._interactive_assistance()
                elif choice == "6":
                    await self._configure_preferences()
                elif choice == "0" or choice.lower() in ['quit', 'exit']:
                    break
                else:
                    self._display_message("Invalid choice. Please try again.", "warning")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                self._display_message(f"Error: {e}", "error")
        
        self._display_message("Documentation session ended. Happy learning! 📚", "info")
    
    def _display_welcome(self) -> None:
        """Display welcome message for documentation"""
        if self.console:
            welcome_panel = Panel(
                "[bold blue]📚 PLC-GBT Interactive Documentation[/bold blue]\n\n"
                "[green]Welcome to the comprehensive help system![/green]\n"
                "This interactive documentation adapts to your experience level and provides:\n\n"
                "• 🚀 Quick start guides and tutorials\n"
                "• 📖 Context-aware help and examples\n"
                "• 🎓 Step-by-step learning paths\n"
                "• 🔍 Smart search and assistance\n"
                "• 💡 Interactive guidance and tips\n\n"
                f"[yellow]Current experience level: {self.current_context.user_level.value.title()}[/yellow]",
                title="🏭 Industrial Control Documentation",
                border_style="blue"
            )
            self.console.print(welcome_panel)
        else:
            print("=== PLC-GBT Interactive Documentation ===")
            print(f"Experience level: {self.current_context.user_level.value.title()}")
    
    async def _get_main_menu_choice(self) -> str:
        """Get user choice from main menu"""
        menu_options = [
            "1. 🚀 Quick Start Guide",
            "2. 📖 Browse Tutorials", 
            "3. 🔍 Search Help Topics",
            "4. 💡 View Examples",
            "5. 🤖 Interactive AI Assistance",
            "6. ⚙️  Configure Preferences",
            "0. 🚪 Exit"
        ]
        
        if self.console:
            menu_table = Table(title="Documentation Menu")
            menu_table.add_column("Options", style="cyan")
            
            for option in menu_options:
                menu_table.add_row(option)
            
            self.console.print(menu_table)
            return Prompt.ask("[bold green]Choose an option[/bold green]", console=self.console)
        else:
            print("\n=== Documentation Menu ===")
            for option in menu_options:
                print(option)
            return input("Choose an option: ").strip()
    
    async def _show_quick_start(self) -> None:
        """Show quick start guide"""
        tutorial = self.tutorials.get("getting_started")
        if tutorial:
            await self._run_tutorial(tutorial)
        else:
            self._display_message("Quick start tutorial not available", "warning")
    
    async def _browse_tutorials(self) -> None:
        """Browse available tutorials"""
        if not self.tutorials:
            self._display_message("No tutorials available", "info")
            return
        
        # Filter tutorials by user level
        suitable_tutorials = [
            t for t in self.tutorials.values()
            if t.difficulty_level.value <= self.current_context.user_level.value or 
               self.current_context.user_level == UserExperienceLevel.EXPERT
        ]
        
        if self.console:
            table = Table(title="Available Tutorials")
            table.add_column("ID", style="cyan")
            table.add_column("Title", style="green")
            table.add_column("Level", style="yellow")
            table.add_column("Time", style="magenta")
            table.add_column("Description", style="white")
            
            for tutorial in suitable_tutorials:
                table.add_row(
                    tutorial.tutorial_id,
                    tutorial.title,
                    tutorial.difficulty_level.value.title(),
                    f"{tutorial.estimated_time} min",
                    tutorial.description[:50] + "..." if len(tutorial.description) > 50 else tutorial.description
                )
            
            self.console.print(table)
        else:
            print("\n=== Available Tutorials ===")
            for tutorial in suitable_tutorials:
                print(f"{tutorial.tutorial_id}: {tutorial.title} ({tutorial.difficulty_level.value})")
        
        # Let user choose tutorial
        if suitable_tutorials:
            choice = Prompt.ask("Enter tutorial ID to start (or 'back')", console=self.console) if self.console else input("Enter tutorial ID: ")
            
            if choice.lower() != 'back':
                tutorial = next((t for t in suitable_tutorials if t.tutorial_id == choice), None)
                if tutorial:
                    await self._run_tutorial(tutorial)
                else:
                    self._display_message("Tutorial not found", "warning")
    
    async def _run_tutorial(self, tutorial: Tutorial) -> None:
        """Run an interactive tutorial"""
        self._display_message(f"Starting tutorial: {tutorial.title}", "info")
        
        if self.console:
            tutorial_panel = Panel(
                f"[bold]{tutorial.title}[/bold]\n\n"
                f"{tutorial.description}\n\n"
                f"[yellow]Difficulty:[/yellow] {tutorial.difficulty_level.value.title()}\n"
                f"[yellow]Estimated time:[/yellow] {tutorial.estimated_time} minutes\n"
                f"[yellow]Steps:[/yellow] {len(tutorial.steps)}\n\n"
                f"[green]Learning objectives:[/green]\n" + 
                "\n".join(f"• {obj}" for obj in tutorial.learning_objectives),
                title="📖 Tutorial Info",
                border_style="green"
            )
            self.console.print(tutorial_panel)
        
        # Confirm start
        if self.console:
            start = Confirm.ask("Start this tutorial?", console=self.console)
        else:
            start = input("Start this tutorial? (y/n): ").lower().startswith('y')
        
        if not start:
            return
        
        # Run tutorial steps
        for i, step in enumerate(tutorial.steps, 1):
            self._display_tutorial_step(step, i, len(tutorial.steps))
            
            # Wait for user to complete step
            if self.console:
                continue_step = Confirm.ask(f"Have you completed step {i}?", console=self.console)
            else:
                continue_step = input(f"Completed step {i}? (y/n): ").lower().startswith('y')
            
            if not continue_step:
                if self.console:
                    show_hints = Confirm.ask("Would you like to see hints?", console=self.console)
                else:
                    show_hints = input("Show hints? (y/n): ").lower().startswith('y')
                
                if show_hints and step.hints:
                    self._display_hints(step.hints)
        
        self._display_message(f"🎉 Tutorial '{tutorial.title}' completed successfully!", "success")
    
    def _display_tutorial_step(self, step: TutorialStep, current: int, total: int) -> None:
        """Display a tutorial step"""
        if self.console:
            step_content = f"[bold]Step {current}/{total}: {step.title}[/bold]\n\n{step.description}"
            
            if step.code_example:
                step_content += f"\n\n[yellow]Example:[/yellow]\n"
                syntax = Syntax(step.code_example, "python", theme="monokai", line_numbers=True)
                
            if step.expected_output:
                step_content += f"\n\n[green]Expected output:[/green]\n{step.expected_output}"
            
            step_panel = Panel(
                step_content,
                title=f"📝 Step {current}",
                border_style="yellow"
            )
            self.console.print(step_panel)
            
            if step.code_example:
                self.console.print(syntax)
        else:
            print(f"\n=== Step {current}/{total}: {step.title} ===")
            print(step.description)
            if step.code_example:
                print(f"Example:\n{step.code_example}")
    
    def _display_hints(self, hints: List[str]) -> None:
        """Display hints for tutorial step"""
        if self.console:
            hints_text = "\n".join(f"💡 {hint}" for hint in hints)
            hints_panel = Panel(hints_text, title="💡 Hints", border_style="cyan")
            self.console.print(hints_panel)
        else:
            print("\n=== Hints ===")
            for hint in hints:
                print(f"💡 {hint}")
    
    async def _search_help(self) -> None:
        """Search help topics"""
        if self.console:
            query = Prompt.ask("Enter search term", console=self.console)
        else:
            query = input("Enter search term: ").strip()
        
        if not query:
            return
        
        # Search in help topics
        results = []
        query_lower = query.lower()
        
        for topic_id, topic in self.help_topics.items():
            if query_lower in topic_id.lower() or query_lower in topic["title"].lower():
                results.append((topic_id, topic))
            elif isinstance(topic["content"], dict):
                for key, value in topic["content"].items():
                    if query_lower in key.lower() or (isinstance(value, str) and query_lower in value.lower()):
                        results.append((topic_id, topic))
                        break
        
        if results:
            self._display_search_results(results, query)
        else:
            self._display_message(f"No help topics found for '{query}'", "info")
            
            # Offer AI assistance
            if self.llm_service:
                if self.console:
                    use_ai = Confirm.ask("Would you like AI assistance with this topic?", console=self.console)
                else:
                    use_ai = input("Use AI assistance? (y/n): ").lower().startswith('y')
                
                if use_ai:
                    await self._ai_help_assistance(query)
    
    def _display_search_results(self, results: List[Tuple[str, Dict[str, Any]]], query: str) -> None:
        """Display search results"""
        if self.console:
            table = Table(title=f"Search Results for '{query}'")
            table.add_column("Topic", style="cyan")
            table.add_column("Title", style="green")
            table.add_column("Category", style="yellow")
            
            for topic_id, topic in results:
                table.add_row(topic_id, topic["title"], topic.get("category", "general"))
            
            self.console.print(table)
        else:
            print(f"\n=== Search Results for '{query}' ===")
            for topic_id, topic in results:
                print(f"{topic_id}: {topic['title']}")
        
        # Let user select a topic
        if self.console:
            choice = Prompt.ask("Enter topic ID to view (or 'back')", console=self.console)
        else:
            choice = input("Enter topic ID to view: ").strip()
        
        if choice.lower() != 'back':
            topic = next((t[1] for t in results if t[0] == choice), None)
            if topic:
                self._display_help_topic(topic)
    
    def _display_help_topic(self, topic: Dict[str, Any]) -> None:
        """Display a help topic"""
        if self.console:
            content = self._format_help_content(topic["content"])
            help_panel = Panel(content, title=f"📚 {topic['title']}", border_style="blue")
            self.console.print(help_panel)
        else:
            print(f"\n=== {topic['title']} ===")
            self._print_help_content(topic["content"])
    
    def _format_help_content(self, content: Any) -> str:
        """Format help content for rich display"""
        if isinstance(content, dict):
            formatted = ""
            for key, value in content.items():
                formatted += f"[bold]{key}[/bold]\n"
                if isinstance(value, list):
                    for item in value:
                        formatted += f"  • {item}\n"
                else:
                    formatted += f"  {value}\n"
                formatted += "\n"
            return formatted
        elif isinstance(content, list):
            return "\n".join(f"• {item}" for item in content)
        else:
            return str(content)
    
    def _print_help_content(self, content: Any) -> None:
        """Print help content for basic display"""
        if isinstance(content, dict):
            for key, value in content.items():
                print(f"{key}:")
                if isinstance(value, list):
                    for item in value:
                        print(f"  • {item}")
                else:
                    print(f"  {value}")
                print()
        elif isinstance(content, list):
            for item in content:
                print(f"• {item}")
        else:
            print(content)
    
    async def _show_examples(self) -> None:
        """Show code examples"""
        if not self.examples:
            self._display_message("No examples available", "info")
            return
        
        # Filter examples by user level
        suitable_examples = {
            k: v for k, v in self.examples.items()
            if v["difficulty"].value <= self.current_context.user_level.value or
               self.current_context.user_level == UserExperienceLevel.EXPERT
        }
        
        if self.console:
            table = Table(title="Available Examples")
            table.add_column("ID", style="cyan")
            table.add_column("Title", style="green")
            table.add_column("Category", style="yellow")
            table.add_column("Level", style="magenta")
            
            for example_id, example in suitable_examples.items():
                table.add_row(
                    example_id,
                    example["title"],
                    example["category"],
                    example["difficulty"].value.title()
                )
            
            self.console.print(table)
        else:
            print("\n=== Available Examples ===")
            for example_id, example in suitable_examples.items():
                print(f"{example_id}: {example['title']} ({example['category']})")
        
        # Let user choose example
        if suitable_examples:
            choice = Prompt.ask("Enter example ID to view (or 'back')", console=self.console) if self.console else input("Enter example ID: ")
            
            if choice.lower() != 'back':
                example = suitable_examples.get(choice)
                if example:
                    self._display_example(example)
                else:
                    self._display_message("Example not found", "warning")
    
    def _display_example(self, example: Dict[str, Any]) -> None:
        """Display a code example"""
        if self.console:
            for i, ex in enumerate(example["examples"], 1):
                example_content = f"[bold]Example {i}: {ex['description']}[/bold]\n\n"
                example_content += f"{ex['explanation']}\n\n"
                
                syntax = Syntax(ex['code'], "python", theme="monokai", line_numbers=True)
                
                example_panel = Panel(
                    example_content,
                    title=f"💻 {example['title']} - Example {i}",
                    border_style="green"
                )
                
                self.console.print(example_panel)
                self.console.print(syntax)
                self.console.print()
        else:
            print(f"\n=== {example['title']} ===")
            for i, ex in enumerate(example["examples"], 1):
                print(f"\nExample {i}: {ex['description']}")
                print(f"Explanation: {ex['explanation']}")
                print(f"Code:\n{ex['code']}")
    
    async def _interactive_assistance(self) -> None:
        """Provide interactive AI assistance"""
        if not self.llm_service:
            self._display_message("AI assistance not available - LLM service not connected", "warning")
            return
        
        self._display_message("🤖 Interactive AI Assistance activated!", "info")
        self._display_message("Ask me anything about PLC-GBT or industrial control systems.", "info")
        self._display_message("Type 'exit' to return to main menu.", "info")
        
        while True:
            if self.console:
                question = Prompt.ask("[bold green]Your question[/bold green]", console=self.console)
            else:
                question = input("Your question: ").strip()
            
            if question.lower() in ['exit', 'quit', 'back']:
                break
            
            if not question:
                continue
            
            # Get AI response
            try:
                response = await self._ai_help_assistance(question)
                if self.console:
                    response_panel = Panel(
                        response,
                        title="🤖 AI Assistant",
                        border_style="blue"
                    )
                    self.console.print(response_panel)
                else:
                    print(f"AI Assistant: {response}")
            except Exception as e:
                self._display_message(f"Error getting AI assistance: {e}", "error")
    
    async def _ai_help_assistance(self, query: str) -> str:
        """Get AI assistance for help query"""
        try:
            if not self.llm_service:
                return "AI assistance not available"
            
            # Create context for documentation assistance
            app_context = ApplicationContext(
                user_input=query,
                conversation_history=[],
                system_state={
                    "mode": "documentation_assistance",
                    "user_level": self.current_context.user_level.value
                },
                metadata={"assistance_type": "documentation"}
            )
            
            # Create specialized prompt for documentation
            documentation_prompt = f"""
            You are a helpful documentation assistant for the PLC-GBT Industrial Control System.
            
            User experience level: {self.current_context.user_level.value}
            User question: {query}
            
            Provide a clear, helpful response that:
            1. Directly answers the question
            2. Includes relevant examples if applicable  
            3. Suggests next steps or related topics
            4. Is appropriate for the user's experience level
            
            Keep the response concise but comprehensive.
            """
            
            # Create LLM request
            request = LLMRequest(
                request_type=LLMRequestType.ASSISTANCE,
                prompt=documentation_prompt,
                context=app_context,
                metadata={"documentation_mode": True}
            )
            
            # Get response
            response = await self.llm_service.send_request(request)
            
            if response and response.content:
                return response.content
            else:
                return "Sorry, I couldn't generate a helpful response for that question."
                
        except Exception as e:
            logger.error(f"Error in AI assistance: {e}")
            return f"Error getting AI assistance: {e}"
    
    async def _configure_preferences(self) -> None:
        """Configure user preferences"""
        if self.console:
            self.console.print(Panel("⚙️ Configure your documentation preferences", border_style="cyan"))
            
            # Experience level
            levels = [level.value for level in UserExperienceLevel]
            for i, level in enumerate(levels, 1):
                self.console.print(f"{i}. {level.title()}")
            
            level_choice = IntPrompt.ask("Select your experience level", choices=[str(i) for i in range(1, len(levels)+1)], console=self.console)
            self.current_context.user_level = UserExperienceLevel(levels[level_choice - 1])
            
            self._display_message(f"Experience level set to: {self.current_context.user_level.value.title()}", "success")
        else:
            print("\n=== Configure Preferences ===")
            print("Experience levels:")
            levels = [level.value for level in UserExperienceLevel]
            for i, level in enumerate(levels, 1):
                print(f"{i}. {level.title()}")
            
            try:
                choice = int(input("Select experience level (1-4): "))
                if 1 <= choice <= len(levels):
                    self.current_context.user_level = UserExperienceLevel(levels[choice - 1])
                    print(f"Experience level set to: {self.current_context.user_level.value.title()}")
            except ValueError:
                print("Invalid choice")
    
    def _display_message(self, message: str, message_type: str = "info") -> None:
        """Display a message with appropriate styling"""
        if self.console:
            style_map = {
                "info": "blue",
                "warning": "yellow",
                "error": "red", 
                "success": "green"
            }
            style = style_map.get(message_type, "white")
            self.console.print(f"[{style}]{message}[/{style}]")
        else:
            print(f"[{message_type.upper()}] {message}")

# Factory function
def create_interactive_documentation() -> InteractiveDocumentation:
    """Create and return InteractiveDocumentation instance"""
    return InteractiveDocumentation()

# Convenience function for direct use
async def start_interactive_docs(user_level: UserExperienceLevel = UserExperienceLevel.INTERMEDIATE) -> None:
    """Start interactive documentation session"""
    docs = create_interactive_documentation()
    context = DocumentationContext(user_level=user_level)
    await docs.start_interactive_help(context)

if __name__ == "__main__":
    # Direct execution support
    import asyncio
    asyncio.run(start_interactive_docs()) 