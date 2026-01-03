import json
import sys

def main():
    payload = json.load(sys.stdin)
    output = {
        "hit_count": 1,
        "top_score": 0.98,
        "score_gap_to_next": None,
        "coverage_flags": {"strong": True, "weak": False, "conflicting": False},
        "retrieved_items": [
            {"id": "A001", "name": "Single Clean-Match Item", "category": "core", "score": 0.98}
        ],
    }
    json.dump(output, sys.stdout)

if __name__ == "__main__":
    main()
