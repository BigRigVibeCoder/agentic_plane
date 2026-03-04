---
id: GOV-003
title: "Coding Standard"
type: reference
status: APPROVED
owner: architect
agents: [all]
tags: [coding, standards, governance, quality, safety]
related: [GOV-001, GOV-002]
created: 2026-03-04
updated: 2026-03-04
version: 1.0.0
---

> **BLUF:** Polyglot coding standard for agent-written code. Covers Python, C/C++, and React/TypeScript. While 99% of this code will never be read by humans, it MUST be written so that in a disaster, a human engineer can understand any function in 30 seconds. NASA Power of 10 rules are the backbone for all languages.

# Coding Standard: The Engineering Discipline

> **"Simple, Verifiable, Obvious."**
> *— JPL Institutional Coding Standard (D-17698)*

---

## 1. The Disaster-Readability Principle

> **"Code written by agents, readable by humans under stress."**

Most code in this system will be written, reviewed, and maintained by AI agents. But when things go catastrophically wrong — production outage at 3 AM, data corruption, security breach — **a human** will be dropped into the codebase cold. That human will be stressed, sleep-deprived, and unfamiliar with the code.

**Every line of code must be written as if a panicked engineer is reading it for the first time.**

### 1.1 The 30-Second Rule

Any function must be understandable by a competent engineer in **30 seconds** without:
- Reading external documentation
- Understanding the broader architecture
- Running the code

### 1.2 Mandatory Commenting Strategy

| Comment Type | When Required | Purpose |
|:-------------|:--------------|:--------|
| **File header** | Every file | Context: what this file does, who uses it |
| **Function docstring** | Every public function | What it does, what it takes, what it returns |
| **"Why" comments** | Any non-obvious logic | Explain the *reason*, not the *mechanism* |
| **Safety comments** | Any safety-critical code | Explain what happens if this fails |
| **TODO/FIXME/HACK** | Temporary workarounds | Must include author and date |
| **Invariant assertions** | Complex algorithms | What must be true at this point |

```python
# ❌ BAD: Comment restates the code
x = x + 1  # Increment x by 1

# ✅ GOOD: Comment explains WHY
x = x + 1  # Compensate for zero-indexed sensor array (firmware bug #42)

# ✅ GOOD: Safety comment
if distance_m < SAFE_STOP_DISTANCE_M:
    # SAFETY: If we don't stop here, the robot WILL collide.
    # Failure mode: physical damage, mission abort.
    emergency_stop()
```

### 1.3 Self-Documenting Structure

- **Small functions**: Maximum 60 lines. If you can't see the whole function without scrolling, split it.
- **Descriptive names**: `calculate_braking_distance_m()` not `calc_dist()`.
- **Guard clauses first**: Error paths at the top, happy path at the bottom.
- **One responsibility**: Each function does ONE thing.

---

## 2. The Power of 10 (Universal Rules)

> **Origin:** Gerard J. Holzmann, NASA/JPL Laboratory for Reliable Software, 2006

These rules apply to **ALL languages**. Static analysis must enforce them.

| # | Rule | Rationale |
|:--|:-----|:----------|
| 1 | **Simple control flow** — No recursion. No deeply nested logic (max 4 levels). | Analyzable by humans and tools. |
| 2 | **Fixed loop bounds** — All loops must have provable termination. | Prevents hangs in production. |
| 3 | **No dynamic allocation in hot loops** — Pre-allocate, reuse. | Prevents GC pauses and memory fragmentation. |
| 4 | **Short functions** — Max 60 lines per function/method. | Fits on one screen = one mental model. |
| 5 | **Assertion density** — Min 2 assertions per non-trivial function. | Internal correctness proofs. |
| 6 | **Minimal data scope** — No module-level mutable state. Smallest scope possible. | Prevents spooky action at a distance. |
| 7 | **Check all return values** — Never ignore results from fallible operations. | Prevents silent failures. |
| 8 | **Pedantic warnings** — All linter/compiler warnings treated as errors. Zero tolerance. | Catches bugs that humans miss. |

---

## 3. Naming Conventions (All Languages)

Names must convey **intent**, **type**, and **scope** without reading the implementation.

### 3.1 Universal Patterns

| Pattern | Use Case | Examples |
|:--------|:---------|:---------|
| `verb_noun` | Functions/methods | `calculate_distance`, `validate_input`, `fetchUserData` |
| `noun_unit` | Physical quantities | `distance_m`, `velocity_mps`, `timeout_ms` |
| `is_`, `has_`, `can_` | Booleans | `is_active`, `has_permission`, `canSubmit` |
| `max_`, `min_`, `default_` | Limits/defaults | `MAX_RETRIES`, `min_temperature_c` |
| `UPPER_SNAKE_CASE` | Constants | `MAX_VELOCITY_MPS`, `API_ENDPOINT` |

### 3.2 Language-Specific Casing

| Element | Python | C/C++ | TypeScript/React |
|:--------|:-------|:------|:-----------------|
| Variables | `snake_case` | `snake_case` | `camelCase` |
| Functions | `snake_case` | `snake_case` | `camelCase` |
| Classes/Components | `PascalCase` | `PascalCase` | `PascalCase` |
| Constants | `UPPER_SNAKE` | `UPPER_SNAKE` | `UPPER_SNAKE` |
| Files | `snake_case.py` | `snake_case.c` | `PascalCase.tsx` or `kebab-case.ts` |
| Private members | `_prefix` | `m_prefix` or `_prefix` | `_prefix` or `#private` |

### 3.3 Forbidden Naming

- ❌ Single-letter variables (except `i`, `j`, `k` in loops, `e` in exceptions)
- ❌ Abbreviations unless universally understood (`cfg` → `config`, `mgr` → `manager`)
- ❌ Generic names: `data`, `info`, `temp`, `result`, `value`, `item` — add context

---

## 4. File Structure & Organization

### 4.1 File Size Limits

| Metric | Limit | Enforcement |
|:-------|:------|:------------|
| Lines per file | ≤300 (target), ≤500 (absolute max) | Linter |
| Lines per function | ≤60 | Linter |
| Cyclomatic complexity | ≤10 per function | Linter |
| Nesting depth | ≤4 levels | Linter |
| Parameters per function | ≤5 (use config objects beyond) | Code review |

### 4.2 Universal File Layout

Every source file follows this order:

```
1. File header comment / module docstring
2. Imports (Standard → Third-party → Local)
3. Constants
4. Type definitions / Interfaces
5. Module-level logger (if applicable)
6. Classes / Functions (public first, private last)
7. Entry point (if applicable)
```

---

## 5. Defensive Coding (All Languages)

### 5.1 Input Validation

All public function inputs **MUST** be validated. Do not trust callers — even other agents.

### 5.2 Guard Clauses First

Handle error conditions at the top of the function, then the happy path:

```python
def process(data: InputData) -> Result:
    if data is None:
        raise ValueError("data cannot be None")
    if not data.is_valid():
        raise ValidationError(f"Invalid data: {data}")
    
    # Happy path starts here
    return transform(data)
```

### 5.3 No Magic Numbers

All numeric literals **MUST** be named constants. The name explains the value.

```python
# ❌ BAD — What is 0.3? Why 0.3?
if distance < 0.3:
    stop()

# ✅ GOOD — Self-documenting
SAFE_STOP_DISTANCE_M = 0.3  # Minimum distance before collision risk
if distance < SAFE_STOP_DISTANCE_M:
    stop()
```

### 5.4 Forbidden Patterns (All Languages)

| Pattern | Why | Alternative |
|:--------|:----|:------------|
| Bare `catch`/`except` | Swallows all errors | Catch specific types |
| `eval()` / `exec()` | Code injection | Structured data |
| Module-level mutable state | Unpredictable | Encapsulate in classes |
| Wildcard imports | Namespace pollution | Import specific names |
| Mutable default arguments | Shared state | Use `None` sentinel |
| Ignoring return values | Silent failures | Always check or comment `_ =` |

---

## 6. Python-Specific Standards

> Primary language. NASA Power of 10 fully adapted.

### 6.1 Type Hinting (100% Coverage)

- 100% of function signatures must be typed
- Use Python 3.10+ syntax: `str | None` over `Optional[str]`
- Forbidden: `Any` (except JSON boundaries), `object`, untyped `lambda`
- Use semantic types: `Meters = float`, `Seconds = float`

### 6.2 Docstrings (Google Style)

```python
def calculate_distance(
    origin: tuple[float, float],
    target: tuple[float, float],
) -> float:
    """Calculate Euclidean distance between two 2D points.

    Uses the standard distance formula. This is called by the
    navigation planner to evaluate waypoint proximity.

    Args:
        origin: Starting point as (x, y) in meters.
        target: Destination point as (x, y) in meters.

    Returns:
        Distance in meters between the two points.

    Raises:
        ValueError: If either point contains NaN values.
    """
```

### 6.3 Import Order

```python
"""Module docstring."""

# 1. Standard library
import os
from pathlib import Path

# 2. Third-party
import structlog
from pydantic import BaseModel

# 3. Local application
from myproject.models import Config
from myproject.utils import validate

# 4. Constants
MAX_RETRIES = 3
logger = structlog.get_logger(__name__)
```

### 6.4 Concurrency (GIL Awareness)

- **CPU-bound**: Use `multiprocessing` or C extensions
- **I/O-bound**: Use `asyncio`
- **Never** use threads for CPU work (GIL blocks parallelism)
- **Never** block the event loop with CPU work — offload via `run_in_executor`

### 6.5 Tools & Enforcement

| Tool | Purpose | CI Gate |
|:-----|:--------|:--------|
| Ruff | Linting + formatting | Zero warnings |
| MyPy `--strict` | Type checking | Zero errors |
| Radon | Cyclomatic complexity | No function > 10 |
| Bandit | Security scanning | Zero HIGH/CRITICAL |

---

## 7. C/C++ Standards

> For performance-critical components, embedded systems, and system-level code.

### 7.1 Compliance Targets

| Standard | When |
|:---------|:-----|
| **MISRA C:2025** | All C code — safety-critical subset |
| **CERT C** | Security-focused modules |
| **C17 or later** | Minimum language standard |
| **C++17 or C++20** | Minimum for C++ |

### 7.2 Key Rules (Beyond Power of 10)

- **No dynamic memory after init** — `malloc`/`free` forbidden after startup. Pre-allocate all buffers.
- **No recursion** — Stack overflow is fatal in embedded. Use iteration.
- **Single level of indirection** — `*ptr` is fine. `**ptr` requires justification.
- **All variables initialized at declaration** — Uninitialized memory is undefined behavior.
- **No `goto`** — Exception: single-point-of-return cleanup pattern in C is acceptable:

```c
int process(data_t *data) {
    int result = -1;
    buffer_t *buf = NULL;
    
    if (data == NULL) goto cleanup;
    
    buf = buffer_alloc(1024);
    if (buf == NULL) goto cleanup;
    
    /* SAFETY: buf is guaranteed allocated here */
    result = transform(data, buf);
    
cleanup:
    buffer_free(buf);  /* Safe: buffer_free(NULL) is a no-op */
    return result;
}
```

### 7.3 Header File Discipline

```c
/**
 * @file motor_controller.h
 * @brief Motor control interface for the drive system.
 * 
 * Provides velocity commands and safety limit enforcement.
 * Used by: arbiter, reflex engine.
 * 
 * SAFETY: All velocity commands are hard-clamped by MAX_VELOCITY_MPS.
 */

#ifndef MOTOR_CONTROLLER_H
#define MOTOR_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>

/** Maximum allowable velocity in meters per second. */
#define MAX_VELOCITY_MPS  (1.5)

/**
 * Set the target velocity for the drive motors.
 * 
 * @param velocity_mps  Target velocity in m/s. Clamped to [-MAX, +MAX].
 * @return 0 on success, -1 on hardware fault.
 * 
 * SAFETY: Returns -1 and stops motors if velocity exceeds physical limits.
 */
int motor_set_velocity(double velocity_mps);

#endif /* MOTOR_CONTROLLER_H */
```

### 7.4 Tools & Enforcement

| Tool | Purpose | CI Gate |
|:-----|:--------|:--------|
| `gcc -Wall -Wextra -Werror -pedantic` | All warnings as errors | Zero warnings |
| `clang-tidy` | Static analysis | Zero findings |
| `cppcheck` | Additional static analysis | Zero HIGH |
| MISRA checker (PC-lint, Polyspace) | MISRA compliance | If safety-critical |
| `valgrind` | Memory error detection | Zero errors |
| `AddressSanitizer` | Runtime memory safety | Clean runs |

---

## 8. React / TypeScript Standards

> For web interfaces, dashboards, and user-facing applications.

### 8.1 TypeScript Configuration

```json
{
  "compilerOptions": {
    "strict": true,
    "strictNullChecks": true,
    "noImplicitAny": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

### 8.2 Component Standards

- **Functional components only** — no class components
- **Max ~150 lines per component** — split if larger
- **Props use `interface`** — state/hooks use `type`
- **One component per file**
- **Early returns** for loading/error states before the main render

```tsx
/**
 * Displays the current system status with health indicators.
 * 
 * Used by: Dashboard, AdminPanel
 * 
 * DISASTER NOTE: If this component fails to render, the operator
 * loses visibility into system health. Fail-safe: raw JSON fallback.
 */
interface StatusPanelProps {
  /** Current system status object */
  status: SystemStatus;
  /** Called when user requests a manual refresh */
  onRefresh: () => void;
}

export function StatusPanel({ status, onRefresh }: StatusPanelProps) {
  if (!status) return <ErrorFallback message="Status unavailable" />;

  return (
    <div className="status-panel">
      <HealthIndicator level={status.health} />
      <button onClick={onRefresh}>Refresh</button>
    </div>
  );
}
```

### 8.3 Naming Conventions

| Element | Convention | Example |
|:--------|:-----------|:--------|
| Components | `PascalCase` | `StatusPanel`, `UserProfile` |
| Hooks | `useCamelCase` | `useAuth`, `useSystemStatus` |
| Event handlers | `handleVerb` or `onVerb` | `handleSubmit`, `onClose` |
| Boolean props | `is/has/should` prefix | `isLoading`, `hasError` |
| Constants | `UPPER_SNAKE` | `MAX_RETRIES`, `API_URL` |
| Utility files | `kebab-case.ts` | `date-utils.ts`, `api-client.ts` |

### 8.4 Tools & Enforcement

| Tool | Purpose | CI Gate |
|:-----|:--------|:--------|
| ESLint + TypeScript parser | Linting | Zero warnings |
| Prettier | Formatting | Pre-commit hook |
| `tsc --noEmit` | Type checking | Zero errors |

---

## 9. Error Handling Pattern (All Languages)

```
1. Validate inputs (guard clauses) → raise/return early
2. Execute the operation
3. Verify the output (post-condition assertions)
4. Handle failures explicitly — never silently swallow
5. Log the failure with full context
```

**The Golden Rules:**
- **Fail fast** — detect errors at the earliest possible point
- **Fail loud** — log with full context, never fail silently
- **Fail safe** — on unrecoverable error, enter a safe/degraded state
- **Fail traceable** — every error includes enough info to reproduce

---

## 10. Compliance Checklist

Before submitting code in **any language**:

- [ ] All functions ≤60 lines
- [ ] Cyclomatic complexity ≤10 per function
- [ ] Nesting depth ≤4 levels
- [ ] All public functions have docstrings/JSDoc/Doxygen comments
- [ ] All magic numbers replaced with named constants
- [ ] All return values checked or explicitly ignored with comment
- [ ] Guard clauses handle error paths first
- [ ] ≥2 assertions per non-trivial function
- [ ] File header explains purpose and consumers
- [ ] No forbidden patterns used
- [ ] All linter/compiler warnings resolved (zero tolerance)
- [ ] A human can understand any function in 30 seconds

---

> **"Code is read far more often than it is written. Write for the reader — especially the panicked one at 3 AM."**
