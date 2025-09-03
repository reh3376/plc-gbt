#!/usr/bin/env python3
"""
Task 23.5.1: Chat Interface Implementation
=========================================

Rich terminal-based chat interface with code syntax highlighting,
progress indicators, and seamless integration with Phase 23.1-23.4 components.

Features:
- Rich text formatting with syntax highlighting
- Real-time progress indicators
- Multi-turn conversation management
- Industrial control system context awareness
- Code execution preview and validation

Author: PLC-GPT Development Team
Date: June 18, 2025
Task: 23.5.1 - Chat Interface
Methodology: AI Task Orchestrator Guide
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Rich console imports for terminal UI
try:
    from rich.columns import Columns
    from rich.console import Console
    from rich.live import Live
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    from rich.prompt import Confirm, Prompt
    from rich.spinner import Spinner
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    logging.warning("Rich library not available - using basic console output")

# Import Phase 23 components
try:
    from ...llm import ApplicationContext, ConversationRole, LLMRequest, LLMRequestType
    from ...llm.conversation import ConversationManager
    from ...llm.service import LLMService, get_llm_service
    from ...llm.task_executor import TaskExecutor
    from ...llm.task_planner import TaskPlanner
except ImportError as e:
    logging.warning(f"Phase 23 components not available: {e}")

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ChatConfig:
    """Configuration for chat interface"""
    max_history: int = 50
    auto_save: bool = True
    syntax_theme: str = "monokai"
    show_progress: bool = True
    enable_voice: bool = False
    context_lines: int = 3
    timeout_seconds: float = 30.0

@dataclass
class ChatMessage:
    """Represents a chat message"""
    role: ConversationRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    code_blocks: List[str] = field(default_factory=list)

class ChatInterface:
    """
    Main chat interface for LLM interaction

    Provides rich terminal-based chat experience with:
    - Syntax highlighted code blocks
    - Real-time progress indicators
    - Multi-turn conversation management
    - Industrial context awareness
    """

    def __init__(self, config: Optional[ChatConfig] = None):
        """
        Initialize chat interface

        Args:
            config: Optional configuration for chat behavior
        """
        self.config = config or ChatConfig()
        self.console = Console() if RICH_AVAILABLE else None
        self.conversation_history: List[ChatMessage] = []
        self.session_id = f"chat_{int(time.time())}"

        # Initialize LLM components
        try:
            self.llm_service = get_llm_service()
            self.conversation_manager = ConversationManager()
            self.task_executor = TaskExecutor()
            self.task_planner = TaskPlanner()
        except Exception as e:
            logger.warning(f"LLM components not fully available: {e}")
            self.llm_service = None

        # State management
        self.is_running = False
        self.current_task = None

    async def start_interactive_session(self) -> None:
        """Start interactive chat session"""
        self.is_running = True

        # Display welcome message
        self._display_welcome()

        try:
            while self.is_running:
                # Get user input
                user_input = await self._get_user_input()

                if not user_input:
                    continue

                # Handle special commands
                if user_input.startswith('/'):
                    await self._handle_command(user_input)
                    continue

                # Process user message
                await self._process_user_message(user_input)

        except KeyboardInterrupt:
            self._display_message("Chat session interrupted by user", "info")
        except Exception as e:
            self._display_message(f"Error in chat session: {e}", "error")
        finally:
            await self._cleanup_session()

    async def send_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Send a message and get response (programmatic interface)

        Args:
            message: User message
            context: Optional context information

        Returns:
            LLM response
        """
        try:
            # Create chat message
            user_message = ChatMessage(
                role=ConversationRole.USER,
                content=message,
                metadata=context or {}
            )

            # Add to history
            self.conversation_history.append(user_message)

            # Get LLM response
            if self.llm_service:
                with self._progress_context("Processing request..."):
                    response = await self._get_llm_response(message, context)
            else:
                response = "LLM service not available - using mock response"

            # Create response message
            assistant_message = ChatMessage(
                role=ConversationRole.ASSISTANT,
                content=response,
                metadata={"context": context}
            )

            # Add to history
            self.conversation_history.append(assistant_message)

            return response

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return f"Error processing message: {e}"

    def _display_welcome(self) -> None:
        """Display welcome message"""
        if self.console:
            welcome_panel = Panel(
                "[bold blue]🤖 PLC-GBT Industrial Control Assistant[/bold blue]\n\n"
                "[green]Welcome to the AI-powered industrial control system assistant![/green]\n"
                "I can help you with:\n"
                "• Control loop analysis and tuning\n"
                "• PLC programming and troubleshooting\n"
                "• System optimization and maintenance\n"
                "• Schema management and configuration\n\n"
                "[yellow]Type '/help' for commands or start chatting![/yellow]",
                title="🏭 Industrial Automation AI",
                border_style="blue"
            )
            self.console.print(welcome_panel)
        else:
            print("=== PLC-GBT Industrial Control Assistant ===")
            print("Welcome! Type '/help' for commands or start chatting!")

    async def _get_user_input(self) -> str:
        """Get user input with rich prompt"""
        try:
            if self.console:
                return Prompt.ask("[bold green]You[/bold green]", console=self.console)
            else:
                return input("You: ").strip()
        except EOFError:
            return "/quit"
        except KeyboardInterrupt:
            return "/quit"

    async def _process_user_message(self, message: str) -> None:
        """Process user message and display response"""
        try:
            # Display user message
            self._display_user_message(message)

            # Get response with progress indicator
            if self.config.show_progress and self.console:
                with Live(self._create_progress_spinner(), console=self.console, refresh_per_second=10):
                    response = await self.send_message(message)
            else:
                response = await self.send_message(message)

            # Display assistant response
            self._display_assistant_message(response)

        except Exception as e:
            self._display_message(f"Error processing message: {e}", "error")

    async def _get_llm_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Get response from LLM service"""
        try:
            if not self.llm_service:
                return "LLM service not available"

            # Create application context
            app_context = ApplicationContext(
                user_input=message,
                conversation_history=self._get_conversation_context(),
                system_state=context or {},
                metadata={"session_id": self.session_id}
            )

            # Create LLM request
            request = LLMRequest(
                request_type=LLMRequestType.CHAT,
                prompt=message,
                context=app_context,
                metadata={"interface": "chat_ui"}
            )

            # Send request to LLM
            response = await self.llm_service.send_request(request)

            if response and response.content:
                return response.content
            else:
                return "No response received from LLM service"

        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            return f"Error communicating with AI assistant: {e}"

    def _get_conversation_context(self) -> List[Dict[str, str]]:
        """Get conversation context for LLM"""
        context = []
        # Get recent messages (limited by config)
        recent_messages = self.conversation_history[-self.config.context_lines*2:]

        for msg in recent_messages:
            context.append({
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            })

        return context

    def _display_user_message(self, message: str) -> None:
        """Display user message with formatting"""
        if self.console:
            user_panel = Panel(
                message,
                title="[bold green]👤 You[/bold green]",
                border_style="green",
                padding=(0, 1)
            )
            self.console.print(user_panel)
        else:
            print(f"You: {message}")

    def _display_assistant_message(self, message: str) -> None:
        """Display assistant message with rich formatting"""
        if self.console:
            # Check for code blocks
            if "```" in message:
                formatted_message = self._format_code_blocks(message)
            else:
                formatted_message = message

            assistant_panel = Panel(
                formatted_message,
                title="[bold blue]🤖 AI Assistant[/bold blue]",
                border_style="blue",
                padding=(0, 1)
            )
            self.console.print(assistant_panel)
        else:
            print(f"AI Assistant: {message}")

    def _format_code_blocks(self, message: str) -> str:
        """Format code blocks with syntax highlighting"""
        if not self.console:
            return message

        # Simple code block detection and formatting
        # In production, would use more sophisticated parsing
        import re

        # Find code blocks
        code_block_pattern = r'```(\w+)?\n(.*?)\n```'

        def replace_code_block(match):
            language = match.group(1) or "text"
            code = match.group(2)

            try:
                syntax = Syntax(code, language, theme=self.config.syntax_theme, line_numbers=True)
                return str(syntax)
            except Exception:
                return f"[code]{code}[/code]"

        formatted = re.sub(code_block_pattern, replace_code_block, message, flags=re.DOTALL)
        return formatted

    def _create_progress_spinner(self) -> Spinner:
        """Create progress spinner for processing"""
        return Spinner("dots", text="🤖 AI is thinking...")

    def _progress_context(self, text: str):
        """Context manager for progress indication"""
        if self.console and self.config.show_progress:
            return Live(Spinner("dots", text=text), console=self.console)
        else:
            return self._null_context()

    def _null_context(self):
        """Null context manager for when rich is not available"""
        from contextlib import nullcontext
        return nullcontext()

    def _display_message(self, message: str, message_type: str = "info") -> None:
        """Display system message"""
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

    async def _handle_command(self, command: str) -> None:
        """Handle special chat commands"""
        cmd = command.lower().strip()

        if cmd == "/help":
            self._display_help()
        elif cmd == "/quit" or cmd == "/exit":
            self.is_running = False
            self._display_message("Goodbye! 👋", "info")
        elif cmd == "/clear":
            if self.console:
                self.console.clear()
            else:
                print("\n" * 50)
        elif cmd == "/history":
            self._display_history()
        elif cmd == "/save":
            await self._save_conversation()
        elif cmd == "/status":
            self._display_status()
        else:
            self._display_message(f"Unknown command: {command}. Type /help for available commands.", "warning")

    def _display_help(self) -> None:
        """Display help information"""
        help_text = """
[bold blue]Available Commands:[/bold blue]

[green]/help[/green]     - Show this help message
[green]/quit[/green]     - Exit the chat session
[green]/clear[/green]    - Clear the screen
[green]/history[/green]  - Show conversation history
[green]/save[/green]     - Save conversation to file
[green]/status[/green]   - Show system status

[bold yellow]Example Queries:[/bold yellow]

• "Analyze the temperature control loop TIC-101"
• "Create a new PID controller schema"
• "What's causing oscillation in my control loop?"
• "Optimize the distillation column control"
• "Generate a tuning report for all loops"
        """

        if self.console:
            help_panel = Panel(help_text, title="🆘 Help", border_style="yellow")
            self.console.print(help_panel)
        else:
            print("=== Help ===")
            print("/help - Show this help")
            print("/quit - Exit chat")
            print("/clear - Clear screen")
            print("/history - Show history")
            print("/save - Save conversation")

    def _display_history(self) -> None:
        """Display conversation history"""
        if not self.conversation_history:
            self._display_message("No conversation history", "info")
            return

        if self.console:
            table = Table(title="Conversation History")
            table.add_column("Time", style="cyan")
            table.add_column("Role", style="green")
            table.add_column("Message", style="white")

            for msg in self.conversation_history[-10:]:  # Show last 10 messages
                time_str = msg.timestamp.strftime("%H:%M:%S")
                role_str = "You" if msg.role == ConversationRole.USER else "AI"
                content_preview = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
                table.add_row(time_str, role_str, content_preview)

            self.console.print(table)
        else:
            print("=== Conversation History ===")
            for msg in self.conversation_history[-10:]:
                role_str = "You" if msg.role == ConversationRole.USER else "AI"
                print(f"[{msg.timestamp.strftime('%H:%M:%S')}] {role_str}: {msg.content[:100]}...")

    async def _save_conversation(self) -> None:
        """Save conversation to file"""
        try:
            filename = f"chat_session_{self.session_id}.txt"
            filepath = Path(filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"PLC-GBT Chat Session - {datetime.now().isoformat()}\n")
                f.write("=" * 50 + "\n\n")

                for msg in self.conversation_history:
                    role_str = "User" if msg.role == ConversationRole.USER else "AI Assistant"
                    f.write(f"[{msg.timestamp.isoformat()}] {role_str}:\n")
                    f.write(f"{msg.content}\n\n")

            self._display_message(f"Conversation saved to {filepath}", "success")

        except Exception as e:
            self._display_message(f"Error saving conversation: {e}", "error")

    def _display_status(self) -> None:
        """Display system status"""
        status_info = {
            "Session ID": self.session_id,
            "Messages": len(self.conversation_history),
            "LLM Service": "Connected" if self.llm_service else "Not Available",
            "Rich UI": "Enabled" if RICH_AVAILABLE else "Basic Mode",
            "Started": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if self.console:
            table = Table(title="System Status")
            table.add_column("Component", style="cyan")
            table.add_column("Status", style="green")

            for key, value in status_info.items():
                table.add_row(key, str(value))

            self.console.print(table)
        else:
            print("=== System Status ===")
            for key, value in status_info.items():
                print(f"{key}: {value}")

    async def _cleanup_session(self) -> None:
        """Cleanup chat session"""
        try:
            if self.config.auto_save and self.conversation_history:
                await self._save_conversation()

            self._display_message("Chat session ended", "info")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Factory function for easy instantiation
def create_chat_interface(config: Optional[ChatConfig] = None) -> ChatInterface:
    """Create and return a configured chat interface"""
    return ChatInterface(config)

# Convenience function for quick chat session
async def start_chat_session(config: Optional[ChatConfig] = None) -> None:
    """Start an interactive chat session"""
    interface = create_chat_interface(config)
    await interface.start_interactive_session()

if __name__ == "__main__":
    # Direct execution support
    import asyncio
    asyncio.run(start_chat_session())
