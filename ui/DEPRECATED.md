# ⚠️ DEPRECATED: Legacy UI Directory

**Status**: DEPRECATED  
**Date**: September 30, 2025  
**Reason**: Theia IDE framework has been completely removed  

---

## 🚨 Important Notice

This directory (`ui/`) contains **legacy files** from the Theia IDE implementation which has been **completely removed** from the PLC-GBT project.

### ❌ Do NOT Use This Directory

- All Theia-related code has been purged
- This directory is kept only for historical reference
- No active development should occur here

### ✅ Use Instead

The **current frontend** is located at:

```
plc-gbt-stack/ui/nextjs/
```

This is a fully functional **Next.js application** with:
- Modern IDE interface
- File Explorer
- Monaco Editor
- Workflow Canvas
- Control Loop Dashboard
- Git Integration UI
- Analytics and Settings

---

## 📁 What's in This Directory

- `package.json` - Legacy Theia dependencies (do not use)
- `node_modules/` - Legacy packages (can be deleted)
- `tsconfig.json` - Theia-specific TypeScript config (deleted)
- `README.md` - Theia documentation (deleted)
- `docs/` - Theia architecture specs (deleted)
- `tests/` - Test framework (may be reusable)
- `config/` - Legacy configuration files

---

## 🗑️ Cleanup Recommendation

This directory should eventually be removed entirely. Before deletion, audit:

1. **Tests Framework** (`tests/framework/`) - May contain reusable testing utilities
2. **Config Files** (`config/`) - May have useful configuration patterns

Everything else can be safely deleted.

---

## ➡️ Migration Path

If you're looking for UI development:

1. Navigate to: `cd ../plc-gbt-stack/ui/nextjs`
2. Read: `docs/QUICK_START.md`
3. Start developing in the Next.js application

---

**For all new development, use `plc-gbt-stack/ui/nextjs/` instead of this directory.**
