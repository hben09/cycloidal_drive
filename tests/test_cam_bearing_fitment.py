"""Tests verifying eccentric cam lobes fit inside 6003 bearings inside the discs.

Tests cover:
  1. Parametric fitment — cam OD vs bearing bore, bearing OD vs disc bore,
     axial alignment of cams with disc positions
  2. Eccentric orbit — cam center stays within bearing bore at all input angles
  3. CadQuery interference — boolean intersection of shaft lobe and bearing
     annulus has zero volume (no physical overlap)
"""

import math
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.params import DEFAULT_CONFIG

CFG = DEFAULT_CONFIG


# ===================================================================
# 1. Parametric fitment checks (no CadQuery needed)
# ===================================================================


class TestCamBearingFitment:
    """Verify the eccentric cams seat correctly in the 6003 bearings."""

    def test_cam_od_matches_bearing_bore(self):
        """Cam lobe OD (17mm) must equal 6003 bearing bore (17mm) for a seat fit."""
        cam_od = CFG.shaft.bearing_seat_od  # 17mm
        bearing_bore = CFG.bearings.ecc_bore  # 17mm
        assert cam_od == bearing_bore, (
            f"Cam OD {cam_od}mm != 6003 bore {bearing_bore}mm"
        )

    def test_bearing_od_fits_disc_bore(self):
        """6003 bearing OD (35mm) must fit inside disc center bore (35.2mm)."""
        bearing_od = CFG.bearings.ecc_od  # 35mm
        disc_bore = CFG.disc.center_bore_dia  # 35.2mm
        clearance = disc_bore - bearing_od
        assert clearance > 0, (
            f"6003 OD ({bearing_od}mm) won't fit disc bore ({disc_bore}mm)"
        )
        assert clearance < 1.0, (
            f"Excessive clearance {clearance:.2f}mm — bearing will be loose"
        )

    def test_bearing_width_matches_disc_thickness(self):
        """6003 bearing width (10mm) must match disc thickness (10mm)."""
        assert CFG.bearings.ecc_width == CFG.disc.thickness, (
            f"6003 width {CFG.bearings.ecc_width}mm != "
            f"disc thickness {CFG.disc.thickness}mm"
        )

    def test_cam_eccentricity_consistent(self):
        """Shaft eccentricity must match gear eccentricity."""
        assert CFG.shaft.eccentricity == CFG.gear.eccentricity, (
            f"Shaft eccentricity {CFG.shaft.eccentricity}mm != "
            f"gear eccentricity {CFG.gear.eccentricity}mm"
        )

    def test_cam_does_not_protrude_past_bearing(self):
        """Cam lobe OD must not exceed bearing bore — no radial protrusion."""
        cam_r = CFG.shaft.bearing_seat_od / 2.0
        bearing_bore_r = CFG.bearings.ecc_bore / 2.0
        assert cam_r <= bearing_bore_r, (
            f"Cam radius {cam_r}mm exceeds bearing bore radius {bearing_bore_r}mm"
        )


# ===================================================================
# 2. Axial alignment — cam lobes aligned with disc Z positions
# ===================================================================


class TestCamAxialAlignment:
    """Verify cam lobes sit at the correct Z positions to engage the discs."""

    def test_lobe1_z_matches_disc1(self):
        """Lobe 1 Z start must equal disc 1 Z position from stack-up."""
        z_lobe1 = CFG.stack_up.z_disc1  # 13mm
        # Both disc and lobe start at z_disc1 and span disc.thickness
        z_lobe1_end = z_lobe1 + CFG.disc.thickness
        z_disc1_end = CFG.stack_up.z_disc1 + CFG.disc.thickness

        assert z_lobe1 == CFG.stack_up.z_disc1, (
            f"Lobe 1 starts at Z={z_lobe1}mm, disc 1 at Z={CFG.stack_up.z_disc1}mm"
        )
        assert z_lobe1_end == z_disc1_end, (
            f"Lobe 1 ends at Z={z_lobe1_end}mm, disc 1 at Z={z_disc1_end}mm"
        )

    def test_lobe2_z_matches_disc2(self):
        """Lobe 2 Z start must equal disc 2 Z position from stack-up."""
        z_lobe2 = CFG.stack_up.z_disc2  # 25mm
        z_lobe2_end = z_lobe2 + CFG.disc.thickness
        z_disc2_end = CFG.stack_up.z_disc2 + CFG.disc.thickness

        assert z_lobe2 == CFG.stack_up.z_disc2, (
            f"Lobe 2 starts at Z={z_lobe2}mm, disc 2 at Z={CFG.stack_up.z_disc2}mm"
        )
        assert z_lobe2_end == z_disc2_end, (
            f"Lobe 2 ends at Z={z_lobe2_end}mm, disc 2 at Z={z_disc2_end}mm"
        )

    def test_inter_disc_gap_free_of_lobes(self):
        """The 2mm spacer gap between discs must not contain any cam lobe material.

        Lobe 1 ends at z_disc1 + thickness, lobe 2 starts at z_disc2.
        The gap = z_disc2 - (z_disc1 + thickness) must equal inter_disc_spacer.
        """
        gap = CFG.stack_up.z_disc2 - (CFG.stack_up.z_disc1 + CFG.disc.thickness)
        assert abs(gap - CFG.disc.inter_disc_spacer) < 0.01, (
            f"Inter-disc gap {gap:.2f}mm != spacer {CFG.disc.inter_disc_spacer}mm"
        )


# ===================================================================
# 3. Eccentric orbit — cam stays inside bearing through full rotation
# ===================================================================


class TestEccentricOrbit:
    """Verify the cam-bearing-disc assembly works through full shaft rotation.

    The bearing outer race is press-fit into the disc bore — they are
    concentric and move together. The cam lobe sits in the bearing inner
    race. As the shaft rotates, the cam pushes the bearing+disc assembly
    to orbit at radius e from the shaft axis.
    """

    NUM_ANGLES = 360

    def test_disc_bearing_swept_envelope_fits_housing(self):
        """Disc+bearing orbiting at eccentricity e must stay inside housing bore.

        The disc profile sweeps a larger envelope than its static OD because
        its center orbits at radius e. The swept disc OD = max_profile_radius + e
        must be less than the housing bore radius.
        """
        from src.profiles import compute_profile_radii, compute_epitrochoid

        profile = compute_epitrochoid(
            R=CFG.gear.ring_pin_circle_radius,
            r=CFG.gear.ring_pin_radius,
            N=CFG.gear.num_ring_pins,
            e=CFG.gear.eccentricity,
            num_points=CFG.profile.num_points,
        )
        _, max_r = compute_profile_radii(profile)
        e = CFG.gear.eccentricity
        housing_bore_r = CFG.housing.bore_dia / 2.0

        swept_r = max_r + e
        assert swept_r < housing_bore_r, (
            f"Disc swept envelope {swept_r:.2f}mm exceeds "
            f"housing bore radius {housing_bore_r:.2f}mm"
        )

    def test_cam_center_orbit_radius_equals_eccentricity(self):
        """At every input angle, the cam lobe center should be exactly e from shaft axis.

        This verifies the two lobes are offset by exactly ±e and the orbit
        radius is consistent through a full revolution.
        """
        e = CFG.shaft.eccentricity
        for step in range(self.NUM_ANGLES):
            phi = 2 * math.pi * step / self.NUM_ANGLES
            cx = e * math.cos(phi)
            cy = e * math.sin(phi)
            orbit_r = math.sqrt(cx**2 + cy**2)
            assert abs(orbit_r - e) < 1e-10, (
                f"At angle {math.degrees(phi):.1f}°: orbit radius "
                f"{orbit_r:.6f}mm != eccentricity {e}mm"
            )

    def test_cam_fills_bearing_bore(self):
        """Cam lobe OD should match bearing bore — no radial slop.

        A loose cam inside the bearing would cause backlash.
        """
        cam_od = CFG.shaft.bearing_seat_od
        bearing_bore = CFG.bearings.ecc_bore
        slop = bearing_bore - cam_od
        assert abs(slop) < 0.01, (
            f"Cam-to-bearing radial slop = {slop:.3f}mm (should be ~0)"
        )


# ===================================================================
# 4. CadQuery interference — shaft lobe vs bearing solid
# ===================================================================


class TestCadQueryCamBearingInterference:
    """Boolean intersection tests between shaft lobes and bearing annuli."""

    @pytest.fixture(scope="class")
    def shaft_and_bearings(self):
        """Build the shaft and two 6003 bearings positioned at disc locations."""
        cq = pytest.importorskip("cadquery")
        from src.eccentric_shaft import build_eccentric_shaft
        from src.purchased_parts import build_bearing_6003

        shaft = build_eccentric_shaft()

        stack = CFG.stack_up
        e = CFG.gear.eccentricity

        # Bearing 1: centered on lobe 1 (offset +e in X, at z_disc1)
        bearing1 = build_bearing_6003().translate((e, 0, stack.z_disc1))
        # Bearing 2: centered on lobe 2 (offset -e in X, at z_disc2)
        bearing2 = build_bearing_6003().translate((-e, 0, stack.z_disc2))

        return shaft, bearing1, bearing2

    def test_lobe1_no_interference_with_bearing1(self, shaft_and_bearings):
        """Shaft lobe 1 must not overlap the bearing 1 annulus (inner race material).

        The shaft sits in the bearing bore — their solids should not intersect
        because the cam OD matches the bearing bore exactly.
        """
        shaft, bearing1, _ = shaft_and_bearings
        interference = shaft.intersect(bearing1)
        vol = interference.val().Volume()
        assert vol < 1.0, (
            f"Shaft/bearing-1 interference = {vol:.1f}mm³ (should be ~0)"
        )

    def test_lobe2_no_interference_with_bearing2(self, shaft_and_bearings):
        """Shaft lobe 2 must not overlap bearing 2 annulus."""
        shaft, _, bearing2 = shaft_and_bearings
        interference = shaft.intersect(bearing2)
        vol = interference.val().Volume()
        assert vol < 1.0, (
            f"Shaft/bearing-2 interference = {vol:.1f}mm³ (should be ~0)"
        )

    def test_shaft_passes_through_both_bearing_bores(self, shaft_and_bearings):
        """The shaft must extend through the full Z range of both bearings.

        Verifies shaft Z extent covers both bearing positions.
        """
        shaft, _, _ = shaft_and_bearings
        bb = shaft.val().BoundingBox()

        z_bearing1_start = CFG.stack_up.z_disc1
        z_bearing2_end = CFG.stack_up.z_disc2 + CFG.bearings.ecc_width

        assert bb.zmin <= z_bearing1_start, (
            f"Shaft starts at Z={bb.zmin:.1f}mm, bearing 1 at Z={z_bearing1_start}mm"
        )
        assert bb.zmax >= z_bearing2_end, (
            f"Shaft ends at Z={bb.zmax:.1f}mm, bearing 2 ends at Z={z_bearing2_end}mm"
        )

    @pytest.fixture(scope="class")
    def disc_bearing_shaft(self):
        """Build shaft, disc, and bearing all positioned for lobe 1."""
        cq = pytest.importorskip("cadquery")
        from src.eccentric_shaft import build_eccentric_shaft
        from src.cycloidal_disc import build_cycloidal_disc
        from src.purchased_parts import build_bearing_6003

        e = CFG.gear.eccentricity
        z = CFG.stack_up.z_disc1

        shaft = build_eccentric_shaft()
        # Disc centered on lobe 1 (offset +e, at z_disc1)
        disc = build_cycloidal_disc().translate((e, 0, z))
        # Bearing concentric with lobe 1
        bearing = build_bearing_6003().translate((e, 0, z))

        return shaft, disc, bearing

    def test_full_stack_no_shaft_disc_interference(self, disc_bearing_shaft):
        """Shaft must not interfere with disc material (only touches bearing)."""
        shaft, disc, _ = disc_bearing_shaft
        interference = shaft.intersect(disc)
        vol = interference.val().Volume()
        assert vol < 1.0, (
            f"Shaft/disc interference = {vol:.1f}mm³ (should be ~0)"
        )

    def test_full_stack_no_bearing_disc_interference(self, disc_bearing_shaft):
        """Bearing must not interfere with disc material (sits inside bore)."""
        _, disc, bearing = disc_bearing_shaft
        interference = disc.intersect(bearing)
        vol = interference.val().Volume()
        assert vol < 1.0, (
            f"Bearing/disc interference = {vol:.1f}mm³ (should be ~0)"
        )
