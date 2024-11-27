from opentrons import protocol_api

metadata = {
    "protocolName": "Dilution series and agar spotting",
    "description": """Part 2 of the high-throughput droplet colony counting protocol. This protocol performs serial dilutions of bacterial samples in column 1 of 96-well plate.""",
    "author": "Shane Hogle"
}

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

#############
# Global vars
#############

DILUTE_PLATE_LOC = [1, 2, 3]
AGAR_PLATE_LOC = [4, 5, 6]
# Each plate dilution series will require one full box of tips
TIPS20_LOC = [7, 8, 9]

# set volumes of dilutant you want to use for 10 fold and 2 fold dilutions
TENFOLD_TRANS_VOL = 10
TWOFOLD_TRANS_VOL = 20

# change the position of the pipette (left/right) if necessary
P300_SIDE = "right"
P20_SIDE = "left"

###########
# Functions
###########


def aspirate_spot(pipette, well_source, agar_dest, spot_vol=1.5, z_speed=75, spotting_dispense_rate=0.05):
    """Aspirates a volume + extra from a source well on a dilution plate. Then spots a defined volume (default 2 ul) onto agar using a safe approach. Pipette moves to safe height above the plate, slowly dispense a droplet, then slowly lowers to touch the droplet to the agar surface"""
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


def transfer_spot(pipette, dilution_plate, agar_plate, transfer_volume, column, offset):
    pipette.pick_up_tip()
    well_source = 'A' + str(column)
    well_target = 'A' + str(column+offset)
    pipette.transfer(transfer_volume,
                     dilution_plate[well_source],
                     dilution_plate[well_target],
                     mix_before=(3, 20),
                     new_tip="never")
    aspirate_spot(pipette,
                  dilution_plate[well_target],
                  agar_plate[well_target],
                  spot_vol=1.5,
                  z_speed=75,
                  spotting_dispense_rate=0.05)
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

    # load plates to be transferred
    dilution_plates = [protocol.load_labware(
        "corning_96_wellplate_360ul_flat", slot, label="dilution plate") for slot in DILUTE_PLATE_LOC]

    # load agar plates for spotting
    agar_plates = [protocol.load_labware(
        "biorad_96_wellplate_200ul_pcr", slot, label="agar plate") for slot in AGAR_PLATE_LOC]

    for plate_dil, plate_agar in zip(dilution_plates, agar_plates):
        # works on 10-fold dilution from A1-A6
        for col in range(1, 6, 1):
            transfer_spot(p20_mult,
                          plate_dil,
                          plate_agar,
                          TENFOLD_TRANS_VOL,
                          col, 1)
        # works on 10-fold dilution from A6-A12, skipping every second
        for col in range(6, 11, 2):
            transfer_spot(p20_mult,
                          plate_dil,
                          plate_agar,
                          TENFOLD_TRANS_VOL,
                          col, 2)
        # works on 2-fold dilution from A7, A9, and A11, transferring from the prior well
        for col in range(6, 11, 2):
            transfer_spot(p20_mult,
                          plate_dil,
                          plate_agar,
                          TWOFOLD_TRANS_VOL,
                          col, 1)

        # return lids to the finished well plate and tray, and take the covers off the next well plate and tray in the series
        protocol.pause("(Un)Cover plates and trays")

        # this delays the protocol for 20 seconds
        # protocol.delay(seconds=20)
