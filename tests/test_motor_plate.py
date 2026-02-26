"""Validation test suite for the motor plate geometry.

Tests cover:
  1. Dimensional checks — feature clearances, bolt patterns (no CadQuery)
  2. CadQuery solid — valid topology, bounding box, volume sanity
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


class TestMotorPlateDimensions:

    def test_motor_bolts_inside_housing(self):
        """M3 motor bolt positions must sit well inside the housing OD."""
        m = CFG.motor
        h = CFG.housing
        # Corner distance from center for 31mm square pattern
        bolt_corner_r = math.sqrt(2) * m.bolt_pattern_square / 2.0  # ~21.9mm
        bolt_hole_r = (m.bolt_dia + 0.4) / 2.0  # 1.7mm clearance radius
        outermost = bolt_corner_r + bolt_hole_r
        assert outermost < h.od / 2.0, (
            f"Motor bolt edge at {outermost:.1f}mm exceeds housing radius "
            f"{h.od / 2.0:.1f}mm"
        )

    def test_housing_bolts_inside_housing(self):
        """M4 housing bolt holes must not break through the OD."""
        h = CFG.housing
        bolt_r = h.bolt_circle_dia / 2.0
        hole_r = (h.bolt_dia + 0.4) / 2.0
        outermost = bolt_r + hole_r
        assert outermost < h.od / 2.0, (
            f"Housing bolt edge at {outermost:.1f}mm exceeds housing radius "
            f"{h.od / 2.0:.1f}mm"
        )

    def test_housing_bolts_have_wall_to_od(self):
        """Housing bolt holes must leave wall material to the OD."""
        h = CFG.housing
        bolt_r = h.bolt_circle_dia / 2.0
        hole_r = (h.bolt_dia + 0.4) / 2.0
        wall = h.od / 2.0 - (bolt_r + hole_r)
        assert wall >= 2.0, (
            f"Wall from bolt edge to OD = {wall:.1f}mm, need >= 2mm"
        )

    def test_counterbore_wall_to_od(self):
        """Counterbore must leave adequate wall to the housing OD."""
        h = CFG.housing
        bolt_r = h.bolt_circle_dia / 2.0
        cb_r = h.bolt_counterbore_dia / 2.0
        wall = h.od / 2.0 - (bolt_r + cb_r)
        assert wall >= 2.0, (
            f"Counterbore wall to OD = {wall:.2f}mm, need >= 2mm"
        )

    def test_counterbore_fits_in_plate(self):
        """Counterbore depth must be less than plate thickness."""
        h = CFG.housing
        stack = CFG.stack_up
        plate_t = stack.motor_plate_wall + stack.inp_bearing_seat
        assert h.bolt_counterbore_depth < plate_t, (
            f"Counterbore {h.bolt_counterbore_depth}mm >= plate {plate_t}mm"
        )

    def test_counterbore_clears_ring_pins(self):
        """Counterbore must not overlap with ring pin holes radially."""
        h = CFG.housing
        g = CFG.gear
        bolt_r = h.bolt_circle_dia / 2.0
        cb_r = h.bolt_counterbore_dia / 2.0
        pin_outer_r = g.ring_pin_circle_dia / 2.0 + g.ring_pin_dia / 2.0
        inner_edge = bolt_r - cb_r
        assert inner_edge > pin_outer_r, (
            f"Counterbore inner edge {inner_edge:.2f}mm <= pin outer {pin_outer_r:.2f}mm"
        )

    def test_pilot_recess_smaller_than_bore(self):
        """Motor pilot recess must be smaller than the housing bore."""
        m = CFG.motor
        h = CFG.housing
        tol = CFG.tolerances
        pilot_dia = m.pilot_dia + tol.mating_surface_add * 2  # 22.30mm
        assert pilot_dia < h.bore_dia, (
            f"Pilot recess {pilot_dia:.2f}mm >= housing bore {h.bore_dia}mm"
        )

    def test_shaft_bore_clears_motor_shaft(self):
        """Central bore must be larger than the motor shaft."""
        m = CFG.motor
        tol = CFG.tolerances
        shaft_bore = m.shaft_dia + tol.sliding_clearance_add * 2
        assert shaft_bore > m.shaft_dia, (
            f"Shaft bore {shaft_bore:.2f}mm <= motor shaft {m.shaft_dia}mm"
        )

    def test_motor_bolts_clear_of_pilot(self):
        """M3 bolt holes must not overlap with the pilot recess."""
        m = CFG.motor
        tol = CFG.tolerances
        half_pat = m.bolt_pattern_square / 2.0  # 15.5mm
        pilot_r = (m.pilot_dia + tol.mating_surface_add * 2) / 2.0  # 11.15mm
        bolt_hole_r = (m.bolt_dia + 0.4) / 2.0  # 1.7mm
        # Bolt center distance from axis
        bolt_center_r = half_pat  # 15.5mm (along X or Y axis)
        clearance = bolt_center_r - pilot_r - bolt_hole_r
        assert clearance > 0, (
            f"Motor bolt overlaps pilot recess, clearance = {clearance:.2f}mm"
        )

    def test_plate_thickness_matches_stackup(self):
        """Plate thickness must equal motor_plate_wall + bearing seat depth."""
        stack = CFG.stack_up
        expected = stack.motor_plate_wall + stack.inp_bearing_seat  # 10mm
        assert expected == 10.0, f"Plate thickness {expected}mm != 10mm"


# ===================================================================
# 2. CadQuery solid validation
# ===================================================================


class TestCadQuerySolid:

    @pytest.fixture(scope="class")
    def plate_solid(self):
        cq = pytest.importorskip("cadquery")
        from src.motor_plate import build_motor_plate

        return build_motor_plate()

    def test_solid_is_valid(self, plate_solid):
        """The built solid should be non-null and have exactly one solid."""
        solids = plate_solid.solids().vals()
        assert len(solids) == 1, f"Expected 1 solid, got {len(solids)}"

    def test_bounding_box_xy(self, plate_solid):
        """XY extent should be the housing OD (120mm)."""
        bb = plate_solid.val().BoundingBox()
        x_size = bb.xmax - bb.xmin
        y_size = bb.ymax - bb.ymin
        expected = CFG.housing.od  # 120mm

        assert abs(x_size - expected) < 0.2, (
            f"X extent {x_size:.2f}mm, expected {expected}mm"
        )
        assert abs(y_size - expected) < 0.2, (
            f"Y extent {y_size:.2f}mm, expected {expected}mm"
        )

    def test_bounding_box_z(self, plate_solid):
        """Z height should be 10mm (motor_plate_wall + bearing seat)."""
        bb = plate_solid.val().BoundingBox()
        z_size = bb.zmax - bb.zmin
        expected = CFG.stack_up.motor_plate_wall + CFG.stack_up.inp_bearing_seat

        assert abs(z_size - expected) < 0.1, (
            f"Z extent {z_size:.2f}mm, expected {expected:.2f}mm"
        )

    def test_volume_sanity(self, plate_solid):
        """Volume should be between reasonable bounds.

        Lower bound: solid disc minus generous hole allowance.
        Upper bound: solid disc (no holes).
        """
        h = CFG.housing
        stack = CFG.stack_up
        plate_t = stack.motor_plate_wall + stack.inp_bearing_seat

        full_disc_vol = math.pi * (h.od / 2.0) ** 2 * plate_t
        vol = plate_solid.val().Volume()

        # Plate with bolt holes only should be at least 90% of a solid disc
        assert vol > full_disc_vol * 0.90, (
            f"Volume {vol:.0f}mm³ too small, expected > {full_disc_vol * 0.90:.0f}"
        )
        assert vol < full_disc_vol, (
            f"Volume {vol:.0f}mm³ exceeds full disc {full_disc_vol:.0f}"
        )
