
**Prohibited outputs:**
- embeddings  
- vector similarity matrices  
- latent-space features  
- multi-layer metadata  
- speculative attributes  
- model confidence distributions  

All backend output must be sanitized to the MVP’s deterministic schema, ensuring Validator receives no unauthorized fields.

---

# 3. Integration Strategy

### Adapter Layer
A small adapter module will wrap the real backend and emit results in the exact MVP signal structure. Its responsibilities:

- Map backend scoring outputs → `top_score`, `hit_count`, `score_gap_to_next`
- Normalize backend coverage annotations → `coverage_flags`
- Transform backend items → `retrieved_items` consistent with Material Manager schema
- Guarantee deterministic ordering (stable sort by score)

### Router Integration
Router v2.1 remains unmodified. Its deterministic rule-set (D → C → A → E → B) will operate directly on the adapter’s normalized signals.

### Architect Integration
Architect v2.1 requires **no changes**; it consumes Router output only.

### Validator Integration
Validator continues to enforce:
- Signal contract legality  
- State–signal consistency  
- Metadata safety  

Backend adapter must ensure all Validator requirements are satisfied before downstream execution.

### Material Manager Alignment
Backend-generated retrieved_items must refer to IDs present in the Material Manager catalog or ingest pipeline. No new metadata fields may be introduced.

---

# 4. Migration Steps

1. **Implement Backend Adapter**  
   Wrap real CE API responses into MVP-compatible structures.

2. **Signal Mapping**  
   Convert backend scoring into:  
   - `top_score`  
   - `score_gap_to_next`  
   - `hit_count`  
   - `coverage_flags`

3. **Catalog Metadata Validation**  
   Check that all backend item references match a known Material Manager item schema (ID, name, category, score placeholder if needed).

4. **Replace Mock Retrieval Module**  
   Swap CE Retrieval Layer v2.1 with the backend adapter while keeping API shape identical.

5. **Backward Compatibility Pass**  
   Re-run all MVP integration tests (quantity, pricing, CE routing, estimator runtime) without modification to higher layers.

6. **CE Safety Tests**  
   Confirm backend returns no disallowed fields. Validator must not encounter enrichment, inferred attributes, or internal model structures.

7. **Stability Verification**  
   Conduct multi-run determinism checks to ensure the backend produces identical results across repeated calls.

---

# 5. Test Plan for CE Backend Integration

A complete backend integration test suite must include:

### Determinism Tests
- Same description → identical signals  
- Identical ordering of retrieved_items  
- No drift in coverage flags or scoring

### State Routing Tests
- Known cases that trigger A, B, C, D, E  
- Ensure Router decisions exactly match expected outcomes

### Clarification Loop Tests
- Inputs requiring additional detail  
- Ensure transitions from C → A/B/E behave identically to mock environment

### No-match & Compatibility Tests
- Validate backend correctly identifies zero-hit cases (D)  
- Validate compatible alternatives for E-state routing

### Metadata Sanitation Tests
- Confirm no embeddings, vectors, or enriched metadata appear  
- Ensure retrieved_items align with Material Manager schema

### Backend Latency & Stability Tests
- Confirm backend response times stay within acceptable thresholds  
- Ensure no transient variability impacts determinism

---

# 6. Acceptance Criteria

Backend integration is deemed complete when:

- Backend produces deterministic, contract-compliant CE signals  
- Router v2.1 preserves correct A–E transitions without modification  
- Architect outputs remain **bit-for-bit identical** across mock and real backend scenarios  
- Validator passes all safe flows and blocks any non-compliant backend outputs  
- Estimator runtime experiences **no behavioural changes**  
- Full MVP + pricing + quantity + integration test suites pass without requiring changes to upper layers

The system will then be ready for full catalog ingestion, UI integration, and development of the production pricing engine in Phase 3.

