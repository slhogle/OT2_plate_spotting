from opentrons import protocol_api

metadata = {
    "protocolName": "Distribute dilutant",
    "description": """Part 01 of the high-throughput droplet colony counting protocol. This
                      protocol distributes the required volumes of dilutant to the 96 well
                      plates.""",
    "author": "Shane Hogle"
}

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

# Functions ####################################################################


# Main body ####################################################################

def run(protocol: protocol_api.ProtocolContext):

    # Loading labware ##########################################################

    # load pipette tips at deck 9
    tips300 = protocol.load_labware("opentrons_96_tiprack_300ul", 9)

    # IMPORTANT!!! CHANGE the position of the pipette (left/right) if necessary
    p300_mult = protocol.load_instrument(
        "p300_multi_gen2", "right", tip_racks=[tips300])

    # load plates that require dilutant
    plate_type = "corning_96_wellplate_360ul_flat"

    # IMPORTANT!!! CHANGE ME this if using fewer plates. The default is: locs = [4, 5, 6, 10, 11]
    # for running the full protocol with 5 plates = 40 samples
    locs = [4, 5, 6, 10, 11]
    dilution_plates = [protocol.load_labware(plate_type, slot, label="Dilution Plates")
                       for slot in locs]

    # Load the dilutant reservoir at deck 8. This is the correct labware version for the
    # autoclavable reservoirs in the lab. This should have at least 10 ml of dilutant
    reservoir = protocol.load_labware("agilent_1_reservoir_290ml", 8)

    # IMPORTANT!!! CHANGE ME to the column of the first available tip. This is necessary if you are
    # using a tip box where some of the tips have already been used. By default it is set to the
    # first column/position (A1) in the tip box. NEVERMIND! this doesn't work for multichannel for
    # some reason. So the robot will always start from Column A.
    # p300_mult.starting_tip = tips300['A1']

    # we will do manual tip management because we are only pipetting dilutant (M9)
    p300_mult.pick_up_tip()

    for plate in dilution_plates:
        # get top row of the plate. these are the columns to dispense 100 ul
        row_list_100 = [plate.rows()[0][col]
                        for col in [1, 2, 3, 4, 5, 6, 8, 10]]
        # these are the columns to dispense
        row_list_50 = [plate.rows()[0][col] for col in [7, 9]]

        p300_mult.transfer(volume=90,
                           source=reservoir['A1'],
                           dest=row_list_100,
                           new_tip="never")
        p300_mult.transfer(volume=50,
                           source=reservoir['A1'],
                           dest=row_list_50,
                           new_tip="never")

    # drop tip and protocol ends
    p300_mult.drop_tip()
