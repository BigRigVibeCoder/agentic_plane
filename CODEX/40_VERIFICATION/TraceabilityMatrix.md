# Traceability Matrix

> **"If you can't trace a test to a requirement, why does the test exist?"** — *GOV-002: Testing Protocol*

This document maps requirements from the Plane Agentic Integration (EVO-001) to executable test cases in the suite. An agent must update this matrix when adding new tests.

| Requirement ID | Requirement Description | Test File | Test Function | Status |
|:---------------|:------------------------|:----------|:--------------|:-------|
| **EVO-001-P1** | Plane deployed locally and accessible | `tests/e2e/test_plane_is_up.py` | `test_plane_responds_200_ok` | ⬜ DRAFT |
| **EVO-001-P1** | Agentic Loop states exist | `tests/integration/test_states.py` | `test_all_8_agentic_states_exist` | ⬜ DRAFT |
| **EVO-001-P1** | CODEX Label taxonomy exists | `tests/integration/test_labels.py` | `test_codex_labels_exist` | ⬜ DRAFT |
| **EVO-001-P2** | Hybrid Client can create work items | `tests/integration/test_client.py` | `test_create_work_item_rest` | ⬜ DRAFT |
| **EVO-001-P2** | Webhook listener validates signature | `tests/unit/test_webhook.py` | `test_invalid_signature_is_401` | ⬜ DRAFT |
| **EVO-001-P2** | Webhook listener triggers DarkGravity | `tests/unit/test_webhook.py` | `test_valid_event_triggers_subprocess`| ⬜ DRAFT |

*Status Key: ⬜ DRAFT | 🟡 FAILING | ✅ PASSING | 🚨 QUARANTINED*
