from opentrons import protocol_api

metadata = {
    "protocolName": "Distribute dilutatnt",
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

    # specify the pipette
    right_pipette = protocol.load_instrument(
        "p300_multi_gen2", "right", tip_racks=[tips300])

    # load plates that require dilutant
    plate_type = "corning_96_wellplate_360ul_flat"
    # these are the locations you would use if running the full protocol with 5 plates = 40 samples
    locs = [4, 5, 6, 10, 11]
    dilution_plates = [protocol.load_labware(plate_type, slot, label="Dilution Plates")
                       for slot in locs]

    # load the dilutant reservoir at deck 8
    reservoir = protocol.load_labware("axygen_1_reservoir_90ml", 8)

    # we will do manual tip management because we are only pipetting dilutant (M9)
    right_pipette.pick_up_tip()

    for plate in dilution_plates:
        protocol.comment('''
                         ##############################
                         ####### CHANGING PLATE #######
                         ##############################
                         ''')
        # get top row of the plate
        # these are the columns to dispense 100 ul
        row_list_100 = [plate.rows()[0][col]
                        for col in [1, 2, 3, 4, 5, 6, 8, 10]]
        # these are the columns to dispense
        row_list_50 = [plate.rows()[0][col] for col in [7, 9]]

        right_pipette.transfer(volume=90,
                               source=reservoir['A1'],
                               dest=row_list_100,
                               new_tip="never")
        right_pipette.transfer(volume=50,
                               source=reservoir['A1'],
                               dest=row_list_50,
                               new_tip="never")

    # drop tip and protocol ends
    right_pipette.drop_tip()
