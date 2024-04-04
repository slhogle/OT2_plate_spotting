from opentrons import protocol_api

metadata = {
    "protocolName": "Dilution series and agar spotting",
    "description": """Part 2 of the high-throughput droplet colony counting protocol. This protocol 
    performs serial dilutions of bacterial samples in column 1 of 96-well plate and then spots 1ul 
    of the different dilutions onto a rectangular tray. After some amount of time of outgrowth the
    spot can be imaged and quantified using a high-throughput imaging system such as the evos 
    m7000""",
    "author": "Shane Hogle"
}

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

# Functions ####################################################################


def aspirate_spot(pipette, well_source, agar_dest, spot_vol=1.5,
                  z_speed=75, spotting_dispense_rate=0.05):
    """Aspirates a volume + extra from a source well on a dilution plate. Then spots a defined
    volume (default 2 ul) onto agar using a safe approach. Pipette moves
    to safe height above the plate, slowly dispense a droplet, then slowly 
    lowers to touch the droplet to the agar surface"""
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
    # force the remaining volume out. there is also the push_out parameter on dispsense, but using
    # it resulted in an error for me: https://docs.opentrons.com/v2/basic_commands/liquids.html#push-out-after-dispense
    pipette.blow_out(well_source)
    # try and knock off remaining droplets from the blowout
    pipette.touch_tip(well_source)


def transfer(pipette, volume, n_mix, well_source, well_dest):
    pipette.transfer(volume=volume,
                     source=well_source,
                     dest=well_dest,
                     mix_before=(n_mix, 20),
                     # mix_after=(n_mix, 20),
                     new_tip="never",
                     # touch_tip=True,
                     # blow_out=True,  # required to set location
                     # blowout_location="destination well"
                     )

# Main body ####################################################################


def run(protocol: protocol_api.ProtocolContext):

    # Loading labware ##########################################################

    # pipette tips on deck 9
    tips20 = protocol.load_labware("opentrons_96_tiprack_20ul", 9)

    # IMPORTANT!!! CHANGE the position of the pipette (left/right) if necessary
    p20_mult = protocol.load_instrument(
        "p20_multi_gen2", "left", tip_racks=[tips20])

    # load plates containing the samples to be spotted at different dilutions
    plate_type = "corning_96_wellplate_360ul_flat"

    # IMPORTANT!!! CHANGE ME this if using fewer plates. The default is: locs = [4, 5, 6, 10, 11]
    # if running the full protocol with 5 plates = 40 samples
    locs = [4, 5, 6, 10, 11]
    dilution_plates = [protocol.load_labware(plate_type, slot, label="dilution plate")
                       for slot in locs]

    # Load the agar plates. They can be any 96-well plate that isn't the same as dilution plate
    agar_plate_type = "biorad_96_wellplate_200ul_pcr"

    # IMPORTANT!!! CHANGE ME this if using fewer plates. The default is: agar_locs = [1, 2, 3, 7, 8]
    # if running the full protocol with 5 plates = 40 samples
    agar_locs = [1, 2, 3, 7, 8]
    agar_plates = [protocol.load_labware(agar_plate_type, slot, label="agar tray")
                   for slot in agar_locs]

    # IMPORTANT!!! CHANGE ME to the column of the first available tip. This is necessary if you are
    # using a tip box where some of the tips have already been used. By default it is set to the
    # first column/position (A1) in the tip box. NEVERMIND! this doesn't work for multichannel for
    # some reason. So the robot will always start from Column A.
    # p20_mult.starting_tip = tips20['A1']

    for p_dl, p_ag in zip(dilution_plates, agar_plates):
        p20_mult.pick_up_tip()
        # transfer 10 ul from column 1 to 7
        for col in range(1, 8):
            w = 'A' + str(col)
            w_offset = 'A' + str(col+1)
            transfer(p20_mult, 10, 3, p_dl[w], p_dl[w_offset])
        # do last transfers where some are 2-fold dilution
        transfer(p20_mult, 50, 3, p_dl['A7'], p_dl['A8'])
        transfer(p20_mult, 10, 3, p_dl['A8'], p_dl['A9'])
        transfer(p20_mult, 50, 3, p_dl['A9'], p_dl['A10'])
        transfer(p20_mult, 10, 3, p_dl['A10'], p_dl['A11'])

        # Now work backwards to spot onto the agar from least concentrated to most concentrated.
        # Important to start from column A11 because A12 and A1 are full concentration. These should
        # be spotted last
        for col in reversed(range(2, 12)):
            w = 'A' + str(col)
            aspirate_spot(p20_mult, p_dl[w], p_ag[w], spot_vol=1.5,
                          z_speed=75, spotting_dispense_rate=0.05)
        # now spot the full concentration samples in A1 and A12
        aspirate_spot(p20_mult, p_dl['A1'], p_ag['A1'], spot_vol=1.5,
                      z_speed=75, spotting_dispense_rate=0.05)
        aspirate_spot(p20_mult, p_dl['A12'], p_ag['A12'], spot_vol=1.5,
                      z_speed=75, spotting_dispense_rate=0.05)
        p20_mult.drop_tip()
