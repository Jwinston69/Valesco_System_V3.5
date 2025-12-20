import os
import argparse
import base64
import hashlib

# ================================================================
# CONFIGURATION
# ================================================================
DEFAULT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))

OUTPUT_DIR_NAME = "ai_context_bundles"   # NEW: Folder for bundle outputs

LAYER_FILES = {
    1: "valesco_bundle_layer1_ops.txt",
    2: "valesco_bundle_layer2_engine.txt",
    3: "valesco_bundle_layer3_docs_governance.txt",
    4: "valesco_bundle_layer4_library_data.txt",
}

BINARY_INDEX_FILE = "valesco_binary_assets_index.txt"

TEXT_EXTS = (
    ".py", ".bat", ".txt", ".md",
    ".yaml", ".yml", ".json", ".jsonl"
)

EXCLUDE_EXTS = (
    ".xlsx", ".xlsm", ".xlsb", ".zip"   # Will appear in index, not bundled
)

binary_assets = []  # Will hold tuples: (path, reason)


# ================================================================
# HELPERS
# ================================================================

def rel(path: str) -> str:
    return path.replace("/", os.sep).lstrip("\\/")


def ensure_output_dir(root: str) -> str:
    out_dir = os.path.join(root, OUTPUT_DIR_NAME)
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def collect_tree_with_exts(root: str, subdir: str, exts):
    files = []
    base = os.path.join(root, rel(subdir))
    if not os.path.isdir(base):
        return files

    for dirpath, _, filenames in os.walk(base):
        for fname in filenames:
            if exts and not fname.lower().endswith(exts):
                continue
            abs_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(abs_path, root)
            files.append(rel_path)

    return sorted(set(files))


def collect_matching(root: str, patterns):
    results = []
    explicit_paths = []
    suffix_patterns = []

    for p in patterns:
        p = rel(p)
        if "*" in p:
            dir_part, pat = os.path.split(p)
            suffix_patterns.append((dir_part, pat))
        else:
            explicit_paths.append(p)

    # explicit paths
    for p in explicit_paths:
        if os.path.isfile(os.path.join(root, p)):
            results.append(p)

    # patterns
    for dir_part, pat in suffix_patterns:
        suffix = pat.replace("*", "")
        abs_dir = os.path.join(root, dir_part)
        if not os.path.isdir(abs_dir):
            continue
        for name in sorted(os.listdir(abs_dir)):
            if suffix and not name.endswith(suffix):
                continue
            rp = os.path.join(dir_part, name)
            if os.path.isfile(os.path.join(root, rp)):
                results.append(rp)

    return sorted(set(results))


# ================================================================
# CHECKSUM
# ================================================================

def sha256_file(abs_path: str):
    h = hashlib.sha256()
    with open(abs_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ================================================================
# FILE WRITER (PATCHED)
# ================================================================

def record_binary(rel_path: str, reason: str):
    """Record binary file into the binary-assets index."""
    binary_assets.append((rel_path, reason))


def read_text_deterministic(abs_path: str):
    """Read text with deterministic decoding.

    Rules:
    - If BOM is present, decode according to BOM.
    - Else decode as strict UTF-8.
    - Else decode as cp1252 with replacement and return a marker.
    """
    raw = open(abs_path, "rb").read()

    # Check longer BOMs first to avoid misclassifying UTF-32 as UTF-16.
    if raw.startswith(b"\xff\xfe\x00\x00") or raw.startswith(b"\x00\x00\xfe\xff"):
        return raw.decode("utf-32"), None
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig"), None
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16"), None

    try:
        return raw.decode("utf-8"), None
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace"), "cp1252+replace"


def write_file_section(root: str, rel_path: str, out):
    abs_path = os.path.join(root, rel_path)

    if not os.path.exists(abs_path):
        out.write(f"=== FILE NOT FOUND: {rel_path} ===\n\n")
        return

    _, ext = os.path.splitext(rel_path.lower())

    # NEW: Always record excluded binaries, but skip bundling them
    if ext in EXCLUDE_EXTS:
        record_binary(rel_path, f"Excluded binary type: {ext}")
        return

    out.write(f"=== FILE: {rel_path} ===\n")

    # SHA-256 checksum
    try:
        checksum = sha256_file(abs_path)
        out.write(f"<<SHA256 {checksum}>>\n")
    except Exception as e:
        out.write(f"<<SHA256_ERROR: {e}>>\n")

    try:
        if ext in TEXT_EXTS:
            data, decode_marker = read_text_deterministic(abs_path)
            if decode_marker is not None:
                out.write(f"<<DECODE {decode_marker}>>\n")
            out.write(data)

        else:
            # Non-excluded binary (rare in Valesco)
            try:
                with open(abs_path, "rb") as f:
                    raw = f.read()
                encoded = base64.b64encode(raw).decode("ascii")
                out.write("<<BINARY_BASE64>>\n")
                out.write(encoded)
                out.write("\n<<END_BINARY>>")
                record_binary(rel_path, "Included as Base64")
            except Exception as e:
                out.write(f"<<BINARY_READ_ERROR: {e}>>")

    except Exception as e:
        out.write(f"<<ERROR READING FILE: {e}>>")

    out.write("\n\n")


# ================================================================
# LAYER DEFINITIONS
# ================================================================

def get_layer1_files(root):
    # Layer 1 = operational entrypoints and thin wrappers.
    # Keep this layer aligned with the real on-disk structure and avoid duplicating
    # Context Engineering scripts that are already included in Layer 2.
    patterns = [
        r"start_valesco_v1.9.bat",  # legacy ops console (non-authoritative)
        r"run_valesco.py",
        r"export_ai_context_bundle.py",
        r"bin\\*.bat",
        r"engine\\scripts\\validate.py",
        r"engine\\scripts\\run_tests_portable.py",
        # Historical/legacy operational scripts (still referenced by tooling)
        r"engine\\scripts\\legacy\\prepare_context.py",
        r"engine\\scripts\\legacy\\material_manager.py",
        r"engine\\scripts\\legacy\\merge.py",
        # MVP runners
        r"engine\\scripts\\mvp_runner_v2_1.py",
        r"engine\\scripts\\mvp_runner_v2_2.py",
    ]
    return collect_matching(root, patterns)


def get_layer2_files(root):
    files = []
    files += collect_tree_with_exts(root, r"engine\modules", (".py",))
    files += collect_tree_with_exts(root, r"engine\scripts\context_engineering", (".py",))
    files += collect_tree_with_exts(root, r"engine\build", (".py",))
    files += collect_tree_with_exts(root, r"engine\config", (".txt", ".yaml", ".yml"))
    files += collect_tree_with_exts(root, r"engine\tests", (".py", ".md"))
    return sorted(set(files))


def get_layer3_files(root):
    files = []
    files += collect_tree_with_exts(root, r"docs", (".md",))
    files += collect_tree_with_exts(root, r"engine\prompts", (".md",))
    files += collect_tree_with_exts(root, r"docs\governance", (".md", ".txt"))
    return sorted(set(files))


def get_layer4_files(root):
    files = []
    files += collect_tree_with_exts(root, r"library", (".yaml", ".yml"))
    files += collect_tree_with_exts(root, r"engine\schemas", (".json",))
    files += collect_tree_with_exts(root, r"workspace\vector_input", (".jsonl",))
    files += collect_tree_with_exts(root, r"workspace\snapshots", (".txt",))
    return sorted(set(files))


LAYER_GETTERS = {
    1: get_layer1_files,
    2: get_layer2_files,
    3: get_layer3_files,
    4: get_layer4_files,
}


# ================================================================
# OUTPUT BUILDERS
# ================================================================

def build_layer(root, out_dir, layer, files):
    out_path = os.path.join(out_dir, LAYER_FILES[layer])
    with open(out_path, "w", encoding="utf-8") as out:
        out.write(f"### Valesco Bundle – Layer {layer} ###\n\n")
        for f in files:
            write_file_section(root, f, out)
    return out_path


def write_binary_index(root, out_dir):
    path = os.path.join(out_dir, BINARY_INDEX_FILE)
    with open(path, "w", encoding="utf-8") as out:
        out.write("### Binary Assets Index ###\n\n")
        for rel_path, reason in binary_assets:
            out.write(f"{rel_path} -- {reason}\n")
    return path


# ================================================================
# MAIN
# ================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=DEFAULT_ROOT)
    parser.add_argument("--layers", default="1,2,3,4")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    out_dir = ensure_output_dir(root)

    wanted = {int(x.strip()) for x in args.layers.split(",")}

    print(f"[INFO] Building bundles into: {out_dir}")

    for lid in sorted(wanted):
        getter = LAYER_GETTERS[lid]
        files = getter(root)
        print(f"[INFO] Layer {lid}: {len(files)} files")
        out = build_layer(root, out_dir, lid, files)
        print(f"[OK] Wrote: {out}")

    index = write_binary_index(root, out_dir)
    print(f"[OK] Binary index written: {index}")
    print("[DONE]")


if __name__ == "__main__":
    main()
