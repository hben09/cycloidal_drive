"""Cycloidal disc model — the core part of the drive.

Both discs are geometrically identical. The 180-degree phase offset
is handled in the assembly by rotating one disc, not by changing
the part geometry.
"""

import math
import sys
import os
import cadquery as cq

# Allow running directly or as a module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.params import DriveConfig, DEFAULT_CONFIG
from src.profiles import compute_epitrochoid


def build_cycloidal_disc(cfg: DriveConfig = DEFAULT_CONFIG) -> cq.Workplane:
    """Build a single cycloidal disc with center bore and output pin holes."""
    gear = cfg.gear
    disc = cfg.disc
    profile_cfg = cfg.profile

    # Generate epitrochoid profile points
    points = compute_epitrochoid(
        R=gear.ring_pin_circle_radius,
        r=gear.ring_pin_radius,
        N=gear.num_ring_pins,
        e=gear.eccentricity,
        num_points=profile_cfg.num_points,
    )

    # Build disc from spline profile using OCC-level periodic spline
    # for exact interpolation of lobe peaks
    pts_3d = [cq.Vector(x, y, 0) for x, y in points]
    edge = cq.Edge.makeSpline(pts_3d, periodic=True)
    wire = cq.Wire.assembleEdges([edge])
    face = cq.Face.makeFromWires(wire)
    solid = cq.Solid.extrudeLinear(face, cq.Vector(0, 0, disc.thickness))
    result = cq.Workplane("XY").add(solid)

    # Center bore for 6003 bearing
    result = result.faces(">Z").workplane().hole(disc.center_bore_dia)

    # Output pin holes: 4x equally spaced on 60mm circle
    pin_hole_r = disc.output_pin_circle_dia / 2.0
    pin_positions = [
        (
            pin_hole_r * math.cos(math.radians(i * 360 / disc.output_pin_count)),
            pin_hole_r * math.sin(math.radians(i * 360 / disc.output_pin_count)),
        )
        for i in range(disc.output_pin_count)
    ]
    result = (
        result.faces(">Z")
        .workplane()
        .pushPoints(pin_positions)
        .hole(disc.output_pin_hole_dia)
    )

    return result


if __name__ == "__main__":
    from ocp_vscode import show_object

    disc = build_cycloidal_disc()
    show_object(disc, name="cycloidal_disc")
