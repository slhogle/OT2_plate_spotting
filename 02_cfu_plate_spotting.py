from opentrons import protocol_api
from opentrons import types
from itertools import combinations, zip_longest
from math import floor

metadata = {
    "protocolName": "High-throughput plate spotting",
    "description": """Part 2 of the high-throughput droplet colony counting protocol. This protocol 
    performs serial dilutions of bacterial samples in column 1 of 96-well plate and then spots 1ul 
    of the different dilutions onto a rectangular tray. After some amount of time of outgrowth the
    spot can be imaged and quantified using a high-throughput imaging system such as the evos 
    m7000""",
    "author": "Shane Hogle"
}

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

# Functions ####################################################################


def aspirate_spot(pipette, well_source, agar_dest, spot_vol=2,
                  z_speed=50, spotting_dispense_rate=0.025):
    """Aspirates a volume + extra from a source well on a dilution plate. Then spots a defined
    volume (default 2 ul) onto agar using a safe approach. Pipette moves
    to safe height above the plate, slowly dispense a droplet, then slowly 
    lowers to touch the droplet to the agar surface"""
    pipette.aspirate(volume=spot_vol+3,
                     location=well_source,
                     rate=1)
    pipette.touch_tip(well_source)
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


def spot_transfer(pipette, mix, well_source, agar_dest, well_dest):
    if mix:
        pipette.mix(repetitions=5,
                    volume=20,
                    location=well_source,
                    rate=1)
        mix = False
    aspirate_spot(pipette=pipette,
                  well_source=well_source,
                  agar_dest=agar_dest,
                  spot_vol=2,
                  z_speed=50,
                  spotting_dispense_rate=0.025)
    pipette.blow_out(pipette.trash_container)
    pipette.transfer(volume=10,
                     source=well_source,
                     dest=well_dest,
                     mix_after=(5, 20),
                     new_tip="never",
                     blow_out=True,  # required to set location
                     blowout_location="destination well")
    return mix

# Main body ####################################################################


def run(protocol: protocol_api.ProtocolContext):

    # Loading labware ##########################################################

    # pipette tips on deck 9
    tips20 = [protocol.load_labware("opentrons_96_tiprack_20ul", 9)]

    # specify the pipette
    left_pipette = protocol.load_instrument(
        "p20_multi_gen2", "left", tip_racks=tips20)

    # load plates containing the samples to be spotted at different dilutions
    plate_type = "corning_96_wellplate_360ul_flat"
    locs = [4, 5, 6, 10, 11]  # change this if using fewer plates
    dilution_plates = [protocol.load_labware(plate_type, slot, label="dilution plate")
                       for slot in locs]

    # Load the agar plates. They can be any 96-well plate that isn't the same as dilution plate
    agar_plate_type = "biorad_96_wellplate_200ul_pcr"
    agar_locs = [1, 2, 3, 7, 8]  # change this if using fewer plates
    agar_plates = [protocol.load_labware(agar_plate_type, slot, label="agar tray")
                   for slot in agar_locs]

    for p_dl, p_ag in zip(dilution_plates, agar_plates):
        protocol.comment('''
                         ##############################
                         ####### CHANGING PLATE #######
                         ##############################
                         ''')
        left_pipette.pick_up_tip()
        mix = True
        for col in range(1, 12):
            w = 'A' + str(col)
            w_offset = 'A' + str(col+1)
            mix = spot_transfer(pipette=left_pipette,
                                mix=mix,
                                well_source=p_dl[w],
                                agar_dest=p_ag[w],
                                well_dest=p_dl[w_offset])
        # do final aspirate and spot to agar for column 12
        aspirate_spot(pipette=left_pipette,
                      well_source=p_dl['A12'],
                      agar_dest=p_ag['A12'],
                      spot_vol=2,
                      z_speed=50,
                      spotting_dispense_rate=0.025)
        left_pipette.drop_tip()
