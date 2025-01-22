from opentrons import protocol_api

metadata = {
    "protocolName": "Step 02: Serial dilution and agar spotting",
    "description": """Performs serial dilutions of bacterial samples in column 1 of 96-well plate and spots the dilutions on an agar tray.""",
    "author": "Shane Hogle"
}

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

#############
# Global vars
#############

DILUTE_PLATE_LOC = [3]
AGAR_PLATE_LOC = [6]
TIPS300_LOC = [9]
TIPS20_LOC = [10]

# set volumes of dilutant you want to use for 10 fold and 2 fold dilutions
TENFOLD_TRANS_VOL = 20

# change the position of the pipette (left/right) if necessary
P300_SIDE = "right"
P20_SIDE = "left"

# setting to True tells the robot to return the tips to the rack
# in all steps. This is useful for prototyping, but DO NOT USE for
# real work
TESTRUN = False

###########
# Functions
###########


def serial_dilution(pipette, transfer_volume, source, destination, test_run=False):
    if test_run:
        trash = False
    else:
        trash = True
    pipette.transfer(transfer_volume,
                     source,
                     destination,
                     mix_before=(2, 100),
                     mix_after=(2, 100),
                     new_tip="always",
                     trash=trash)


def mix_aspirate(pipette, well_source, mix=True, mixreps=1):
    if mix:
        pipette.mix(repetitions=mixreps,
                    volume=20,
                    location=well_source)

        pipette.aspirate(volume=20,
                         location=well_source)


def spot(pipette, agar_dest, spot_vol=1.5, z_speed=75, spotting_dispense_rate=0.15):
    """Aspirates a volume + extra from a source well on a dilution plate. Then spots a defined volume (default 2 ul) onto agar using a safe approach. Pipette moves to safe height above the plate, slowly dispense a droplet, then slowly lowers to touch the droplet to the agar surface. This has an extra mixing step compared to the function in script 02_cfu_serial_dilution_spot.py"""

    # for safety, set the z-axis speed limit to default of 75 mm/s.
    pipette.default_speed = z_speed
    # now slowly move to 2 mm above the top center of the well
    pipette.move_to(agar_dest.top(2))
    # dispense the spot volume. The drop will probably hang at the bottom of the tip
    pipette.dispense(volume=spot_vol, rate=spotting_dispense_rate)
    # this needs to be calibrated so that top is right at the surface of the agar in the well plate!
    pipette.move_to(agar_dest.top(0))
    # reset the max Z speed to 400
    pipette.default_speed = None


def mix_aspirate_spot(pipette, source_plate, target_agar, test_run=False):
    pipette.pick_up_tip()
    source_pos = [9, 8, 7, 6]
    target_pos = [12, 9, 6, 3]

    for s_pos, t_pos in zip(source_pos, target_pos):
        s_well = 'A'+str(s_pos)
        # mix then aspirate full pipette from source well
        mix_aspirate(pipette, source_plate[s_well], mix=True, mixreps=1)
        # spot in three columns for each dilution (technical replicates)
        for t in [t_pos, t_pos-1, t_pos-2]:
            t_well = 'A'+str(t)
            spot(pipette, target_agar[t_well],
                 spot_vol=2, z_speed=75,
                 spotting_dispense_rate=0.5)
        # dispense any remaining volume back into the source well
        pipette.dispense(location=source_plate[s_well])
        # force the remaining volume out. there is also the push_out parameter on dispense, but using it resulted in an error for me: https://docs.opentrons.com/v2/basic_commands/liquids.html#push-out-after-dispense
        pipette.blow_out(source_plate[s_well])
        # try and knock off remaining droplets from the blowout
        pipette.touch_tip(source_plate[s_well])

    if test_run:
        pipette.return_tip()
    else:
        pipette.drop_tip()

###########
# Main body
###########


def run(protocol: protocol_api.ProtocolContext):

    # Tips
    tips20 = [protocol.load_labware(
        "opentrons_96_tiprack_20ul", slot) for slot in TIPS20_LOC]
    tips300 = [protocol.load_labware(
        "opentrons_96_tiprack_300ul", slot) for slot in TIPS300_LOC]
    # Pipettes
    p20_mult = protocol.load_instrument(
        "p20_multi_gen2", P20_SIDE, tip_racks=tips20)
    p300_mult = protocol.load_instrument(
        "p300_multi_gen2", P300_SIDE, tip_racks=tips300)
    # Dilution plates
    dilution_plates = [protocol.load_labware(
        "corning_96_wellplate_360ul_flat", slot, label="dilution plate") for slot in DILUTE_PLATE_LOC]
    # Agar plates
    agar_plates = [protocol.load_labware(
        "biorad_96_wellplate_200ul_pcr", slot, label="agar plate") for slot in AGAR_PLATE_LOC]

    for plate_dil, plate_agar in zip(dilution_plates, agar_plates):
        serial_dilution(p300_mult, TENFOLD_TRANS_VOL,
                        plate_dil.rows()[0][0:8],
                        plate_dil.rows()[0][1:9],
                        test_run=TESTRUN)

        mix_aspirate_spot(p20_mult, plate_dil, plate_agar, test_run=TESTRUN)

        # return lids to the finished well plate and tray, and take the covers off the next well plate and tray in the series
        protocol.comment("(Un)Cover plates and trays")
        protocol.delay(seconds=20, minutes=0)
