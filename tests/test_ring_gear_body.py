"""Validation test suite for the ring gear body geometry.

Tests cover:
  1. Dimensional checks — zone heights, clearances, fit relationships (no CadQuery)
  2. CadQuery solid — valid topology, bounding box, volume, bore verification
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


class TestRingGearBodyDimensions:

    def test_body_height_matches_stackup(self):
        """Body height must equal z_output_cap - z_motor_plate_inner."""
        stack = CFG.stack_up
        expected = stack.z_output_cap - stack.z_motor_plate_inner  # 47mm
        actual = (
            stack.input_clearance
            + stack.disc_thickness * 2
            + stack.inter_disc_spacer
            + stack.output_clearance
            + stack.output_bearing_total
        )
        assert abs(actual - expected) < 0.01, (
            f"Body height {actual}mm != expected {expected}mm"
        )

    def test_housing_bolts_inside_od(self):
        """M4 housing bolt holes must not break through the OD."""
        h = CFG.housing
        bolt_r = h.bolt_circle_dia / 2.0
        hole_r = (h.bolt_dia + 0.4) / 2.0
        outermost = bolt_r + hole_r
        assert outermost < h.od / 2.0, (
            f"Housing bolt edge at {outermost:.1f}mm exceeds housing radius "
            f"{h.od / 2.0:.1f}mm"
        )

    def test_pin_holes_dont_breach_bearing_seat(self):
        """Ring pin holes must not cut into the bearing seat bore."""
        g = CFG.gear
        h = CFG.housing
        tol = CFG.tolerances
        pin_circle_r = g.ring_pin_circle_dia / 2.0  # 54mm
        pin_hole_r = (g.ring_pin_dia - tol.ring_pin_press_sub) / 2.0  # ~1.94mm
        bearing_seat_r = h.output_bearing_seat_dia / 2.0  # 45.075mm

        pin_inner_edge = pin_circle_r - pin_hole_r
        gap = pin_inner_edge - bearing_seat_r
        assert gap >= 5.0, (
            f"Pin hole inner edge to bearing seat wall = {gap:.2f}mm, need >= 5mm"
        )

    def test_pin_holes_inside_housing_od(self):
        """Ring pin holes must not break through the housing OD."""
        g = CFG.gear
        h = CFG.housing
        tol = CFG.tolerances
        pin_circle_r = g.ring_pin_circle_dia / 2.0  # 54mm
        pin_hole_r = (g.ring_pin_dia - tol.ring_pin_press_sub) / 2.0
        outermost = pin_circle_r + pin_hole_r
        assert outermost < h.od / 2.0, (
            f"Pin hole outer edge at {outermost:.2f}mm exceeds housing "
            f"radius {h.od / 2.0}mm"
        )

    def test_bolt_holes_do_not_overlap_pin_holes(self):
        """No housing bolt hole should overlap with any ring pin hole."""
        g = CFG.gear
        h = CFG.housing
        tol = CFG.tolerances

        pin_circle_r = g.ring_pin_circle_dia / 2.0  # 54mm
        bolt_circle_r = h.bolt_circle_dia / 2.0  # 55mm
        pin_hole_r = (g.ring_pin_dia - tol.ring_pin_press_sub) / 2.0  # ~1.94mm
        bolt_hole_r = (h.bolt_dia + 0.4) / 2.0  # 2.2mm
        min_distance = pin_hole_r + bolt_hole_r  # ~4.14mm (no overlap)

        bolt_angles = compute_housing_bolt_angles(CFG)
        pin_angles = [2 * math.pi * i / g.num_ring_pins for i in range(g.num_ring_pins)]

        for bi, ba in enumerate(bolt_angles):
            bx = bolt_circle_r * math.cos(ba)
            by = bolt_circle_r * math.sin(ba)
            for pi_, pa in enumerate(pin_angles):
                px = pin_circle_r * math.cos(pa)
                py = pin_circle_r * math.sin(pa)
                dist = math.sqrt((bx - px) ** 2 + (by - py) ** 2)
                assert dist >= min_distance, (
                    f"Bolt {bi} (angle {math.degrees(ba):.1f}°) overlaps "
                    f"pin {pi_} (angle {math.degrees(pa):.1f}°): "
                    f"distance {dist:.2f}mm < min {min_distance:.2f}mm"
                )

    def test_bolt_holes_do_not_overlap_each_other(self):
        """No two housing bolt holes should overlap."""
        h = CFG.housing
        bolt_circle_r = h.bolt_circle_dia / 2.0
        bolt_hole_r = (h.bolt_dia + 0.4) / 2.0
        min_distance = 2 * bolt_hole_r  # 4.4mm

        bolt_angles = compute_housing_bolt_angles(CFG)

        for i in range(len(bolt_angles)):
            for j in range(i + 1, len(bolt_angles)):
                ax = bolt_circle_r * math.cos(bolt_angles[i])
                ay = bolt_circle_r * math.sin(bolt_angles[i])
                bx = bolt_circle_r * math.cos(bolt_angles[j])
                by = bolt_circle_r * math.sin(bolt_angles[j])
                dist = math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)
                assert dist >= min_distance, (
                    f"Bolt {i} and bolt {j} overlap: "
                    f"distance {dist:.2f}mm < min {min_distance:.2f}mm"
                )

    def test_shoulder_bore_clears_output_hub(self):
        """Shoulder ring bore must be >= output hub OD for assembly clearance."""
        b = CFG.bearings
        hub = CFG.output_hub
        shoulder_bore = b.out_bore  # 70mm (used as shoulder bore)
        assert shoulder_bore >= hub.od, (
            f"Shoulder bore {shoulder_bore}mm < output hub OD {hub.od}mm"
        )

    def test_shoulder_retains_bearing(self):
        """Shoulder bore must be smaller than 6814 outer race OD."""
        b = CFG.bearings
        shoulder_bore = b.out_bore  # 70mm
        bearing_od = b.out_od  # 90mm
        assert shoulder_bore < bearing_od, (
            f"Shoulder bore {shoulder_bore}mm >= bearing OD {bearing_od}mm "
            "— bearing would pass through"
        )

    def test_bearing_seat_is_press_fit(self):
        """Bearing seat must be slightly larger than bearing OD (press fit)."""
        h = CFG.housing
        b = CFG.bearings
        assert h.output_bearing_seat_dia > b.out_od, (
            f"Bearing seat {h.output_bearing_seat_dia}mm <= bearing OD "
            f"{b.out_od}mm — won't accept bearing"
        )
        gap = h.output_bearing_seat_dia - b.out_od
        assert gap < 0.5, (
            f"Bearing seat gap {gap:.2f}mm too large for press fit"
        )

    def test_housing_bolts_outside_bore(self):
        """Housing bolt holes must sit entirely outside the 116mm bore.

        Bolts at radius < bore_radius would be unsupported in the disc zone
        and would physically interfere with the orbiting cycloidal discs.
        """
        h = CFG.housing
        bolt_r = h.bolt_circle_dia / 2.0
        hole_r = (h.bolt_dia + 0.4) / 2.0
        bore_r = h.bore_dia / 2.0

        bolt_inner_edge = bolt_r - hole_r
        assert bolt_inner_edge > bore_r, (
            f"Housing bolt inner edge at {bolt_inner_edge:.1f}mm is inside "
            f"bore radius {bore_r:.1f}mm — bolts would be unsupported and "
            f"interfere with disc orbit"
        )

    def test_housing_bolts_have_wall_to_bore(self):
        """Housing bolt holes must leave >=1mm wall between bore and bolt edge."""
        h = CFG.housing
        bolt_r = h.bolt_circle_dia / 2.0
        hole_r = (h.bolt_dia + 0.4) / 2.0
        bore_r = h.bore_dia / 2.0

        wall = (bolt_r - hole_r) - bore_r
        assert wall >= 1.0, (
            f"Wall from bore to bolt hole = {wall:.1f}mm, need >= 1mm"
        )

    def test_housing_bolts_clear_disc_sweep(self):
        """Housing bolt hole inner edge must clear the disc sweep envelope.

        The disc's max radius plus eccentricity gives the swept radius.
        Bolt holes must be entirely outside this zone.
        """
        from src.profiles import compute_epitrochoid, compute_profile_radii

        g = CFG.gear
        h = CFG.housing

        pts = compute_epitrochoid(
            R=g.ring_pin_circle_dia / 2.0,
            r=g.ring_pin_dia / 2.0,
            N=g.num_ring_pins,
            e=g.eccentricity,
        )
        _, max_r = compute_profile_radii(pts)
        disc_sweep_r = max_r + g.eccentricity

        bolt_r = h.bolt_circle_dia / 2.0
        hole_r = (h.bolt_dia + 0.4) / 2.0
        bolt_inner_edge = bolt_r - hole_r

        clearance = bolt_inner_edge - disc_sweep_r
        assert clearance > 0, (
            f"Disc sweep radius {disc_sweep_r:.2f}mm reaches bolt hole "
            f"inner edge at {bolt_inner_edge:.2f}mm — interference of "
            f"{-clearance:.2f}mm"
        )

    def test_disc_fits_through_main_bore(self):
        """Cycloidal disc (with eccentricity) must fit through the 116mm bore."""
        from src.profiles import compute_epitrochoid

        g = CFG.gear
        h = CFG.housing
        pts = compute_epitrochoid(
            R=g.ring_pin_circle_dia / 2.0,
            r=g.ring_pin_dia / 2.0,
            N=g.num_ring_pins,
            e=g.eccentricity,
        )
        max_r = max(math.sqrt(x**2 + y**2) for x, y in pts)
        # Disc center orbits at ± eccentricity
        max_sweep = max_r + g.eccentricity
        bore_r = h.bore_dia / 2.0
        assert max_sweep < bore_r, (
            f"Disc max sweep {max_sweep:.2f}mm >= bore radius {bore_r}mm"
        )


# ===================================================================
# 2. CadQuery solid validation
# ===================================================================


class TestCadQuerySolid:

    @pytest.fixture(scope="class")
    def body_solid(self):
        cq = pytest.importorskip("cadquery")
        from src.ring_gear_body import build_ring_gear_body

        return build_ring_gear_body()

    def test_solid_is_valid(self, body_solid):
        """The built solid should be non-null and have exactly one solid."""
        solids = body_solid.solids().vals()
        assert len(solids) == 1, f"Expected 1 solid, got {len(solids)}"
        assert solids[0].isValid(), "Solid is not valid"

    def test_outer_diameter(self, body_solid):
        """XY extent should be the housing OD (120mm)."""
        bb = body_solid.val().BoundingBox()
        x_size = bb.xmax - bb.xmin
        y_size = bb.ymax - bb.ymin
        expected = CFG.housing.od  # 120mm

        assert abs(x_size - expected) < 0.2, (
            f"X extent {x_size:.2f}mm, expected {expected}mm"
        )
        assert abs(y_size - expected) < 0.2, (
            f"Y extent {y_size:.2f}mm, expected {expected}mm"
        )

    def test_height(self, body_solid):
        """Z height should match the stack-up (47mm)."""
        bb = body_solid.val().BoundingBox()
        z_size = bb.zmax - bb.zmin
        stack = CFG.stack_up
        expected = stack.z_output_cap - stack.z_motor_plate_inner  # 47mm

        assert abs(z_size - expected) < 0.1, (
            f"Z extent {z_size:.2f}mm, expected {expected:.2f}mm"
        )

    def test_bore_diameter(self, body_solid):
        """Section area at disc zone should match a 116/120mm annulus.

        At the disc zone midpoint, the only material is the thin outer
        wall (58mm to 60mm radius) — bolt and pin holes are inside the
        bore and don't affect the section.
        """
        stack = CFG.stack_up
        h = CFG.housing

        disc_zone_mid = (
            stack.input_clearance
            + stack.disc_thickness
            + stack.inter_disc_spacer / 2.0
        )  # 14mm

        section = body_solid.section(height=disc_zone_mid)
        area = section.val().Area()

        housing_r = h.od / 2.0  # 60mm
        bore_r = h.bore_dia / 2.0  # 58mm
        expected_area = math.pi * (housing_r**2 - bore_r**2)  # ~741 mm²

        assert abs(area - expected_area) / expected_area < 0.05, (
            f"Section area {area:.1f}mm² vs expected annulus {expected_area:.1f}mm² "
            f"(>{5}% deviation)"
        )

    def test_output_bearing_seat(self, body_solid):
        """Section area at bearing zone should reflect the 90.15mm seat.

        At the bearing zone midpoint the annulus runs from 45.075mm
        to 60mm, minus 21 pin holes and 8 bolt holes.
        """
        g = CFG.gear
        h = CFG.housing
        tol = CFG.tolerances
        stack = CFG.stack_up

        bearing_mid = (
            stack.input_clearance
            + stack.disc_thickness * 2
            + stack.inter_disc_spacer
            + stack.output_clearance
            + stack.output_bearing_total / 2.0
        )  # 37mm

        section = body_solid.section(height=bearing_mid)
        area = section.val().Area()

        housing_r = h.od / 2.0  # 60mm
        bearing_seat_r = h.output_bearing_seat_dia / 2.0  # 45.075mm
        annulus_area = math.pi * (housing_r**2 - bearing_seat_r**2)

        # Subtract approximate pin and bolt hole areas
        pin_hole_r = (g.ring_pin_dia - tol.ring_pin_press_sub) / 2.0
        bolt_hole_r = (h.bolt_dia + 0.4) / 2.0
        pin_area = g.num_ring_pins * math.pi * pin_hole_r**2
        bolt_area = h.bolt_count * math.pi * bolt_hole_r**2
        expected_area = annulus_area - pin_area - bolt_area

        # Allow 15% tolerance for hole merging at coincident bolt/pin angles
        assert abs(area - expected_area) / expected_area < 0.15, (
            f"Bearing zone section area {area:.1f}mm² vs expected "
            f"{expected_area:.1f}mm² (>{15}% deviation)"
        )

    def test_volume_sanity(self, body_solid):
        """Volume should be between reasonable bounds.

        Lower bound: outer cylinder minus max possible bore, minus holes.
        Upper bound: outer cylinder minus min bore.
        """
        h = CFG.housing
        stack = CFG.stack_up
        body_h = stack.z_output_cap - stack.z_motor_plate_inner  # 47mm
        bore_r = h.bore_dia / 2.0  # 58mm
        housing_r = h.od / 2.0  # 60mm
        bearing_r = h.output_bearing_seat_dia / 2.0  # 45.075mm

        # Upper bound: full cylinder minus smallest bore (bearing seat through full height)
        upper = math.pi * housing_r**2 * body_h - math.pi * bearing_r**2 * body_h

        # Lower bound: thin-wall tube (116mm bore) for full height
        # (ignores the shoulder and bearing zone material, so very conservative)
        lower = math.pi * (housing_r**2 - bore_r**2) * body_h

        vol = body_solid.val().Volume()
        assert vol > lower, (
            f"Volume {vol:.0f}mm³ below lower bound {lower:.0f}"
        )
        assert vol < upper, (
            f"Volume {vol:.0f}mm³ above upper bound {upper:.0f}"
        )
