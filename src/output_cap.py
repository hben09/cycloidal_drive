"""Output cap — closes the output end of the housing, retains 6814 bearings.

3D-printed PETG housing part.  Sits at global Z=57mm (z_output_cap) to
Z=60mm (total_housing_depth).  Local Z=0 is the inner face (bearing-facing
side).

Features:
  - Central bore clears the output hub (rotating, ~70mm OD)
  - Annular inner face retains 6814 outer races (90mm) — the bearing can't
    pass through the ~70mm bore
  - 8× M4 housing-bolt through-holes on 125mm circle (matching motor plate
    and ring gear body)

The output hub spins freely through the center bore.  The eccentric shaft
output stub and 625 bearing are entirely contained within the output hub,
so no shaft bore or bearing pocket is needed here.
"""

import math
import sys
import os

import cadquery as cq

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.params import DriveConfig, DEFAULT_CONFIG, compute_housing_bolt_angles


def build_output_cap(cfg: DriveConfig = DEFAULT_CONFIG) -> cq.Workplane:
    """Build the output-side housing cap.

    Return a valid CadQuery Workplane with exactly one solid.
    """
    h = cfg.housing
    hub = cfg.output_hub
    tol = cfg.tolerances
    stack = cfg.stack_up

    # ── Dimensions ────────────────────────────────────────────────
    cap_thickness = stack.output_wall  # 3mm
    housing_r = h.od / 2.0  # 67mm

    # Center bore: clears the output hub with sliding fit
    hub_bore_dia = hub.od + tol.sliding_clearance_add  # 70.25mm

    # ── 1. Base disc ──────────────────────────────────────────────
    result = (
        cq.Workplane("XY")
        .circle(housing_r)
        .extrude(cap_thickness)
    )

    # ── 2. Center bore (through, clears output hub) ───────────────
    center_bore = (
        cq.Workplane("XY")
        .circle(hub_bore_dia / 2.0)
        .extrude(cap_thickness)
    )
    result = result.cut(center_bore)

    # ── 3. M4 housing bolt holes (through, clearance fit) ─────────
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
        .extrude(cap_thickness)
    )
    result = result.cut(bolt_holes)

    # ── 4. Hex nut pockets (outer face, Z = cap_thickness side) ─────
    # Each hex oriented with a flat facing radially outward to maximise
    # wall thickness toward the housing perimeter.
    nut_circ_dia = h.bolt_nut_af / math.cos(math.radians(30))  # ~8.31mm
    for angle, pt in zip(bolt_angles, bolt_pts):
        hex_pocket = (
            cq.Workplane("XY")
            .workplane(offset=cap_thickness - h.bolt_nut_depth)
            .center(pt[0], pt[1])
            .transformed(rotate=(0, 0, math.degrees(angle)))
            .polygon(6, nut_circ_dia)
            .extrude(h.bolt_nut_depth)
        )
        result = result.cut(hex_pocket)

    return result


if __name__ == "__main__":
    from ocp_vscode import show_object

    cap = build_output_cap()
    show_object(cap, name="output_cap", options={"color": "slategray", "alpha": 0.7})
