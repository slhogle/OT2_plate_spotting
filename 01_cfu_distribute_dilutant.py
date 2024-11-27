from opentrons import protocol_api

metadata = {
    "protocolName": "Distribute dilutant",
    "description": """Part 01 of the high-throughput droplet colony counting protocol. This protocol distributes the required volumes of dilutant to the 96 well plates.""",
    "author": "Shane Hogle"
}

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

#############
# Global vars
#############

DILUTE_PLATE_LOC = [1, 2, 3, 4, 5]
RESERVOIR_LOC = 6
TIPS300_LOC = 9

# set volumes of dilutant you want to use for 10 fold and 2 fold dilutions
TENFOLD_DILUTE_VOL = 90
TWOFOLD_DILUTE_VOL = 20

# change the position of the pipette (left/right) if necessary
P300_SIDE = "right"
P20_SIDE = "left"

###########
# Main body
###########


def run(protocol: protocol_api.ProtocolContext):

    # Loading labware

    tips300 = protocol.load_labware("opentrons_96_tiprack_300ul", TIPS300_LOC)

    p300_mult = protocol.load_instrument(
        "p300_multi_gen2", P300_SIDE, tip_racks=[tips300])

    # load plates that require dilutant
    plate_type = "corning_96_wellplate_360ul_flat"

    dilution_plates = [protocol.load_labware(
        plate_type, slot, label="Dilution Plates") for slot in DILUTE_PLATE_LOC]

    # Load the dilutant reservoir. This is the correct labware version for the autoclavable reservoirs in the lab. For running 5 full plates this should have at least 15 ml of dilutant
    dilutant = protocol.load_labware(
        "agilent_1_reservoir_290ml", RESERVOIR_LOC)

    # pick up tip
    p300_mult.pick_up_tip()

    # loop through the plates
    for plate in dilution_plates:

        # columns for 10-fold dilution. reference top row of the plate.
        ten_fold_row_list = [plate.rows()[0][col]
                             for col in [1, 2, 3, 4, 5, 7, 9, 11]]

        # columns for 2-fold dilution. reference top row of the plate.
        two_fold_row_list = [plate.rows()[0][col] for col in [6, 8, 10]]

        p300_mult.distribute(volume=TENFOLD_DILUTE_VOL,
                             source=dilutant['A1'],
                             dest=ten_fold_row_list,
                             new_tip="never")

        p300_mult.distribute(volume=TWOFOLD_DILUTE_VOL,
                             source=dilutant['A1'],
                             dest=two_fold_row_list,
                             new_tip="never")
    # trash the tips
    p300_mult.drop_tip()
