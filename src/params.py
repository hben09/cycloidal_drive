"""Central parameter definitions for the cycloidal drive.

Every dimension from the spec lives here. Part files import DriveConfig
and never hardcode numbers.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GearParams:
    """Core gear geometry — spec Section 1.1 & 1.2."""

    num_lobes: int = 20
    num_ring_pins: int = 21  # N + 1
    eccentricity: float = 1.5  # mm
    ring_pin_circle_dia: float = 108.0  # mm
    ring_pin_dia: float = 4.0  # mm, h6 ground steel
    ring_pin_length: float = 30.0  # mm

    @property
    def ring_pin_circle_radius(self) -> float:
        return self.ring_pin_circle_dia / 2.0

    @property
    def ring_pin_radius(self) -> float:
        return self.ring_pin_dia / 2.0

    @property
    def gear_ratio(self) -> int:
        return self.num_lobes


@dataclass(frozen=True)
class DiscParams:
    """Cycloidal disc dimensions — spec Section 1.2 & 1.3."""

    thickness: float = 10.0  # mm, matches 6003 bearing width
    center_bore_dia: float = 35.20  # mm, 35mm bearing OD + 0.20mm clearance
    inter_disc_spacer: float = 2.0  # mm
    output_pin_count: int = 4
    output_pin_circle_dia: float = 60.0  # mm
    output_pin_dia: float = 4.0  # mm (M4)
    output_pin_hole_dia: float = 8.0  # mm (4mm + 2*1.5mm ecc + 1mm clearance)


@dataclass(frozen=True)
class ShaftParams:
    """Eccentric shaft dimensions — spec Section 1.4."""

    input_bore_dia: float = 5.0  # mm, matches motor shaft and 625 bearing bore
    bearing_seat_od: float = 17.0  # mm, matches 6003 bore
    eccentricity: float = 1.5  # mm
    spine_od: float = 5.0  # mm, shaft OD outside the lobe regions
    dcut_flat: float = 4.5  # mm, D-cut flat-to-round width (matches motor shaft)
    input_stub_length: float = 2.0  # mm, extends past motor-side 625 into coupler
    output_stub_length: float = 7.0  # mm, extends past disc 2 for output-side 625


@dataclass(frozen=True)
class BearingParams:
    """All bearing dimensions — spec Section 2."""

    # 6003-2RS (eccentric bearings)
    ecc_bore: float = 17.0  # mm
    ecc_od: float = 35.0  # mm
    ecc_width: float = 10.0  # mm
    ecc_qty: int = 2

    # 6814-2RS (output bearings)
    out_bore: float = 70.0  # mm
    out_od: float = 90.0  # mm
    out_width: float = 10.0  # mm
    out_qty: int = 2

    # 625-2RS (input shaft support)
    inp_bore: float = 5.0  # mm
    inp_od: float = 16.0  # mm
    inp_width: float = 5.0  # mm
    inp_qty: int = 2


@dataclass(frozen=True)
class HousingParams:
    """Housing dimensions — spec Section 5."""

    od: float = 120.0  # mm
    bore_dia: float = 116.0  # mm
    wall_thickness: float = 2.0  # mm
    motor_plate_wall: float = 5.0  # mm
    output_wall: float = 3.0  # mm
    bolt_count: int = 8
    bolt_circle_dia: float = 110.0  # mm
    bolt_dia: float = 4.0  # mm (M4)
    output_bearing_seat_dia: float = 90.15  # mm (press fit for 6814 outer race)


@dataclass(frozen=True)
class MotorParams:
    """NEMA 17 motor dimensions — spec Section 3.1."""

    shaft_dia: float = 5.0  # mm
    shaft_length: float = 20.0  # mm
    shaft_dcut_flat: float = 4.5  # mm, D-cut flat-to-round width
    shaft_dcut_length: float = 18.0  # mm, D-cut extends from shaft tip inward
    bolt_pattern_square: float = 31.0  # mm (center-to-center)
    bolt_dia: float = 3.0  # mm (M3)
    bolt_hole_depth: float = 4.5  # mm, threaded blind holes in mounting face
    pilot_dia: float = 22.0  # mm (NEMA 17 centering boss)
    body_width: float = 42.3  # mm (NEMA 17 standard)
    body_length: float = 48.0  # mm


@dataclass(frozen=True)
class CouplerParams:
    """Shaft coupler dimensions — spec Section 3.2."""

    od: float = 19.0  # mm
    length: float = 25.0  # mm
    bore: float = 5.0  # mm


@dataclass(frozen=True)
class OutputHubParams:
    """Output hub/plate dimensions — spec Section 5.3."""

    od: float = 70.0  # mm (matches 6814 bore, light press)
    shaft_clearance_bore: float = 5.4  # mm (5mm shaft + clearance)
    arm_mount_bolt_circle_dia: float = 50.0  # mm
    arm_mount_bolt_count: int = 4
    arm_mount_bolt_dia: float = 4.4  # mm (M4 clearance)


@dataclass(frozen=True)
class PETGTolerances:
    """PETG-specific fit adjustments — spec Section 6.

    Applied to nominal dimensions in part builders. Midpoints of spec ranges.
    """

    bearing_seat_bore_add: float = 0.075  # +0.05 to +0.10mm
    bearing_inner_shaft_sub: float = 0.075  # -0.05 to -0.10mm
    ring_pin_press_sub: float = 0.125  # -0.10 to -0.15mm
    sliding_clearance_add: float = 0.25  # +0.20 to +0.30mm
    mating_surface_add: float = 0.15  # +0.15mm


@dataclass(frozen=True)
class ProfileParams:
    """Epitrochoid profile generation settings."""

    num_points: int = 2000  # points per revolution
    spline_tolerance: float = 0.001  # mm, for CadQuery splineApprox


@dataclass(frozen=True)
class StackUp:
    """Axial stack-up Z positions — spec Section 4.

    Z=0 is the outer face of the motor plate (motor mounting face).
    All values in mm, measured from Z=0 inward.
    """

    motor_plate_wall: float = 5.0
    inp_bearing_seat: float = 5.0  # 625 bearing depth in motor plate
    coupler_clearance: float = 3.0
    disc_thickness: float = 10.0
    inter_disc_spacer: float = 2.0
    output_clearance: float = 2.0
    output_bearing_total: float = 20.0  # 2 x 6814 width
    output_wall: float = 3.0

    @property
    def z_motor_plate_inner(self) -> float:
        return self.motor_plate_wall + self.inp_bearing_seat  # 10mm

    @property
    def z_disc1(self) -> float:
        return self.z_motor_plate_inner + self.coupler_clearance  # 13mm

    @property
    def z_disc2(self) -> float:
        return self.z_disc1 + self.disc_thickness + self.inter_disc_spacer  # 25mm

    @property
    def z_output_bearings(self) -> float:
        return self.z_disc2 + self.disc_thickness + self.output_clearance  # 37mm

    @property
    def z_output_cap(self) -> float:
        return self.z_output_bearings + self.output_bearing_total  # 57mm

    @property
    def total_housing_depth(self) -> float:
        return self.z_output_cap + self.output_wall  # 60mm


@dataclass
class DriveConfig:
    """Top-level configuration aggregating all parameter groups."""

    gear: GearParams = field(default_factory=GearParams)
    disc: DiscParams = field(default_factory=DiscParams)
    shaft: ShaftParams = field(default_factory=ShaftParams)
    bearings: BearingParams = field(default_factory=BearingParams)
    housing: HousingParams = field(default_factory=HousingParams)
    motor: MotorParams = field(default_factory=MotorParams)
    coupler: CouplerParams = field(default_factory=CouplerParams)
    output_hub: OutputHubParams = field(default_factory=OutputHubParams)
    tolerances: PETGTolerances = field(default_factory=PETGTolerances)
    profile: ProfileParams = field(default_factory=ProfileParams)
    stack_up: StackUp = field(default_factory=StackUp)


# Default configuration instance
DEFAULT_CONFIG = DriveConfig()
