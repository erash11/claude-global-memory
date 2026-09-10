# Use MCP for agent access and CLI for operations

The project will expose one shared retrieval and promotion core through an MCP server for conversational agent access and a CLI for setup, diagnostics, synchronization, and batch operations. A Zotero desktop plugin is deferred because it would add client-version coupling without improving the core access path; it will be reconsidered only if a working MCP/CLI pilot reveals recurring need for native Zotero buttons, status, or event hooks.
