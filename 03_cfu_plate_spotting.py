from opentrons import protocol_api

metadata = {
    "protocolName": "Dilution series and agar spotting",
    "description": """Part 3 of the high-throughput droplet colony counting protocol. This protocol spots a small volume of the different dilutions onto a rectangular tray.""",
    "author": "Shane Hogle"
}

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}


#############
# Global vars
#############

DILUTE_PLATE_LOC = [1]
AGAR_PLATE_LOC = [4]
# Each plate dilution series will require one full box of tips
TIPS20_LOC = [7]

# change the position of the pipette (left/right) if necessary
P300_SIDE = "right"
P20_SIDE = "left"

###########
# Functions
###########


def aspirate_spot(pipette, well_source, agar_dest, spot_vol=1.5, z_speed=75, spotting_dispense_rate=0.05, mix=True, mixreps=1):
    """Aspirates a volume + extra from a source well on a dilution plate. Then spots a defined volume (default 2 ul) onto agar using a safe approach. Pipette moves to safe height above the plate, slowly dispense a droplet, then slowly lowers to touch the droplet to the agar surface. This has an extra mixing step compared to the function in script 02_cfu_serial_dilution_spot.py"""
    if mix:
        pipette.mix(repetitions=mixreps,
                    volume=20,
                    location=well_source)

    pipette.aspirate(volume=15,
                     location=well_source)
    # for safety, set the z-axis speed limit to default of 50 mm/s.
    pipette.default_speed = z_speed
    # now slowly move to 2 mm above the top center of the well
    pipette.move_to(agar_dest.top(2))
    # dispense the spot volume. The drop will probably hang at the bottom of the tip
    pipette.dispense(volume=spot_vol, rate=spotting_dispense_rate)
    # this needs to be calibrated so that top is right at the surface of the agar in the well plate!
    pipette.move_to(agar_dest.top(0))
    # reset the max Z speed to 400
    pipette.default_speed = None
    # dispense the remaining volume back into the source well
    pipette.dispense(location=well_source)
    # force the remaining volume out. there is also the push_out parameter on dispense, but using it resulted in an error for me: https://docs.opentrons.com/v2/basic_commands/liquids.html#push-out-after-dispense
    pipette.blow_out(well_source)
    # try and knock off remaining droplets from the blowout
    # pipette.touch_tip(well_source)


def aspirate_spot_iterate(pipette, source_dilution, target_agar):
    pipette.pick_up_tip()
    for col in reversed(range(2, 13)):
        well_target = 'A' + str(col)
        aspirate_spot(pipette,
                      source_dilution[well_target],
                      target_agar[well_target],
                      spot_vol=2,
                      z_speed=75,
                      spotting_dispense_rate=0.5,
                      mix=True,
                      mixreps=1)
    pipette.drop_tip()

###########
# Main body
###########


def run(protocol: protocol_api.ProtocolContext):

    # Loading labware
    tips20 = [protocol.load_labware(
        "opentrons_96_tiprack_20ul", slot) for slot in TIPS20_LOC]

    p20_mult = protocol.load_instrument(
        "p20_multi_gen2", P20_SIDE, tip_racks=tips20)

    # load dilution series plates
    dilution_plates = [protocol.load_labware(
        "corning_96_wellplate_360ul_flat", slot, label="dilution plate") for slot in DILUTE_PLATE_LOC]

    # load agar plates for spotting
    agar_plates = [protocol.load_labware(
        "biorad_96_wellplate_200ul_pcr", slot, label="agar plate") for slot in AGAR_PLATE_LOC]

    for plate_dil, plate_agar in zip(dilution_plates, agar_plates):

        aspirate_spot_iterate(p20_mult, plate_dil, plate_agar)

        # return lids to the finished well plate and tray, and take the covers off the next well plate and tray in the series
        protocol.pause("(Un)Cover plates and trays")

        # this delays the protocol for 20 seconds
        # protocol.delay(seconds=20)
