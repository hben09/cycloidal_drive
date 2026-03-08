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
  assembly.py              # Interactive viewer — compose and display parts in OCP CAD Viewer
  export.py                # Export all parts to STL/STEP + full assembly STEP
  export/                  # Generated files (gitignored)
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

- Central spine cylinder (full shaft length, 5mm OD) with 10mm OD input collar for D-bore wall
- Lobe 1: 17mm OD cylinder offset +1.5mm in X, extruded 10mm at disc 1 Z position
- Lobe 2: 17mm OD cylinder offset -1.5mm in X (180-degree), extruded 10mm at disc 2 Z position
- Union all sections, subtract 5mm through-bore

### 5. `src/ring_gear_body.py` — Main housing cylinder

- Tube: 140mm OD, 116mm bore, height = 47mm (from input clearance through output bearings per stack-up)
- Output bearing seat: 90.15mm counterbore, 20mm deep from output end
- 8x M4 housing bolt through-holes (4.4mm clearance) on 125mm circle
- Reveal windows: outer wall cut away in disc zone (Z=3mm to Z=25mm) to expose ring pins, retaining only 16mm ⌀ cylindrical pillars around each bolt hole and a 3mm solid rim at the input face for motor-plate mating

### 6. `src/motor_plate.py` — Motor-side housing plate

- 140mm OD disc, 10mm thick (5mm wall + 5mm for 625 bearing seat)
- Center bore clears motor shaft (~5.5mm)
- NEMA 17 bolt pattern: 4x M3 clearance holes on 31mm square
- 21x ring pin press-fit blind holes (3.875mm dia) on 108mm circle
- 8x M4 housing bolt through-holes on 125mm circle with 7.4mm ⌀ × 4.5mm counterbores on outer face

### 7. `src/output_cap.py` — Output-side cap

- 140mm OD disc, 8mm thick
- Center bore clears output hub (70.25mm)
- 8x M4 housing bolt through-holes on 125mm circle with hex nut pockets (7.2mm AF × 4.0mm deep) on outer face

### 8. `src/output_hub.py` — Output plate

- 69.925mm OD cylinder (light press into 6814 bore), ~25mm long
- 625 bearing seat counterbore from inner face
- 5.4mm through-bore for shaft clearance
- 4x M3 tap holes on 60mm circle (inner face, for output pins/shoulder bolts)
- 4x arm mounting holes on outer face

### 9. `src/purchased_parts.py` — Simplified models for all purchased components

Simple cylinder/box models for visualization only (not for manufacturing):
- **Bearings** (6003-2RS x2, 6814-2RS x2, 625-2RS x1): annular cylinders with correct bore/OD/width
- **NEMA 17 motor**: 42.3mm square body, 48mm long, 5mm shaft stub with D-cut
- **Ring pins**: 21x 4mm x 35mm cylinders on 108mm circle
- **Output pins**: 4x M3 shoulder bolts (4mm × 45mm shoulder + M3 × 6mm thread) on 60mm circle
- **Housing bolts**: 8x M4 × 60mm SHCS (7mm head + 4mm shank) on 125mm circle
- **Housing nuts**: 8x M4 hex nuts (7mm AF × 3.2mm) on 125mm circle

Each returns a `cq.Workplane` solid, colored distinctly in the assembly.

### 10. `assembly.py` — Interactive assembly viewer

Position all parts along Z axis per the axial stack-up (spec Section 4) and display in OCP CAD Viewer. Comment/uncomment sections to show specific parts.

| Part | Z start |
|---|---|
| Motor plate | 0mm |
| Ring gear body | 10mm |
| Disc 1 (offset +1.5mm X) | 13mm |
| Disc 2 (rotated 180-deg, offset -1.5mm X) | 25mm |
| Output bearings region | 37mm |
| Output cap | 57mm (8mm thick) |
| Output hub | 37mm |
| Housing bolts | Z=0.5 (head recessed in counterbore) |
| Housing nuts | Z=61 (in nut pocket floor) |
| Eccentric shaft | spans full length |
| Motor (external) | -48mm (behind motor plate) |
| All bearings, pins | at their respective Z positions |

### 11. `export.py` — Export script

- Builds all custom parts from `DEFAULT_CONFIG`
- Exports individual STEP + STL to `export/step/` and `export/stl/`
- Exports combined `export/assembly.step`

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

### `tests/test_cam_bearing_fitment.py` — Cam-to-bearing fitment (DONE)

**TestCamBearingFitment** (5 tests)
| Test | What it checks |
|---|---|
| `test_cam_od_matches_bearing_bore` | Cam lobe OD = 6003 bore (17mm) |
| `test_bearing_od_fits_disc_bore` | 6003 OD fits disc center bore with clearance |
| `test_bearing_width_matches_disc_thickness` | Bearing width = disc thickness (10mm) |
| `test_cam_eccentricity_consistent` | Shaft and gear eccentricity match |
| `test_cam_does_not_protrude_past_bearing` | Cam + eccentricity ≤ bearing OD |

**TestCamAxialAlignment** (3 tests)
| Test | What it checks |
|---|---|
| `test_lobe1_z_matches_disc1` | Lobe 1 Z position matches disc 1 |
| `test_lobe2_z_matches_disc2` | Lobe 2 Z position matches disc 2 |
| `test_inter_disc_gap_free_of_lobes` | No lobe material in inter-disc spacer zone |

**TestEccentricOrbit** (3 tests)
| Test | What it checks |
|---|---|
| `test_disc_bearing_swept_envelope_fits_housing` | Swept envelope fits housing bore |
| `test_cam_center_orbit_radius_equals_eccentricity` | Cam orbit radius = eccentricity |
| `test_cam_fills_bearing_bore` | Cam fills bearing bore (no excessive play) |

**TestCadQueryCamBearingInterference** (5 tests)
| Test | What it checks |
|---|---|
| `test_lobe1_no_interference_with_bearing1` | No boolean intersection between lobe 1 and bearing 1 |
| `test_lobe2_no_interference_with_bearing2` | No boolean intersection between lobe 2 and bearing 2 |
| `test_shaft_passes_through_both_bearing_bores` | Shaft fits through both bearing bores |
| `test_full_stack_no_shaft_disc_interference` | No shaft-to-disc interference |
| `test_full_stack_no_bearing_disc_interference` | No bearing-to-disc interference |

---

### `tests/test_eccentric_shaft.py` — Shaft geometry (DONE)

**TestShaftDimensions** (5 tests)
| Test | What it checks |
|---|---|
| `test_thin_wall_minimum` | Lobe radius − spine radius − eccentricity ≥ 4mm |
| `test_lobes_180_degrees_apart` | Shaft eccentricity == gear eccentricity (consistent offset) |
| `test_lobe_fits_in_6003_bearing` | Lobe OD matches 6003 bore exactly |
| `test_shaft_spans_both_discs` | Z range covers both disc positions from stack-up |
| `test_lobe_engulfs_spine` | Lobe radius > eccentricity + spine radius (watertight union) |

**TestDBore** (4 tests)
| Test | What it checks |
|---|---|
| `test_collar_contains_bore` | ≥ 1.5mm wall around D-bore in input collar |
| `test_bore_does_not_break_lobe_thin_side` | ≥ 2mm wall on lobe thin side around D-bore |
| `test_bore_matches_motor_shaft` | D-bore diameter accommodates motor shaft |
| `test_bore_depth_gives_adequate_engagement` | D-bore depth ≥ 8mm engagement |

**TestCadQuerySolid** (4 tests)
| Test | What it checks |
|---|---|
| `test_solid_is_valid` | Single valid solid |
| `test_bounding_box_z` | Z height matches computed shaft length |
| `test_bounding_box_xy` | XY extent reflects 17mm lobe + eccentricity offset |
| `test_volume_sanity` | Volume between spine-only lower and full-lobe upper bounds |

---

### `tests/test_ring_gear_body.py` — Housing body (DONE)

**TestRingGearBodyDimensions** (15 tests)
| Test | What it checks |
|---|---|
| `test_body_height_matches_stackup` | Body height = z_output_cap − z_motor_plate_inner (47mm) |
| `test_housing_bolts_inside_od` | Bolt holes don't break through OD |
| `test_pin_holes_dont_breach_bearing_seat` | Pin hole inner edge ≥ 5mm from bearing seat |
| `test_pin_holes_inside_housing_od` | Pin holes don't break through OD |
| `test_bolt_holes_do_not_overlap_pin_holes` | No bolt/pin hole overlap (computed angles) |
| `test_bolt_holes_do_not_overlap_each_other` | No bolt-to-bolt overlap |
| `test_shoulder_bore_clears_output_hub` | 70mm shoulder ≥ output hub OD |
| `test_shoulder_retains_bearing` | Shoulder bore < 6814 OD (bearing can't pass) |
| `test_bearing_seat_is_press_fit` | Seat dia slightly > bearing OD, gap < 0.5mm |
| `test_housing_bolts_outside_bore` | Bolt inner edge outside 116mm bore |
| `test_housing_bolts_have_wall_to_bore` | ≥ 1mm wall from bore to bolt edge |
| `test_housing_bolts_clear_disc_sweep` | Bolt holes outside disc sweep envelope |
| `test_pillar_wall_around_bolt` | ≥ 3mm wall around bolt in each pillar |
| `test_pillar_stays_outside_disc_orbit` | Pillar inner edge vs bore geometry |
| `test_window_rim_height_is_positive` | Rim height > 0 |
| `test_windows_stay_within_disc_zone` | Windows don't extend into shoulder/bearing zones |
| `test_disc_fits_through_main_bore` | Disc sweep < bore radius |

**TestCadQuerySolid** (7 tests)
| Test | What it checks |
|---|---|
| `test_solid_is_valid` | Single valid solid |
| `test_outer_diameter` | XY extent = housing OD |
| `test_height` | Z extent matches stack-up (47mm) |
| `test_window_zone_has_pillars_only` | Window zone area < 40% of full annulus |
| `test_rim_zone_is_full_annulus` | Input rim area ≈ full annulus (minus bolt holes) |
| `test_output_bearing_seat` | Bearing zone section area matches 90.15mm seat |
| `test_volume_sanity` | Volume between reasonable bounds |

---

### `tests/test_motor_plate.py` — Motor-side plate (DONE)

| Test | What it checks |
|---|---|
| `test_solid_is_valid` | Single valid solid |
| `test_outer_diameter` | OD = 140mm |
| `test_thickness` | 10mm (5mm wall + 5mm bearing seat) |
| `test_nema17_bolt_pattern` | 4× M3 holes on 31mm square |
| `test_ring_pin_holes` | 21 blind holes on 108mm circle, press-fit diameter (3.875mm) |
| `test_center_bore_clears_motor_shaft` | Center bore >= 5mm motor shaft |
| `test_housing_bolt_holes` | 8 holes on 125mm circle |
| `test_counterbore_wall_to_od` | Counterbore leaves ≥2mm wall to OD |
| `test_counterbore_fits_in_plate` | Counterbore depth < plate thickness |
| `test_counterbore_clears_ring_pins` | Counterbore inner edge clears ring pin outer edge |

---

### `tests/test_output_cap.py` — Output-side cap (DONE)

| Test | What it checks |
|---|---|
| `test_solid_is_valid` | Single valid solid |
| `test_outer_diameter` | OD = 140mm |
| `test_thickness` | 8mm |
| `test_center_bore_clears_hub` | Center bore = 70.25mm |
| `test_housing_bolt_holes` | 8 holes on 125mm circle |
| `test_nut_pocket_fits_in_cap` | Nut pocket depth < cap thickness |
| `test_nut_pocket_floor_thickness` | Floor ≥ 2mm for PETG |
| `test_nut_pocket_wall_to_od` | Hex pocket leaves ≥2mm wall to OD |

---

### `tests/test_output_hub.py` — Output plate (DONE)

**TestOutputHubDimensions** (12 tests)
| Test | What it checks |
|---|---|
| `test_hub_od_fits_bearing_bore` | Hub OD (with tolerance) ≤ 6814 bore |
| `test_hub_od_is_light_press` | Hub-to-bearing gap < 0.2mm |
| `test_hub_height_matches_bearing_stack` | Height = output bearing total (20mm) |
| `test_shaft_bore_clears_spine` | Shaft bore > spine OD with ≥ 0.2mm clearance |
| `test_625_pocket_clears_shaft_bore` | 625 pocket dia > shaft clearance bore |
| `test_625_pocket_inside_hub` | ≥ 5mm wall from 625 pocket to hub OD |
| `test_output_pin_holes_inside_hub` | Pin hole edges inside hub OD |
| `test_output_pin_holes_clear_625_pocket` | ≥ 2mm wall from pin holes to 625 pocket |
| `test_arm_mount_holes_inside_hub` | Arm mount edges inside hub OD |
| `test_arm_mount_holes_clear_shaft_bore` | ≥ 2mm wall from arm mounts to shaft bore |
| `test_output_pins_clear_arm_mounts` | No overlap between pin and arm mount holes (45° offset) |
| `test_output_pin_holes_clear_bearing_bore` | Pin edges inside 6814 bore |

**TestCadQuerySolid** (4 tests)
| Test | What it checks |
|---|---|
| `test_solid_is_valid` | Single valid solid |
| `test_outer_diameter` | XY extent = 69.925mm |
| `test_height` | Z = 20mm (output bearing total) |
| `test_volume_sanity` | Volume between reasonable bounds |

---

### `tests/test_assembly_clearances.py` — Assembly-level clearance verification (DONE)

**TestAxialStackUp** (8 tests)
| Test | What it checks |
|---|---|
| `test_total_housing_depth` | Stack-up layers sum to total housing depth |
| `test_total_depth_is_65mm` | Total depth = 65mm |
| `test_disc1_before_disc2` | Disc 1 Z < disc 2 Z |
| `test_disc2_ends_before_output_bearings` | Disc 2 end Z < output bearings Z |
| `test_output_clearance_gap` | 2mm gap between disc 2 and output bearings |
| `test_output_bearings_end_at_output_cap` | Bearings end at output cap Z |
| `test_motor_plate_inner_face` | Motor plate inner face at correct Z |
| `test_ring_gear_body_height` | Body height matches stack-up |

**TestHousingAlignment** (3 tests)
| Test | What it checks |
|---|---|
| `test_all_housing_parts_same_od` | Motor plate, ring body, output cap share OD |
| `test_housing_bolt_angles_consistent` | Bolt angles match across all housing parts |
| `test_housing_bolts_clear_ring_pins` | Bolt holes don't overlap ring pin holes |

**TestRadialClearances** (6 tests)
| Test | What it checks |
|---|---|
| `test_disc_orbit_clears_housing_bore` | Disc sweep fits inside 116mm bore |
| `test_output_pins_inside_6814_bore` | Output pin circle inside bearing bore |
| `test_output_hub_clears_output_cap_bore` | Hub OD < output cap bore |
| `test_output_hub_fits_6814_inner` | Hub OD matches 6814 bore (light press) |
| `test_6814_outer_fits_housing_seat` | 6814 OD fits housing seat |
| `test_ring_pins_inside_housing_bore` | Ring pins inside 116mm bore |
| `test_disc_output_pin_holes_clear_center_bore` | Pin holes don't breach center bore |

**TestBearingRetention** (4 tests)
| Test | What it checks |
|---|---|
| `test_6814_retained_by_shoulder` | 6814 can't pass through 70mm shoulder |
| `test_6814_retained_by_output_cap` | Output cap retains 6814 |
| `test_6003_retained_by_disc_bore` | 6003 retained by disc center bore |
| `test_625_retained_by_output_hub_pocket` | 625 retained by hub pocket |

**TestShaftReach** (3 tests)
| Test | What it checks |
|---|---|
| `test_motor_shaft_reaches_through_plate` | Motor shaft reaches D-bore |
| `test_eccentric_shaft_reaches_625_bearing` | Shaft stub reaches 625 pocket |
| `test_eccentric_shaft_stub_fits_625_bore` | Stub OD fits 625 bore |

**TestRingPinSpan** (3 tests)
| Test | What it checks |
|---|---|
| `test_pin_length_spans_disc_zone_plus_engagement` | Pin length = disc zone + 2× engagement |
| `test_pin_length_equals_35mm` | Pin length = 35mm |
| `test_disc_zone_is_25mm` | Disc zone = 25mm |

**TestHousingBoltEngagement** (5 tests)
| Test | What it checks |
|---|---|
| `test_bolt_reaches_nut` | Bolt length spans full housing stack |
| `test_full_nut_engagement` | Full nut thickness engaged by bolt thread |
| `test_bolt_does_not_protrude` | Bolt doesn't protrude past nut pocket |
| `test_counterbore_recesses_head` | Counterbore recesses bolt head |
| `test_counterbore_wall_to_od` | Counterbore leaves ≥ 2mm wall to OD |
| `test_counterbore_fits_in_motor_plate` | Counterbore depth < motor plate thickness |

**TestCadQueryAssemblyInterference** (4 tests)
| Test | What it checks |
|---|---|
| `test_motor_plate_ring_body_no_interference` | No boolean intersection between motor plate and ring body |
| `test_ring_body_output_cap_no_interference` | No boolean intersection between ring body and output cap |
| `test_motor_plate_output_cap_no_interference` | No boolean intersection between motor plate and output cap |
| `test_output_hub_clears_output_cap` | Output hub doesn't interfere with output cap |
| `test_disc_clears_ring_gear_shoulder` | Disc doesn't interfere with ring gear shoulder |
| `test_output_hub_clears_ring_body` | Output hub doesn't interfere with ring body |

---

### `tests/test_purchased_parts.py` — Simplified visualization parts (DONE)

| Test | What it checks |
|---|---|
| `test_bearing_dimensions` | Each bearing model matches bore/OD/width from spec |
| `test_motor_body_size` | 42.3mm square × 48mm body, 5mm shaft with D-cut |
| `test_ring_pin_count_and_size` | 21× 4mm × 35mm cylinders |
| `test_output_pin_count_and_size` | 4× M3 shoulder bolts on 60mm circle |
| `test_housing_bolt_solid_valid` | 8× M4 SHCS solids, correct Z extent (64mm) |
| `test_housing_nut_solid_valid` | 8× hex nut solids, correct Z extent (3.2mm) |

---

---

## Remaining TODO

- `tests/test_export.py` — Integration tests for the export script

---

## Verification (non-test)

- **Visual**: `python assembly.py` to view in OCP CAD Viewer, or open `export/step/*.step` in external CAD viewer
- **Export**: `python export.py` to generate STL + STEP files in `export/`
- **Run individual parts**: Each `src/*.py` file has an `if __name__ == "__main__"` block using `ocp_vscode.show_object`
