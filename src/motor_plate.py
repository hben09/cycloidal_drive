"""Motor plate — mounts the NEMA 17 and supports the input shaft.

3D-printed PETG housing part. Sits at Z=0 (outer/motor face) to Z=10mm
(inner face). Features:
  - Motor pilot recess and M3 bolt pattern on the outer face
  - Central shaft bore for motor shaft pass-through (direct D-shaft engagement)
  - 8 M4 housing-bolt through-holes on the perimeter

No motor-side 625 bearing — the motor shaft passes through the plate
and engages the eccentric shaft D-bore directly. Motor internal bearings
and 6003 disc bearings provide adequate radial support.

Ring pins press into blind holes on the inner face (5mm deep), providing
dual-end retention together with the ring gear body shoulder.
"""

import math
import sys
import os

import cadquery as cq

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.params import DriveConfig, DEFAULT_CONFIG, compute_housing_bolt_angles


def build_motor_plate(cfg: DriveConfig = DEFAULT_CONFIG) -> cq.Workplane:
    """Build the motor-side housing plate.

    Return a valid CadQuery Workplane with exactly one solid.
    """
    h = cfg.housing
    m = cfg.motor
    tol = cfg.tolerances
    stack = cfg.stack_up

    plate_thickness = stack.motor_plate_wall + stack.inp_bearing_seat  # 10mm
    housing_r = h.od / 2.0  # 67mm

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

    # ── 4. M3 motor bolt holes (through, clearance fit) ──────────────
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

    # ── 5. Ring-pin blind holes (21×, press-fit from inner face) ──
    # Pins are 35mm long; disc zone takes 25mm, leaving 10mm split
    # evenly: 5mm into the motor plate, 5mm into the ring gear body.
    g = cfg.gear
    pin_hole_dia = g.ring_pin_dia - tol.ring_pin_press_sub  # 3.875mm
    pin_circle_r = g.ring_pin_circle_dia / 2.0  # 54mm
    disc_zone = (
        stack.input_clearance
        + 2 * cfg.disc.thickness
        + cfg.disc.inter_disc_spacer
    )  # 25mm
    pin_engagement = (g.ring_pin_length - disc_zone) / 2.0  # 5mm per side
    pin_pts = [
        (
            pin_circle_r * math.cos(2 * math.pi * i / g.num_ring_pins),
            pin_circle_r * math.sin(2 * math.pi * i / g.num_ring_pins),
        )
        for i in range(g.num_ring_pins)
    ]
    pin_holes = (
        cq.Workplane("XY")
        .workplane(offset=plate_thickness - pin_engagement)
        .pushPoints(pin_pts)
        .circle(pin_hole_dia / 2.0)
        .extrude(pin_engagement)
    )
    result = result.cut(pin_holes)

    # ── 6. M4 housing bolt holes (through, clearance fit) ─────────
    # Bolt angles match ring gear body — offset to avoid ring pin holes.
    m4_clearance_dia = h.bolt_dia + 0.4  # 4.4mm
    bolt_r = h.bolt_circle_dia / 2.0  # 62.5mm
    bolt_angles = compute_housing_bolt_angles(cfg)
    bolt_pts = [
        (bolt_r * math.cos(a), bolt_r * math.sin(a))
        for a in bolt_angles
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
