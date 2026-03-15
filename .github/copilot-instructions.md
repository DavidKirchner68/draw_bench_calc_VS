# DrawBench Copilot Instructions

## Commands

### Run the desktop app

- `python draw_bench_calc_PY.py`
- `python draw_bench_calc_VS.py`

### Validate Python syntax

- Full validation of the two primary calculator scripts: `python -m py_compile draw_bench_calc_PY.py draw_bench_calc_VS.py`
- Single-file validation: `python -m py_compile draw_bench_calc_PY.py`
- Single-file validation: `python -m py_compile draw_bench_calc_VS.py`

## Architecture

- `proc_draw.prg` is the original FoxPro/VFP source for the wire-drawing formulas. The Python calculators are direct ports and should stay formula-compatible with that file.
- `draw_bench_calc_PY.py` is the baseline Tkinter application. It is organized as one `DrawBenchApp` class with notebook tabs for `Basic`, `Die Geometry`, `Stress & Force`, `Thermal`, and `Pass Schedule`.
- `draw_bench_calc_VS.py` is an expanded variant of the same application. It keeps the same overall structure but adds dual-unit result/input presentation, material presets, block-speed and work-hardening helpers, Archard die-wear calculations, and tighter synchronization between tabs.
- The pure engineering formulas live at module scope near the top of the Python files. UI code calls those functions and caches intermediate results on `self._...` attributes for downstream tabs.
- The calculation flow is chained across tabs rather than isolated:
  - `_calc_basic()` establishes `self._d0`, `self._d1`, and `self._ra`, then triggers die calculations and syncs the schedule inputs.
  - `_calc_die()` computes deformation geometry (`Δ`, `Ld`, `Φ`, angle-derived values) and stores state needed by stress and wear calculations.
  - `_calc_stress()` computes flow stress, drawing stress, force/power, and then refreshes thermal, die-wear, and schedule outputs from the same state.
  - `_calc_thermal()` assumes the stress step already populated SI/MPa state and converts to Pa for thermal equations.
- `draw_bench_calc_PY.py`, `draw_bench_calc_VS.py`, and several `*Copy*.py` files are near-duplicates. Confirm which script the user actually wants changed before applying behavior changes broadly.

## Key conventions

- The UI exposes **full included die angle**, but the formulas use **semi-angle in radians**. The code consistently divides the entered angle by 2 before calling geometry/stress formulas.
- Diameter units are user-selectable (`in` or `mm`), but thermal and many force calculations are normalized to SI internally. When editing those paths, preserve the explicit inch/mm to meter conversions before area, power, strain-rate, and temperature calculations.
- In `draw_bench_calc_VS.py`, stress inputs are user-entered in `psi` with auto-converted `MPa` display, while thermal properties are entered in SI with read-only imperial reference values. Keep that dual-unit directionality intact.
- Cross-tab synchronization relies on `StringVar.trace_add(...)`, `_suppress`, `_syncing_angle`, and cached `_last_unit` state. Reuse those mechanisms instead of introducing parallel copies of the same synchronization logic.
- Unit toggles do not just relabel widgets: `_update_unit_labels()` also converts existing diameter-like inputs (`D0`, `D1`, block diameter, allowable wear, schedule diameters). Preserve that behavior when adding new diameter fields.
- Error handling is UI-first: invalid required inputs raise `ValueError`, then the caller shows `messagebox.showerror(...)` and updates the status bar. Follow that pattern for new required calculations.
- The `Pass Schedule` tab encodes process planning logic with three strategies: equal number of passes, constant RA per pass, and constant `Δ` per pass. The constant-`Δ` path solves for RA via `_ra_for_delta(...)` instead of hard-coding a closed-form approximation.
- `draw_bench_calc_VS.py` contains features that do not exist in `draw_bench_calc_PY.py` (material presets, block speed, work hardening, die wear, angle sync, richer unit handling). Do not assume a fix in one file automatically applies cleanly to the other.
