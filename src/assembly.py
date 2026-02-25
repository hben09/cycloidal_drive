"""Interactive viewer — compose and display selected parts.

Run this file to visualize parts together in OCP CAD Viewer.
Comment/uncomment sections to show what you want to see.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import cadquery as cq
from ocp_vscode import show_object

from src.params import DEFAULT_CONFIG
from src.cycloidal_disc import build_cycloidal_disc
from src.eccentric_shaft import build_eccentric_shaft
from src.motor_plate import build_motor_plate
from src.purchased_parts import (
    build_bearing_6003,
    build_bearing_6814,
    build_nema17_motor,
    build_ring_pins,
    build_output_pins,
)

cfg = DEFAULT_CONFIG
stack = cfg.stack_up
e = cfg.gear.eccentricity  # 1.5mm

# At input angle φ=0, disc 1 center is at (+e, 0) and disc 2 at (-e, 0).
# Each disc + bearing is concentric with its shaft lobe.

# ── Disc 1 + its 6003 bearing ──────────────────────────────────
disc1 = build_cycloidal_disc()
disc1 = disc1.translate((e, 0, stack.z_disc1))

bearing_6003_1 = build_bearing_6003()
bearing_6003_1 = bearing_6003_1.translate((e, 0, stack.z_disc1))

show_object(disc1, name="disc_1", options={"color": "steelblue", "alpha": 0.6})
show_object(bearing_6003_1, name="bearing_6003_1", options={"color": "orange"})

# ── Disc 2 + its 6003 bearing (180° offset) ────────────────────
disc2 = build_cycloidal_disc()
disc2 = disc2.rotateAboutCenter((0, 0, 1), 180).translate((-e, 0, stack.z_disc2))

bearing_6003_2 = build_bearing_6003()
bearing_6003_2 = bearing_6003_2.translate((-e, 0, stack.z_disc2))

show_object(disc2, name="disc_2", options={"color": "lightblue", "alpha": 0.6})
show_object(bearing_6003_2, name="bearing_6003_2", options={"color": "orange"})

# ── 6814 output bearings ─────────────────────────────────────
# bearing_6814_1 = build_bearing_6814()
# bearing_6814_1 = bearing_6814_1.translate((0, 0, stack.z_output_bearings))
# show_object(bearing_6814_1, name="bearing_6814_1", options={"color": "coral"})

# bearing_6814_2 = build_bearing_6814()
# bearing_6814_2 = bearing_6814_2.translate((0, 0, stack.z_output_bearings + cfg.bearings.out_width))
# show_object(bearing_6814_2, name="bearing_6814_2", options={"color": "coral"})

# ── Eccentric shaft ────────────────────────────────────────────
shaft = build_eccentric_shaft()
show_object(shaft, name="eccentric_shaft", options={"color": "silver"})

# ── Ring pins ──────────────────────────────────────────────────
# pins = build_ring_pins()
# pins = pins.translate((0, 0, stack.z_disc1))
# show_object(pins, name="ring_pins", options={"color": "gray"})

# ── Output pins ────────────────────────────────────────────────
# output = build_output_pins()
# output = output.translate((0, 0, stack.z_disc1))
# show_object(output, name="output_pins", options={"color": "darkgray"})

# ── Motor ──────────────────────────────────────────────────────
motor = build_nema17_motor()
show_object(motor, name="nema17_motor", options={"color": "dimgray"})

# ── Motor plate ──────────────────────────────────────────────────
motor_plate = build_motor_plate()
show_object(motor_plate, name="motor_plate", options={"color": "slategray", "alpha": 0.4})
