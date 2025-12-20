import os
import sys
import json
import glob

# Try importing dependencies
try:
    import yaml
    from jsonschema import validate, ValidationError
except ImportError:
    print("\n  [!] CRITICAL ERROR: Python dependencies missing.")
    print("      Please run 'Option 1: INSTALL DEPENDENCIES' in the Master Console.")
    sys.exit(1)

# --- CONFIGURATION ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LIBRARY_DIR = os.path.join(ROOT_DIR, "library")
SCHEMA_DIR = os.path.join(ROOT_DIR, "engine", "schemas")

# Allowed Units (From valesco_instructions.txt)
UNIT_WHITELIST = {
    "m", "m2", "m3", "lm", "hr", "nr", "day", "week", "item", "t", "l", "kg", "each"
}

# --- UTILITIES ---
def load_yaml(filepath):
    if not os.path.exists(filepath):
        print(f"  [!] MISSING FILE: {os.path.basename(filepath)}")
        return None
    try:
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"  [!] CORRUPT YAML: {os.path.basename(filepath)} - {str(e)}")
        return None

def print_status(component, status, message=""):
    symbol = "[+]" if status == "PASS" else "[!]"
    print(f"  {symbol} {component:<20} : {status} {message}")

# --- VALIDATORS ---

def validate_materials():
    path = os.path.join(LIBRARY_DIR, "core", "valesco_materials.yaml")
    data = load_yaml(path)
    if not data: return set(), False

    valid_codes = set()
    errors = 0
    
    # Structure Check
    if "materials" not in data:
        print_status("Materials", "FAIL", "Missing 'materials' root key")
        return set(), False

    # Logic Check
    for item in data["materials"]:
        code = item.get("code", "UNKNOWN")
        unit = item.get("unit", "").lower()
        
        valid_codes.add(code)
        
        if unit not in UNIT_WHITELIST:
            print(f"      - Invalid Unit in {code}: '{unit}'")
            errors += 1
            
    if errors == 0:
        print_status("Materials", "PASS", f"Indexed {len(valid_codes)} items")
        return valid_codes, True
    else:
        print_status("Materials", "FAIL", f"Found {errors} logic errors")
        return valid_codes, False

def validate_tasks(material_codes):
    path = os.path.join(LIBRARY_DIR, "core", "valesco_tasks.yaml")
    data = load_yaml(path)
    if not data: return False

    errors = 0
    
    # Iterate through groups and tasks
    # Structure: groups -> [group_key] -> tasks -> [task_key]
    if "groups" in data:
        for group_id, group_data in data["groups"].items():
            if "tasks" in group_data:
                for task_id, task in group_data["tasks"].items():
                    
                    # Check Material Links (Hard Links)
                    if "materials" in task:
                        for mat_ref in task["materials"]:
                            ref_code = mat_ref.get("code")
                            if ref_code and ref_code not in material_codes:
                                print(f"      - ORPHAN LINK: Task {task_id} references missing material '{ref_code}'")
                                errors += 1

                    # Check Productivity Units
                    if "productivity" in task:
                        for key in task["productivity"]:
                            if key.startswith("output_") and key.endswith("_day"):
                                unit = key.split("_")[1] # extract 'm2' from 'output_m2_day'
                                if unit not in UNIT_WHITELIST:
                                    print(f"      - INVALID PROD UNIT: Task {task_id} uses '{unit}'")
                                    errors += 1

    if errors == 0:
        print_status("Tasks", "PASS", "Integrity confirmed")
        return True
    else:
        print_status("Tasks", "FAIL", f"{errors} logic errors found")
        return False

def validate_pack():
    path = os.path.join(LIBRARY_DIR, "packs", "valesco_pack.yaml")
    data = load_yaml(path)
    if not data: return False

    # Simple check for required keys
    required = ["labour", "plant", "prelims"]
    missing = [k for k in required if k not in data]

    if missing:
        print_status("Pack", "FAIL", f"Missing keys: {missing}")
        return False
    
    print_status("Pack", "PASS", "Structure valid")
    return True

def validate_subcontractors():
    path = os.path.join(LIBRARY_DIR, "core", "valesco_subcontractors.yaml")
    if not os.path.exists(path):
        # Optional file, warn but pass
        print_status("Subcontractors", "SKIP", "File not present (Optional)")
        return True
        
    data = load_yaml(path)
    if not data: return False
    
    print_status("Subcontractors", "PASS", "Structure valid")
    return True

# --- MAIN ---
def main():
    print(f"  [*] Root: {ROOT_DIR}")
    print("  --------------------------------------------------")
    
    # 1. Validate Materials (Source of Truth)
    mat_codes, mat_valid = validate_materials()
    
    # 2. Validate Pack
    pack_valid = validate_pack()
    
    # 3. Validate Tasks (Needs Material Codes for reference check)
    tasks_valid = validate_tasks(mat_codes)
    
    # 4. Validate Subs
    subs_valid = validate_subcontractors()

    print("  --------------------------------------------------")
    
    if mat_valid and pack_valid and tasks_valid and subs_valid:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()