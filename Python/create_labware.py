from opentrons import labware, instruments
from opentrons.util.vector import Vector as v
from time import sleep

metadata = {
    'protocolName': 'HydraBot Labware Creation',
    'author': 'Ben Avants <bwa1@rice.edu>',
    'source': 'HydraBot Vivarium Project'
    }

def circle(location, radius, steps=50, pause=.05):
    step = 2 * 3.14159 / steps
    for i in range(steps):
        vect = location.from_center(r=radius, theta=step*i, h=1)
        pipette.move_to((location, vect), strategy='direct')
        sleep(pause)
    pipette.move_to(location, strategy='direct')

redefine = False
if redefine is True:
    from opentrons.data_storage import database
    database.delete_container('3x2_plate')
    database.delete_container('3x2_plate_eppendorf')
    database.delete_container('3x2_plate_corning')
    database.delete_container('3x2_plate_falcon')

#  6-well plate custom entry
plate_name = '3x2_plate_eppendorf'
if plate_name not in labware.list():
    hydra_plate = labware.create(
        plate_name,
        grid=(3, 2),
        spacing=(38, 40),
        diameter=35,
        depth=17,
        volume=3000
    )

plate_name = '3x2_plate_corning'
if plate_name not in labware.list():
    hydra_plate = labware.create(
        plate_name,
        grid=(3, 2),
        spacing=(39.12, 39.12),
        diameter=34.8,
        depth=17.4,
        volume=16800
    )

plate_name = '3x2_plate_falcon'
if plate_name not in labware.list():
    hydra_plate = labware.create(
        plate_name,
        grid=(3, 2),
        spacing=(39.24, 39.24),
        diameter=35.71,
        depth=17.65,
        volume=3000
    )

plate_2 = labware.load(plate_name, '2')

tiprack = labware.load('tiprack-1000ul', 11)

pipette = instruments.P1000_Single('right', tip_racks=[tiprack])

pipette.pick_up_tip()

pipette.aspirate(100, plate_2.wells('A1'))
sleep(2)

h = 20
x_off = 34/2
y_off = 34/2


locations = [('A1', v(x_off, 0, h)), ('A1', v(0, y_off, h)),
             ('A2', v(x_off, 0, h)), ('A2', v(0, y_off, h)),
             ('A3', v(x_off, 0, h)), ('A3', v(0, y_off, h)),
             ('B1', v(x_off, 0, h)), ('B1', v(0, y_off, h)),
             ('B2', v(x_off, 0, h)), ('B2', v(0, y_off, h)),
             ('B3', v(x_off, 0, h)), ('B3', v(0, y_off, h)),
             ]

for place in locations:
    pipette.move_to((plate_2.wells(place[0]), place[1]))
    sleep(2)

pipette.return_tip()
