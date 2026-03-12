# Cycloidal Drive Specification — Shoulder Joint

## Overview

| Parameter | Value |
|---|---|
| Application | Shoulder joint, 3-DOF robotic arm, ~400mm reach |
| Type | Two-disc cycloidal drive, 180° offset |
| Gear Ratio | 20:1 (20 lobes, 21 ring pins) |
| Motor | NEMA 17, 48mm body, 20mm shaft, 5mm ⌀ |
| Eccentricity | 1.5mm |
| Housing OD | ~140mm |
| Print Material | PETG, 100% infill on discs |

---

## 1. Drive Geometry

### 1.1 Ring Gear

| Parameter | Value | Notes |
|---|---|---|
| Number of ring pins | 21 | N + 1 where N = 20 lobes |
| Ring pin diameter | 4.00mm | Ground steel dowel, h6 tolerance |
| Ring pin circle ⌀ | 108.00mm | Centered in housing bore |
| Ring pin length | 35mm | 5mm motor plate + 25mm disc zone + 5mm ring gear body |
| Housing bore ⌀ | 116.00mm | 140mm OD − 2 × 12mm wall |

### 1.2 Cycloidal Disc

| Parameter | Value | Notes |
|---|---|---|
| Number of lobes | 20 | Sets the ratio |
| Disc count | 2 | Offset 180° to cancel vibration |
| Approximate OD | ~108mm | Defined by epitrochoid profile |
| Center bore ⌀ | 35.20mm | 35mm bearing OD + 0.20mm clearance (PETG) |
| Disc thickness | 10.00mm | Matched to 6003-2RS bearing width |
| Inter-disc spacer | 2.00mm | Separates the two discs |
| Output pin holes | 4× equally spaced | See Section 1.3 |

### 1.3 Output Stage

| Parameter | Value | Notes |
|---|---|---|
| Output pin count | 4 | Equally spaced at 90° |
| Output pin circle ⌀ | 60.00mm | — |
| Output pin ⌀ | 4.00mm | M3 shoulder bolt (45mm shoulder) + nut |
| Disc pin hole ⌀ | 8.00mm | 4mm pin + 2 × 1.5mm ecc + 1mm clearance |
| Pin hole approach | Oversized, no bearings | Greased sliding fit |

**Clearance check — output pin holes:**

- Pin hole center radius: 30.00mm
- Pin hole edge (inner): 30.00 − 4.00 = 26.00mm from center
- Center bore radius: 17.60mm
- **Wall between bore and pin hole: 8.40mm** ✓
- Pin hole edge (outer): 30.00 + 4.00 = 34.00mm from center
- Disc lobe valley (approx inner radius): ~49mm from center
- **Wall between pin hole and lobe root: ~15mm** ✓

### 1.4 Eccentric Shaft

| Parameter | Value | Notes |
|---|---|---|
| Shaft OD at bearing seats | 17.10mm | Slight clearance for 6003 bearing bore |
| Eccentricity | 1.50mm | Offset between shaft center and bearing seat center |
| Spine OD | 5.00mm | Between lobes |
| Input collar OD | 10.00mm | Enlarged input section for D-bore wall |
| D-bore ⌀ | 5.00mm + tolerance | Receives motor shaft directly |
| D-bore flat | 4.50mm | Matches motor shaft D-cut |
| D-bore depth | 10.00mm | Motor shaft engagement length |
| Support pin hole ⌀ | 4.70mm | Blind hole for 5mm steel dowel press-fit (5.00 − 2×0.15mm) |
| Support pin hole depth | 12.00mm | Through lobe 2 into bridge zone |
| Support pin | 5mm × 20mm ground steel dowel, h6 | Press-fit into shaft, supports 625 bearing |
| Material | PETG | 3D printed; use 100% infill, 0.16mm layer height |

The eccentric shaft has two lobes offset 180° from each other, one per disc. Each lobe is a cylindrical section with center offset 1.5mm from the shaft axis. The input end has a D-bore socket that receives the motor shaft directly (no coupler). A 10mm OD collar at the input provides wall thickness around the D-bore.

The output end has a blind hole (4.70mm × 12mm deep) centered on the shaft axis, extending from the output face of lobe 2 through into the bridge zone. A 5mm × 20mm ground steel dowel pin (h6) is pressed into this hole and extends through the 2mm clearance gap into the 625 bearing in the output hub, providing rigid radial support for the shaft's free end. Pin breakdown: 12mm insertion + 2mm gap + 5mm bearing + 1mm proud = 20mm.

The bridge between the two lobes (spanning the 2mm inter-disc spacer zone) is enlarged to 23.10mm OD (lobe OD + 6mm, 3mm radial flange per side) and acts as a bearing retention flange, preventing the two 6003 bearings from sliding toward each other. The bridge is a ruled loft that transitions the eccentric center from (+e, 0) to (−e, 0).

---

## 2. Bearings

### 2.1 Eccentric Bearings — 6003-2RS

| Parameter | Value |
|---|---|
| Quantity | 2 (one per disc) |
| Designation | 6003-2RS |
| Bore (d) | 17mm |
| OD (D) | 35mm |
| Width (B) | 10mm |
| Type | Deep groove ball bearing, sealed |
| Dynamic load rating | ~5.4 kN (typical) |
| Purpose | Supports cycloidal disc on eccentric shaft |

Each bearing press-fits into the center bore of one cycloidal disc. The eccentric shaft's lobed sections seat in the bearing bore.

### 2.2 Output Bearings — 6814-2RS (×2, end-to-end)

| Parameter | Value |
|---|---|
| Quantity | 2 |
| Designation | 6814-2RS |
| Bore (d) | 70mm |
| OD (D) | 90mm |
| Width (B) | 10mm each (20mm total) |
| Type | Deep groove ball bearing, sealed |
| Dynamic load rating | ~7.0 kN (typical) |
| Purpose | Main output support, carries radial + moment loads |

Two bearings mounted end-to-end in the housing. The inner races sit on the output hub. The outer races sit in the housing bore. Paired arrangement provides significantly better moment load resistance than a single bearing.

**Clearance check — output bearing vs. output pins:**

- Output bearing bore radius: 35.00mm
- Output pin hole outer edge: 34.00mm from center
- **Clearance between pin holes and bearing bore: 1.00mm** — Note: this is the clearance on the output plate hub, not the disc. The pin holes in the discs do not interact with the output bearing. The output pins pass through the discs and thread into the output plate, which passes through the bearing bore. The 60mm pin circle sits well inside the 70mm bearing bore.

### 2.3 Input Shaft Support Bearing — 625-2RS

| Parameter | Value |
|---|---|
| Quantity | 1 |
| Designation | 625-2RS |
| Bore (d) | 5mm |
| OD (D) | 16mm |
| Width (B) | 5mm |
| Type | Deep groove ball bearing, sealed |
| Dynamic load rating | ~1.0 kN (typical) |
| Purpose | Supports eccentric shaft at output side |

Located in the output hub, supporting the eccentric shaft's free end via the 5mm steel dowel pin.

---

## 3. Non-Bearing Purchased Parts

### 3.1 Motor

| Parameter | Value |
|---|---|
| Type | NEMA 17 |
| Faceplate size | 42.3mm × 42.3mm |
| Body length | 48mm (excluding shaft) |
| Shaft diameter | 5mm (with D-cut flat at 4.5mm across) |
| Shaft length | 20mm (18mm D-cut from tip, 2mm round base) |
| Pilot / centering boss | 22mm ⌀ × 2mm |
| Mounting hole spacing | 31mm × 31mm (center-to-center) |
| Mounting hole thread | M3, tapped 4.5mm deep |
| Holding torque | ~0.45 Nm (typical) |

### 3.2 Ring Pins

| Parameter | Value |
|---|---|
| Quantity | 21 (buy 25) |
| Diameter | 4.00mm, h6 ground |
| Length | 35mm |
| Material | Hardened steel dowel pin |

### 3.3 Output Pins

| Parameter | Value |
|---|---|
| Quantity | 4 |
| Type | M3 shoulder bolt (4mm shoulder, M3×0.5 thread) |
| Shoulder ⌀ | 4.00mm |
| Shoulder length | 45mm |
| Thread | M3×0.5, 6mm long |
| Head ⌀ | 7mm (3mm hex socket) |
| Total length | 54.5mm |
| Retained by | Head on hub output face, M3 nut on disc 1 side |

### 3.4 Housing Bolts

| Parameter | Value |
|---|---|
| Quantity | 8 |
| Type | M4 × 60mm socket head cap screw (ISO 4762) |
| Head ⌀ | 7.0mm |
| Head height | 4.0mm |
| Shank ⌀ | 4.0mm |
| Shank length | 60mm |
| Retained by | Counterbore in motor plate, M4 hex nut in output cap |

### 3.5 Housing Nuts

| Parameter | Value |
|---|---|
| Quantity | 8 |
| Type | M4 hex nut |
| Width across flats | 7.0mm |
| Thickness | 3.2mm |
| Captured in | Hex nut pocket in output cap outer face |

### 3.6 Other Fasteners

| Item | Spec | Qty | Purpose |
|---|---|---|---|
| Motor mounting bolts | M3 × 10mm socket head (5.3mm head ⌀ × 3mm head height, 13mm total) | 4 | Mount motor to housing (6mm through plate + 4mm thread engagement, head recessed in 4mm counterbore on inner face) |

---

## 4. Axial Stack-Up

Measured from motor mounting face inward:

| Layer | Thickness | Running Total |
|---|---|---|
| Motor-side housing plate wall | 5mm | 5mm |
| Motor plate inner wall | 5mm | 10mm |
| Input clearance (D-shaft collar) | 3mm | 13mm |
| Cycloidal disc 1 + 6003 bearing | 10mm | 23mm |
| Inter-disc spacer | 2mm | 25mm |
| Cycloidal disc 2 + 6003 bearing | 10mm | 35mm |
| Clearance to output bearing | 2mm | 37mm |
| Output bearings (2 × 6814) | 20mm | 57mm |
| Output-side housing wall | 8mm | 65mm |

**Total housing depth: ~65mm** (not including motor body protrusion)

**Total assembly depth including NEMA 17:** ~65mm + 48mm motor + 5mm standoff = **~118mm**

---

## 5. Housing Design Notes

### 5.1 Overall Envelope

| Dimension | Value |
|---|---|
| OD | 140mm |
| Depth | ~65mm (housing only) |
| Housing bore (ring pin area) | 116mm |
| Output bearing seat OD | 90.15mm (press fit for 6814 outer race) |
| Output bearing seat depth | 20mm (for 2 × 6814) |

### 5.2 Housing Split

Recommend splitting the housing into 3 printed parts:

1. **Motor plate** — NEMA 17 bolt pattern, shaft bore for D-shaft pass-through, 21 ring-pin through-holes (4.20mm ⌀), 8× M4 counterbore holes (7.4mm ⌀ × 4.5mm deep) on outer face
2. **Ring gear body** — Main cylinder with 21 ring-pin blind holes (4.20mm ⌀, 30mm deep, chamfered entry), output bearing seat bore, 8× M4 clearance through-holes
3. **Output cap** — Retains output bearings, seals housing, 8× hex nut pockets (7.2mm AF × 4.0mm deep) on outer face

Parts joined with 8× M4 × 60mm socket head cap screws on a 125mm bolt circle. Bolt heads sit in counterbores on the motor plate; M4 hex nuts captured in hex pockets on the output cap.

### 5.3 Output Hub / Plate

A separate printed or aluminum part that:

- Has 4× clearance holes (4mm + tolerance) on the 60mm pin circle for shoulder bolts
- Passes through the 2× 6814 bearing inner races (hub OD = 70mm, light press)
- Has a flat output face for the next arm link
- Houses a 625 bearing seat on the inner side to support the eccentric shaft output end

---

## 6. PETG Print Tolerances

| Fit Type | Nominal Adjustment | Application |
|---|---|---|
| Bearing outer race → housing | +0.05 to +0.10mm on bore ⌀ | 6814 and 625 outer race seats |
| Bearing inner race → shaft/hub | −0.05 to −0.10mm on shaft ⌀ | Output hub through 6814 inner race |
| Ring pin holes (motor plate) | +0.20mm on hole ⌀ (4.20mm) | 4mm pins, clearance through-holes |
| Ring pin holes (ring gear body) | +0.20mm on hole ⌀ (4.20mm) | 4mm pins, clearance blind holes |
| Sliding / clearance fit | +0.20 to +0.30mm on hole ⌀ | Output pin holes in disc, disc center bore |
| Dowel press-fit bore | −0.15mm on bore ⌀ (4.70mm for 5mm pin) | Steel dowel pin hole in eccentric shaft |
| General mating surfaces | +0.15mm clearance | Housing halves, spacers |

**Notes:**

- Print all cycloidal discs flat (lobes in XY plane) at 100% infill
- Use 0.16mm or finer layer height for bearing seats
- Test-print a bearing fit gauge before committing to full parts
- PETG shrinks ~0.3–0.5% — account for this on large dimensions (140mm housing may need to be designed at ~140.5mm)

---

## 7. Performance Estimates

| Parameter | Value | Notes |
|---|---|---|
| Motor torque | 0.45 Nm | Typical NEMA 17 48mm |
| Gear ratio | 20:1 | |
| Theoretical output torque | 9.0 Nm | Before losses |
| Estimated efficiency | 55–65% | 3D printed, no pin bearings |
| **Practical output torque** | **5.0–5.9 Nm** | |
| Max payload at 400mm | ~1.3–1.5 kg | Including arm weight |
| Input speed (typical) | 200–500 RPM | |
| Output speed | 10–25 RPM | |
| Backdrivability | Not backdrivable | Inherent to cycloidal drives |

**Torque budget warning:** 5–6 Nm at the shoulder with 400mm reach is marginal for a 3-DOF arm. The arm structure, two additional joint motors, and wiring may consume most of the payload budget. This design is suitable for a lightweight demonstrator arm. For heavier payloads, consider upgrading to NEMA 23 or increasing the ratio.

---

## 8. Cycloidal Disc Profile

The disc profile is an **epitrochoid** defined by:

```
x(θ) = R·cos(θ) − r·cos(θ + ψ) − e·cos(N·θ)
y(θ) = −R·sin(θ) + r·sin(θ + ψ) + e·sin(N·θ)

where:
  ψ = atan2(sin((1 − N)·θ), (R / (e·N)) − cos((1 − N)·θ))

  R = ring pin circle radius = 54.00mm
  r = ring pin radius = 2.00mm
  N = number of ring pins = 21
  e = eccentricity = 1.50mm
```

The number of lobes on the disc = N − 1 = 20, giving the 20:1 ratio.

Generate this profile at high resolution (e.g., 1000+ points per full revolution of θ from 0 to 2π) and export as DXF or SVG for CAD import.

---

## 9. Shopping List (Summary)

| # | Part | Specification | Qty | Est. Cost |
|---|---|---|---|---|
| 1 | NEMA 17 stepper | 48mm body, 5mm × 20mm shaft | 1 | $10–15 |
| 2 | Eccentric bearing | 6003-2RS (17 × 35 × 10mm) | 2 | $4–8 |
| 3 | Output bearing | 6814-2RS (70 × 90 × 10mm) | 2 | $16–40 |
| 4 | Input shaft bearing | 625-2RS (5 × 16 × 5mm) | 1 | $1–2 |
| 5 | Ring pins | 4mm × 35mm ground dowel h6 | 25 | $8–12 |
| 6 | Output pins | M3 × 54.5mm shoulder bolt (4mm × 45mm shoulder) | 4 | $3–6 |
| 6a | Output pin nuts | M3 nut | 4 | $1 |
| 7 | Motor bolts | M3 × 10mm socket head (13mm total) | 4 | $1–2 |
| 8 | Housing bolts | M4 × 60mm socket head cap screw | 8 | $2–4 |
| 8a | Housing nuts | M4 hex nut | 8 | $1 |
| 9 | Shaft support pin | 5mm × 20mm ground steel dowel pin, h6 | 1 | $0.50–1 |
| | | | **Total** | **~$47–87** |

---

## 10. Project Structure & Development

### File Layout

```
src/
  params.py              # All dimensions, tolerances, counts (frozen dataclasses)
  profiles.py            # Epitrochoid math (pure numpy)
  eccentric_shaft.py     # Machined shaft with two offset lobes + D-bore
  cycloidal_disc.py      # Epitrochoid profile disc (print 2 copies)
  ring_gear_body.py      # Main housing cylinder + bearing seat + reveal windows
  motor_plate.py         # NEMA 17 mount + ring pin holes
  output_cap.py          # Output-side cap + nut pockets
  output_hub.py          # Output plate through 6814 bearings + 625 seat
  purchased_parts.py     # Simplified bearings, motor, pins for visualization
assembly.py              # OCP CAD Viewer — all parts positioned per stack-up
export.py                # Export STEP + STL to export/
```

### Environment

- CadQuery 2.7.0 managed via `uv` (`pyproject.toml` + `uv.lock`)
- Disc profile uses `cq.Edge.makeSpline(periodic=True)` for high-precision closed curves
- Both discs are identical — 180° offset is applied in the assembly only

### Commands

- `uv run pytest tests/ -v` — run all tests
- `uv run python assembly.py` — interactive 3D viewer
- `uv run python export.py` — generate `export/step/` and `export/stl/`
- Each `src/*.py` has an `if __name__ == "__main__"` block for standalone viewing
