Valesco Estimating Framework — Developer Checklist

Version: 1.7
Status: Authoritative operational guideline
Purpose: Ensure all edits to Valesco system files follow the Truth Hierarchy and preserve system stability.

1. Before Editing Anything

Always confirm:

- You know which layer you are editing
  (Docs → Engine → Library → Workspace)

- You understand the Truth Hierarchy
  No downstream file may contradict upstream truth.

- You have the correct file open
  Many issues come from editing the wrong tier.

2. Before Editing Instructions (docs/governance)

Only edit instructions if:

- A behavioural rule needs changing
- A unit whitelist change is required
- A system-wide mechanic must be updated

Checklist:

- [ ] Version bump required
- [ ] All schemas affected must be reviewed
- [ ] No circular rules introduced
- [ ] Impact on materials/tasks/subs/pack understood
- [ ] Must not reference downstream files

3. Before Editing Any Schema (engine/schemas)

Checklist:

- [ ] Schema follows instructions (especially unit rules)
- [ ] No behavioural logic added (schema = structure only)
- [ ] All required keys explicitly defined
- [ ] No unintended additionalProperties: true
- [ ] Compatibility with `validate.bat` confirmed
- [ ] Downstream files reviewed for impact

Schemas enforce shape, not meaning.

4. Before Editing the Materials Library (library/core)

Materials are authoritative.

Checklist:

- [ ] **DO NOT EDIT MANUALLY** — Use `material_manager.bat`
- [ ] All materials use valid MAT.STD codes
- [ ] Code prefix, category, group match the `materials_allocator.yaml`
- [ ] Units come from the global whitelist
- [ ] Rates are numeric and non-negative
- [ ] Description is meaningful and non-generic
- [ ] No duplicates by code

Never:

- Invent new units
- Use unknown categories or groups
- Add materials directly into packs unless explicitly required

5. Before Editing Tasks (library/core)

Tasks define system behaviour.

Checklist:

- [ ] Output keys follow output_<unit>_day
- [ ] Unit is in global whitelist (includes `week`)
- [ ] Labour/plant references align with pack defaults
- [ ] No pack-level logic duplicated
- [ ] **Materials referenced via hard-links (`code`)**
- [ ] Task groups maintain correct order[]
- [ ] No invented productivity units (e.g., “plants”, “trees” → use `nr`)
- [ ] Schema validation required

Tasks must never:

- Introduce new unit types
- Contradict behaviour defined in instructions

6. Before Editing Subcontractors (library/core)

Checklist:

- [ ] Unit tokens in whitelist
- [ ] Descriptions clear
- [ ] Methods valid and consistent
- [ ] No duplicates
- [ ] Follows schema structure

Subs must never override:

- Task definitions
- Material definitions

7. Before Editing Packs (library/packs)

The pack is a consumer, not a source of truth.

Checklist:

- [ ] Uses only allowed units (whitelist for all rate-bearing items)
- [ ] No invented material codes
- [ ] **Materials block omitted** (relies on Core Library)
- [ ] No productivity rules duplicated or altered
- [ ] Prelims structurally correct (arrays for items)
- [ ] Waste follows `disposal`/`haulage`/`skips` object structure
- [ ] Plant/labour types consistent with tasks
- [ ] No override of core library behaviour
- [ ] Pack-specific rules must not contradict system rules

Packs may:

- Override labour/plant rates
- Add or adjust prelims
- Add project-level rules

Packs may NOT:

- Invent units
- Override task behaviour
- Contradict instructions
- Redefine material codes

8. Before Editing Extensions (library/extensions)

Checklist:

- [ ] Additive only (no overrides)
- [ ] Valid codes (Must use **MAT.BES** prefix)
- [ ] Valid units
- [ ] Must later promote into core libraries via Manager Script
- [ ] Must include provenance notes

9. Before Processing Proposals (workspace/proposals)

Checklist:

- [ ] Treat all proposal items as provisional
- [ ] Validate units and structure
- [ ] Validate material codes before merge
- [ ] Parse suggestions but do not treat them as truth
- [ ] Only merge into extension files via `merge.bat`

10. Before Running Validation

Checklist:

- [ ] Run `_START_VALESCO.bat` -> Option 4
- [ ] Cross-file rules pass (Data Integrity):
    - Pack.materials codes exist in materials
    - Task units follow whitelist
    - Subcontractor units valid
    - Productivity keys valid
    - Rates non-negative
    - No missing provenance
- [ ] Watchdog Audit passes (Structural Integrity):
    - All critical files exist (no missing prompts/scripts)
    - All script paths reference valid files (no broken links)

11. Before Exporting (human/json)

Checklist:

- [ ] Session hash generated
- [ ] All assumptions confirmed
- [ ] No PROVISIONAL-MATERIAL unless intentional
- [ ] No missing rates
- [ ] Pack, materials, tasks, subs all validated

Exports are outputs only.
Never modify exports.

12. Before Promoting Changes to Main Libraries

Checklist:

- [ ] Use `material_manager.bat` (Promote option)
- [ ] Extensions reviewed
- [ ] Naming conventions followed
- [ ] Allocator categories current
- [ ] MD5 and version notes updated
- [ ] Material/library diffs reviewed manually
- [ ] No accidental deletion of existing codes

Promotion must be deterministic and reversible.

13. Golden Rules

1. Instructions override everything.
2. Schemas enforce shape.
3. Allocator defines Categories.
4. Materials define codes.
5. Tasks define productivity.
6. Packs consume truth; they don’t create it.
7. Extensions add only.
8. Proposals are never authoritative.
9. Exports are read-only.
10. Always validate before exporting.

14. BATCH SCRIPT SAFETY (The "Air Gap")
    [ ] 14.1 No `set /p` for Python arguments. Python must read `sys.argv`.
    [ ] 14.2 `_START_VALESCO.bat` and sub-scripts must NOT contain `pause` in critical paths (except menu loops).
    [ ] 14.3 Debug by running scripts directly with arguments (e.g., `script.bat "arg"`).
    [ ] 14.4 Batch scripts must NOT trim/clean paths. All string sanitisation happens in Python.
    [ ] 14.5 Cloud Safety: Quotes around all file paths (e.g., `"%ROOT%\file.txt"`) to handle spaces in "Google Drive".
    [ ] 14.6 Syntax Safety: DO NOT use ampersands (&), pipes (|), or brackets () in `echo` statements unless strictly escaped (^&). Use "+" or "and" instead.
    [ ] 14.7 Delayed Expansion Safety:
        * Constraint: Do NOT use `EnableDelayedExpansion` globally if the script echoes special characters (e.g. !, &, |).
        * Mechanism: Use standard `setlocal` for echo blocks, or escape strictly with `^^!`.
        * Reason: Prevents variable stripping and header corruption during file generation.
End of document.