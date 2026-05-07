"""Validation test suite for the shared housing-profile cutter.

The cutter at ``src/helpers/housing_profile.py`` defines the 8-pillar /
8-window outer profile shared by the motor plate, ring gear body, and
output cap.  These tests exercise the helper directly so that any change
to the profile (pillar dims, bolt angles, bore radii) is caught here
before the dependent part tests.

Tests cover:
  1. Cutter solid validity, bounding box, and volume sanity
  2. Pillar voids in the cutter line up with bolt angles (sample-point
     checks confirm material-vs-void at expected (r, θ) locations)
  3. Cross-part alignment — motor plate, ring gear body, and output cap
     all show solid material at every pillar centre and a void at every
     window centre (mid-Z slice).
"""

import math
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.params import DEFAULT_CONFIG, compute_housing_bolt_angles

CFG = DEFAULT_CONFIG


# ===================================================================
# 1. Direct cutter checks
# ===================================================================


class TestCutter:

    @pytest.fixture(scope="class")
    def cutter(self):
        cq = pytest.importorskip("cadquery")
        from src.helpers.housing_profile import build_reveal_window_cutter

        return build_reveal_window_cutter(CFG, height=10.0)

    def test_solid_is_valid(self, cutter):
        """Subtracting 8 pillars from the annular ring produces 8 disjoint
        window-shaped solids, one per inter-pillar gap."""
        solids = cutter.solids().vals()
        assert len(solids) == CFG.housing.bolt_count, (
            f"Expected {CFG.housing.bolt_count} solids (one per window), "
            f"got {len(solids)}"
        )
        for s in solids:
            assert s.isValid()

    def test_bounding_box(self, cutter):
        """Cutter spans housing OD in XY and the full requested height in Z.

        The outermost X (and Y, by symmetry) is reached just off-axis at
        the corner where a pillar's trapezoidal edge meets the outer
        annulus circle — slightly less than ``od + 0.2mm`` because the
        pillars eat into the outer ring at the bolt axes.
        """
        bb = cutter.val().BoundingBox()
        # Loose: span is between the bore (116mm) and OD overshoot (140.2mm).
        x_span = bb.xmax - bb.xmin
        y_span = bb.ymax - bb.ymin
        assert CFG.housing.bore_dia < x_span < CFG.housing.od + 0.2
        assert CFG.housing.bore_dia < y_span < CFG.housing.od + 0.2
        # Z span is exact.
        assert abs((bb.zmax - bb.zmin) - 10.0) < 0.05

    def test_volume_sanity(self, cutter):
        """Cutter volume ≈ annular wall − 8 trapezoidal pillars.

        Annular wall: π * (housing_r² − bore_r²) * height (using the 0.1mm
        overshoot makes < 1% difference, ignored).  Each pillar ≈ trapezoid
        with parallel sides 18mm (at bore) and 10mm (at OD), radial span
        clipped to the wall (~12mm).
        """
        h = CFG.housing
        housing_r = h.od / 2.0
        bore_r = h.bore_dia / 2.0
        height = 10.0

        annular = math.pi * (housing_r ** 2 - bore_r ** 2) * height
        # Pillar trapezoid clipped to the wall (radial span = housing_r − bore_r)
        radial_span = housing_r - bore_r
        pillar_area = (18.0 + 10.0) / 2.0 * radial_span
        pillars = h.bolt_count * pillar_area * height

        expected = annular - pillars
        vol = cutter.val().Volume()
        # 15% margin — overshoot, trapezoid clipping, and bolt-hole interactions
        assert abs(vol - expected) / expected < 0.15, (
            f"Cutter volume {vol:.0f}mm³ vs expected {expected:.0f}mm³"
        )


# ===================================================================
# 2. Material-vs-void sample-point checks across all three parts
# ===================================================================


def _is_inside(solid, x, y, z):
    """Return True if point (x, y, z) is inside the CadQuery solid."""
    cq = pytest.importorskip("cadquery")
    return solid.val().isInside(cq.Vector(x, y, z), 1e-6)


class TestProfileAlignment:
    """All three housing parts must show solid at pillar centres and void
    at window centres, at the same (r, θ) coordinates."""

    @pytest.fixture(scope="class")
    def parts(self):
        pytest.importorskip("cadquery")
        from src.motor_plate import build_motor_plate
        from src.ring_gear_body import build_ring_gear_body
        from src.output_cap import build_output_cap
        from src.params import DEFAULT_CONFIG as CFG

        # Each part's pillar zone — sample at a Z near mid-thickness.
        return [
            ("motor_plate", build_motor_plate(), 5.0),
            ("ring_gear_body", build_ring_gear_body(), 23.5),
            ("output_cap", build_output_cap(), 4.0),
        ]

    def test_pillar_centres_are_solid(self, parts):
        """At every bolt angle, sample a point on the bolt circle (62.5mm)
        offset slightly tangentially to avoid the M4 through-hole.  All
        three parts must have material there.
        """
        bolt_r = CFG.housing.bolt_circle_dia / 2.0  # 62.5mm
        # Offset 4mm tangentially → still inside pillar (≥6mm half-width
        # at bolt radius), well clear of the 4.4mm-⌀ bolt hole.
        offset = 4.0
        for angle in compute_housing_bolt_angles(CFG):
            x = bolt_r * math.cos(angle) - offset * math.sin(angle)
            y = bolt_r * math.sin(angle) + offset * math.cos(angle)
            for name, part, z in parts:
                assert _is_inside(part, x, y, z), (
                    f"{name}: expected solid at pillar centre "
                    f"angle={math.degrees(angle):.1f}° (x={x:.2f}, y={y:.2f}, z={z})"
                )

    def test_window_centres_are_void(self, parts):
        """Midway between bolt angles (window centres), the outer ring
        must be void in all three parts.  Sample at radius 64mm — outside
        the pillar trapezoid edge at that angle, well inside the 70mm OD.
        """
        bolt_angles = compute_housing_bolt_angles(CFG)
        step = 2 * math.pi / CFG.housing.bolt_count
        sample_r = 64.0  # between pillar_inner_r=57 and housing_r=70
        for angle in bolt_angles:
            mid = angle + step / 2.0
            x = sample_r * math.cos(mid)
            y = sample_r * math.sin(mid)
            for name, part, z in parts:
                assert not _is_inside(part, x, y, z), (
                    f"{name}: expected void at window centre "
                    f"angle={math.degrees(mid):.1f}° (x={x:.2f}, y={y:.2f}, z={z})"
                )
