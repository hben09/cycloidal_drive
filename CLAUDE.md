# Cycloidal Drive Specification — Shoulder Joint

## Overview

| Parameter | Value |
|---|---|
| Application | Shoulder joint, 3-DOF robotic arm, ~400mm reach |
| Type | Two-disc cycloidal drive, 180° offset |
| Gear Ratio | 20:1 (20 lobes, 21 ring pins) |
| Motor | NEMA 17, 48mm body, 20mm shaft, 5mm ⌀ |
| Eccentricity | 1.5mm |
| Housing OD | ~120mm |
| Print Material | PETG, 100% infill on discs |

---

## 1. Drive Geometry

### 1.1 Ring Gear

| Parameter | Value | Notes |
|---|---|---|
| Number of ring pins | 21 | N + 1 where N = 20 lobes |
| Ring pin diameter | 4.00mm | Ground steel dowel, h6 tolerance |
| Ring pin circle ⌀ | 108.00mm | Centered in housing bore |
| Ring pin length | 30mm | Spans both discs + spacer + press-fit |
| Housing bore ⌀ | 116.00mm | 120mm OD − 2 × 2mm wall |

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
| Output pin circle ⌀ | 60.00mm | Increased from 52mm for better torque arm |
| Output pin ⌀ | 4.00mm (M4) | Shoulder bolt or ground dowel |
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
| Input bore | 5.00mm | Matches motor shaft via coupler |
| Shaft OD at bearing seats | 17.00mm | Matches 6003 bearing bore |
| Eccentricity | 1.50mm | Offset between shaft center and bearing seat center |
| Thin side wall | 4.50mm | (17 − 5) / 2 − 1.5 = 4.5mm ✓ exceeds 4mm min |
| Thick side wall | 7.50mm | (17 − 5) / 2 + 1.5 = 7.5mm |
| Material | Steel or aluminum | Recommend machined; do NOT 3D print this part |

The eccentric shaft has two lobes offset 180° from each other, one per disc. Each lobe is a cylindrical section with center offset 1.5mm from the shaft axis.

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

### 2.3 Input Shaft Support Bearings — 625-2RS

| Parameter | Value |
|---|---|
| Quantity | 2 |
| Designation | 625-2RS |
| Bore (d) | 5mm |
| OD (D) | 16mm |
| Width (B) | 5mm |
| Type | Deep groove ball bearing, sealed |
| Dynamic load rating | ~1.0 kN (typical) |
| Purpose | Supports eccentric shaft at motor side and output side |

One in the motor-side housing plate, one in the output-side housing plate (or internal support wall).

---

## 3. Non-Bearing Purchased Parts

### 3.1 Motor

| Parameter | Value |
|---|---|
| Type | NEMA 17 |
| Body length | 48mm |
| Shaft diameter | 5mm |
| Shaft length | 20mm |
| Holding torque | ~0.45 Nm (typical) |
| Mounting pattern | 31mm square, M3 |

### 3.2 Shaft Coupler

| Parameter | Value |
|---|---|
| Type | Flexible jaw coupler (spider type) |
| Bore 1 | 5mm (motor shaft) |
| Bore 2 | 5mm (eccentric shaft) |
| Size | D20 × L25 (20mm OD × 25mm long) |

### 3.3 Ring Pins

| Parameter | Value |
|---|---|
| Quantity | 21 (buy 25) |
| Diameter | 4.00mm, h6 ground |
| Length | 30mm |
| Material | Hardened steel dowel pin |

### 3.4 Output Pins

| Parameter | Value |
|---|---|
| Quantity | 4 |
| Type | M4 shoulder bolt (preferred) or 4mm ground dowel |
| Shoulder ⌀ | 4.00mm |
| Shoulder length | ≥25mm (spans both discs + spacer) |
| Thread | M4 (for fastening to output plate) |

### 3.5 Fasteners

| Item | Spec | Qty | Purpose |
|---|---|---|---|
| Motor mounting bolts | M3 × 8mm socket head | 4 | Mount motor to housing |
| Housing assembly bolts | M4 × 40–50mm socket head | 6–8 | Clamp housing halves |
| Output plate bolts | Per application | — | Attach arm link to output |

---

## 4. Axial Stack-Up

Measured from motor mounting face inward:

| Layer | Thickness | Running Total |
|---|---|---|
| Motor-side housing plate wall | 5mm | 5mm |
| 625 bearing seat (motor side) | 5mm | 10mm |
| Shaft coupler clearance | 3mm | 13mm |
| Cycloidal disc 1 + 6003 bearing | 10mm | 23mm |
| Inter-disc spacer | 2mm | 25mm |
| Cycloidal disc 2 + 6003 bearing | 10mm | 35mm |
| Clearance to output bearing | 2mm | 37mm |
| Output bearings (2 × 6814) | 20mm | 57mm |
| Output-side housing wall | 3mm | 60mm |

**Total housing depth: ~60mm** (not including motor body protrusion)

**Total assembly depth including NEMA 17:** ~60mm + 48mm motor + 5mm standoff = **~113mm**

---

## 5. Housing Design Notes

### 5.1 Overall Envelope

| Dimension | Value |
|---|---|
| OD | 120mm |
| Depth | ~60mm (housing only) |
| Housing bore (ring pin area) | 116mm |
| Output bearing seat OD | 90.15mm (press fit for 6814 outer race) |
| Output bearing seat depth | 20mm (for 2 × 6814) |

### 5.2 Housing Split

Recommend splitting the housing into 3 printed parts:

1. **Motor plate** — NEMA 17 bolt pattern, 625 bearing seat, ring pin holes (one end)
2. **Ring gear body** — Main cylinder with 21 ring pin through-holes, output bearing seat bore
3. **Output cap** — Retains output bearings, seals housing, second 625 bearing seat

Parts joined with M4 through-bolts around the perimeter (6–8 bolts on a ~110mm bolt circle).

### 5.3 Output Hub / Plate

A separate printed or aluminum part that:

- Has 4× M4 threaded holes (or shoulder bolt seats) on the 60mm pin circle
- Passes through the 2× 6814 bearing inner races (hub OD = 70mm, light press)
- Has a flat output face with mounting holes for the next arm link
- Houses a 625 bearing seat on the inner side to support the eccentric shaft output end

---

## 6. PETG Print Tolerances

| Fit Type | Nominal Adjustment | Application |
|---|---|---|
| Bearing outer race → housing | +0.05 to +0.10mm on bore ⌀ | 6814 and 625 outer race seats |
| Bearing inner race → shaft/hub | −0.05 to −0.10mm on shaft ⌀ | Output hub through 6814 inner race |
| Ring pin press-fit holes | −0.10 to −0.15mm on hole ⌀ | 4mm pins into housing plates |
| Sliding / clearance fit | +0.20 to +0.30mm on hole ⌀ | Output pin holes in disc, disc center bore |
| General mating surfaces | +0.15mm clearance | Housing halves, spacers |

**Notes:**

- Print all cycloidal discs flat (lobes in XY plane) at 100% infill
- Use 0.16mm or finer layer height for bearing seats
- Test-print a bearing fit gauge before committing to full parts
- PETG shrinks ~0.3–0.5% — account for this on large dimensions (120mm housing may need to be designed at ~120.4mm)

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
| 2 | Shaft coupler | 5mm–5mm flexible jaw, D20L25 | 1 | $3–5 |
| 3 | Eccentric bearing | 6003-2RS (17 × 35 × 10mm) | 2 | $4–8 |
| 4 | Output bearing | 6814-2RS (70 × 90 × 10mm) | 2 | $16–40 |
| 5 | Input shaft bearing | 625-2RS (5 × 16 × 5mm) | 2 | $2–4 |
| 6 | Ring pins | 4mm × 30mm ground dowel h6 | 25 | $8–12 |
| 7 | Output pins | M4 × 35mm shoulder bolt | 4 | $3–6 |
| 8 | Motor bolts | M3 × 8mm socket head | 4 | $1–2 |
| 9 | Housing bolts | M4 × 50mm socket head | 8 | $2–4 |
| | | | **Total** | **~$50–95** |

---

## 10. Design Sequence

Recommended order of CAD operations:

1. Model the eccentric shaft around the 6003 bearing dimensions and 5mm input bore
2. Generate the cycloidal disc profile from the equations in Section 8
3. Add center bore (35.2mm) and 4× output pin holes (8mm on 60mm circle) to disc
4. Model the ring gear body with 21× pin holes on 108mm circle and output bearing seat
5. Model the output hub to fit through 2× 6814 inner races with pin mounting
6. Model the motor plate with NEMA 17 pattern and 625 bearing seat
7. Model the output cap with 625 bearing seat and housing bolt holes
8. Verify all clearances in assembly
