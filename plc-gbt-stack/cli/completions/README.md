# PLC-GBT CLI Shell Completions

This directory contains shell completion scripts for the PLC-GBT Memory System CLI (`plc-memory`). These completions provide context-aware command and parameter suggestions for enhanced productivity.

## Supported Shells

- **Bash** - Complete command and option completion with dynamic content
- **Zsh** - Advanced completion with descriptions and intelligent suggestions
- **Fish** - Rich interactive completions with dynamic content loading

## Features

- **Context-Aware Completions**: Suggests relevant options based on current command context
- **Dynamic Content**: Loads actual schema names, instance names, and other resources
- **Comprehensive Coverage**: All commands, subcommands, and options supported
- **Performance Optimized**: Fast completion with minimal system impact

## Quick Installation

### Automatic Installation

The easiest way to install completions for your current shell:

```bash
# For current shell (auto-detected)
plc-memory completion install

# For specific shell
plc-memory completion install --shell bash
plc-memory completion install --shell zsh
plc-memory completion install --shell fish
```

### Manual Installation

If you prefer manual installation or the automatic installer doesn't work:

## Bash Completion

### System-wide Installation (requires root)

```bash
# Copy the completion script
sudo cp bash_completion.sh /etc/bash_completion.d/plc-memory

# Or for newer systems
sudo cp bash_completion.sh /usr/share/bash-completion/completions/plc-memory
```

### User Installation

```bash
# Create completion directory if it doesn't exist
mkdir -p ~/.local/share/bash-completion/completions

# Copy the completion script
cp bash_completion.sh ~/.local/share/bash-completion/completions/plc-memory

# Add to your .bashrc
echo 'source ~/.local/share/bash-completion/completions/plc-memory' >> ~/.bashrc
```

### Manual Source (temporary)

```bash
# Source directly in current session
source bash_completion.sh
```

## Zsh Completion

### Using Oh-My-Zsh

```bash
# Copy to Oh-My-Zsh completions directory
cp zsh_completion.zsh ~/.oh-my-zsh/completions/_plc-memory

# Reload completions
compinit
```

### System-wide Installation

```bash
# Copy to system completion directory
sudo cp zsh_completion.zsh /usr/share/zsh/site-functions/_plc-memory
```

### User Installation

```bash
# Create user completion directory
mkdir -p ~/.zsh/completions

# Copy completion script
cp zsh_completion.zsh ~/.zsh/completions/_plc-memory

# Add to .zshrc
echo 'fpath=(~/.zsh/completions $fpath)' >> ~/.zshrc
echo 'autoload -U compinit && compinit' >> ~/.zshrc
```

### Manual Installation

```bash
# Add directly to .zshrc
cat zsh_completion.zsh >> ~/.zshrc
```

## Fish Completion

### User Installation (Recommended)

```bash
# Create Fish completion directory
mkdir -p ~/.config/fish/completions

# Copy completion script
cp fish_completion.fish ~/.config/fish/completions/plc-memory.fish
```

### System-wide Installation

```bash
# Copy to system completion directory (requires root)
sudo cp fish_completion.fish /usr/share/fish/completions/plc-memory.fish
```

### Package Manager Installation

```bash
# If installing via package manager, completions should be automatic
# Check your package manager's fish completion package
```

## Verification

After installation, verify completions work:

### Bash
```bash
# Type and press TAB twice
plc-memory [TAB][TAB]

# Should show: schema instance batch plc memory interactive validate monitor backup restore
```

### Zsh
```bash
# Type and press TAB
plc-memory [TAB]

# Should show commands with descriptions
```

### Fish
```bash
# Type and press TAB
plc-memory [TAB]

# Should show interactive completions with descriptions
```

## Advanced Configuration

### Performance Tuning

For systems with many schemas/instances, you can configure completion caching:

```bash
# Set environment variables in your shell profile
export PLC_MEMORY_COMPLETION_CACHE=true
export PLC_MEMORY_COMPLETION_CACHE_TTL=300  # 5 minutes
```

### Custom Completion Paths

If plc-memory is installed in a non-standard location:

```bash
# Set the path in your shell profile
export PLC_MEMORY_CLI_PATH="/path/to/plc-memory"
```

### Disable Dynamic Completions

For environments where dynamic completion queries might be slow:

```bash
# Disable dynamic content loading
export PLC_MEMORY_COMPLETION_STATIC=true
```

## Troubleshooting

### Common Issues

#### Completions Not Working

1. **Check installation path**:
   ```bash
   # Bash
   ls /etc/bash_completion.d/plc-memory
   ls ~/.local/share/bash-completion/completions/plc-memory
   
   # Zsh
   ls ~/.zsh/completions/_plc-memory
   ls /usr/share/zsh/site-functions/_plc-memory
   
   # Fish
   ls ~/.config/fish/completions/plc-memory.fish
   ```

2. **Verify shell configuration**:
   ```bash
   # Check if completion loading is enabled
   grep -i completion ~/.bashrc ~/.zshrc ~/.config/fish/config.fish
   ```

3. **Reload shell configuration**:
   ```bash
   # Bash
   source ~/.bashrc
   
   # Zsh
   source ~/.zshrc
   
   # Fish
   source ~/.config/fish/config.fish
   ```

#### Dynamic Completions Not Working

1. **Check plc-memory accessibility**:
   ```bash
   which plc-memory
   plc-memory --version
   ```

2. **Test individual completion functions**:
   ```bash
   # Test schema listing
   plc-memory schema list --format=names
   ```

3. **Check error messages**:
   ```bash
   # Run with debug output
   set -x  # Bash
   set fish_trace 1  # Fish
   # Then try completion
   ```

#### Performance Issues

1. **Enable completion caching**:
   ```bash
   export PLC_MEMORY_COMPLETION_CACHE=true
   ```

2. **Reduce completion scope**:
   ```bash
   export PLC_MEMORY_COMPLETION_LIMIT=50
   ```

3. **Use static completions**:
   ```bash
   export PLC_MEMORY_COMPLETION_STATIC=true
   ```

### Getting Help

If you encounter issues:

1. **Check CLI help**:
   ```bash
   plc-memory completion --help
   ```

2. **Enable debug mode**:
   ```bash
   plc-memory --verbose completion install
   ```

3. **Check system logs**:
   ```bash
   # Look for completion-related errors
   journalctl -f | grep plc-memory
   ```

## Updating Completions

When updating the PLC-GBT CLI:

1. **Automatic update**:
   ```bash
   plc-memory completion update
   ```

2. **Manual update**:
   ```bash
   # Re-run installation
   plc-memory completion install --force
   ```

3. **Verify new features**:
   ```bash
   plc-memory completion verify
   ```

## Development

### Testing Completions

For developers working on completion scripts:

```bash
# Test Bash completions
bash -c "source bash_completion.sh; complete -p plc-memory"

# Test Zsh completions
zsh -c "source zsh_completion.zsh; which _plc_memory"

# Test Fish completions
fish -c "source fish_completion.fish; complete -C'plc-memory '"
```

### Adding New Completions

When adding new commands or options:

1. Update the relevant completion script
2. Test with `source script_name`
3. Verify all completion paths work
4. Update this README if needed

### Performance Profiling

To profile completion performance:

```bash
# Bash
time complete -W "$(plc-memory schema list --format=names)" plc-memory

# Zsh
zprof  # Enable profiling in .zshrc
# Use completions, then check output

# Fish
time fish -c "complete -C'plc-memory schema '"
```

## Shell-Specific Features

### Bash Features

- Tab completion with double-tab for options
- Filename completion for file arguments
- Command chaining support

### Zsh Features

- Menu completion with arrow key navigation
- Completion descriptions for better UX
- Advanced matching (fuzzy, approximate)
- Completion caching for performance

### Fish Features

- Real-time suggestions as you type
- Syntax highlighting for commands
- History-based completions
- Visual completion menu

## Integration Examples

### Combining with Other Tools

```bash
# Use with watch for monitoring
watch -n 1 'plc-memory instance list | grep running'

# Use with grep for filtering
plc-memory schema list | grep pid

# Use with jq for JSON processing
plc-memory memory status --format=json | jq '.redis.memory_usage'
```

### Automation Scripts

```bash
#!/bin/bash
# Example automation script using completions

# Get all running instances
instances=$(plc-memory instance list --status=running --format=names)

for instance in $instances; do
    echo "Checking $instance..."
    plc-memory instance status "$instance" --detailed
done
```

## Version Compatibility

- **Bash**: 4.0+ (uses associative arrays)
- **Zsh**: 5.0+ (uses modern completion system)
- **Fish**: 3.0+ (uses modern completion syntax)

## License

These completion scripts are part of the PLC-GBT project and follow the same license terms. 