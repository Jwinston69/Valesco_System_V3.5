import os
import sys
import json
import yaml
import time

# --- CONFIGURATION ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROPOSALS_DIR = os.path.join(ROOT_DIR, "workspace", "proposals")
EXTENSIONS_DIR = os.path.join(ROOT_DIR, "library", "extensions")
TARGET_FILE = os.path.join(EXTENSIONS_DIR, "materials_ext.yaml")

# --- UTILS ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def ensure_extensions_exist():
    if not os.path.exists(EXTENSIONS_DIR):
        os.makedirs(EXTENSIONS_DIR)
    if not os.path.exists(TARGET_FILE):
        with open(TARGET_FILE, 'w') as f:
            yaml.dump({"meta": {"type": "extension", "version": "1.0"}, "materials": []}, f)

def load_proposals():
    if not os.path.exists(PROPOSALS_DIR):
        os.makedirs(PROPOSALS_DIR)
        return []
    
    files = [f for f in os.listdir(PROPOSALS_DIR) if f.endswith(".json")]
    proposals = []
    
    for f in files:
        try:
            with open(os.path.join(PROPOSALS_DIR, f), 'r') as pf:
                data = json.load(pf)
                proposals.append({"filename": f, "data": data})
        except Exception as e:
            print(f"  [!] Bad JSON: {f} ({e})")
            
    return proposals

def merge_proposal(prop):
    ensure_extensions_exist()
    
    # 1. Load Target
    with open(TARGET_FILE, 'r') as f:
        target_data = yaml.safe_load(f) or {"materials": []}
    
    if "materials" not in target_data:
        target_data["materials"] = []

    # 2. Extract Items
    new_items = prop["data"].get("materials", [])
    if not new_items:
        print("  [!] Proposal contains no materials.")
        return False

    # 3. Append (Simple Logic for v1.9)
    count = 0
    for item in new_items:
        # Check for dupes by code could go here
        target_data["materials"].append(item)
        count += 1
        
    # 4. Save
    with open(TARGET_FILE, 'w') as f:
        yaml.dump(target_data, f, sort_keys=False)
        
    print(f"  [+] Merged {count} items into materials_ext.yaml")
    
    # 5. Archive Proposal (Rename to .done)
    src = os.path.join(PROPOSALS_DIR, prop["filename"])
    dst = src + ".done"
    try:
        if os.path.exists(dst): os.remove(dst)
        os.rename(src, dst)
    except Exception as e:
        print(f"  [!] Could not archive file: {e}")
        
    return True

# --- MAIN ---
def main():
    while True:
        clear_screen()
        print("\n  =========================================")
        print("   VALESCO MERGE AGENT               v1.9.1")
        print("  =========================================")
        
        proposals = load_proposals()
        
        if not proposals:
            print("   Status: No pending proposals found.")
            print("   (Place .json files in /workspace/proposals)")
            print("\n   [1] Exit")
            choice = input("\n   Select > ")
            sys.exit(0)
            
        print(f"   Found {len(proposals)} pending proposals:\n")
        
        for idx, p in enumerate(proposals):
            print(f"   [{idx+1}] {p['filename']}")
            
        print(f"   [{len(proposals)+1}] Exit")
        
        try:
            choice = input("\n   Select Proposal to Merge > ")
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)

        if choice == str(len(proposals)+1):
            sys.exit(0)
            
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(proposals):
                print("\n  Processing...")
                merge_proposal(proposals[idx])
                time.sleep(2)
            else:
                print("  [!] Invalid selection")
                time.sleep(1)
        except ValueError:
            pass

if __name__ == "__main__":
    main()