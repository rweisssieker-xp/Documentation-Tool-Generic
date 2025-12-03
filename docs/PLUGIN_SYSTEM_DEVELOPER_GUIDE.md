# Plugin System & Marketplace - Developer Guide

**Version:** 3.0.0  
**Last Updated:** 2025-12-01  
**Target Audience:** Plugin Developers, System Integrators, ISVs

---

## Table of Contents

1. [Introduction](#introduction)
2. [Plugin Architecture](#plugin-architecture)
3. [Creating Your First Plugin](#creating-your-first-plugin)
4. [Plugin SDK Reference](#plugin-sdk-reference)
5. [Hooks and Events](#hooks-and-events)
6. [Security and Sandboxing](#security-and-sandboxing)
7. [Plugin Marketplace](#plugin-marketplace)
8. [Best Practices](#best-practices)
9. [Examples](#examples)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is the Plugin System?

The Plugin System enables third-party developers to extend AHG functionality through custom plugins. Similar to VSCode extensions or WordPress plugins, this system allows you to:

- Add custom export formats
- Integrate with third-party services
- Create custom workflows
- Extend UI functionality
- Add new AI model integrations

### Key Benefits

- **Extensibility**: Add features without modifying core code
- **Sandboxed Execution**: Safe plugin execution environment
- **Marketplace**: Share plugins with the community
- **SDK Support**: Comprehensive SDK for plugin development
- **Version Management**: Plugin versioning and updates

---

## Plugin Architecture

### Components

```
Plugin System
├── Plugin Manager      # Loads and manages plugins
├── Plugin Loader       # Loads plugin code safely
├── Plugin SDK          # Base classes and utilities
├── Hook System         # Plugin hooks for extension points
├── Event System        # Event-driven plugin communication
├── Sandbox Executor    # Secure execution environment
└── Marketplace        # Plugin discovery and distribution
```

### Plugin Lifecycle

1. **Discovery**: Plugin found in plugins directory or marketplace
2. **Loading**: Plugin code loaded and validated
3. **Initialization**: Plugin's `on_load()` method called
4. **Execution**: Plugin responds to hooks and events
5. **Unloading**: Plugin's `on_unload()` method called

---

## Creating Your First Plugin

### Step 1: Create Plugin Directory

Create a directory for your plugin:

```bash
mkdir plugins/my_custom_export
cd plugins/my_custom_export
```

### Step 2: Create Plugin File

Create `plugin.py`:

```python
from src.plugins.sdk.base import BasePlugin
from typing import Dict, Any

class MyCustomExportPlugin(BasePlugin):
    """Custom export format plugin"""
    
    def on_load(self):
        """Called when plugin is loaded"""
        self.logger.info(f"Plugin {self.metadata.name} loaded")
    
    def on_unload(self):
        """Called when plugin is unloaded"""
        self.logger.info(f"Plugin {self.metadata.name} unloaded")
    
    def export_document(self, session_data: Dict[str, Any], output_path: str):
        """Custom export method"""
        # Your export logic here
        pass
```

### Step 3: Create Metadata File

Create `metadata.json`:

```json
{
  "id": "my_custom_export",
  "name": "My Custom Export",
  "version": "1.0.0",
  "description": "Custom export format for my organization",
  "author": "Your Name",
  "dependencies": {
    "some_package": ">=1.0.0"
  }
}
```

### Step 4: Load Plugin

#### Using GUI

1. Open AHG application
2. Navigate to: **🚀 Innovation** → **🔌 Plugin System...**
3. Click **Load Plugin**
4. Select your `plugin.py` file

#### Using CLI

```bash
python cli/innovation_cli.py plugin load --path plugins/my_custom_export/plugin.py
```

#### Using Python

```python
from src.plugins import PluginManager

manager = PluginManager()
success = manager.load_plugin("plugins/my_custom_export/plugin.py")
```

---

## Plugin SDK Reference

### BasePlugin Class

All plugins must inherit from `BasePlugin`:

```python
from src.plugins.sdk.base import BasePlugin

class MyPlugin(BasePlugin):
    def on_load(self):
        """Called when plugin is loaded"""
        pass
    
    def on_unload(self):
        """Called when plugin is unloaded"""
        pass
```

### Plugin Metadata

Access plugin metadata:

```python
class MyPlugin(BasePlugin):
    def on_load(self):
        print(f"Plugin ID: {self.metadata.id}")
        print(f"Plugin Name: {self.metadata.name}")
        print(f"Plugin Version: {self.metadata.version}")
        print(f"Plugin Author: {self.metadata.author}")
```

### Logger

Use the built-in logger:

```python
class MyPlugin(BasePlugin):
    def on_load(self):
        self.logger.info("Plugin loaded")
        self.logger.warning("This is a warning")
        self.logger.error("This is an error")
```

---

## Hooks and Events

### Hooks

Hooks allow plugins to extend functionality at specific points:

```python
from src.plugins.sdk.hooks import HookSystem

class MyPlugin(BasePlugin):
    def on_load(self):
        # Register hook
        hook_system = HookSystem()
        hook_system.register_hook("before_export", self.my_export_handler)
    
    def my_export_handler(self, session_data):
        """Called before document export"""
        # Modify session_data or perform actions
        return session_data
```

### Events

Events enable event-driven plugin communication:

```python
from src.plugins.sdk.events import EventSystem, EventType

class MyPlugin(BasePlugin):
    def on_load(self):
        event_system = EventSystem()
        event_system.subscribe(EventType.SESSION_STARTED, self.on_session_started)
    
    def on_session_started(self, session_id):
        """Called when session starts"""
        self.logger.info(f"Session started: {session_id}")
```

### Available Event Types

- `SESSION_STARTED` - Session started
- `SESSION_STOPPED` - Session stopped
- `STEP_ADDED` - Step added to session
- `DOCUMENT_GENERATED` - Document generated
- `PLUGIN_LOADED` - Plugin loaded
- `PLUGIN_UNLOADED` - Plugin unloaded

---

## Security and Sandboxing

### Sandboxed Execution

Plugins run in a sandboxed environment with restricted access:

**Allowed Modules:**
- `json`, `pathlib`, `datetime`, `typing`
- `collections`, `enum`, `logging`

**Blocked Modules:**
- `os`, `sys`, `subprocess`, `socket`
- `pickle`, `marshal`, `ctypes`

### Security Best Practices

1. **Validate Input**: Always validate plugin input
2. **Limit Permissions**: Request only necessary permissions
3. **No File System Access**: Use provided APIs instead
4. **No Network Access**: Use provided HTTP clients
5. **Code Review**: Review plugin code before distribution

---

## Plugin Marketplace

### Registering Plugins

Plugins can be registered in the marketplace:

```python
from src.plugins.marketplace.registry import PluginRegistry

registry = PluginRegistry()
registry.register_plugin(
    plugin_id="my_plugin",
    metadata={
        "name": "My Plugin",
        "version": "1.0.0",
        "description": "Plugin description",
        "author": "Author Name"
    }
)
```

### Searching Plugins

```python
registry = PluginRegistry()
results = registry.search_plugins("export")
for plugin in results:
    print(f"{plugin['name']}: {plugin['description']}")
```

---

## Best Practices

### Plugin Design

1. **Single Responsibility**: Each plugin should do one thing well
2. **Clear Naming**: Use descriptive names for plugins and methods
3. **Error Handling**: Implement comprehensive error handling
4. **Documentation**: Document all public methods and hooks
5. **Versioning**: Use semantic versioning for plugins

### Performance

1. **Lazy Loading**: Load resources only when needed
2. **Caching**: Cache expensive operations
3. **Async Operations**: Use async for long-running tasks
4. **Resource Cleanup**: Clean up resources in `on_unload()`

### Testing

1. **Unit Tests**: Test plugin functionality in isolation
2. **Integration Tests**: Test plugin interaction with AHG
3. **Mock Dependencies**: Mock external dependencies
4. **Test Hooks**: Test hook registration and execution

---

## Examples

### Example 1: Custom Export Format

```python
from src.plugins.sdk.base import BasePlugin
from typing import Dict, Any
import json

class JSONExportPlugin(BasePlugin):
    """Export sessions as JSON"""
    
    def on_load(self):
        self.logger.info("JSON Export Plugin loaded")
    
    def on_unload(self):
        self.logger.info("JSON Export Plugin unloaded")
    
    def export_session(self, session_data: Dict[str, Any], output_path: str):
        """Export session as JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Exported to {output_path}")
```

### Example 2: Jira Integration

```python
from src.plugins.sdk.base import BasePlugin
from src.plugins.sdk.events import EventSystem, EventType

class JiraIntegrationPlugin(BasePlugin):
    """Integrate with Jira"""
    
    def on_load(self):
        event_system = EventSystem()
        event_system.subscribe(
            EventType.DOCUMENT_GENERATED,
            self.create_jira_ticket
        )
    
    def create_jira_ticket(self, document_data):
        """Create Jira ticket when document is generated"""
        # Jira integration logic
        pass
```

---

## Troubleshooting

### Plugin Won't Load

**Problem**: Plugin fails to load

**Solution**: Check:
- Plugin inherits from `BasePlugin`
- `on_load()` and `on_unload()` methods exist
- Metadata file is valid JSON
- No syntax errors in plugin code

### Hook Not Executing

**Problem**: Hook registered but not executing

**Solution**: Ensure:
- Hook is registered in `on_load()`
- Hook name matches exactly
- Hook system is initialized

### Sandbox Errors

**Problem**: `ImportError` for blocked modules

**Solution**: Use provided APIs instead of direct imports

---

## Additional Resources

- [Plugin SDK API Reference](./PLUGIN_SDK_API.md)
- [Hook System Documentation](./HOOK_SYSTEM.md)
- [Event System Documentation](./EVENT_SYSTEM.md)
- [Marketplace Guidelines](./MARKETPLACE_GUIDELINES.md)

---

**Document Version:** 3.0.0  
**Last Updated:** 2025-12-01  
**Maintained By:** Technical Writing Team






