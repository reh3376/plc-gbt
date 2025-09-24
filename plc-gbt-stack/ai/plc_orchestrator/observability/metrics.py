"""Metrics collection singleton and factory for the PLC Task Orchestrator."""


from plc_orchestrator.observability import MetricsCollector

# Global metrics collector instance
_metrics_collector: MetricsCollector | None = None


def get_metrics_collector() -> MetricsCollector:
    """
    Get the global metrics collector instance.

    Returns:
        The singleton MetricsCollector instance
    """
    global _metrics_collector

    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()

    return _metrics_collector


def reset_metrics_collector() -> None:
    """
    Reset the global metrics collector instance.
    
    This is mainly useful for testing or when you need to 
    completely reinitialize the metrics system.
    """
    global _metrics_collector

    if _metrics_collector is not None:
        # Attempt to export any pending metrics
        if hasattr(_metrics_collector, 'export'):
            try:
                _metrics_collector.export()
            except Exception:
                pass  # Best effort

    _metrics_collector = None


def create_metrics_collector(**kwargs) -> MetricsCollector:
    """
    Create a new metrics collector instance.
    
    This creates a new instance without affecting the global singleton.
    Useful when you need multiple independent metrics collectors.
    
    Args:
        **kwargs: Arguments to pass to MetricsCollector constructor
    
    Returns:
        A new MetricsCollector instance
    """
    return MetricsCollector(**kwargs)
