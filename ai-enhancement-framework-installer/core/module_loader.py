#!/usr/bin/env python3
"""
🔄 AI Enhancement Framework - Dynamic Module Loader

Provides conditional module loading based on the modular configuration system.
Handles graceful imports, dependency validation, and runtime module availability.

Features:
- Conditional module imports based on configuration
- Graceful fallbacks when modules are unavailable
- Dependency resolution and validation
- Runtime module availability checking
- Performance optimization with lazy loading
- Circular dependency detection
- Module health verification

Author: AI Enhancement Framework
Created: 2025-01-20
License: MIT
"""

import sys
import importlib
import importlib.util
import logging
import warnings
from typing import Dict, List, Any, Optional, Set, Tuple, Type, Callable, Union
from pathlib import Path
from functools import wraps, lru_cache
from contextlib import contextmanager

try:
    from ..config import get_module_config, is_module_enabled
except ImportError:
    # Fallback for direct execution
    try:
        from config import get_module_config, is_module_enabled
    except ImportError:
        # Last fallback - import from ai_enhancement_framework
        from ai_enhancement_framework.config import get_module_config, is_module_enabled

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModuleLoadError(Exception):
    """Exception raised when a required module cannot be loaded"""
    pass

class DependencyError(Exception):
    """Exception raised when module dependencies are not satisfied"""
    pass

class ModuleLoader:
    """Dynamic module loader with conditional imports"""
    
    def __init__(self):
        self.config = get_module_config()
        self.loaded_modules: Dict[str, Any] = {}
        self.failed_modules: Set[str] = set()
        self.loading_stack: List[str] = []
        self.module_availability: Dict[str, bool] = {}
    
    @contextmanager
    def loading_context(self, module_name: str):
        """Context manager for tracking module loading to detect circular dependencies"""
        if module_name in self.loading_stack:
            raise ModuleLoadError(f"Circular dependency detected: {' -> '.join(self.loading_stack)} -> {module_name}")
        
        self.loading_stack.append(module_name)
        try:
            yield
        finally:
            self.loading_stack.pop()
    
    def check_module_availability(self, module_name: str) -> bool:
        """Check if a module is available for loading"""
        try:
            # Always check if the module is enabled in configuration first (don't cache this)
            # Use the loader's config if available, otherwise fall back to global
            if hasattr(self, 'config') and self.config:
                enabled = self.config.is_module_enabled(module_name)
            else:
                enabled = is_module_enabled(module_name)
                
            if not enabled:
                # Module is disabled, clear from cache and return False
                self.module_availability[module_name] = False
                return False
            
            # Check cache for file existence (only if module is enabled)
            if module_name in self.module_availability and self.module_availability[module_name] is not False:
                return self.module_availability[module_name]
            
            # Check if the module file exists
            module_path = self._get_module_path(module_name)
            if module_path and module_path.exists():
                self.module_availability[module_name] = True
                return True
            else:
                self.module_availability[module_name] = False
                return False
                
        except Exception as e:
            logger.warning(f"Error checking availability for module '{module_name}': {e}")
            self.module_availability[module_name] = False
            return False
    
    def _get_module_path(self, module_name: str) -> Optional[Path]:
        """Get the file path for a module"""
        module_mapping = {
            "task_orchestrator": "core/enhanced_task_orchestrator.py",
            "memory_management": "core/memory_manager.py", 
            "code_analysis": "core/enhanced_code_analyzer.py",
            "wolfram_integration": "core/wolfram_integration.py",
            "llm_integration": "core/llm_integration.py",
            "database_providers": "providers/enhanced_provider_abstraction.py",
            "model_providers": "providers/enhanced_model_abstraction.py",
            "code_optimization": "optimization/code_quality_optimizer.py",
            "modular_extraction": "optimization/modular_extractor.py",
            "validation_framework": "core/validation_framework.py",
            "health_monitoring": "monitoring/health_check.py",
            "docker_integration": "docker/docker_manager.py"
        }
        
        if module_name in module_mapping:
            framework_root = Path(__file__).parent.parent
            return framework_root / module_mapping[module_name]
        
        return None
    
    def load_module(self, module_name: str, required: bool = False) -> Any:
        """Load a module with conditional logic"""
        
        # Return cached module if already loaded
        if module_name in self.loaded_modules:
            return self.loaded_modules[module_name]
        
        # Check if module failed to load previously
        if module_name in self.failed_modules:
            if required:
                raise ModuleLoadError(f"Required module '{module_name}' previously failed to load")
            return None
        
        # Check availability
        if not self.check_module_availability(module_name):
            if required:
                raise ModuleLoadError(f"Required module '{module_name}' is not available or disabled")
            logger.info(f"Module '{module_name}' is disabled or unavailable, skipping")
            return None
        
        with self.loading_context(module_name):
            try:
                # Validate dependencies first
                self._validate_dependencies(module_name)
                
                # Load the module
                module = self._import_module(module_name)
                
                # Cache successful load
                self.loaded_modules[module_name] = module
                logger.info(f"Successfully loaded module: {module_name}")
                return module
                
            except Exception as e:
                self.failed_modules.add(module_name)
                error_msg = f"Failed to load module '{module_name}': {e}"
                
                if required:
                    raise ModuleLoadError(error_msg)
                else:
                    logger.warning(error_msg)
                    return None
    
    def _validate_dependencies(self, module_name: str) -> None:
        """Validate that module dependencies are satisfied"""
        module_info = self.config.get_module_info(module_name)
        if not module_info:
            return
        
        # Check required dependencies
        for dependency in module_info.get("dependencies", []):
            if not is_module_enabled(dependency):
                raise DependencyError(f"Module '{module_name}' requires '{dependency}' but it's disabled")
            
            # Recursively load dependencies if not already loaded
            if dependency not in self.loaded_modules:
                self.load_module(dependency, required=True)
    
    def _import_module(self, module_name: str) -> Any:
        """Import the actual module"""
        import_mapping = {
            "task_orchestrator": "ai_enhancement_framework.core.enhanced_task_orchestrator",
            "memory_management": "ai_enhancement_framework.core.memory_manager",
            "code_analysis": "ai_enhancement_framework.core.enhanced_code_analyzer", 
            "wolfram_integration": "ai_enhancement_framework.core.wolfram_integration",
            "llm_integration": "ai_enhancement_framework.core.llm_integration",
            "database_providers": "ai_enhancement_framework.providers.enhanced_provider_abstraction",
            "model_providers": "ai_enhancement_framework.providers.enhanced_model_abstraction",
            "code_optimization": "ai_enhancement_framework.optimization.code_quality_optimizer",
            "modular_extraction": "ai_enhancement_framework.optimization.modular_extractor",
            "validation_framework": "ai_enhancement_framework.core.validation_framework",
            "health_monitoring": "ai_enhancement_framework.monitoring.health_check",
            "docker_integration": "ai_enhancement_framework.docker.docker_manager"
        }
        
        module_path = import_mapping.get(module_name)
        if not module_path:
            raise ModuleLoadError(f"Unknown module: {module_name}")
        
        try:
            return importlib.import_module(module_path)
        except ImportError as e:
            # Try alternative import paths or graceful fallbacks
            logger.warning(f"Standard import failed for {module_name}: {e}")
            return self._try_alternative_import(module_name)
    
    def _try_alternative_import(self, module_name: str) -> Any:
        """Try alternative import methods when standard import fails"""
        try:
            # Special handling for code_analysis when libcst is not available
            if module_name == "code_analysis":
                try:
                    import libcst
                except ImportError:
                    logger.warning(f"libcst not available - creating fallback for {module_name}")
                    # Create a fallback module
                    import types
                    fallback_module = types.ModuleType(f'{module_name}_fallback')
                    fallback_module.__dict__.update({
                        'available': False,
                        'reason': 'libcst not available',
                        'fallback': True,
                        'EnhancedCodeAnalyzer': None,
                        'AnalysisLevel': None
                    })
                    return fallback_module
            
            # Try importing from relative path
            relative_paths = {
                "task_orchestrator": ".enhanced_task_orchestrator",
                "memory_management": ".memory_manager",
                "code_analysis": ".enhanced_code_analyzer",
                "wolfram_integration": ".wolfram_integration", 
                "llm_integration": ".llm_integration",
                "validation_framework": ".validation_framework"
            }
            
            if module_name in relative_paths:
                return importlib.import_module(relative_paths[module_name], package="ai_enhancement_framework.core")
            
            # Try importing from providers
            provider_paths = {
                "database_providers": ".enhanced_provider_abstraction",
                "model_providers": ".enhanced_model_abstraction"
            }
            
            if module_name in provider_paths:
                return importlib.import_module(provider_paths[module_name], package="ai_enhancement_framework.providers")
            
            # Try importing from optimization
            optimization_paths = {
                "code_optimization": ".code_quality_optimizer",
                "modular_extraction": ".modular_extractor"
            }
            
            if module_name in optimization_paths:
                return importlib.import_module(optimization_paths[module_name], package="ai_enhancement_framework.optimization")
            
            raise ModuleLoadError(f"No alternative import found for {module_name}")
            
        except Exception as e:
            # For known optional modules, provide fallbacks instead of failing
            if module_name in ["code_analysis", "code_optimization", "modular_extraction"]:
                logger.warning(f"Creating fallback module for {module_name}: {e}")
                import types
                fallback_module = types.ModuleType(f'{module_name}_fallback')
                fallback_module.__dict__.update({
                    'available': False,
                    'reason': str(e),
                    'fallback': True
                })
                return fallback_module
            
            raise ModuleLoadError(f"Alternative import failed for {module_name}: {e}")
    
    def get_available_modules(self) -> Dict[str, bool]:
        """Get list of all available modules and their status"""
        all_modules = self.config.get_all_module_names()
        availability = {}
        
        for module_name in all_modules:
            availability[module_name] = self.check_module_availability(module_name)
        
        return availability
    
    def get_loaded_modules(self) -> Dict[str, Any]:
        """Get all currently loaded modules"""
        return self.loaded_modules.copy()
    
    def get_failed_modules(self) -> Set[str]:
        """Get list of modules that failed to load"""
        return self.failed_modules.copy()
    
    def reload_module(self, module_name: str) -> Any:
        """Reload a specific module"""
        # Clear from caches
        if module_name in self.loaded_modules:
            del self.loaded_modules[module_name]
        
        if module_name in self.failed_modules:
            self.failed_modules.remove(module_name)
        
        if module_name in self.module_availability:
            del self.module_availability[module_name]
        
        # Reload
        return self.load_module(module_name)
    
    def preload_enabled_modules(self) -> Dict[str, bool]:
        """Preload all enabled modules"""
        enabled_modules = self.config.get_enabled_modules()
        results = {}
        
        for module_name in enabled_modules:
            try:
                module = self.load_module(module_name)
                results[module_name] = module is not None
            except Exception as e:
                logger.error(f"Failed to preload {module_name}: {e}")
                results[module_name] = False
        
        return results
    
    def validate_configuration(self) -> Tuple[bool, List[str]]:
        """Validate the current module configuration"""
        issues = []
        
        # Check dependency validation
        valid_deps, dep_issues = self.config.validate_dependencies()
        if not valid_deps:
            issues.extend(dep_issues)
        
        # Check module availability
        for module_name in self.config.get_enabled_modules():
            if not self.check_module_availability(module_name):
                issues.append(f"Enabled module '{module_name}' is not available")
        
        return len(issues) == 0, issues
    
    def clear_cache(self) -> None:
        """Clear all cached module availability and loaded modules"""
        self.module_availability.clear()
        self.loaded_modules.clear()
        self.failed_modules.clear()
    
    def clear_module_cache(self, module_name: str) -> None:
        """Clear cache for a specific module"""
        if module_name in self.module_availability:
            del self.module_availability[module_name]
        if module_name in self.loaded_modules:
            del self.loaded_modules[module_name]
        if module_name in self.failed_modules:
            self.failed_modules.remove(module_name)

# Global module loader instance
_module_loader: Optional[ModuleLoader] = None

def get_module_loader() -> ModuleLoader:
    """Get global module loader instance"""
    global _module_loader
    if _module_loader is None:
        _module_loader = ModuleLoader()
    return _module_loader

def load_module(module_name: str, required: bool = False) -> Any:
    """Quick module loading function"""
    return get_module_loader().load_module(module_name, required)

def safe_import(module_name: str, fallback: Any = None) -> Any:
    """Safely import a module with fallback"""
    try:
        return load_module(module_name, required=False) or fallback
    except Exception:
        return fallback

def require_module(module_name: str) -> Any:
    """Require a module to be available"""
    return load_module(module_name, required=True)

def conditional_import(condition: bool, module_name: str, fallback: Any = None) -> Any:
    """Conditionally import a module"""
    if condition:
        return safe_import(module_name, fallback)
    return fallback

# Decorators for conditional functionality
def requires_module(module_name: str):
    """Decorator to require a module for function execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not is_module_enabled(module_name):
                raise ModuleLoadError(f"Function '{func.__name__}' requires module '{module_name}' to be enabled")
            
            module = require_module(module_name)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def optional_module(module_name: str, fallback_func: Optional[Callable] = None):
    """Decorator for optional module functionality"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if is_module_enabled(module_name):
                try:
                    module = load_module(module_name)
                    if module:
                        return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Optional module '{module_name}' failed: {e}")
            
            if fallback_func:
                return fallback_func(*args, **kwargs)
            else:
                logger.info(f"Skipping function '{func.__name__}' - module '{module_name}' not available")
                return None
        return wrapper
    return decorator 