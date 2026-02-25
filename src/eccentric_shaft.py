"""Eccentric shaft — converts motor rotation into disc wobble.

Machined steel or aluminum. Two 17mm OD lobes offset 180° from each
other (one per disc), connected by a 5mm OD spine. The lobe centers
are offset ±eccentricity from the shaft axis.
"""

import sys
import os

import cadquery as cq

# Allow running directly or as a module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.params import DriveConfig, DEFAULT_CONFIG


def build_eccentric_shaft(cfg: DriveConfig = DEFAULT_CONFIG) -> cq.Workplane:
    """Build the eccentric shaft with two offset lobes and a central spine."""
    shaft = cfg.shaft
    stack = cfg.stack_up
    disc_t = cfg.disc.thickness

    e = shaft.eccentricity
    lobe_r = shaft.bearing_seat_od / 2.0
    spine_r = shaft.spine_od / 2.0

    # Z positions from stack-up
    z_start = stack.z_motor_plate_inner - stack.inp_bearing_seat - shaft.input_stub_length  # 3mm
    z_lobe1 = stack.z_disc1  # 13mm
    z_lobe2 = stack.z_disc2  # 25mm
    z_end = z_lobe2 + disc_t + shaft.output_stub_length  # 42mm
    total_length = z_end - z_start

    # Spine: full-length 5mm OD cylinder on the shaft axis
    spine = (
        cq.Workplane("XY")
        .workplane(offset=z_start)
        .circle(spine_r)
        .extrude(total_length)
    )

    # Lobe 1: 17mm OD, center offset +e in X
    lobe1 = (
        cq.Workplane("XY")
        .workplane(offset=z_lobe1)
        .center(e, 0)
        .circle(lobe_r)
        .extrude(disc_t)
    )

    # Lobe 2: 17mm OD, center offset -e in X (180° from lobe 1)
    lobe2 = (
        cq.Workplane("XY")
        .workplane(offset=z_lobe2)
        .center(-e, 0)
        .circle(lobe_r)
        .extrude(disc_t)
    )

    result = spine.union(lobe1).union(lobe2)
    return result


if __name__ == "__main__":
    from ocp_vscode import show_object

    shaft = build_eccentric_shaft()
    show_object(shaft, name="eccentric_shaft")
