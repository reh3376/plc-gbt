# PLC Engineer Workflow Guide

## Overview

This guide provides comprehensive instructions for engineers working with PLC files in the automated version control workflow. The system provides seamless integration between Studio 5000 development and GitHub-based collaboration.

## Quick Start

### 1. Clone Repository
```bash
# Clone your assigned PLC repository
plc-clone https://github.com/reh3376/plc-100.git

# Navigate to repository
cd plc-100

# Check repository status
plc-status
```

### 2. Open in Studio 5000
1. Open Studio 5000
2. Navigate to `plc-acd/` directory
3. Open the `.acd` file
4. Begin development work

### 3. Create Feature Branch
```bash
# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Example: 
git checkout -b feature/update-pid-parameters
```

### 4. Make Changes and Commit
```bash
# Validate files before commit
plc-validate

# Add changes
git add plc-acd/

# Commit with descriptive message
git commit -m "Update PID parameters for temperature control loop"

# Push to GitHub
git push origin feature/your-feature-name
```

### 5. Create Pull Request
1. Go to GitHub repository
2. Click "New Pull Request"
3. Select your feature branch
4. Add description of changes
5. Submit for review

## Directory Structure

```
repository/
├── plc-acd/                    # Current ACD file (work here)
│   └── PLC100_Mashing.acd     # Your Studio 5000 file
├── plc-l5x/                    # Current L5X file (auto-generated)
│   └── PLC100_Mashing.L5X     # Automatically converted
├── plc-acd-previous/           # Previous ACD versions
│   ├── PLC100_Mashing_20250707_120000.acd
│   └── PLC100_Mashing_20250706_150000.acd
└── plc-l5x-previous/           # Previous L5X versions
    ├── PLC100_Mashing_20250707_120000.L5X
    └── PLC100_Mashing_20250706_150000.L5X
```

## CLI Tools Reference

### plc-clone
Clone PLC repository with automated setup
```bash
plc-clone <repository-url> [target-directory]
plc-clone --validate  # Validate after cloning
plc-clone --no-lfs    # Skip Git LFS setup
```

### plc-status
Check repository and file status
```bash
plc-status            # Basic status
plc-status --detailed # Detailed file information
plc-status --git      # Git status only
plc-status --files    # File inventory only
```

### plc-validate
Validate files before commit
```bash
plc-validate                    # Validate current files
plc-validate --all             # Validate all files
plc-validate --structure       # Structure only
plc-validate --strict          # Strict validation
plc-validate file1.acd file2.l5x  # Specific files
```

## Studio 5000 Integration

### Best Practices

1. **Always work with files in `plc-acd/` directory**
2. **Save frequently and commit logical changes**
3. **Use descriptive commit messages**
4. **Test changes before pushing**
5. **Create feature branches for all changes**

### File Management

- **Single File Rule**: Only one `.acd` file in `plc-acd/` directory
- **Auto-Archival**: Previous versions automatically moved to `plc-acd-previous/`
- **Auto-Conversion**: L5X files automatically generated from ACD files
- **Version History**: Complete history maintained with timestamps

### Common Workflows

#### Adding New Ladder Logic
1. Open ACD file in Studio 5000
2. Add new rungs/routines
3. Save and verify in Studio 5000
4. Validate: `plc-validate`
5. Commit: `git add plc-acd/ && git commit -m "Add new safety interlock logic"`
6. Push and create PR

#### Modifying PID Parameters
1. Open ACD file in Studio 5000
2. Navigate to PID instruction
3. Modify parameters (Kp, Ki, Kd)
4. Save and test in emulation
5. Validate: `plc-validate`
6. Commit: `git add plc-acd/ && git commit -m "Tune PID parameters for loop 101"`
7. Push and create PR

#### Adding New Tags
1. Open ACD file in Studio 5000
2. Add tags in Controller Tags
3. Save file
4. Validate: `plc-validate`
5. Commit: `git add plc-acd/ && git commit -m "Add tags for new sensor inputs"`
6. Push and create PR

## Automated Workflows

### Pull Request Validation
When you create a PR, automated validation runs:
- ✅ Directory structure compliance
- ✅ File format validation
- ✅ Single file constraint checking
- ✅ Conversion compatibility testing

### Merge Automation
When your PR is approved and merged:
- 🔄 Current files archived with timestamp
- 🔄 New files become current
- 🔄 L5X files automatically generated from ACD
- 🔄 All changes committed automatically

### Error Handling
If conversion fails:
- 🚨 GitHub issue automatically created
- 📧 Team notified of conversion error
- 🔄 Manual intervention required
- 📋 Detailed error information provided

## Troubleshooting

### Common Issues

#### "Multiple files in plc-acd/" Error
**Problem**: More than one ACD file in current directory
**Solution**: 
```bash
# Check current files
plc-status --files

# Move extra files to previous directory
mv plc-acd/extra_file.acd plc-acd-previous/extra_file_$(date +%Y%m%d_%H%M%S).acd
```

#### "File validation failed" Error
**Problem**: File corruption or format issues
**Solution**:
```bash
# Validate specific file
plc-validate plc-acd/your_file.acd

# Check file in Studio 5000
# Re-save if necessary
```

#### "Git LFS pointer file" Error
**Problem**: File not downloaded from Git LFS
**Solution**:
```bash
# Download LFS files
git lfs pull

# Check LFS status
git lfs ls-files
```

### Getting Help

1. **Check status**: `plc-status --detailed`
2. **Validate files**: `plc-validate --all`
3. **Review Git status**: `git status`
4. **Check recent commits**: `git log --oneline -5`
5. **Contact repository administrator** if issues persist

## Advanced Features

### Branch Management
```bash
# List branches
git branch -a

# Switch branches
git checkout main
git checkout feature/your-branch

# Merge latest changes
git checkout main
git pull origin main
git checkout feature/your-branch
git merge main
```

### Conflict Resolution
If merge conflicts occur:
1. Repository owner will be notified
2. Manual resolution required
3. Follow conflict resolution procedures
4. Coordinate with team for complex conflicts

### File History
```bash
# View file history
git log --follow plc-acd/your_file.acd

# Compare with previous version
git diff HEAD~1 plc-acd/your_file.acd

# Restore previous version if needed
git checkout HEAD~1 -- plc-acd/your_file.acd
```

## Security and Compliance

### Access Control
- All changes require pull request approval
- Repository owner has final authority
- Branch protection prevents direct pushes to main
- Code owners automatically requested for review

### Audit Trail
- Complete change history maintained
- All actions logged and traceable
- Automated backup and recovery
- Compliance reporting available

### Data Protection
- Secure file storage and transmission
- Access logging and monitoring
- Regular automated backups
- Disaster recovery procedures

---

**Support**: Contact repository administrator for assistance
**Documentation**: Updated automatically with workflow changes
**Training**: Video tutorials and hands-on sessions available
