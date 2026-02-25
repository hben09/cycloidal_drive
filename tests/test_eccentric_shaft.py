"""Validation test suite for the eccentric shaft geometry.

Tests cover:
  1. Dimensional checks — thin wall, lobe offsets, bearing fits (numpy only)
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
        """Lobe OD must match the 6003 bearing bore exactly."""
        assert CFG.shaft.bearing_seat_od == CFG.bearings.ecc_bore, (
            f"Lobe OD {CFG.shaft.bearing_seat_od}mm != "
            f"6003 bore {CFG.bearings.ecc_bore}mm"
        )

    def test_spine_fits_in_625_bearing(self):
        """Spine OD must match the 625 bearing bore."""
        assert CFG.shaft.spine_od == CFG.bearings.inp_bore, (
            f"Spine OD {CFG.shaft.spine_od}mm != "
            f"625 bore {CFG.bearings.inp_bore}mm"
        )

    def test_shaft_spans_both_discs(self):
        """Shaft Z range must cover both disc positions from StackUp."""
        stack = CFG.stack_up
        shaft = CFG.shaft
        disc_t = CFG.disc.thickness

        z_start = stack.z_motor_plate_inner - stack.inp_bearing_seat  # 5mm
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

        z_start = stack.z_motor_plate_inner - stack.inp_bearing_seat
        z_end = stack.z_disc2 + disc_t + shaft.output_stub_length
        expected_length = z_end - z_start  # 37mm

        bb = shaft_solid.val().BoundingBox()
        z_size = bb.zmax - bb.zmin
        assert abs(z_size - expected_length) < 0.1, (
            f"Z extent {z_size:.2f}mm, expected {expected_length:.2f}mm"
        )

    def test_bounding_box_xy(self, shaft_solid):
        """XY extent should reflect 17mm lobe + eccentricity offset.

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

        expected_x = 2 * (lobe_r + e)  # 2 * (8.5 + 1.5) = 20mm
        expected_y = 2 * lobe_r  # 17mm

        assert abs(x_size - expected_x) < 0.1, (
            f"X extent {x_size:.2f}mm, expected {expected_x:.2f}mm"
        )
        assert abs(y_size - expected_y) < 0.1, (
            f"Y extent {y_size:.2f}mm, expected {expected_y:.2f}mm"
        )

    def test_volume_sanity(self, shaft_solid):
        """Volume should be between reasonable bounds.

        Lower bound: just the spine cylinder (no lobes).
        Upper bound: a full 17mm OD cylinder spanning the whole length.
        """
        shaft = CFG.shaft
        stack = CFG.stack_up
        disc_t = CFG.disc.thickness

        lobe_r = shaft.bearing_seat_od / 2.0
        spine_r = shaft.spine_od / 2.0
        z_start = stack.z_motor_plate_inner - stack.inp_bearing_seat
        z_end = stack.z_disc2 + disc_t + shaft.output_stub_length
        total_length = z_end - z_start

        vol = shaft_solid.val().Volume()

        lower = math.pi * spine_r**2 * total_length
        upper = math.pi * lobe_r**2 * total_length

        assert lower < vol < upper, (
            f"Volume {vol:.0f}mm³ outside expected range [{lower:.0f}, {upper:.0f}]"
        )
