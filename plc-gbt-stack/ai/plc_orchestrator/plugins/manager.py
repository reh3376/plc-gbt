"""Plugin manager singleton and factory for the PLC Task Orchestrator."""


from plc_orchestrator.plugins.base import PluginManager

# Global plugin manager instance
_plugin_manager: PluginManager | None = None


def get_plugin_manager() -> PluginManager:
    """
    Get the global plugin manager instance.

    Returns:
        The singleton PluginManager instance
    """
    global _plugin_manager

    if _plugin_manager is None:
        _plugin_manager = PluginManager()

    return _plugin_manager


def reset_plugin_manager() -> None:
    """
    Reset the global plugin manager instance.
    
    This is mainly useful for testing or when you need to 
    completely reinitialize the plugin system.
    """
    global _plugin_manager

    if _plugin_manager is not None:
        # Attempt to shutdown gracefully
        if hasattr(_plugin_manager, 'shutdown'):
            _plugin_manager.shutdown()

    _plugin_manager = None


def create_plugin_manager() -> PluginManager:
    """
    Create a new plugin manager instance.
    
    This creates a new instance without affecting the global singleton.
    Useful when you need multiple independent plugin managers.
    
    Returns:
        A new PluginManager instance
    """
    return PluginManager()
