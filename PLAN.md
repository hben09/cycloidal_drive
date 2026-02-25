# CadQuery Implementation Plan — Cycloidal Drive

## Context

The repo contains a complete engineering spec (`CLAUDE.md`) for a 20:1 two-disc cycloidal drive (shoulder joint for a robotic arm) but zero code. CadQuery 2.7.0 is already installed in the `cad_env` conda environment. This plan creates the full parametric CAD model from scratch.

---

## Project Structure

```
cycloidal_drive/
  src/
    __init__.py
    params.py              # All dimensions, tolerances, counts
    profiles.py            # Epitrochoid math (numpy, no CadQuery)
    eccentric_shaft.py     # Machined shaft with two offset lobes
    cycloidal_disc.py      # Epitrochoid profile disc (print 2 copies)
    ring_gear_body.py      # Main housing cylinder + bearing seat
    motor_plate.py         # NEMA 17 mount + 625 seat + ring pin holes
    output_cap.py          # Output-side cap + ring pin holes
    output_hub.py          # Output plate through 6814 bearings
    purchased_parts.py     # Simplified bearings, motor, pins for visualization
    assembly.py            # All parts positioned per axial stack-up
  build.py                 # CLI entry: builds all parts, exports STEP + STL
  output/                  # Generated files (gitignored)
    step/
    stl/
```

---

## Implementation Steps (in order)

### 1. `src/params.py` — Central parameters

Frozen dataclasses grouped by subsystem: `GearParams`, `DiscParams`, `ShaftParams`, `BearingParams`, `HousingParams`, `MotorParams`, `OutputHubParams`, `PETGTolerances`. All wrapped in a top-level `DriveConfig` with a `DEFAULT_CONFIG` singleton. Every dimension from the spec goes here — part files never hardcode numbers.

### 2. `src/profiles.py` — Epitrochoid math

Pure numpy function implementing the profile equations from spec Section 8:
```
x(θ) = R·cos(θ) − r·cos(θ+ψ) − e·cos(N·θ)
y(θ) = −R·sin(θ) + r·sin(θ+ψ) + e·sin(N·θ)
ψ = atan2(sin((1−N)·θ), (R/(e·N)) − cos((1−N)·θ))
```
Parameters: R=54mm, r=2mm, N=21, e=1.5mm. Generate 2000 points. Also includes `compute_profile_radii()` for clearance checks.

### 3. `src/cycloidal_disc.py` — Most critical part

- Build profile with `splineApprox(points, tol=0.001)` (70x smaller STEP than interpolated spline)
- `.close().extrude(10mm)`
- Subtract center bore (35.20mm) and 4x output pin holes (8mm on 60mm circle) with `polarArray`
- Both discs are identical parts — the 180-degree offset is handled in the assembly

### 4. `src/eccentric_shaft.py` — Machined part (no PETG tolerances)

- Central spine cylinder (full shaft length, ~10mm OD, 5mm bore)
- Lobe 1: 17mm OD cylinder offset +1.5mm in X, extruded 10mm at disc 1 Z position
- Lobe 2: 17mm OD cylinder offset -1.5mm in X (180-degree), extruded 10mm at disc 2 Z position
- Union all sections, subtract 5mm through-bore

### 5. `src/ring_gear_body.py` — Main housing cylinder

- Tube: 120mm OD, 116mm bore, height = 47mm (from coupler clearance through output bearings per stack-up)
- Output bearing seat: 90.15mm counterbore, 20mm deep from output end
- 8x M4 housing bolt through-holes on 110mm circle

### 6. `src/motor_plate.py` — Motor-side housing plate

- 120mm OD disc, 10mm thick (5mm wall + 5mm for 625 bearing seat)
- Center bore clears coupler (~22mm)
- 625 bearing seat: counterbore from inner face (16.075mm dia, 5mm deep)
- NEMA 17 bolt pattern: 4x M3 clearance holes on 31mm square
- 21x ring pin press-fit blind holes (3.875mm dia) on 108mm circle
- 8x housing bolt holes

### 7. `src/output_cap.py` — Output-side cap

- 120mm OD disc, 3mm thick
- Center bore clears output hub (70.25mm)
- 21x ring pin press-fit holes on 108mm circle
- 8x housing bolt holes

### 8. `src/output_hub.py` — Output plate

- 69.925mm OD cylinder (light press into 6814 bore), ~25mm long
- 625 bearing seat counterbore from inner face
- 5.4mm through-bore for shaft clearance
- 4x M4 tap holes on 60mm circle (inner face, for output pins/shoulder bolts)
- 4x arm mounting holes on outer face

### 9. `src/purchased_parts.py` — Simplified models for all purchased components

Simple cylinder/box models for visualization only (not for manufacturing):
- **Bearings** (6003-2RS x2, 6814-2RS x2, 625-2RS x2): annular cylinders with correct bore/OD/width
- **NEMA 17 motor**: 42.3mm square body, 48mm long, 5mm shaft stub
- **Shaft coupler**: 19mm OD x 25mm cylinder
- **Ring pins**: 21x 4mm x 30mm cylinders on 108mm circle
- **Output pins**: 4x 4mm x 25mm cylinders on 60mm circle

Each returns a `cq.Workplane` solid, colored distinctly in the assembly (bearings = red, motor = dark gray, pins = silver).

### 10. `src/assembly.py` — Full assembly with all components

Position all parts along Z axis per the axial stack-up (spec Section 4):
| Part | Z start |
|---|---|
| Motor plate | 0mm |
| Ring gear body | 10mm |
| Disc 1 (offset +1.5mm X) | 13mm |
| Disc 2 (rotated 180-deg, offset -1.5mm X) | 25mm |
| Output bearings region | 37mm |
| Output cap | 57mm |
| Output hub | 37mm |
| Eccentric shaft | spans full length |
| Motor (external) | -48mm (behind motor plate) |
| All bearings, pins, coupler | at their respective Z positions |

Use `cq.Assembly` with `cq.Location` for positioning and `cq.Color` for visual distinction.

### 11. `build.py` — Build script

- Builds all parts from `DEFAULT_CONFIG`
- Exports individual STEP + STL to `output/step/` and `output/stl/`
- Exports combined `output/assembly.step`
- Prints clearance verification report

---

## Tests

All tests use **pytest** with module-scoped fixtures. CadQuery-dependent tests use `pytest.importorskip("cadquery")` so the geometry/clearance tests still run without CadQuery installed.

Run: `pytest tests/ -v` from the repo root (with `cad_env` activated).

---

### `tests/test_disc_geometry.py` — Cycloidal disc validation (DONE)

14 tests across 4 classes:

**TestProfileGeometry** (5 tests)
| Test | What it checks |
|---|---|
| `test_lobe_count` | Exactly 20 radial peaks detected in profile |
| `test_profile_radii_range` | Min/max radii within ±2mm of theoretical (R−r±e) |
| `test_profile_closure` | Wrap-around gap ≈ one step length (periodic) |
| `test_profile_smoothness` | No angle change > 15° between consecutive tangents |
| `test_no_self_intersection` | Sampled segment-pair intersection check |

**TestClearances** (3 tests)
| Test | What it checks |
|---|---|
| `test_center_bore_to_pin_hole_wall` | Wall between 35.2mm bore and output pin holes >= 5mm (spec: 8.4mm) |
| `test_pin_hole_to_lobe_valley_wall` | Wall between pin hole outer edge and disc valley >= 10mm (spec: ~15mm) |
| `test_disc_fits_in_housing` | max_radius + eccentricity < housing bore radius (58mm) |

**TestMeshing** (2 tests — 360 input angles each)
| Test | What it checks |
|---|---|
| `test_ring_pin_no_interference` | No ring pin penetrates disc at any angle (d >= pin_r − 0.15mm) |
| `test_ring_pin_contact_exists` | At least one ring pin near-contact at every angle (gap < 0.5mm) |

**TestCadQuerySolid** (4 tests)
| Test | What it checks |
|---|---|
| `test_solid_is_valid` | Exactly 1 valid CQ solid produced |
| `test_bounding_box_dimensions` | XY ≈ 108mm, Z = 10mm |
| `test_volume_sanity` | Volume between annulus lower bound and full-circle upper bound |

---

### `tests/test_params.py` — Parameter validation (TODO)

| Test | What it checks |
|---|---|
| `test_default_config_exists` | `DEFAULT_CONFIG` is a valid `DriveConfig` instance |
| `test_all_fields_frozen` | Every dataclass rejects attribute mutation |
| `test_gear_ratio` | `num_ring_pins - 1 == num_lobes` (21 − 1 = 20) |
| `test_eccentricity_wall_thickness` | Thin wall = (bearing_seat_od − input_bore) / 2 − e >= 4mm |
| `test_output_pin_hole_clearance` | Hole dia >= pin dia + 2×eccentricity + clearance |
| `test_stack_up_total` | Sum of all stack-up layers == total housing depth (60mm) |
| `test_bearing_fit_tolerances` | Press-fit dims < nominal, clearance-fit dims > nominal |

---

### `tests/test_eccentric_shaft.py` — Shaft geometry (TODO)

| Test | What it checks |
|---|---|
| `test_solid_is_valid` | Single valid solid |
| `test_through_bore_diameter` | 5mm bore runs full length |
| `test_lobe_offset` | Each lobe center offset exactly 1.5mm from shaft axis |
| `test_lobe_180_separation` | Lobe 2 offset is 180° from lobe 1 |
| `test_lobe_od` | Each lobe OD = 17mm (6003 bearing bore) |
| `test_thin_wall_minimum` | Minimum wall between bore and lobe OD >= 4mm (spec: 4.5mm) |
| `test_total_length` | Shaft spans the full axial stack-up |

---

### `tests/test_ring_gear_body.py` — Housing body (TODO)

| Test | What it checks |
|---|---|
| `test_solid_is_valid` | Single valid solid |
| `test_outer_diameter` | OD = 120mm |
| `test_bore_diameter` | Inner bore = 116mm |
| `test_ring_pin_hole_count` | 21 through-holes present |
| `test_ring_pin_hole_positions` | All holes on 108mm circle, equally spaced |
| `test_output_bearing_seat` | Counterbore dia = 90.15mm, depth = 20mm |
| `test_housing_bolt_holes` | 8 holes on 110mm circle |
| `test_height` | Matches stack-up (47mm body section) |

---

### `tests/test_motor_plate.py` — Motor-side plate (TODO)

| Test | What it checks |
|---|---|
| `test_solid_is_valid` | Single valid solid |
| `test_outer_diameter` | OD = 120mm |
| `test_thickness` | 10mm (5mm wall + 5mm bearing seat) |
| `test_nema17_bolt_pattern` | 4× M3 holes on 31mm square |
| `test_625_bearing_seat` | Counterbore dia = 16.075mm, depth = 5mm |
| `test_ring_pin_holes` | 21 blind holes on 108mm circle, press-fit diameter (3.875mm) |
| `test_center_bore_clears_coupler` | Center bore >= 22mm |
| `test_housing_bolt_holes` | 8 holes on 110mm circle |

---

### `tests/test_output_cap.py` — Output-side cap (TODO)

| Test | What it checks |
|---|---|
| `test_solid_is_valid` | Single valid solid |
| `test_outer_diameter` | OD = 120mm |
| `test_thickness` | 3mm |
| `test_center_bore_clears_hub` | Center bore = 70.25mm |
| `test_ring_pin_holes` | 21 holes on 108mm circle, press-fit diameter |
| `test_housing_bolt_holes` | 8 holes on 110mm circle |

---

### `tests/test_output_hub.py` — Output plate (TODO)

| Test | What it checks |
|---|---|
| `test_solid_is_valid` | Single valid solid |
| `test_hub_od` | 69.925mm (press into 6814 bore) |
| `test_625_bearing_seat` | Counterbore on inner face for input shaft support |
| `test_shaft_clearance_bore` | 5.4mm through-bore |
| `test_output_pin_tap_holes` | 4× M4 holes on 60mm circle |
| `test_mounting_holes_on_output_face` | Arm attachment holes present |
| `test_hub_length` | ~25mm (spans bearing stack) |

---

### `tests/test_assembly.py` — Full assembly (TODO)

| Test | What it checks |
|---|---|
| `test_assembly_builds` | `cq.Assembly` completes without error |
| `test_part_count` | All expected parts present in assembly |
| `test_disc_180_offset` | Disc 2 rotated 180° relative to disc 1 |
| `test_z_positions` | Each part at correct Z per axial stack-up table |
| `test_no_interference` | Bounding box overlap check between adjacent parts |
| `test_eccentric_offset_directions` | Disc 1 offset +X, disc 2 offset −X |

---

### `tests/test_purchased_parts.py` — Simplified visualization parts (TODO)

| Test | What it checks |
|---|---|
| `test_bearing_dimensions` | Each bearing model matches bore/OD/width from spec |
| `test_motor_body_size` | 42.3mm square × 48mm body, 5mm shaft |
| `test_coupler_size` | 19mm OD × 25mm length |
| `test_ring_pin_count_and_size` | 21× 4mm × 30mm cylinders |
| `test_output_pin_count_and_size` | 4× 4mm × 25mm cylinders |

---

### `tests/test_build.py` — Build script integration (TODO)

| Test | What it checks |
|---|---|
| `test_build_completes` | `build.py` runs without error |
| `test_step_files_exported` | All individual STEP files created in `output/step/` |
| `test_stl_files_exported` | All individual STL files created in `output/stl/` |
| `test_assembly_step_exported` | Combined `output/assembly.step` exists and is non-empty |
| `test_clearance_report` | Clearance verification report prints with all checks passing |

---

## Verification (non-test)

- **Visual**: Open `output/assembly.step` in a CAD viewer to check part fitment
- **Run**: `python build.py` from the repo root (with `cad_env` activated)
