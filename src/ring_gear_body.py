"""Ring gear body — main housing cylinder with bearing seat and pin retention.

3D-printed PETG housing part.  Spans from the motor plate inner face
(global Z=10mm) to the output cap (global Z=57mm).  Local Z=0 at the
input face.

Stepped internal bore:
  Z=0  to Z=27  — 116mm bore (disc orbit clearance + 2mm output gap)
  Z=27 to Z=47  — 90.15mm bore (press-fit seat for 2× 6814-2RS output
                   bearings)

Bearing axial retention relies on press-fit into the 90.15mm seat and
the output cap clamping the outer race from the far side.  No shoulder
ring is used — the disc envelope (~108mm) exceeds the 6814 OD (90mm),
so a shoulder cannot simultaneously clear the disc and block the bearing.

Ring-pin retention (dual-end):
  35mm pins press 5mm into the motor plate (blind holes) and 4mm into
  the ring gear body bearing zone.  The middle 27mm spans the disc +
  clearance zone (116mm bore — pins in air).  Blind holes (31mm deep)
  from the input face avoid cutting through the bearing seat wall.

Other features:
  - 21 ring-pin blind holes on 108mm circle (4.20mm clearance dia, 31mm deep)
  - 8 M4 housing-bolt through-holes on 125mm circle

Assembly: insert ring pins through the motor plate's through-holes,
then slide the ring gear body onto the protruding pin ends.  Chamfered
entries on both parts guide the pins in.  No need to align all 21
pins simultaneously — insert and seat them one at a time.
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
    tol = cfg.tolerances
    stack = cfg.stack_up

    # ── Dimensions ────────────────────────────────────────────────
    body_height = stack.z_output_cap - stack.z_motor_plate_inner  # 47mm
    housing_r = h.od / 2.0  # 67mm
    bore_r = h.bore_dia / 2.0  # 58mm (116mm bore)
    bearing_seat_r = h.output_bearing_seat_dia / 2.0  # 45.075mm

    # Zone boundaries (local Z)
    disc_zone_end = (
        stack.input_clearance
        + stack.disc_thickness * 2
        + stack.inter_disc_spacer
    )  # 25mm
    bore_zone_end = disc_zone_end + stack.output_clearance  # 27mm (2mm disc clearance)
    bearing_z = bore_zone_end  # 27mm
    bearing_h = stack.output_bearing_total  # 20mm

    # Pin hole dimensions
    pin_hole_dia = g.ring_pin_dia - tol.ring_pin_press_sub  # 4.20mm clearance
    pin_circle_r = g.ring_pin_circle_dia / 2.0  # 54mm

    # ── 1. Base cylinder ─────────────────────────────────────────
    result = (
        cq.Workplane("XY")
        .circle(housing_r)
        .extrude(body_height)
    )

    # ── 2. Main bore: Z=0 to Z=27 (116mm, disc orbit + clearance) ─
    main_bore = (
        cq.Workplane("XY")
        .circle(bore_r)
        .extrude(bore_zone_end)
    )
    result = result.cut(main_bore)

    # ── 3. Output bearing seat: Z=27 to Z=47 (90.15mm) ──────────
    bearing_bore = (
        cq.Workplane("XY")
        .workplane(offset=bearing_z)
        .circle(bearing_seat_r)
        .extrude(bearing_h)
    )
    result = result.cut(bearing_bore)

    # ── 4. Ring-pin blind holes (21×, press-fit) ──────────────────
    # Holes go from Z=0 (input face) through the bore zone (27mm,
    # air at 54mm radius inside 58mm bore) plus 4mm of press-fit
    # engagement into the bearing zone.  Total depth 31mm.
    pin_engagement = (g.ring_pin_length - bore_zone_end) / 2.0  # 4mm
    pin_hole_depth = bore_zone_end + pin_engagement  # 31mm
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
        .extrude(pin_hole_depth)
    )
    result = result.cut(pin_holes)

    # Chamfer at bore/bearing transition — pins are in air (116mm bore)
    # from Z=0 to Z=27, then enter solid bearing-zone material.
    chamfer_depth = 1.0  # mm
    chamfer_dia = pin_hole_dia + 1.0  # mm, funnel entry
    for pt in pin_pts:
        cone = (
            cq.Workplane("XY")
            .workplane(offset=bore_zone_end)
            .center(pt[0], pt[1])
            .circle(chamfer_dia / 2.0)
            .workplane(offset=chamfer_depth)
            .circle(pin_hole_dia / 2.0)
            .loft(ruled=True)
        )
        result = result.cut(cone)

    # ── 5. M4 housing-bolt through-holes ─────────────────────────
    # Bolt angles are offset to sit at midpoints between adjacent
    # ring pins, preventing hole overlap on the shared annular wall.
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
        .extrude(body_height)
    )
    result = result.cut(bolt_holes)

    # ── 6. Reveal windows — expose ring pins between bolt pillars ──
    # Cut away the outer wall in the disc zone, keeping only cylindrical
    # pillars around each housing bolt and a solid rim at the input face.
    rim_h = 3.0  # solid rim at input face for motor-plate mating
    window_z_start = rim_h
    window_h = bore_zone_end - rim_h  # 24mm
    pillar_dia = 16.0  # ~5.8mm wall around 4.4mm bolt hole

    # Full annular wall section to remove
    wall_removal = (
        cq.Workplane("XY")
        .workplane(offset=window_z_start)
        .circle(housing_r + 0.1)
        .circle(bore_r)
        .extrude(window_h)
    )

    # Preserve cylindrical pillars around each bolt hole
    pillar_pts = [
        (bolt_r * math.cos(a), bolt_r * math.sin(a))
        for a in bolt_angles
    ]
    pillars = (
        cq.Workplane("XY")
        .workplane(offset=window_z_start)
        .pushPoints(pillar_pts)
        .circle(pillar_dia / 2.0)
        .extrude(window_h)
    )
    wall_removal = wall_removal.cut(pillars)

    result = result.cut(wall_removal)

    return result


if __name__ == "__main__":
    from ocp_vscode import show_object

    body = build_ring_gear_body()
    show_object(body, name="ring_gear_body", options={"color": "slategray", "alpha": 0.5})
