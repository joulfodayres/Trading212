# 📦 Obsolete Documentation Archive

**Purpose:** This directory contains documentation files that are no longer actively used or have been superseded by current implementations.

**Status:** Phase 4 Complete - Reorganization in progress

---

## 📋 Files Pending Review for Archival

The following files have been identified as potential candidates for archival. They are currently still in `docs/` but should be reviewed:

### 1. **CLEANUP_PLAN.md**
- **Location:** `docs/CLEANUP_PLAN.md`
- **Status:** ❓ Pending review
- **Reason:** Appears to be a cleanup plan, but unclear if cleanup was completed or if still relevant
- **Action:** 
  - If cleanup is complete and no longer needed → Move here
  - If cleanup is ongoing → Keep in docs/ and update regularly
  - If cleanup is abandoned → Move here with deprecation note

### 2. **SIMPLIFY_TO_SINGLEUSER.md**
- **Location:** `docs/SIMPLIFY_TO_SINGLEUSER.md`
- **Status:** ❌ Likely Obsolete
- **Reason:** Appears to be an old design consideration from earlier phases. Current system uses proper Supabase multi-user authentication with Row-Level Security (RLS).
- **Action:** Recommend moving to this directory with deprecation note
- **Replacement:** See KNOWLEDGE_BASE.md → Database Schema → RLS for current auth model

### 3. **STRATEGY_TABLES_DESIGN.md**
- **Location:** `docs/STRATEGY_TABLES_DESIGN.md`
- **Status:** ❌ Superseded
- **Reason:** This file documents the design of strategy tables. The actual implementation now uses `strategies` and `strategy_parameters` tables with a more sophisticated approach (10 parameters, pos -1/0/1).
- **Action:** Recommend moving to this directory
- **Replacement:** See CODE_EXAMPLES.md → Database examples and KNOWLEDGE_BASE.md → Database Schema

### 4. **STRATEGY_TABLES_COMPARISON.md**
- **Location:** `docs/STRATEGY_TABLES_COMPARISON.md`
- **Status:** ❌ Superseded
- **Reason:** Compares old design options. Current implementation supersedes all options discussed.
- **Action:** Recommend moving to this directory
- **Replacement:** See current strategy_parameters implementation in backend code

### 5. **DOCUMENTATION_INDEX.md**
- **Location:** `docs/DOCUMENTATION_INDEX.md`
- **Status:** ⚠️ Superseded
- **Reason:** This was an old markdown-based documentation index. Now replaced by modern `index.html` with better search and navigation.
- **Action:** Keep as backup or move to this directory
- **Replacement:** Use `docs/index.html` for documentation navigation

---

## 🗂️ Archive Structure

```
docs/_obsolete/
├── README.md (this file)
├── CLEANUP_PLAN.md (pending)
├── SIMPLIFY_TO_SINGLEUSER.md (pending)
├── STRATEGY_TABLES_DESIGN.md (pending)
├── STRATEGY_TABLES_COMPARISON.md (pending)
├── DOCUMENTATION_INDEX.md (pending)
└── deprecated-notes/
    └── [deprecation notes explaining why each file was archived]
```

---

## 📝 Deprecation Process

When a file is moved here, create a deprecation note:

```markdown
# DEPRECATION NOTICE

**Deprecated Date:** YYYY-MM-DD  
**Reason:** [Brief explanation]  
**Last Known Use:** [When was this last relevant?]  
**Replacement Documentation:** [Point to current docs]  
**Archived By:** [Who/when]

---

## Why This File Was Archived

[Detailed explanation of why this is no longer needed]

---

## Historical Context

[Brief history of what this file was about]
```

---

## 🔍 How to Find Historical Information

If you need information from archived docs:

1. **Search this directory** for topic keywords
2. **Check git history** for when files were changed:
   ```bash
   git log --all --full-history -- docs/FILENAME.md
   ```
3. **Review _archive/ folders** for phase-specific documentation:
   - `docs/_archive/phase-2/` - Phase 2 implementation docs
   - `docs/_archive/phase-3/` - Phase 3 implementation docs
   - `docs/_archive/sessions/` - Development session notes

---

## ✅ Archival Checklist

When archiving a file:

- [ ] Confirm it's truly obsolete or superseded
- [ ] Identify the replacement/current documentation
- [ ] Create deprecation note
- [ ] Move file to _obsolete/
- [ ] Update any internal links
- [ ] Check git history for context
- [ ] Update DOCUMENTATION_STRUCTURE.md

---

## 🔗 Current Documentation References

Instead of using files in this directory, reference these current docs:

| Topic | Current Documentation |
|-------|----------------------|
| Project Overview | `KNOWLEDGE_BASE.md` |
| API Endpoints | `API_REFERENCE.md` |
| Strategy Implementation | `CODE_EXAMPLES.md` + `KNOWLEDGE_BASE.md#database-schema` |
| Strategy Tables Design | `KNOWLEDGE_BASE.md#strategies-table` |
| User Authentication | `KNOWLEDGE_BASE.md#users-table` + `DEVELOPMENT.md` |
| Documentation Index | `index.html` |
| Quick Lookup | `QUICK_REFERENCE.md` |

---

## 📊 Statistics

**Files Pending Archival:** 5

**Estimated Lines to Archive:** ~500 lines

**Space Saved:** ~200KB

---

## 🚀 Next Steps

1. **Review Decision**
   - Confirm which files to archive
   - Get approval if needed

2. **Create Deprecation Notes**
   - For each file being archived
   - Explain why and point to replacements

3. **Move Files**
   - Run: `git mv docs/FILENAME.md docs/_obsolete/`
   - Commit with message: `docs: Archive FILENAME - superseded by [replacement]`

4. **Update References**
   - Update DOCUMENTATION_STRUCTURE.md
   - Update any links in other docs
   - Update navigation in index.html if needed

5. **Communicate**
   - Let team know about changes
   - Point to new documentation locations

---

## 📞 Questions?

If you're unsure whether a file should be archived:
- Check DOCUMENTATION_STRUCTURE.md for guidance
- Review the file's content to understand its purpose
- Ask: "Is this still used or referenced in current code?"
- Ask: "Is there newer documentation on this topic?"

---

**Last Updated:** 2026-09-21  
**Status:** Awaiting archival decisions  
**Maintained By:** Claude Code

---

**Note:** This directory is intended to keep documentation organized and accessible. Files here are preserved for historical reference but should not be used for current development. Always reference the current documentation in `docs/` and linked from `docs/index.html`.
