---
trigger: manual
description: 
globs: 
---

## File Path Tool Call Guidelines

When using Edit, MultiEdit, or other file manipulation tools, always use the COMPLETE file path, never just a directory path. 

**Common Error Pattern:**
- ❌ WRONG: `/home/wouter/Repos/spellbook/apps/Serendipity/`
- ✅ CORRECT: `/home/wouter/Repos/spellbook/apps/Serendipity/scripts/ValyrianGames/script_name.py`

**How to Fix When This Happens:**
1. If you get a gitignore error or "Access prohibited" error, check if you're passing a directory path instead of a file path
2. Always include the complete path including the filename and extension
3. Use the Read tool first to verify the file exists and get the exact content before making edits
4. The file_path parameter must point to a specific file, not a directory

**Example of Correct Usage:**
```python
# Read the file first
Read(file_path="/home/wouter/Repos/spellbook/apps/Serendipity/scripts/ValyrianGames/run_coding_challenge_phase_2.py")

# Then edit with the complete file path
Edit(file_path="/home/wouter/Repos/spellbook/apps/Serendipity/scripts/ValyrianGames/run_coding_challenge_phase_2.py", ...)
