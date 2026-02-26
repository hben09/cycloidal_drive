"""Validation test suite for the output cap geometry.

Tests cover:
  1. Dimensional checks — bearing retention, hub clearance, bolt layout (no CadQuery)
  2. CadQuery solid — valid topology, bounding box, volume
"""

import math
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.params import DEFAULT_CONFIG, compute_housing_bolt_angles

CFG = DEFAULT_CONFIG


# ===================================================================
# 1. Dimensional checks (no CadQuery needed)
# ===================================================================


class TestOutputCapDimensions:

    def test_center_bore_clears_output_hub(self):
        """Center bore must be larger than the output hub OD."""
        hub = CFG.output_hub
        tol = CFG.tolerances
        bore_dia = hub.od + tol.sliding_clearance_add  # 70.25mm
        hub_od = hub.od - tol.bearing_inner_shaft_sub  # 69.925mm
        clearance = bore_dia - hub_od
        assert clearance > 0, (
            f"Cap bore {bore_dia}mm <= hub OD {hub_od}mm"
        )

    def test_center_bore_blocks_6814_outer_race(self):
        """Center bore must be smaller than 6814 outer race OD for retention."""
        hub = CFG.output_hub
        b = CFG.bearings
        tol = CFG.tolerances
        bore_dia = hub.od + tol.sliding_clearance_add  # 70.25mm
        assert bore_dia < b.out_od, (
            f"Cap bore {bore_dia}mm >= 6814 OD {b.out_od}mm — bearings not retained"
        )

    def test_center_bore_blocks_bearing_seat(self):
        """Center bore must be smaller than the bearing seat bore in ring gear body."""
        hub = CFG.output_hub
        h = CFG.housing
        tol = CFG.tolerances
        bore_dia = hub.od + tol.sliding_clearance_add  # 70.25mm
        assert bore_dia < h.output_bearing_seat_dia, (
            f"Cap bore {bore_dia}mm >= bearing seat {h.output_bearing_seat_dia}mm"
        )

    def test_cap_od_matches_housing(self):
        """Cap OD must match the housing OD."""
        h = CFG.housing
        assert h.od == 140.0, f"Housing OD {h.od}mm != 140mm"

    def test_cap_thickness(self):
        """Cap thickness must equal the output wall from the stack-up."""
        stack = CFG.stack_up
        assert stack.output_wall == 8.0, (
            f"Output wall {stack.output_wall}mm != 8mm"
        )

    def test_nut_pocket_fits_in_cap(self):
        """Nut pocket depth must be less than cap thickness."""
        h = CFG.housing
        stack = CFG.stack_up
        assert h.bolt_nut_depth < stack.output_wall, (
            f"Nut pocket {h.bolt_nut_depth}mm >= cap thickness {stack.output_wall}mm"
        )

    def test_nut_pocket_floor_thickness(self):
        """Floor under nut pocket must be at least 2mm for PETG."""
        h = CFG.housing
        stack = CFG.stack_up
        floor = stack.output_wall - h.bolt_nut_depth
        assert floor >= 2.0, (
            f"Nut pocket floor {floor:.1f}mm < 2mm"
        )

    def test_nut_pocket_wall_to_od(self):
        """Hex nut pocket must leave adequate wall to housing OD."""
        h = CFG.housing
        bolt_r = h.bolt_circle_dia / 2.0
        nut_circ_r = (h.bolt_nut_af / 2.0) / math.cos(math.radians(30))
        wall = h.od / 2.0 - (bolt_r + nut_circ_r)
        assert wall >= 2.0, (
            f"Nut pocket wall to OD = {wall:.2f}mm, need >= 2mm"
        )

    def test_bolt_count_matches_housing(self):
        """Cap must have the same number of housing bolts as the other pieces."""
        bolt_angles = compute_housing_bolt_angles(CFG)
        assert len(bolt_angles) == CFG.housing.bolt_count, (
            f"Got {len(bolt_angles)} bolt angles, expected {CFG.housing.bolt_count}"
        )

    def test_bolt_holes_inside_cap(self):
        """All bolt holes must sit within the cap annulus (between bore and OD)."""
        h = CFG.housing
        hub = CFG.output_hub
        tol = CFG.tolerances
        bore_r = (hub.od + tol.sliding_clearance_add) / 2.0
        housing_r = h.od / 2.0
        bolt_r = h.bolt_circle_dia / 2.0
        bolt_hole_r = (h.bolt_dia + 0.4) / 2.0  # M4 clearance

        # Inner edge of bolt holes must clear the center bore
        inner_edge = bolt_r - bolt_hole_r
        assert inner_edge > bore_r, (
            f"Bolt hole inner edge {inner_edge:.2f}mm <= bore radius {bore_r:.3f}mm"
        )

        # Outer edge of bolt holes must fit within cap OD
        outer_edge = bolt_r + bolt_hole_r
        assert outer_edge < housing_r, (
            f"Bolt hole outer edge {outer_edge:.2f}mm >= housing radius {housing_r}mm"
        )

    def test_retention_shoulder_width(self):
        """The annular face retaining the bearings must be wide enough.

        The shoulder is the ring from the center bore to the bearing seat.
        """
        hub = CFG.output_hub
        h = CFG.housing
        tol = CFG.tolerances
        bore_r = (hub.od + tol.sliding_clearance_add) / 2.0  # 35.125mm
        seat_r = h.output_bearing_seat_dia / 2.0  # 45.075mm
        shoulder = seat_r - bore_r
        assert shoulder >= 5.0, (
            f"Bearing retention shoulder {shoulder:.2f}mm, need >= 5mm"
        )


# ===================================================================
# 2. CadQuery solid validation
# ===================================================================


class TestCadQuerySolid:

    @pytest.fixture(scope="class")
    def cap_solid(self):
        cq = pytest.importorskip("cadquery")
        from src.output_cap import build_output_cap

        return build_output_cap()

    def test_solid_is_valid(self, cap_solid):
        """The built solid should be non-null and have exactly one solid."""
        solids = cap_solid.solids().vals()
        assert len(solids) == 1, f"Expected 1 solid, got {len(solids)}"
        assert solids[0].isValid(), "Solid is not valid"

    def test_outer_diameter(self, cap_solid):
        """XY extent should match housing OD (134mm)."""
        bb = cap_solid.val().BoundingBox()
        x_size = bb.xmax - bb.xmin
        y_size = bb.ymax - bb.ymin
        expected = CFG.housing.od  # 134mm

        assert abs(x_size - expected) < 0.2, (
            f"X extent {x_size:.2f}mm, expected {expected}mm"
        )
        assert abs(y_size - expected) < 0.2, (
            f"Y extent {y_size:.2f}mm, expected {expected}mm"
        )

    def test_height(self, cap_solid):
        """Z height should match output wall (3mm)."""
        bb = cap_solid.val().BoundingBox()
        z_size = bb.zmax - bb.zmin
        expected = CFG.stack_up.output_wall  # 3mm

        assert abs(z_size - expected) < 0.1, (
            f"Z extent {z_size:.2f}mm, expected {expected:.2f}mm"
        )

    def test_volume_sanity(self, cap_solid):
        """Volume should be between reasonable bounds.

        Lower bound: annulus (cap OD minus bore) minus all bolt holes.
        Upper bound: annulus with no bolt holes.
        """
        h = CFG.housing
        hub = CFG.output_hub
        tol = CFG.tolerances
        stack = CFG.stack_up

        housing_r = h.od / 2.0
        bore_r = (hub.od + tol.sliding_clearance_add) / 2.0
        thickness = stack.output_wall

        # Upper: annulus only
        upper = math.pi * (housing_r ** 2 - bore_r ** 2) * thickness

        # Lower: subtract bolt holes generously
        bolt_hole_r = (h.bolt_dia + 0.4) / 2.0
        bolt_vol = h.bolt_count * math.pi * bolt_hole_r ** 2 * thickness
        lower = (upper - bolt_vol) * 0.9  # 10% margin

        vol = cap_solid.val().Volume()
        assert vol > lower, f"Volume {vol:.0f}mm³ below lower bound {lower:.0f}"
        assert vol < upper, f"Volume {vol:.0f}mm³ above upper bound {upper:.0f}"
