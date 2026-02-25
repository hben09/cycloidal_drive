"""Motor plate — mounts the NEMA 17 and supports the input shaft.

3D-printed PETG housing part. Sits at Z=0 (outer/motor face) to Z=10mm
(inner face). Features:
  - Motor pilot recess and M3 bolt pattern on the outer face
  - 625-2RS bearing seat on the inner face
  - 8 M4 housing-bolt through-holes on the perimeter

Ring pins are retained entirely by the ring gear body (press-fit).
The bolt circle (110mm) and pin circle (108mm) are too close radially
for both hole patterns in the same plate.
"""

import math
import sys
import os

import cadquery as cq

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.params import DriveConfig, DEFAULT_CONFIG


def build_motor_plate(cfg: DriveConfig = DEFAULT_CONFIG) -> cq.Workplane:
    """Build the motor-side housing plate.

    Return a valid CadQuery Workplane with exactly one solid.
    """
    h = cfg.housing
    m = cfg.motor
    b = cfg.bearings
    tol = cfg.tolerances
    stack = cfg.stack_up

    plate_thickness = stack.motor_plate_wall + stack.inp_bearing_seat  # 10mm
    housing_r = h.od / 2.0  # 60mm

    # ── 1. Base disc ────────────────────────────────────────────────
    result = (
        cq.Workplane("XY")
        .circle(housing_r)
        .extrude(plate_thickness)
    )

    # ── 2. Motor pilot recess (outer face, Z=0 side) ───────────────
    pilot_recess_dia = m.pilot_dia + tol.mating_surface_add * 2  # 22.30mm
    pilot_depth = 2.0  # matches NEMA 17 boss height
    pilot_cut = (
        cq.Workplane("XY")
        .circle(pilot_recess_dia / 2.0)
        .extrude(pilot_depth)
    )
    result = result.cut(pilot_cut)

    # ── 3. Central shaft bore (through full plate) ──────────────────
    shaft_bore_dia = m.shaft_dia + tol.sliding_clearance_add * 2  # 5.50mm
    shaft_bore = (
        cq.Workplane("XY")
        .circle(shaft_bore_dia / 2.0)
        .extrude(plate_thickness)
    )
    result = result.cut(shaft_bore)

    # ── 4. 625 bearing seat (inner face, 5mm deep pocket) ──────────
    bearing_seat_dia = b.inp_od + tol.bearing_seat_bore_add  # 16.075mm
    bearing_pocket = (
        cq.Workplane("XY")
        .workplane(offset=stack.motor_plate_wall)  # Z=5
        .circle(bearing_seat_dia / 2.0)
        .extrude(stack.inp_bearing_seat)  # 5mm → Z=10
    )
    result = result.cut(bearing_pocket)

    # ── 5. M3 motor bolt holes (through, clearance fit) ─────────────
    m3_clearance_dia = m.bolt_dia + 0.4  # 3.4mm
    half_pat = m.bolt_pattern_square / 2.0  # 15.5mm
    motor_bolt_pts = [
        (half_pat, half_pat),
        (-half_pat, half_pat),
        (-half_pat, -half_pat),
        (half_pat, -half_pat),
    ]
    motor_bolts = (
        cq.Workplane("XY")
        .pushPoints(motor_bolt_pts)
        .circle(m3_clearance_dia / 2.0)
        .extrude(plate_thickness)
    )
    result = result.cut(motor_bolts)

    # ── 6. M4 housing bolt holes (through, clearance fit) ─────────
    m4_clearance_dia = h.bolt_dia + 0.4  # 4.4mm
    bolt_r = h.bolt_circle_dia / 2.0  # 55mm
    bolt_pts = [
        (
            bolt_r * math.cos(2 * math.pi * i / h.bolt_count),
            bolt_r * math.sin(2 * math.pi * i / h.bolt_count),
        )
        for i in range(h.bolt_count)
    ]
    bolt_holes = (
        cq.Workplane("XY")
        .pushPoints(bolt_pts)
        .circle(m4_clearance_dia / 2.0)
        .extrude(plate_thickness)
    )
    result = result.cut(bolt_holes)

    return result


if __name__ == "__main__":
    from ocp_vscode import show_object

    plate = build_motor_plate()
    show_object(plate, name="motor_plate", options={"color": "slategray", "alpha": 0.7})
