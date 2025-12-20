# Valesco System Dependency Map
===============================
Version: 1.9.1
Status:  ACTIVE

This document defines the "Blast Radius" of changes within the Intelligent-Tools Architecture.

0. THE COGNITIVE CHAIN (AI "Brain" Dependencies)
------------------------------------------------
These components establish the AI's persona and rules.
IF YOU CHANGE THIS...              | ...THE AI WILL FAIL HERE
-----------------------------------|---------------------------------------
docs/governance/valesco_instructions| 1. **The Logic Model** (AI won't know how to price)
                                   | 2. **Schema Enforcement** (AI won't respect units)
                                   | 3. **Truth Hierarchy** (AI might override Core data)
-----------------------------------|---------------------------------------
bin/prepare_context.bat            | 1. **Activation Failure** (The Header/Handshake won't work)
(Specifically the Header injection)| 2. **Persona Collapse** (AI reverts to generic GPT behavior)
-----------------------------------|---------------------------------------
engine/prompts/agent_*.md          | 1. **Role Failure** (Estimator won't check for missing rates)
(Note: Must be .md)                | 2. **Security Breach** (Architect won't block code generation)
                                   | 3. **Script Crash** (Material Manager.py looks for .md)

1. THE DATA CHAIN (Logical Dependencies)
----------------------------------------
IF YOU CHANGE THIS...              | ...THIS WILL BREAK
-----------------------------------|---------------------------------------
engine/config/materials_allocator  | 1. Material Manager (Script Generation)
                                   | 2. Core Materials (Validation Fails)
-----------------------------------|---------------------------------------
library/core/valesco_materials     | 1. Core Tasks (Hard links to Codes)
                                   | 2. Packs (Rules referencing Codes)
                                   | 3. Snapshots (Historical integrity)
-----------------------------------|---------------------------------------
library/core/valesco_tasks         | 1. Estimates (Productivity calcs)
                                   | 2. Merge Script (If task merging added)

2. THE STRUCTURAL CHAIN (Path & File Dependencies)
--------------------------------------------------
IF YOU RENAME THIS...              | ...THIS WILL CRASH
-----------------------------------|---------------------------------------
Folder: /library                   | All Scripts (Relative path ../../library)
Folder: /engine                    | All .bat Launchers (Path to python)
-----------------------------------|---------------------------------------
File: valesco_pack.yaml            | 1. **Python Tools** (The "Open Box" upload requires this physical file)
                                   | 2. validate.bat
                                   | 3. prepare_context.bat (Hardcoded copy target)
-----------------------------------|---------------------------------------
File: _ACTIVATION_KEY.txt          | **User Interface** (If this text is wrong, the AI won't wake up)

3. THE VALIDATION CHAIN (Schema Dependencies)
---------------------------------------------
IF YOU EDIT THIS...                | ...THIS MAY FAIL
-----------------------------------|---------------------------------------
engine/schemas/*.json              | 1. validate.bat
                                   | 2. merge.bat (Validates before merge)
                                   | 3. material_manager.bat (Implicitly)

4. CRITICAL DEPENDENCY RULES
----------------------------
1. **Never Rename Core Files:** The Python engine AND the Batch scripts expect specific filenames.
2. **The Hybrid Payload Rule:** The AI now requires **BOTH** the Text Bundle (for reasoning) AND the Physical YAML files (for Python tools). `prepare_context.bat` ensures this sync.
3. **The Activation Handshake:** Use `_ACTIVATION_KEY.txt`. If you do not paste the command, the dependencies above are never loaded into the AI's active context.
4. **Instructions are Supreme:** Even if the code passes validation, if `valesco_instructions.txt` contradicts the code, the AI will be confused. Keep them synchronized.