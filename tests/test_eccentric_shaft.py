"""Validation test suite for the eccentric shaft geometry.

Tests cover:
  1. Dimensional checks — thin wall, lobe offsets, bearing fits, D-bore (no CadQuery)
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


class TestShaftDimensions:

    def test_thin_wall_minimum(self):
        """Thin-side wall between spine corridor and lobe surface must be >= 4mm.

        Thin wall = lobe_radius - spine_radius - eccentricity.
        Spec Section 1.4 says 4.5mm.
        """
        shaft = CFG.shaft
        lobe_r = shaft.bearing_seat_od / 2.0  # 8.5
        spine_r = shaft.spine_od / 2.0  # 2.5
        thin_wall = lobe_r - spine_r - shaft.eccentricity
        assert thin_wall >= 4.0, (
            f"Thin-side wall = {thin_wall:.2f}mm, need >= 4mm"
        )

    def test_lobes_180_degrees_apart(self):
        """Lobe offsets must be exactly opposite (+e vs -e).

        This is enforced by the build function using +e and -e,
        but we verify the eccentricity value is consistent.
        """
        assert CFG.shaft.eccentricity == CFG.gear.eccentricity, (
            f"Shaft eccentricity {CFG.shaft.eccentricity} != "
            f"gear eccentricity {CFG.gear.eccentricity}"
        )

    def test_lobe_fits_in_6003_bearing(self):
        """Lobe OD (17.10mm) must be >= 6003 bearing bore (17mm) for a light press."""
        assert CFG.shaft.bearing_seat_od >= CFG.bearings.ecc_bore, (
            f"Lobe OD {CFG.shaft.bearing_seat_od}mm < "
            f"6003 bore {CFG.bearings.ecc_bore}mm"
        )
        assert CFG.shaft.bearing_seat_od - CFG.bearings.ecc_bore <= 0.2, (
            f"Lobe OD {CFG.shaft.bearing_seat_od}mm exceeds "
            f"6003 bore {CFG.bearings.ecc_bore}mm by more than 0.2mm"
        )

    def test_shaft_spans_both_discs(self):
        """Shaft Z range must cover both disc positions from StackUp."""
        stack = CFG.stack_up
        shaft = CFG.shaft
        disc_t = CFG.disc.thickness

        z_start = stack.z_motor_plate_inner  # 10mm
        z_end = stack.z_disc2 + disc_t + shaft.output_stub_length  # 42mm

        # Shaft must start before disc 1 and end after disc 2
        assert z_start < stack.z_disc1, (
            f"Shaft starts at Z={z_start}mm, disc 1 starts at Z={stack.z_disc1}mm"
        )
        assert z_end > stack.z_disc2 + disc_t, (
            f"Shaft ends at Z={z_end}mm, disc 2 ends at Z={stack.z_disc2 + disc_t}mm"
        )

    def test_lobe_engulfs_spine(self):
        """Lobe radius must exceed eccentricity + spine radius for a watertight union."""
        shaft = CFG.shaft
        lobe_r = shaft.bearing_seat_od / 2.0
        spine_r = shaft.spine_od / 2.0
        assert lobe_r > shaft.eccentricity + spine_r, (
            f"Lobe radius {lobe_r}mm <= eccentricity {shaft.eccentricity}mm + "
            f"spine radius {spine_r}mm — union will have a gap"
        )


class TestDBore:
    """Checks for the direct D-shaft engagement bore."""

    def test_collar_contains_bore(self):
        """Input collar must have wall around the D-bore."""
        shaft = CFG.shaft
        tol = CFG.tolerances
        bore_r = (shaft.d_bore_dia + tol.sliding_clearance_add * 2) / 2.0
        collar_r = shaft.input_collar_od / 2.0
        wall = collar_r - bore_r
        assert wall >= 1.5, (
            f"Collar wall around D-bore = {wall:.2f}mm, need >= 1.5mm"
        )

    def test_bore_does_not_break_lobe_thin_side(self):
        """D-bore must not break through the lobe on its thin side.

        The lobe center is offset by eccentricity from shaft axis.
        The D-bore is centered on the shaft axis. On the thin side,
        the wall = lobe_radius - eccentricity - bore_radius.
        """
        shaft = CFG.shaft
        tol = CFG.tolerances
        lobe_r = shaft.bearing_seat_od / 2.0  # 8.55mm
        bore_r = (shaft.d_bore_dia + tol.sliding_clearance_add * 2) / 2.0  # 2.75mm
        e = shaft.eccentricity  # 1.5mm
        thin_wall = lobe_r - e - bore_r
        assert thin_wall >= 2.0, (
            f"Lobe thin-side wall around D-bore = {thin_wall:.2f}mm, need >= 2mm"
        )

    def test_bore_matches_motor_shaft(self):
        """D-bore diameter must accommodate the motor shaft."""
        shaft = CFG.shaft
        tol = CFG.tolerances
        bore_dia = shaft.d_bore_dia + tol.sliding_clearance_add * 2
        assert bore_dia > CFG.motor.shaft_dia, (
            f"D-bore {bore_dia:.2f}mm <= motor shaft {CFG.motor.shaft_dia}mm"
        )

    def test_bore_depth_gives_adequate_engagement(self):
        """D-bore must provide at least 8mm of motor shaft engagement."""
        assert CFG.shaft.d_bore_depth >= 8.0, (
            f"D-bore depth {CFG.shaft.d_bore_depth}mm < 8mm minimum engagement"
        )


# ===================================================================
# 2. CadQuery solid validation
# ===================================================================


class TestCadQuerySolid:

    @pytest.fixture(scope="class")
    def shaft_solid(self):
        cq = pytest.importorskip("cadquery")
        from src.eccentric_shaft import build_eccentric_shaft

        return build_eccentric_shaft()

    def test_solid_is_valid(self, shaft_solid):
        """The built solid should be non-null and have exactly one solid."""
        solids = shaft_solid.solids().vals()
        assert len(solids) == 1, f"Expected 1 solid, got {len(solids)}"

    def test_bounding_box_z(self, shaft_solid):
        """Z height should match the computed shaft length."""
        stack = CFG.stack_up
        shaft = CFG.shaft
        disc_t = CFG.disc.thickness

        z_start = stack.z_motor_plate_inner
        z_end = stack.z_disc2 + disc_t + shaft.output_stub_length
        expected_length = z_end - z_start  # 32mm

        bb = shaft_solid.val().BoundingBox()
        z_size = bb.zmax - bb.zmin
        assert abs(z_size - expected_length) < 0.1, (
            f"Z extent {z_size:.2f}mm, expected {expected_length:.2f}mm"
        )

    def test_bounding_box_xy(self, shaft_solid):
        """XY extent should reflect 17.10mm lobe + eccentricity offset.

        The max X extent is lobe_radius + eccentricity on one side (thick side)
        and lobe_radius - eccentricity on the other, but since both lobes
        are at opposite offsets, total X span = 2 * (lobe_r + e).
        Y extent = 2 * lobe_r (lobes are symmetric in Y).
        """
        shaft = CFG.shaft
        lobe_r = shaft.bearing_seat_od / 2.0
        e = shaft.eccentricity

        bb = shaft_solid.val().BoundingBox()
        x_size = bb.xmax - bb.xmin
        y_size = bb.ymax - bb.ymin

        expected_x = 2 * (lobe_r + e)  # 2 * (8.55 + 1.5) = 20.10mm
        expected_y = 2 * lobe_r  # 17.10mm

        assert abs(x_size - expected_x) < 0.1, (
            f"X extent {x_size:.2f}mm, expected {expected_x:.2f}mm"
        )
        assert abs(y_size - expected_y) < 0.1, (
            f"Y extent {y_size:.2f}mm, expected {expected_y:.2f}mm"
        )

    def test_volume_sanity(self, shaft_solid):
        """Volume should be between reasonable bounds.

        Lower bound: just the spine cylinder (no lobes, no collar).
        Upper bound: a full 17.10mm OD cylinder spanning the whole length.
        """
        shaft = CFG.shaft
        stack = CFG.stack_up
        disc_t = CFG.disc.thickness

        lobe_r = shaft.bearing_seat_od / 2.0
        spine_r = shaft.spine_od / 2.0
        z_start = stack.z_motor_plate_inner
        z_end = stack.z_disc2 + disc_t + shaft.output_stub_length
        total_length = z_end - z_start

        vol = shaft_solid.val().Volume()

        lower = math.pi * spine_r**2 * total_length
        upper = math.pi * lobe_r**2 * total_length

        assert lower < vol < upper, (
            f"Volume {vol:.0f}mm³ outside expected range [{lower:.0f}, {upper:.0f}]"
        )
