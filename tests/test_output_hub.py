"""Validation test suite for the output hub geometry.

Tests cover:
  1. Dimensional checks — clearances, fit relationships, hole spacing (no CadQuery)
  2. CadQuery solid — valid topology, bounding box, volume
"""

import math
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.params import DEFAULT_CONFIG

CFG = DEFAULT_CONFIG


# ===================================================================
# 1. Dimensional checks (no CadQuery needed)
# ===================================================================


class TestOutputHubDimensions:

    def test_hub_od_fits_bearing_bore(self):
        """Hub OD (with tolerance) must be <= 6814 bearing bore."""
        hub = CFG.output_hub
        b = CFG.bearings
        tol = CFG.tolerances
        hub_od = hub.od - tol.bearing_inner_shaft_sub  # 69.925mm
        assert hub_od <= b.out_bore, (
            f"Hub OD {hub_od}mm > bearing bore {b.out_bore}mm"
        )

    def test_hub_od_is_light_press(self):
        """Hub OD should be within 0.2mm of bearing bore (light press)."""
        hub = CFG.output_hub
        b = CFG.bearings
        tol = CFG.tolerances
        hub_od = hub.od - tol.bearing_inner_shaft_sub
        gap = b.out_bore - hub_od
        assert gap < 0.2, (
            f"Hub-to-bearing gap {gap:.3f}mm too large for light press"
        )

    def test_hub_height_matches_bearing_stack(self):
        """Hub height must equal output bearing total (20mm)."""
        stack = CFG.stack_up
        assert stack.output_bearing_total == CFG.bearings.out_width * CFG.bearings.out_qty, (
            f"Output bearing total {stack.output_bearing_total}mm != "
            f"{CFG.bearings.out_width}mm × {CFG.bearings.out_qty}"
        )

    def test_shaft_bore_clears_spine(self):
        """Shaft clearance bore must be larger than eccentric shaft spine."""
        hub = CFG.output_hub
        s = CFG.shaft
        clearance = hub.shaft_clearance_bore - s.spine_od
        assert clearance > 0, (
            f"Shaft bore {hub.shaft_clearance_bore}mm <= spine OD {s.spine_od}mm"
        )
        assert clearance >= 0.2, (
            f"Shaft clearance {clearance}mm too tight (need >= 0.2mm)"
        )

    def test_625_pocket_clears_shaft_bore(self):
        """625 bearing pocket must be larger than shaft clearance bore."""
        hub = CFG.output_hub
        b = CFG.bearings
        tol = CFG.tolerances
        pocket_dia = b.inp_od + tol.bearing_seat_bore_add  # 16.075mm
        assert pocket_dia > hub.shaft_clearance_bore, (
            f"625 pocket {pocket_dia}mm <= shaft bore {hub.shaft_clearance_bore}mm"
        )

    def test_625_pocket_inside_hub(self):
        """625 bearing pocket must fit well within the hub OD."""
        hub = CFG.output_hub
        b = CFG.bearings
        tol = CFG.tolerances
        pocket_r = (b.inp_od + tol.bearing_seat_bore_add) / 2.0
        hub_r = (hub.od - tol.bearing_inner_shaft_sub) / 2.0
        wall = hub_r - pocket_r
        assert wall >= 5.0, (
            f"Wall from 625 pocket to hub OD = {wall:.2f}mm, need >= 5mm"
        )

    def test_output_pin_holes_inside_hub(self):
        """Output pin hole outer edges must not breach the hub OD."""
        d = CFG.disc
        hub = CFG.output_hub
        tol = CFG.tolerances
        pin_outer = d.output_pin_circle_dia / 2.0 + d.output_pin_dia / 2.0
        hub_r = (hub.od - tol.bearing_inner_shaft_sub) / 2.0
        assert pin_outer < hub_r, (
            f"Output pin edge at {pin_outer}mm >= hub radius {hub_r:.3f}mm"
        )

    def test_output_pin_holes_clear_625_pocket(self):
        """Output pin holes must not overlap the 625 bearing pocket."""
        d = CFG.disc
        b = CFG.bearings
        tol = CFG.tolerances
        pin_inner = d.output_pin_circle_dia / 2.0 - d.output_pin_dia / 2.0
        pocket_r = (b.inp_od + tol.bearing_seat_bore_add) / 2.0
        wall = pin_inner - pocket_r
        assert wall >= 2.0, (
            f"Pin hole to 625 pocket wall = {wall:.2f}mm, need >= 2mm"
        )

    def test_arm_mount_holes_inside_hub(self):
        """Arm mount hole outer edges must not breach the hub OD."""
        hub = CFG.output_hub
        tol = CFG.tolerances
        arm_outer = hub.arm_mount_bolt_circle_dia / 2.0 + hub.arm_mount_bolt_dia / 2.0
        hub_r = (hub.od - tol.bearing_inner_shaft_sub) / 2.0
        assert arm_outer < hub_r, (
            f"Arm mount edge at {arm_outer}mm >= hub radius {hub_r:.3f}mm"
        )

    def test_arm_mount_holes_clear_shaft_bore(self):
        """Arm mount holes must not overlap the central shaft bore."""
        hub = CFG.output_hub
        arm_inner = hub.arm_mount_bolt_circle_dia / 2.0 - hub.arm_mount_bolt_dia / 2.0
        shaft_r = hub.shaft_clearance_bore / 2.0
        wall = arm_inner - shaft_r
        assert wall >= 2.0, (
            f"Arm mount to shaft bore wall = {wall:.2f}mm, need >= 2mm"
        )

    def test_output_pins_clear_arm_mounts(self):
        """Output pin holes and arm mount holes (45° offset) must not overlap."""
        d = CFG.disc
        hub = CFG.output_hub
        pin_r = d.output_pin_circle_dia / 2.0  # 30mm
        arm_r = hub.arm_mount_bolt_circle_dia / 2.0  # 25mm
        pin_hole_r = d.output_pin_dia / 2.0  # 2mm
        arm_hole_r = hub.arm_mount_bolt_dia / 2.0  # 2.2mm
        min_distance = pin_hole_r + arm_hole_r  # 4.2mm

        # Closest pair: a pin at 0° and an arm mount at 45°
        angle_sep = math.pi / 4.0
        dist = math.sqrt(
            pin_r ** 2 + arm_r ** 2
            - 2 * pin_r * arm_r * math.cos(angle_sep)
        )
        assert dist >= min_distance, (
            f"Closest pin-to-arm-mount distance {dist:.2f}mm < "
            f"min {min_distance:.2f}mm"
        )

    def test_output_pin_holes_clear_bearing_bore(self):
        """Output pin holes must sit inside the 6814 bearing bore.

        The pins pass through the hub, which sits inside the bearing.
        Pin outer edges must not extend past the bearing bore.
        """
        d = CFG.disc
        b = CFG.bearings
        pin_outer = d.output_pin_circle_dia / 2.0 + d.output_pin_dia / 2.0
        bearing_bore_r = b.out_bore / 2.0
        assert pin_outer < bearing_bore_r, (
            f"Pin edge at {pin_outer}mm >= bearing bore radius {bearing_bore_r}mm"
        )


# ===================================================================
# 2. CadQuery solid validation
# ===================================================================


class TestCadQuerySolid:

    @pytest.fixture(scope="class")
    def hub_solid(self):
        cq = pytest.importorskip("cadquery")
        from src.output_hub import build_output_hub

        return build_output_hub()

    def test_solid_is_valid(self, hub_solid):
        """The built solid should be non-null and have exactly one solid."""
        solids = hub_solid.solids().vals()
        assert len(solids) == 1, f"Expected 1 solid, got {len(solids)}"
        assert solids[0].isValid(), "Solid is not valid"

    def test_outer_diameter(self, hub_solid):
        """XY extent should match hub OD (69.925mm)."""
        bb = hub_solid.val().BoundingBox()
        x_size = bb.xmax - bb.xmin
        y_size = bb.ymax - bb.ymin
        hub = CFG.output_hub
        tol = CFG.tolerances
        expected = hub.od - tol.bearing_inner_shaft_sub  # 69.925mm

        assert abs(x_size - expected) < 0.2, (
            f"X extent {x_size:.2f}mm, expected {expected}mm"
        )
        assert abs(y_size - expected) < 0.2, (
            f"Y extent {y_size:.2f}mm, expected {expected}mm"
        )

    def test_height(self, hub_solid):
        """Z height should match output bearing total (20mm)."""
        bb = hub_solid.val().BoundingBox()
        z_size = bb.zmax - bb.zmin
        expected = CFG.stack_up.output_bearing_total  # 20mm

        assert abs(z_size - expected) < 0.1, (
            f"Z extent {z_size:.2f}mm, expected {expected:.2f}mm"
        )

    def test_volume_sanity(self, hub_solid):
        """Volume should be between reasonable bounds.

        Lower bound: solid cylinder minus all holes and pockets.
        Upper bound: solid cylinder minus only shaft bore.
        """
        hub = CFG.output_hub
        d = CFG.disc
        b = CFG.bearings
        tol = CFG.tolerances
        stack = CFG.stack_up

        hub_r = (hub.od - tol.bearing_inner_shaft_sub) / 2.0
        height = stack.output_bearing_total
        shaft_r = hub.shaft_clearance_bore / 2.0

        # Upper: full cylinder minus shaft bore only
        upper = math.pi * hub_r ** 2 * height - math.pi * shaft_r ** 2 * height

        # Lower: subtract all features generously
        pocket_r = (b.inp_od + tol.bearing_seat_bore_add) / 2.0
        pocket_vol = math.pi * pocket_r ** 2 * b.inp_width
        pin_vol = d.output_pin_count * math.pi * (d.output_pin_dia / 2.0) ** 2 * height
        arm_vol = (
            hub.arm_mount_bolt_count
            * math.pi
            * (hub.arm_mount_bolt_dia / 2.0) ** 2
            * height
        )
        lower = (
            math.pi * hub_r ** 2 * height
            - math.pi * shaft_r ** 2 * height
            - pocket_vol
            - pin_vol
            - arm_vol
        ) * 0.9  # 10% margin for overlap

        vol = hub_solid.val().Volume()
        assert vol > lower, f"Volume {vol:.0f}mm³ below lower bound {lower:.0f}"
        assert vol < upper, f"Volume {vol:.0f}mm³ above upper bound {upper:.0f}"
