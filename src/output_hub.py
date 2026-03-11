"""Output hub — passes through 2× 6814 inner races, carries output pins.

3D-printed PETG part.  Sits at global Z=37mm (z_output_bearings) to Z=57mm
(z_output_cap).  Local Z=0 is the inner face (disc-facing side).

Features:
  - 625 bearing pocket on inner face (supports eccentric shaft output stub)
  - 4× output pin holes on 60mm circle (M3 shoulder bolt seats)
  - 4× arm mount bolt holes on 50mm circle (M4 clearance, 45° offset)
  - Central shaft clearance bore (6.0mm)

The hub OD is sized for a light press into the 6814 bearing bores (70mm
nominal, reduced by PETG inner-shaft tolerance).  Arm mount holes are
rotated 45° from the output pin holes to maintain wall thickness between
the two hole circles.
"""

import math
import sys
import os

import cadquery as cq

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.params import DriveConfig, DEFAULT_CONFIG


def build_output_hub(cfg: DriveConfig = DEFAULT_CONFIG) -> cq.Workplane:
    """Build the output hub/plate that passes through 2× 6814 bearings.

    Return a valid CadQuery Workplane with exactly one solid.
    """
    hub = cfg.output_hub
    d = cfg.disc
    b = cfg.bearings
    tol = cfg.tolerances
    stack = cfg.stack_up

    # ── Dimensions ──────────────────────────────────────────────────
    hub_od = hub.od - tol.bearing_inner_shaft_sub  # 69.925mm (light press)
    hub_height = stack.output_bearing_total  # 20mm (2× 6814 width)
    shaft_bore_dia = hub.shaft_clearance_bore  # 6.0mm

    # 625 bearing pocket (outer race press-fit seat on inner face)
    bearing_pocket_dia = b.inp_od + tol.bearing_seat_bore_add  # 16.075mm
    bearing_pocket_depth = b.inp_width  # 5mm

    # Output pin holes (M4 shoulder bolt seats)
    pin_circle_r = d.output_pin_circle_dia / 2.0  # 30mm
    pin_hole_dia = d.output_pin_dia  # 4.0mm

    # Arm mount holes (M4 clearance, 45° offset from output pins)
    arm_circle_r = hub.arm_mount_bolt_circle_dia / 2.0  # 25mm
    arm_hole_dia = hub.arm_mount_bolt_dia  # 4.4mm

    # ── 1. Base cylinder ────────────────────────────────────────────
    result = (
        cq.Workplane("XY")
        .circle(hub_od / 2.0)
        .extrude(hub_height)
    )

    # ── 2. Central shaft clearance bore (through) ───────────────────
    shaft_bore = (
        cq.Workplane("XY")
        .circle(shaft_bore_dia / 2.0)
        .extrude(hub_height)
    )
    result = result.cut(shaft_bore)

    # ── 3. 625 bearing pocket (inner face, Z=0) ────────────────────
    bearing_pocket = (
        cq.Workplane("XY")
        .circle(bearing_pocket_dia / 2.0)
        .extrude(bearing_pocket_depth)
    )
    result = result.cut(bearing_pocket)

    # ── 4. Output pin holes (4×, 60mm circle) ──────────────────────
    pin_pts = [
        (
            pin_circle_r * math.cos(2 * math.pi * i / d.output_pin_count),
            pin_circle_r * math.sin(2 * math.pi * i / d.output_pin_count),
        )
        for i in range(d.output_pin_count)
    ]
    pin_holes = (
        cq.Workplane("XY")
        .pushPoints(pin_pts)
        .circle(pin_hole_dia / 2.0)
        .extrude(hub_height)
    )
    result = result.cut(pin_holes)

    # ── 5. Arm mount bolt holes (4×, 50mm circle, 45° offset) ──────
    offset_angle = math.pi / 4.0  # 45° offset from output pins
    arm_pts = [
        (
            arm_circle_r * math.cos(
                2 * math.pi * i / hub.arm_mount_bolt_count + offset_angle
            ),
            arm_circle_r * math.sin(
                2 * math.pi * i / hub.arm_mount_bolt_count + offset_angle
            ),
        )
        for i in range(hub.arm_mount_bolt_count)
    ]
    arm_holes = (
        cq.Workplane("XY")
        .pushPoints(arm_pts)
        .circle(arm_hole_dia / 2.0)
        .extrude(hub_height)
    )
    result = result.cut(arm_holes)

    return result


if __name__ == "__main__":
    from ocp_vscode import show_object

    hub = build_output_hub()
    show_object(hub, name="output_hub", options={"color": "goldenrod", "alpha": 0.7})
