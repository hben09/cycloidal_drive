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
- **Shaft coupler**: 20mm OD x 25mm cylinder
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

## Verification

- **Visual**: Open `assembly.step` in a CAD viewer to check part fitment
- **Programmatic clearance checks** (built into `build.py`):
  - Bore-to-pin-hole wall >= 5mm
  - Pin-hole-to-lobe-root wall >= 10mm
  - Disc OD + eccentricity sweep vs housing bore
  - Output bearing bore vs output pin circle
  - Eccentric shaft thin wall >= 4mm
- **Run**: `python build.py` from the repo root (with `cad_env` activated)
