import os
import sys
import yaml
import time

# --- CONFIGURATION ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MATERIALS_PATH = os.path.join(ROOT_DIR, "library", "core", "valesco_materials.yaml")
ALLOCATOR_PATH = os.path.join(ROOT_DIR, "engine", "config", "materials_allocator.yaml")

# --- UTILS ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_yaml(filepath):
    if not os.path.exists(filepath):
        print(f"[!] Missing file: {filepath}")
        return None
    try:
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"[!] Error loading {filepath}: {e}")
        return None

# --- FEATURES ---

def show_stats(data):
    clear_screen()
    print("\n  === LIBRARY STATISTICS ===")
    
    if "materials" not in data:
        print("  [!] Invalid Data Structure")
        return

    total = len(data["materials"])
    units = {}
    
    for item in data["materials"]:
        u = item.get("unit", "N/A")
        units[u] = units.get(u, 0) + 1

    print(f"  Total Items: {total}")
    print("\n  [Unit Breakdown]")
    for u, count in units.items():
        print(f"   - {u:<5} : {count}")
    
    input("\n  Press Enter to return...")

def search_materials(data):
    while True:
        clear_screen()
        print("\n  === MATERIAL SEARCH ===")
        query = input("  Enter search term (or 'q' to quit): ").lower().strip()
        
        if query == 'q':
            break
            
        matches = []
        for item in data.get("materials", []):
            code = item.get("code", "")
            desc = item.get("description", "").lower()
            
            if query in code.lower() or query in desc:
                matches.append(item)
        
        print(f"\n  Found {len(matches)} matches:\n")
        print(f"  {'CODE':<15} | {'UNIT':<5} | {'RATE':<8} | {'DESCRIPTION'}")
        print("  " + "-"*60)
        
        for m in matches[:15]: # Limit to 15 results
            print(f"  {m['code']:<15} | {m['unit']:<5} | £{m['rate']:<7} | {m['description']}")
            
        if len(matches) > 15:
            print(f"  ... and {len(matches) - 15} more.")
            
        input("\n  Press Enter to search again...")

# --- MAIN MENU ---

def main():
    # Load Data once
    print("  [*] Loading Materials Database...")
    mat_data = load_yaml(MATERIALS_PATH)
    
    if not mat_data:
        print("  [!] Failed to load database.")
        time.sleep(2)
        return

    while True:
        clear_screen()
        print("\n  =========================================")
        print("   VALESCO MATERIAL MANAGER          v1.9.1")
        print("  =========================================")
        print(f"   Database: {len(mat_data.get('materials', []))} items loaded")
        print("  =========================================")
        print("   [1] Search Database")
        print("   [2] View Statistics")
        print("   [3] Exit")
        print("\n")
        
        choice = input("   Select > ")
        
        if choice == "1":
            search_materials(mat_data)
        elif choice == "2":
            show_stats(mat_data)
        elif choice == "3":
            sys.exit(0)

if __name__ == "__main__":
    main()