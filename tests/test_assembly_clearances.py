"""Assembly-level clearance verification — Design Sequence Step 8.

Verifies all cross-part relationships when parts are positioned per the
axial stack-up (params.StackUp).  Tests cover:

  1. Axial stack-up — Z positions are consistent, no gaps or overlaps
  2. Housing alignment — motor plate, ring gear body, output cap mate flush
  3. Radial clearances — discs clear housing, pins clear bearings, hub clears cap
  4. Bearing retention — 6814 trapped between shoulder and cap
  5. Shaft reach — motor shaft engages D-bore, eccentric shaft reaches 625 pocket
  6. Ring pin span — pins seat in motor plate and ring gear body
  7. CadQuery interference — boolean checks on key mating pairs
"""

import math
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.params import DEFAULT_CONFIG, compute_housing_bolt_angles

CFG = DEFAULT_CONFIG


# ===================================================================
# 1. Axial stack-up consistency
# ===================================================================


class TestAxialStackUp:
    """Verify Z positions are self-consistent and sum correctly."""

    def test_total_housing_depth(self):
        """Total depth must equal the sum of all layers."""
        s = CFG.stack_up
        expected = (
            s.motor_plate_wall
            + s.motor_plate_inner_wall
            + s.input_clearance
            + s.disc_thickness * 2
            + s.inter_disc_spacer
            + s.output_clearance
            + s.output_bearing_total
            + s.output_wall
        )
        assert abs(s.total_housing_depth - expected) < 0.01, (
            f"Total depth {s.total_housing_depth}mm != sum {expected}mm"
        )

    def test_total_depth_is_65mm(self):
        """Housing depth: 10mm plate + 47mm body + 8mm cap = 65mm."""
        assert abs(CFG.stack_up.total_housing_depth - 65.0) < 0.01

    def test_disc1_before_disc2(self):
        """Disc 1 must sit at a lower Z than disc 2."""
        s = CFG.stack_up
        assert s.z_disc1 < s.z_disc2

    def test_disc2_ends_before_output_bearings(self):
        """Disc 2 top face must be below the output bearings."""
        s = CFG.stack_up
        disc2_top = s.z_disc2 + s.disc_thickness
        assert disc2_top <= s.z_output_bearings, (
            f"Disc 2 top {disc2_top}mm >= output bearings {s.z_output_bearings}mm"
        )

    def test_output_clearance_gap(self):
        """There must be a clearance gap between disc 2 and output bearings."""
        s = CFG.stack_up
        disc2_top = s.z_disc2 + s.disc_thickness
        gap = s.z_output_bearings - disc2_top
        assert abs(gap - s.output_clearance) < 0.01, (
            f"Output clearance {gap}mm != spec {s.output_clearance}mm"
        )

    def test_output_bearings_end_at_output_cap(self):
        """Output bearings top must align with output cap Z."""
        s = CFG.stack_up
        bearing_top = s.z_output_bearings + s.output_bearing_total
        assert abs(bearing_top - s.z_output_cap) < 0.01, (
            f"Bearing top {bearing_top}mm != output cap Z {s.z_output_cap}mm"
        )


# ===================================================================
# 2. Housing part alignment
# ===================================================================


class TestHousingAlignment:
    """Verify the three housing pieces mate flush."""

    def test_motor_plate_inner_face(self):
        """Motor plate inner face at Z=10mm."""
        s = CFG.stack_up
        expected = s.motor_plate_wall + s.motor_plate_inner_wall  # 5+5=10mm
        assert abs(s.z_motor_plate_inner - expected) < 0.01

    def test_ring_gear_body_height(self):
        """Ring gear body spans from motor plate inner face to output cap."""
        s = CFG.stack_up
        body_height = s.z_output_cap - s.z_motor_plate_inner
        assert abs(body_height - 47.0) < 0.01, (
            f"Ring gear body height {body_height}mm != 47mm"
        )

    def test_all_housing_parts_same_od(self):
        """Motor plate, ring gear body, and output cap should share the housing OD."""
        # This is enforced by all parts using cfg.housing.od, but verify the value
        assert CFG.housing.od == 140.0

    def test_housing_bolt_angles_consistent(self):
        """All housing parts use the same bolt angle computation."""
        angles = compute_housing_bolt_angles(CFG)
        assert len(angles) == CFG.housing.bolt_count
        # Angles must be sorted and within [0, 2π)
        for i in range(len(angles) - 1):
            assert angles[i] < angles[i + 1], "Bolt angles not sorted"
        assert angles[0] >= 0
        assert angles[-1] < 2 * math.pi

    def test_housing_bolts_clear_ring_pins(self):
        """Housing bolts must not overlap ring pin holes (2D distance check).

        Bolts and pins sit at different radii (62.5mm vs 54mm), so the
        real clearance is the Euclidean distance between hole centers
        minus the sum of hole radii.
        """
        g = CFG.gear
        h = CFG.housing
        bolt_angles = compute_housing_bolt_angles(CFG)
        bolt_r = h.bolt_circle_dia / 2.0  # 62.5mm
        pin_r = g.ring_pin_circle_dia / 2.0  # 54mm

        bolt_hole_r = (h.bolt_dia + 0.4) / 2.0  # 2.2mm
        pin_hole_r = g.ring_pin_dia / 2.0  # 2.0mm
        min_center_dist = bolt_hole_r + pin_hole_r  # 4.2mm

        for ba in bolt_angles:
            bx = bolt_r * math.cos(ba)
            by = bolt_r * math.sin(ba)
            for i in range(g.num_ring_pins):
                pa = 2 * math.pi * i / g.num_ring_pins
                px = pin_r * math.cos(pa)
                py = pin_r * math.sin(pa)
                dist = math.hypot(bx - px, by - py)
                assert dist > min_center_dist, (
                    f"Bolt at {math.degrees(ba):.1f}° is only {dist:.2f}mm "
                    f"from pin {i} (need > {min_center_dist:.2f}mm)"
                )


# ===================================================================
# 3. Radial clearances
# ===================================================================


class TestRadialClearances:
    """Verify parts don't interfere radially."""

    def test_disc_orbit_clears_housing_bore(self):
        """Disc max radius + eccentricity must be less than housing bore radius."""
        from src.profiles import compute_epitrochoid, compute_profile_radii

        profile = compute_epitrochoid(
            R=CFG.gear.ring_pin_circle_radius,
            r=CFG.gear.ring_pin_radius,
            N=CFG.gear.num_ring_pins,
            e=CFG.gear.eccentricity,
            num_points=CFG.profile.num_points,
        )
        _, max_r = compute_profile_radii(profile)
        swept_r = max_r + CFG.gear.eccentricity
        bore_r = CFG.housing.bore_dia / 2.0

        assert swept_r < bore_r, (
            f"Disc swept radius {swept_r:.2f}mm >= housing bore radius {bore_r}mm"
        )
        clearance = bore_r - swept_r
        assert clearance >= 0.5, (
            f"Disc-to-housing clearance only {clearance:.2f}mm (want >= 0.5mm)"
        )

    def test_output_pins_inside_6814_bore(self):
        """Output pin outer edges must sit within the 6814 bearing bore."""
        d = CFG.disc
        b = CFG.bearings
        pin_outer_r = d.output_pin_circle_dia / 2.0 + d.output_pin_dia / 2.0
        bearing_bore_r = b.out_bore / 2.0
        assert pin_outer_r < bearing_bore_r, (
            f"Output pin edge at {pin_outer_r}mm >= 6814 bore radius {bearing_bore_r}mm"
        )

    def test_output_hub_clears_output_cap_bore(self):
        """Output hub OD must be smaller than output cap center bore."""
        hub = CFG.output_hub
        tol = CFG.tolerances
        hub_od = hub.od - tol.bearing_inner_shaft_sub  # 69.925mm
        cap_bore = hub.od + tol.sliding_clearance_add  # 70.25mm
        clearance = cap_bore - hub_od
        assert clearance > 0, (
            f"Hub OD {hub_od}mm >= cap bore {cap_bore}mm"
        )
        assert clearance >= 0.2, (
            f"Hub-to-cap clearance only {clearance:.3f}mm (want >= 0.2mm)"
        )

    def test_output_hub_fits_6814_inner(self):
        """Output hub OD must fit inside the 6814 bearing bore."""
        hub = CFG.output_hub
        b = CFG.bearings
        tol = CFG.tolerances
        hub_od = hub.od - tol.bearing_inner_shaft_sub
        assert hub_od <= b.out_bore, (
            f"Hub OD {hub_od}mm > 6814 bore {b.out_bore}mm"
        )

    def test_6814_outer_fits_housing_seat(self):
        """6814 OD must fit in the housing bearing seat bore."""
        b = CFG.bearings
        h = CFG.housing
        assert b.out_od <= h.output_bearing_seat_dia, (
            f"6814 OD {b.out_od}mm > bearing seat {h.output_bearing_seat_dia}mm"
        )

    def test_ring_pins_inside_housing_bore(self):
        """Ring pins must sit inside the housing bore (pins in air in disc zone)."""
        g = CFG.gear
        pin_outer_r = g.ring_pin_circle_dia / 2.0 + g.ring_pin_dia / 2.0
        bore_r = CFG.housing.bore_dia / 2.0
        assert pin_outer_r < bore_r, (
            f"Ring pin outer edge {pin_outer_r}mm >= housing bore radius {bore_r}mm"
        )

    def test_disc_output_pin_holes_clear_center_bore(self):
        """Output pin holes in disc must not overlap with the center bore."""
        d = CFG.disc
        pin_inner_r = d.output_pin_circle_dia / 2.0 - d.output_pin_hole_dia / 2.0
        bore_r = d.center_bore_dia / 2.0
        wall = pin_inner_r - bore_r
        assert wall >= 5.0, (
            f"Disc bore-to-pin wall {wall:.2f}mm < 5mm"
        )


# ===================================================================
# 4. Bearing retention
# ===================================================================


class TestBearingRetention:
    """Verify all bearings are axially constrained."""

    def test_6814_retained_by_shoulder(self):
        """Ring gear body shoulder (70mm bore) blocks 6814 (90mm OD) on input side."""
        b = CFG.bearings
        shoulder_bore = b.out_bore  # 70mm
        bearing_od = b.out_od  # 90mm
        assert shoulder_bore < bearing_od, (
            f"Shoulder bore {shoulder_bore}mm >= 6814 OD {bearing_od}mm — not retained"
        )

    def test_6814_retained_by_output_cap(self):
        """Output cap center bore must be smaller than 6814 OD on output side."""
        hub = CFG.output_hub
        b = CFG.bearings
        tol = CFG.tolerances
        cap_bore = hub.od + tol.sliding_clearance_add  # 70.25mm
        assert cap_bore < b.out_od, (
            f"Cap bore {cap_bore}mm >= 6814 OD {b.out_od}mm — not retained"
        )

    def test_6003_retained_by_disc_bore(self):
        """6003 OD fits into disc center bore — disc material retains it."""
        b = CFG.bearings
        d = CFG.disc
        assert b.ecc_od <= d.center_bore_dia, (
            f"6003 OD {b.ecc_od}mm > disc bore {d.center_bore_dia}mm"
        )

    def test_625_retained_by_output_hub_pocket(self):
        """625 bearing pocket in hub is smaller than hub OD — bearing is captured."""
        hub = CFG.output_hub
        b = CFG.bearings
        tol = CFG.tolerances
        pocket_dia = b.inp_od + tol.bearing_seat_bore_add
        hub_od = hub.od - tol.bearing_inner_shaft_sub
        assert pocket_dia < hub_od, (
            f"625 pocket {pocket_dia}mm >= hub OD {hub_od}mm"
        )


# ===================================================================
# 5. Shaft reach
# ===================================================================


class TestShaftReach:
    """Verify shaft engagement at both ends."""

    def test_motor_shaft_reaches_through_plate(self):
        """Motor shaft (20mm) must be long enough to pass through the motor plate
        and engage the eccentric shaft D-bore.
        """
        m = CFG.motor
        s = CFG.stack_up
        plate_thickness = s.motor_plate_wall + s.motor_plate_inner_wall  # 10mm
        remaining = m.shaft_length - plate_thickness  # 20 - 10 = 10mm
        d_bore_depth = CFG.shaft.d_bore_depth  # 10mm
        assert remaining >= d_bore_depth, (
            f"Motor shaft only {remaining}mm past plate, D-bore needs {d_bore_depth}mm"
        )

    def test_eccentric_shaft_pin_reaches_625_bearing(self):
        """Steel dowel pin must protrude enough to reach through the 625 bearing."""
        s = CFG.stack_up
        shaft = CFG.shaft
        disc2_end = s.z_disc2 + s.disc_thickness  # 35mm
        z_625_end = s.z_output_bearings + CFG.bearings.inp_width  # 42mm
        pin_tip_z = disc2_end + (shaft.support_pin_length - shaft.support_pin_hole_depth)
        assert pin_tip_z >= z_625_end, (
            f"Pin tip at Z={pin_tip_z}mm doesn't reach 625 far face at Z={z_625_end}mm"
        )

    def test_eccentric_shaft_pin_fits_625_bore(self):
        """Steel dowel pin OD must fit inside the 625 bearing bore."""
        assert CFG.shaft.support_pin_dia <= CFG.bearings.inp_bore, (
            f"Pin OD {CFG.shaft.support_pin_dia}mm > 625 bore {CFG.bearings.inp_bore}mm"
        )

    def test_eccentric_shaft_pin_clears_hub_bore(self):
        """Support pin must have clearance inside the output hub shaft bore."""
        clearance = CFG.output_hub.shaft_clearance_bore - CFG.shaft.support_pin_dia
        assert clearance >= 0.5, (
            f"Pin-to-hub-bore clearance {clearance:.2f}mm < 0.5mm minimum"
        )


# ===================================================================
# 6. Ring pin span
# ===================================================================


class TestRingPinSpan:
    """Verify ring pin length covers both engagement zones."""

    def test_pin_length_spans_disc_zone_plus_engagement(self):
        """Pin length = 5mm motor plate + 25mm disc zone + 5mm ring gear body."""
        g = CFG.gear
        s = CFG.stack_up
        disc_zone = (
            s.input_clearance
            + s.disc_thickness * 2
            + s.inter_disc_spacer
        )
        engagement_per_side = (g.ring_pin_length - disc_zone) / 2.0
        assert abs(engagement_per_side - 5.0) < 0.01, (
            f"Pin engagement {engagement_per_side}mm per side != 5mm"
        )

    def test_pin_length_equals_35mm(self):
        """Spec defines ring pin length as 35mm."""
        assert CFG.gear.ring_pin_length == 35.0

    def test_disc_zone_is_25mm(self):
        """Disc zone (input clearance + 2 discs + spacer) should be 25mm."""
        s = CFG.stack_up
        disc_zone = s.input_clearance + s.disc_thickness * 2 + s.inter_disc_spacer
        assert abs(disc_zone - 25.0) < 0.01


# ===================================================================
# 7. Housing bolt engagement
# ===================================================================


class TestHousingBoltEngagement:
    """Verify M4 × 60mm bolt fits the housing stack with counterbore and nut pocket."""

    def test_bolt_reaches_nut(self):
        """Bolt shank must extend past the nut pocket floor."""
        h = CFG.housing
        s = CFG.stack_up
        bolt_tip_z = h.bolt_counterbore_depth + h.bolt_length
        nut_floor_z = s.total_housing_depth - h.bolt_nut_depth
        assert bolt_tip_z > nut_floor_z, (
            f"Bolt tip at {bolt_tip_z}mm doesn't reach nut floor at {nut_floor_z}mm"
        )

    def test_full_nut_engagement(self):
        """Bolt must pass through the full nut thickness."""
        h = CFG.housing
        s = CFG.stack_up
        bolt_tip_z = h.bolt_counterbore_depth + h.bolt_length
        nut_floor_z = s.total_housing_depth - h.bolt_nut_depth
        engagement = bolt_tip_z - nut_floor_z
        assert engagement >= h.bolt_nut_thickness, (
            f"Thread engagement {engagement:.1f}mm < nut thickness {h.bolt_nut_thickness}mm"
        )

    def test_bolt_does_not_protrude(self):
        """Bolt tip must not extend past the output cap outer face."""
        h = CFG.housing
        s = CFG.stack_up
        bolt_tip_z = h.bolt_counterbore_depth + h.bolt_length
        assert bolt_tip_z <= s.total_housing_depth, (
            f"Bolt tip at {bolt_tip_z}mm protrudes past cap at {s.total_housing_depth}mm"
        )

    def test_counterbore_recesses_head(self):
        """Counterbore must be at least as deep as the bolt head height."""
        h = CFG.housing
        assert h.bolt_counterbore_depth >= h.bolt_head_height, (
            f"Counterbore {h.bolt_counterbore_depth}mm < head height {h.bolt_head_height}mm"
        )

    def test_counterbore_wall_to_od(self):
        """Counterbore must leave adequate wall to housing OD."""
        h = CFG.housing
        bolt_r = h.bolt_circle_dia / 2.0
        cb_r = h.bolt_counterbore_dia / 2.0
        wall = h.od / 2.0 - (bolt_r + cb_r)
        assert wall >= 2.0, (
            f"Counterbore wall to OD = {wall:.2f}mm, need >= 2mm"
        )

    def test_counterbore_fits_in_motor_plate(self):
        """Counterbore depth must be less than motor plate thickness."""
        h = CFG.housing
        s = CFG.stack_up
        plate_t = s.motor_plate_wall + s.motor_plate_inner_wall
        assert h.bolt_counterbore_depth < plate_t, (
            f"Counterbore {h.bolt_counterbore_depth}mm >= plate thickness {plate_t}mm"
        )


# ===================================================================
# 8. CadQuery interference checks — key mating pairs
# ===================================================================


class TestCadQueryAssemblyInterference:
    """Boolean intersection checks between parts in assembly position."""

    @pytest.fixture(scope="class")
    def housing_parts(self):
        """Build and position the three housing parts."""
        cq = pytest.importorskip("cadquery")
        from src.motor_plate import build_motor_plate
        from src.ring_gear_body import build_ring_gear_body
        from src.output_cap import build_output_cap

        s = CFG.stack_up
        mp = build_motor_plate()
        rgb = build_ring_gear_body().translate((0, 0, s.z_motor_plate_inner))
        oc = build_output_cap().translate((0, 0, s.z_output_cap))
        return mp, rgb, oc

    def test_motor_plate_ring_body_no_interference(self, housing_parts):
        """Motor plate and ring gear body must not overlap."""
        mp, rgb, _ = housing_parts
        interference = mp.intersect(rgb)
        vol = interference.val().Volume()
        assert vol < 1.0, (
            f"Motor plate / ring body interference = {vol:.1f}mm³"
        )

    def test_ring_body_output_cap_no_interference(self, housing_parts):
        """Ring gear body and output cap must not overlap."""
        _, rgb, oc = housing_parts
        interference = rgb.intersect(oc)
        vol = interference.val().Volume()
        assert vol < 1.0, (
            f"Ring body / output cap interference = {vol:.1f}mm³"
        )

    def test_motor_plate_output_cap_no_interference(self, housing_parts):
        """Motor plate and output cap must not overlap (they're far apart)."""
        mp, _, oc = housing_parts
        interference = mp.intersect(oc)
        vol = interference.val().Volume()
        assert vol < 1.0, (
            f"Motor plate / output cap interference = {vol:.1f}mm³"
        )

    @pytest.fixture(scope="class")
    def output_hub_and_cap(self):
        """Build and position output hub and cap."""
        cq = pytest.importorskip("cadquery")
        from src.output_hub import build_output_hub
        from src.output_cap import build_output_cap

        s = CFG.stack_up
        hub = build_output_hub().translate((0, 0, s.z_output_bearings))
        cap = build_output_cap().translate((0, 0, s.z_output_cap))
        return hub, cap

    def test_output_hub_clears_output_cap(self, output_hub_and_cap):
        """Output hub (rotating) must not interfere with output cap (static)."""
        hub, cap = output_hub_and_cap
        interference = hub.intersect(cap)
        vol = interference.val().Volume()
        assert vol < 1.0, (
            f"Output hub / cap interference = {vol:.1f}mm³"
        )

    @pytest.fixture(scope="class")
    def disc_and_housing(self):
        """Build disc 1 at max eccentricity and the ring gear body."""
        cq = pytest.importorskip("cadquery")
        from src.cycloidal_disc import build_cycloidal_disc
        from src.ring_gear_body import build_ring_gear_body

        s = CFG.stack_up
        e = CFG.gear.eccentricity

        disc = build_cycloidal_disc().translate((e, 0, s.z_disc1))
        rgb = build_ring_gear_body().translate((0, 0, s.z_motor_plate_inner))
        return disc, rgb

    def test_disc_clears_ring_gear_shoulder(self, disc_and_housing):
        """Disc at max eccentricity must not hit the ring gear body shoulder."""
        disc, rgb = disc_and_housing
        interference = disc.intersect(rgb)
        vol = interference.val().Volume()
        assert vol < 1.0, (
            f"Disc / ring gear body interference = {vol:.1f}mm³"
        )

    @pytest.fixture(scope="class")
    def output_hub_in_ring_body(self):
        """Build output hub inside the ring gear body."""
        cq = pytest.importorskip("cadquery")
        from src.output_hub import build_output_hub
        from src.ring_gear_body import build_ring_gear_body

        s = CFG.stack_up
        hub = build_output_hub().translate((0, 0, s.z_output_bearings))
        rgb = build_ring_gear_body().translate((0, 0, s.z_motor_plate_inner))
        return hub, rgb

    def test_output_hub_clears_ring_body(self, output_hub_in_ring_body):
        """Output hub must pass through the ring gear body without interference."""
        hub, rgb = output_hub_in_ring_body
        interference = hub.intersect(rgb)
        vol = interference.val().Volume()
        assert vol < 1.0, (
            f"Output hub / ring body interference = {vol:.1f}mm³"
        )
