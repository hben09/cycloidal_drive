"""Simplified purchased-part models for assembly visualization.

These are not manufacturing models — just enough geometry to verify
fitment, clearances, and the axial stack-up.
"""

import math
import sys
import os

import cadquery as cq

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.params import DriveConfig, DEFAULT_CONFIG


# -------------------------------------------------------------------
# Bearings — annular cylinders (bore/OD/width)
# -------------------------------------------------------------------


def build_bearing_6003(cfg: DriveConfig = DEFAULT_CONFIG) -> cq.Workplane:
    """6003-2RS eccentric bearing: 17×35×10mm."""
    b = cfg.bearings
    return (
        cq.Workplane("XY")
        .circle(b.ecc_od / 2.0)
        .circle(b.ecc_bore / 2.0)
        .extrude(b.ecc_width)
    )


def build_bearing_6814(cfg: DriveConfig = DEFAULT_CONFIG) -> cq.Workplane:
    """6814-2RS output bearing: 70×90×10mm."""
    b = cfg.bearings
    return (
        cq.Workplane("XY")
        .circle(b.out_od / 2.0)
        .circle(b.out_bore / 2.0)
        .extrude(b.out_width)
    )


def build_bearing_625(cfg: DriveConfig = DEFAULT_CONFIG) -> cq.Workplane:
    """625-2RS input shaft bearing: 5×16×5mm."""
    b = cfg.bearings
    return (
        cq.Workplane("XY")
        .circle(b.inp_od / 2.0)
        .circle(b.inp_bore / 2.0)
        .extrude(b.inp_width)
    )


# -------------------------------------------------------------------
# NEMA 17 motor — square body + cylindrical shaft
# -------------------------------------------------------------------


def build_nema17_motor(cfg: DriveConfig = DEFAULT_CONFIG) -> cq.Workplane:
    """NEMA 17 stepper: 42.3mm square × 48mm body with 5mm × 20mm shaft.

    Built so that the mounting face is at Z=0 and the body extends in -Z.
    The shaft extends in +Z from the mounting face.
    The shaft has a D-cut flat (4.5mm across) over the top 18mm.
    4× M3 threaded blind holes on the 31mm square bolt pattern.
    """
    m = cfg.motor
    shaft_r = m.shaft_dia / 2.0

    # Body: square prism extending in -Z
    body = (
        cq.Workplane("XY")
        .rect(m.body_width, m.body_width)
        .extrude(-m.body_length)
    )

    # Centering pilot / boss on the mounting face
    pilot = (
        cq.Workplane("XY")
        .circle(m.pilot_dia / 2.0)
        .extrude(2.0)  # typical 2mm boss height
    )

    # Shaft: full 5mm round base section (bottom 2mm), then D-cut section
    round_length = m.shaft_length - m.shaft_dcut_length  # 2mm round base
    shaft_round = (
        cq.Workplane("XY")
        .circle(shaft_r)
        .extrude(round_length)
    )

    # D-cut section: 5mm circle intersected with a half-space to create the flat
    # The flat is at distance dcut_flat/2 from center, cutting the +Y side
    dcut_offset = m.shaft_dcut_flat / 2.0  # 2.25mm from center
    shaft_dcut = (
        cq.Workplane("XY")
        .workplane(offset=round_length)
        .circle(shaft_r)
        .extrude(m.shaft_dcut_length)
    )
    # Cut block to create the D-flat: remove material beyond the flat
    cut_depth = shaft_r - dcut_offset  # 2.5 - 2.25 = 0.25mm
    cut_block = (
        cq.Workplane("XY")
        .workplane(offset=round_length)
        .transformed(offset=(0, shaft_r - cut_depth / 2.0, 0))
        .rect(m.shaft_dia, cut_depth)
        .extrude(m.shaft_dcut_length)
    )
    shaft_dcut = shaft_dcut.cut(cut_block)

    result = body.union(pilot).union(shaft_round).union(shaft_dcut)

    # M3 threaded blind holes on 31mm square bolt pattern (into mounting face)
    # Holes go from Z=0 into -Z (into the body)
    half_pat = m.bolt_pattern_square / 2.0
    bolt_positions = [
        (half_pat, half_pat),
        (-half_pat, half_pat),
        (-half_pat, -half_pat),
        (half_pat, -half_pat),
    ]
    holes = (
        cq.Workplane("XY")
        .pushPoints(bolt_positions)
        .circle(m.bolt_dia / 2.0)
        .extrude(-m.bolt_hole_depth)
    )
    result = result.cut(holes)

    return result


# -------------------------------------------------------------------
# Shaft coupler — simple cylinder
# -------------------------------------------------------------------


def build_coupler(cfg: DriveConfig = DEFAULT_CONFIG) -> cq.Workplane:
    """Flexible jaw coupler: 19mm OD × 25mm, 5mm bore."""
    c = cfg.coupler
    return (
        cq.Workplane("XY")
        .circle(c.od / 2.0)
        .circle(c.bore / 2.0)
        .extrude(c.length)
    )


# -------------------------------------------------------------------
# Ring pins — 21 cylinders on 108mm circle
# -------------------------------------------------------------------


def build_ring_pins(cfg: DriveConfig = DEFAULT_CONFIG) -> cq.Workplane:
    """21× 4mm × 30mm ring pins on the 108mm pin circle."""
    g = cfg.gear
    r = g.ring_pin_circle_dia / 2.0
    positions = [
        (
            r * math.cos(2 * math.pi * i / g.num_ring_pins),
            r * math.sin(2 * math.pi * i / g.num_ring_pins),
        )
        for i in range(g.num_ring_pins)
    ]
    return (
        cq.Workplane("XY")
        .pushPoints(positions)
        .circle(g.ring_pin_dia / 2.0)
        .extrude(g.ring_pin_length)
    )


# -------------------------------------------------------------------
# Output pins — 4 cylinders on 60mm circle
# -------------------------------------------------------------------


def build_output_pins(cfg: DriveConfig = DEFAULT_CONFIG) -> cq.Workplane:
    """4× M3 shoulder bolts on the 60mm output pin circle.

    Actual bolt: 7mm head, 4mm × 45mm shoulder, M3×0.5 × 6mm thread.
    Head bears on hub output face, shoulder passes through hub (20mm) +
    disc zone (24mm), M3 thread pokes out for a nut.
    Total length: 54.5mm.
    """
    d = cfg.disc
    r = d.output_pin_circle_dia / 2.0
    shoulder_length = 45.0  # mm, actual bolt shoulder length
    thread_length = 6.0  # mm, actual M3 thread length
    positions = [
        (
            r * math.cos(2 * math.pi * i / d.output_pin_count),
            r * math.sin(2 * math.pi * i / d.output_pin_count),
        )
        for i in range(d.output_pin_count)
    ]
    # Shoulder section (4mm)
    shoulder = (
        cq.Workplane("XY")
        .pushPoints(positions)
        .circle(d.output_pin_dia / 2.0)
        .extrude(shoulder_length)
    )
    # Threaded section (2.5mm, stepped down from shoulder)
    thread = (
        cq.Workplane("XY")
        .workplane(offset=shoulder_length)
        .pushPoints(positions)
        .circle(2.5 / 2.0)
        .extrude(thread_length)
    )
    return shoulder.union(thread)


if __name__ == "__main__":
    from ocp_vscode import show_object

    show_object(build_bearing_6003(), name="bearing_6003")
    show_object(build_bearing_6814(), name="bearing_6814")
    show_object(build_bearing_625(), name="bearing_625")
    show_object(build_nema17_motor(), name="nema17_motor")
    show_object(build_coupler(), name="coupler")
    show_object(build_ring_pins(), name="ring_pins")
    show_object(build_output_pins(), name="output_pins")
