"""Ring gear body — main housing cylinder with bearing seat and pin retention.

3D-printed PETG housing part.  Spans from the motor plate inner face
(global Z=10mm) to the output cap (global Z=57mm).  Local Z=0 at the
input face.

Stepped internal bore:
  Z=0  to Z=25  — 116mm bore (full clearance for cycloidal disc orbit)
  Z=25 to Z=27  — 70mm bore shoulder ring (retains output bearings and
                   provides 2mm of ring-pin press-fit engagement)
  Z=27 to Z=47  — 90.15mm bore (press-fit seat for 2× 6814-2RS output
                   bearings; ring-pin holes continue through this wall
                   for an additional 20mm of press-fit engagement)

Other features:
  - 21 ring-pin through-holes on 108mm circle (3.875mm press-fit dia)
  - 8 M4 housing-bolt through-holes on 110mm circle

Assembly: slide the disc+shaft assembly in from the input end (116mm bore
clears the ~108mm disc), then insert ring pins one at a time while
rotating the discs to align lobe valleys with each pin path.
"""

import math
import sys
import os

import cadquery as cq

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.params import DriveConfig, DEFAULT_CONFIG, compute_housing_bolt_angles


def build_ring_gear_body(cfg: DriveConfig = DEFAULT_CONFIG) -> cq.Workplane:
    """Build the ring gear body housing cylinder.

    Return a valid CadQuery Workplane with exactly one solid.
    """
    g = cfg.gear
    h = cfg.housing
    b = cfg.bearings
    tol = cfg.tolerances
    stack = cfg.stack_up

    # ── Dimensions ────────────────────────────────────────────────
    body_height = stack.z_output_cap - stack.z_motor_plate_inner  # 47mm
    housing_r = h.od / 2.0  # 60mm
    bore_r = h.bore_dia / 2.0  # 58mm (116mm bore)
    bearing_seat_r = h.output_bearing_seat_dia / 2.0  # 45.075mm
    shoulder_bore_r = b.out_bore / 2.0  # 35mm (70mm — clears output hub)

    # Zone boundaries (local Z)
    disc_zone_end = (
        stack.input_clearance
        + stack.disc_thickness * 2
        + stack.inter_disc_spacer
    )  # 25mm
    shoulder_h = stack.output_clearance  # 2mm
    shoulder_z = disc_zone_end  # 25mm
    bearing_z = shoulder_z + shoulder_h  # 27mm
    bearing_h = stack.output_bearing_total  # 20mm

    # Pin hole dimensions
    pin_hole_dia = g.ring_pin_dia - tol.ring_pin_press_sub  # 3.875mm
    pin_circle_r = g.ring_pin_circle_dia / 2.0  # 54mm

    # ── 1. Base cylinder ─────────────────────────────────────────
    result = (
        cq.Workplane("XY")
        .circle(housing_r)
        .extrude(body_height)
    )

    # ── 2. Main bore: Z=0 to Z=25 (116mm, disc orbit clearance) ─
    main_bore = (
        cq.Workplane("XY")
        .circle(bore_r)
        .extrude(disc_zone_end)
    )
    result = result.cut(main_bore)

    # ── 3. Shoulder ring bore: Z=25 to Z=27 (70mm) ──────────────
    # Provides bearing retention shoulder (6814 OD 90mm can't pass
    # through 70mm bore) and first 2mm of ring-pin engagement.
    shoulder_bore = (
        cq.Workplane("XY")
        .workplane(offset=shoulder_z)
        .circle(shoulder_bore_r)
        .extrude(shoulder_h)
    )
    result = result.cut(shoulder_bore)

    # ── 4. Output bearing seat: Z=27 to Z=47 (90.15mm) ──────────
    bearing_bore = (
        cq.Workplane("XY")
        .workplane(offset=bearing_z)
        .circle(bearing_seat_r)
        .extrude(bearing_h)
    )
    result = result.cut(bearing_bore)

    # ── 5. Ring-pin through-holes (21×, press-fit) ───────────────
    # Holes run full body height.  In the 116mm bore zone they pass
    # through air (no material at 54mm radius).  In the shoulder
    # ring and bearing zone they cut into solid material, providing
    # up to 22mm of press-fit retention per pin.
    pin_pts = [
        (
            pin_circle_r * math.cos(2 * math.pi * i / g.num_ring_pins),
            pin_circle_r * math.sin(2 * math.pi * i / g.num_ring_pins),
        )
        for i in range(g.num_ring_pins)
    ]
    pin_holes = (
        cq.Workplane("XY")
        .pushPoints(pin_pts)
        .circle(pin_hole_dia / 2.0)
        .extrude(body_height)
    )
    result = result.cut(pin_holes)

    # ── 6. M4 housing-bolt through-holes ─────────────────────────
    # Bolt angles are offset to sit at midpoints between adjacent
    # ring pins, preventing hole overlap on the shared annular wall.
    m4_clearance_dia = h.bolt_dia + 0.4  # 4.4mm
    bolt_r = h.bolt_circle_dia / 2.0  # 55mm
    bolt_angles = compute_housing_bolt_angles(cfg)
    bolt_pts = [
        (bolt_r * math.cos(a), bolt_r * math.sin(a))
        for a in bolt_angles
    ]
    bolt_holes = (
        cq.Workplane("XY")
        .pushPoints(bolt_pts)
        .circle(m4_clearance_dia / 2.0)
        .extrude(body_height)
    )
    result = result.cut(bolt_holes)

    return result


if __name__ == "__main__":
    from ocp_vscode import show_object

    body = build_ring_gear_body()
    show_object(body, name="ring_gear_body", options={"color": "slategray", "alpha": 0.5})
