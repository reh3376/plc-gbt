# 🚀 @git Automation System

The `@git` code word provides instant Git workflow automation for AI coding agents and developers.

## ⚡ Quick Setup

```bash
# Run the setup script
./plc-gbt-stack/scripts/setup-git-alias.sh

# Or manually add to your shell config
echo "alias @git='$(pwd)/plc-gbt-stack/scripts/git-auto-commit.sh'" >> ~/.zshrc
source ~/.zshrc
```

## 🎯 Usage

### Basic Usage (Auto-generated commit message)
```bash
@git
```

### Custom Commit Message
```bash
@git "feat: implement workflow monitor enhancements"
```

## 🔄 What @git Does

1. **📁 Saves Work**: Ensures all changes are preserved
2. **📦 Stages All**: Runs `git add .` to stage all modifications
3. **💬 Smart Commits**: Generates contextual commit messages or uses your custom message
4. **🚀 Pushes**: Automatically pushes to remote origin with upstream setup
5. **✅ Validates**: Confirms all operations succeeded
6. **📊 Reports**: Returns `success` or creates detailed error report

## 🧠 Smart Commit Message Generation

The script analyzes changed files to generate meaningful commit messages:

| File Pattern | Generated Message |
|--------------|-------------------|
| `WorkflowPanel.tsx` | `feat: enhance workflow monitor with persistence and view modes` |
| `*.tsx`, `*.ts` | `feat: update ComponentName component implementation` |
| `*.md` | `docs: update documentation and guides` |
| `package.json` | `deps: update project dependencies` |
| `*.sh`, `*.py` | `script: update automation and utility scripts` |
| Multiple files (>5) | `feat: major codebase updates and improvements` |
| Default | `feat: implement code improvements and fixes` |

## 📝 Output Modes

### Success Output
```
success
```

### Error Output
```
git-error-report-20250114_143022.md
```

## 🛠️ Error Report Contents

When errors occur, the script generates a detailed markdown report with:

- **Timestamp and context**
- **Exact error message**
- **Current git status**
- **Staged changes**
- **Recent commit history**
- **Suggested recovery actions**
- **Quick recovery commands**

### Example Error Report Structure
```markdown
# Git Automation Error Report

**Timestamp**: Mon Jan 14 14:30:22 PST 2025
**Working Directory**: /Users/user/repos/plc-gbt
**Branch**: main

## Error Details
```bash
Failed to push to remote: remote rejected
```

## Suggested Actions
1. Review the error message above
2. Check branch permissions
3. Verify remote configuration
...
```

## 🔧 AI Agent Integration

Perfect for AI coding agents because:

### ✅ **Simple Trigger**: Just `@git` - easy to remember and type
### ✅ **Zero Configuration**: Works out of the box after setup
### ✅ **Smart Defaults**: Generates appropriate commit messages automatically
### ✅ **Error Handling**: Provides detailed reports for troubleshooting
### ✅ **Status Feedback**: Clear success/failure indication

## 🎨 Advanced Usage

### Custom Commit Types
```bash
@git "fix: resolve workflow panel date formatting issue"
@git "docs: update API documentation"
@git "feat: add new search functionality"
@git "refactor: optimize component performance"
@git "test: add comprehensive test suite"
```

### Conventional Commits Support
The script supports conventional commit format:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

## 🚨 Safety Features

1. **Pre-flight Checks**: Validates git repository state
2. **Staged Change Verification**: Ensures there's something to commit
3. **Atomic Operations**: Either all steps succeed or none
4. **Rollback Information**: Error reports include recovery commands
5. **Branch Protection**: Respects remote branch permissions

## 🔍 Troubleshooting

### Common Issues and Solutions

#### "Not in a git repository"
```bash
# Ensure you're in the project directory
cd /path/to/your/project
@git
```

#### "Failed to push to remote"
```bash
# Check remote configuration
git remote -v

# Set upstream branch
git push -u origin $(git branch --show-current)
```

#### "Permission denied"
```bash
# Check SSH keys or credentials
ssh -T git@github.com

# Or use HTTPS with token
git config credential.helper store
```

## 📋 Prerequisites

- Git repository initialized
- Remote origin configured
- Proper authentication (SSH keys or credentials)
- Bash/Zsh shell environment

## 🎯 Perfect For

- **AI Coding Agents**: Single command automation
- **Rapid Development**: Quick commit/push cycles
- **Consistent Workflow**: Standardized commit messages
- **Error Recovery**: Detailed troubleshooting reports
- **Team Collaboration**: Consistent commit formats

## 💡 Tips

1. **Use descriptive custom messages** for important commits
2. **Let auto-generation handle routine commits**
3. **Check error reports** for detailed troubleshooting
4. **Set up proper SSH keys** for seamless authentication
5. **Use from any directory** in your project

---

*The @git system is designed to streamline Git workflows while maintaining safety and providing excellent error reporting for both human developers and AI coding agents.*
