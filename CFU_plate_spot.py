from opentrons import protocol_api

metadata = {
    "protocolName": "Tray spotting",
    "description": """Spots dilutions from a 96-well plate onto rectangular Omnitrays with agar.""",
    "author": "Shane Hogle"
}

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}


#############
# Global vars
#############

# Plate dictionary has dilution 96-well plate as key and list of agar plates as values
# for example {1: [4,7]} would indicate the dilution plate in deck position 1 will be spotted
# in dulicate onto agar trays in deck positions 4 and 7.
PLATE_DICTIONARY = {1: [4,7], 2: [5,8]}

# Each plate dilution series will require one column of tips
TIPS20_LOC = [10]

# change the position of the pipette (left/right) if necessary
P300_SIDE = "right"
P20_SIDE = "left"

# can manually set starting tip if the tip box has had some of the tips used
#STARTING_TIP = "A2"

#if STARTING_TIP is None:
#    STARTING_TIP = "A1"

# setting to True tells the robot to return the tips to the rack
# in all steps. This is useful for prototyping, but DO NOT USE for
# real work
TESTRUN = False

# Spotting volume in ul
SPOT_VOL = 2

###########
# Functions
###########

def mix_aspirate(pipette, well_source, mix=True, mixreps=1):
    if mix:
        pipette.mix(repetitions=mixreps,
                    volume=20,
                    location=well_source)

        pipette.aspirate(volume=20,
                         location=well_source)


def spot(pipette, agar_dest, spot_vol=SPOT_VOL, z_speed=75, spotting_dispense_rate=0.15):
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
    # Column 9 = E-8, Column 8 = E-7, Column 7 = E-6, Column 6 = E-5, Column 5 = E-4
    source_pos = [8, 7, 6, 5]
    target_pos = [12, 9, 6, 3]

    for s_pos, t_pos in zip(source_pos, target_pos):
        s_well = 'A'+str(s_pos)
        # mix then aspirate full pipette from source well
        mix_aspirate(pipette, source_plate[s_well], mix=True, mixreps=1)
        # spot in three columns for each dilution (technical replicates)
        for ta in target_agar:
            for t in [t_pos, t_pos-1, t_pos-2]:
                t_well = 'A'+str(t)
                spot(pipette, ta[t_well],
                     spot_vol=SPOT_VOL, z_speed=75,
                     spotting_dispense_rate=0.5)
        # dispense any remaining volume back into the source well
        pipette.dispense(location=source_plate[s_well])
        # force the remaining volume out. there is also the push_out parameter on dispense, but using it resulted in an error for me: https://docs.opentrons.com/v2/basic_commands/liquids.html#push-out-after-dispense
        pipette.blow_out(source_plate[s_well])
        # try and knock off remaining droplets from the blowout
        #pipette.touch_tip(source_plate[s_well])
    if test_run:
        pipette.return_tip()
    else:
        pipette.drop_tip()

###########
# Main body
###########

def run(protocol: protocol_api.ProtocolContext):

    # Loading tips
    tips20 = [protocol.load_labware(
        "opentrons_96_tiprack_20ul", slot) for slot in TIPS20_LOC]
    
    # load p20 pipette
    p20_mult = protocol.load_instrument(
        "p20_multi_gen2", P20_SIDE, tip_racks=tips20)

    #p20_mult.starting_tip = tips20.well(STARTING_TIP)

    for plate_dil,plate_agar in PLATE_DICTIONARY.items():
        
        dilution_plate = protocol.load_labware("corning_96_wellplate_360ul_flat", plate_dil, label="dilution plate")
        
        agar_plates = [protocol.load_labware("biorad_96_wellplate_200ul_pcr", slot, label="agar plate") for slot in plate_agar]
        
        mix_aspirate_spot(p20_mult, dilution_plate, agar_plates, test_run=TESTRUN)