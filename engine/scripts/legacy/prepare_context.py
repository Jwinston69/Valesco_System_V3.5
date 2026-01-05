import os
import sys
import glob

# --- CONFIGURATION ---
if len(sys.argv) < 2:
    print("  [!] Error: No output directory provided.")
    sys.exit(1)

OUTPUT_DIR = sys.argv[1]
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "VALESCO_FULL_CONTEXT.txt")
ARCHIVE_DIR = os.path.join(ROOT_DIR, "docs", "_archive", "v1.x")


def prefer_existing_path(*paths):
    for path in paths:
        if os.path.exists(path):
            return path
    return paths[-1]

# --- OPERATIONAL FILE REGISTRY ---
FILES_TO_BUNDLE = [
    # 1. SYSTEM DEFINITION
    prefer_existing_path(
        os.path.join(ARCHIVE_DIR, "VALESCO_SYSTEM_MANIFEST_v1.9.1.md"),
        os.path.join(ROOT_DIR, "docs", "VALESCO_SYSTEM_MANIFEST_v1.9.1.md"),
    ),
    
    # 2. THE LAWS (Logic & Hierarchy)
    os.path.join(ROOT_DIR, "docs", "governance", "VALESCO_TRUTH_HIERARCHY.md"),
    os.path.join(ROOT_DIR, "docs", "governance", "valesco_instructions.txt"),
    
    # 3. THE SAFETY RAILS
    prefer_existing_path(
        os.path.join(ARCHIVE_DIR, "VALESCO_DEPENDENCY_MAP.md"),
        os.path.join(ROOT_DIR, "docs", "VALESCO_DEPENDENCY_MAP.md"),
    ),
    
    # 4. THE CODES (Registry)
    os.path.join(ROOT_DIR, "engine", "config", "materials_allocator.yaml"),
]

# --- DYNAMIC INJECTION ---

# 5. THE FORMATS (Schemas)
# CRITICAL: This fixes "Misbehavior" by showing the AI the exact JSON structure required.
SCHEMAS_DIR = os.path.join(ROOT_DIR, "engine", "schemas")
if os.path.exists(SCHEMAS_DIR):
    FILES_TO_BUNDLE.extend(glob.glob(os.path.join(SCHEMAS_DIR, "*.json")))

# 6. THE PERSONALITY (Prompts)
PROMPTS_DIR = os.path.join(ROOT_DIR, "engine", "prompts")
if os.path.exists(PROMPTS_DIR):
    FILES_TO_BUNDLE.extend(glob.glob(os.path.join(PROMPTS_DIR, "*.txt")))
    FILES_TO_BUNDLE.extend(glob.glob(os.path.join(PROMPTS_DIR, "*.md")))

def bundle_files():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        # Header
        outfile.write("### VALESCO SYSTEM ACTIVATION HEADER\n")
        outfile.write("### ARCHITECTURE: v1.9.1 (Hybrid)\n")
        outfile.write("### GENERATED: Operational Context (Logic + Structure)\n")
        outfile.write("### CONTENTS: Governance, Instructions, Schemas, Prompts.\n\n")
        
        count = 0
        for filepath in FILES_TO_BUNDLE:
            if os.path.exists(filepath):
                filename = os.path.basename(filepath)
                outfile.write(f"\n--- FILE: {filename} ---\n")
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                        outfile.write("\n")
                    count += 1
                except Exception as e:
                    print(f"      [!] Error reading {filename}: {e}")
            else:
                # Only warn if it's a core file, ignore missing optional glob matches
                if "governance" in filepath:
                    print(f"      [!] WARNING: Doc Missing: {os.path.basename(filepath)}")
                
        print(f"  [+] Bundled {count} files into Operational Context.")

if __name__ == "__main__":
    bundle_files()
