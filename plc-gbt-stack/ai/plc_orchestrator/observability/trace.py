"""Tracing singleton and factory for the PLC Task Orchestrator."""

from typing import Optional

from plc_orchestrator.observability import Tracer

# Global tracer instance
_tracer: Optional[Tracer] = None


def get_tracer() -> Tracer:
    """
    Get the global tracer instance.

    Returns:
        The singleton Tracer instance
    """
    global _tracer
    
    if _tracer is None:
        _tracer = Tracer()
    
    return _tracer


def reset_tracer() -> None:
    """
    Reset the global tracer instance.
    
    This is mainly useful for testing or when you need to 
    completely reinitialize the tracing system.
    """
    global _tracer
    
    if _tracer is not None:
        # Attempt to export any pending spans
        if hasattr(_tracer, 'export'):
            try:
                _tracer.export()
            except Exception:
                pass  # Best effort
    
    _tracer = None


def create_tracer(**kwargs) -> Tracer:
    """
    Create a new tracer instance.
    
    This creates a new instance without affecting the global singleton.
    Useful when you need multiple independent tracers.
    
    Args:
        **kwargs: Arguments to pass to Tracer constructor
    
    Returns:
        A new Tracer instance
    """
    return Tracer(**kwargs)
