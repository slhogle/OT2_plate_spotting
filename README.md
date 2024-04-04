# Introduction

This is a protocol to dilute and spot bacteria for colony forming unit (CFU) quantification.
Bacterial samples are passed through a series of 10x and 2x serial dilutions with each dilution
spotted onto a rectangular agar plate such as the [Nunc
OmniTray](https://www.sigmaaldrich.com/FI/en/product/sigma/o0764) or something similar. These
plates are incubated for some duration of time, which needs to be optimized by species, and then
imaged using an instrument like the Evos m7000 to count the colonies at the different dilutions. The
protocol can process up to 40 bacterial samples at a time (5 plates x 8 wells (1 column) per plate).
This protocol was strongly inspired by the protocol [available here](https://protocols.opentrons.com/protocol/33y0f3).

# Reagents

- Agar media (usually PPY), sterile
- M9, sterile

# Equipment

- Standard lab 1-well reservoir (the kind that can be autoclaved) for M9 dilutant (e.g., axygen_1_reservoir_90ml)
- 96 well plates for the serial dilution
- Rectangular tray (e.g., the [Nunc
OmniTray](https://www.sigmaaldrich.com/FI/en/product/sigma/o0764) or something similar) with *30 ml*
of the selective agar of choice
- [Opentrons P20 8 Channel Electronic Pipette (GEN2)](https://shop.opentrons.com/8-channel-electronic-pipette/)
- [Opentrons OT-2 96 Tip Rack - 20 µL](https://shop.opentrons.com/opentrons-20-l-tips-160-racks-800-refills/)
  ## Optional: if using OT2 to distribute dilutant
- [Opentrons P300 8 Channel Electronic Pipette (GEN2)](https://shop.opentrons.com/8-channel-electronic-pipette/)
- [Opentrons OT-2 96 Tip Rack - 300 µL](https://shop.opentrons.com/opentrons-300ul-tips-1000-refills/)
  ## OR: if manually distributing dilutant to plate
- A multichannel pipette that can pipette 50 to 100 µl.

# IMPORTANT: Editing scripts
If you need to change defaults in these scripts you will need to edit the scripts directly before importing them into
the Opentrons app. The only things that would possibly need to be changed are:
1. If the p20 or p300 are on the left or right side of the robot. This can be
   reviewed/changed at line 26-27 of `01_cfu_distribute_dilutant.py` and line 68-69 of
   `02_cfu_plate_spotting.py`
2. If using fewer than the default 5 plates/40 samples then you need to change the plate
   numbers at line 34 of `01_cfu_distribute_dilutant.py` and lines 76 and 85 in
   `02_cfu_plate_spotting.py`
3. ~~If some columns of tips have already been used in your tip box then you can specify the tip
   position you want the robot to start from. The default is 'A1.' This can be changed at lines 45
   and 92 in the two scripts.~~  **NEVERMIND!** This works for a single channel pipette but not the
   multichannel. Thus, we will always need to start the protocol from column A of the tip box.

# Procedure

1. Gather the required reagents and disposables. Agar plates should be prepared in advance by
   filling the Rectangular trays with 30 mL of melted agar. These should be dried on as flat a
   surface as possible to ensure consistent heights across the plate.
2. Distribute dilutant. Importantly, columns 8 and 10 are a **2-fold**
   dilution of the prior column and not a 10-fold dilution. This is done to optimize the dynamic
   range of CFUs for counting, but it will probably take some trial and error to select which
   dilutions in the series to use. The dilution series is presented in the table below.
   - If you are using the `01_cfu_distribute_dilutant.py` protocol, the only work that needs to be
     done outside of the OT-2 is to load 100 µL of your samples into columns 1 and 12 of a 96 well
     plate inside of a biosafety cabinet.
   - If you do no wish to use the robot to add dilutant to the plate, then you can use a
     multichannel pipette to add **90 µl** to columns 2-7, 9, and 11 and **50 µl** to columns 8 and
     10 in a biosafety cabinet.

| **Plate column**  | 1   | 2    | 3    | 4    | 5    | 6    | 7    | 8    | 9    | 10   | 11   | 12  |
|--------------|-----|------|------|------|------|------|------|------|------|------|------|-----|
| Concentration (X)         | 1E0 | 1E-1 | 1E-2 | 1E-3 | 1E-4 | 1E-5 | 1E-6 | **5E-7** | 1E-7 | **5E-8** | 1E-9 | 1E0 |
| Culture vol (µL) | 100 |      |      |      |      |      |      |      |      |      |      | 100 |
| Dilutant vol (µL) |     | 90   | 90   | 90   | 90   | 90   | 90   | **50**   | 90   | **50**   | 90   |     |
| Transfer vol (µL)    |     | 10   | 10   | 10   | 10   | 10   | 10   | **50**   | 10   | **50**   | 10   |     |

3. Next the 96-well plates with bacteria and dilutant should be loaded on the OT-2 deck into positions **4, 5, 6, 10, and 11**
   as in the figure below. Not all positions need to be used at once (e.g., you could use only
   positions 4 and 5 or just position 4), but this will need to be changed from the default in the
   protocol `01_cfu_distribute_dilutant.py.` The default is to use all 5 plates/trays and process
   the maximum of 40 samples at once.

   <img src="images/OT-2-deck-plate-pos.png" alt="Deck layout for 96-well plates" width="500"/>
4. If using the robot to add dilutant to the plate, [import](https://support.opentrons.com/s/article/Get-started-Import-a-protocol) and
   [run](https://support.opentrons.com/s/article/Get-started-Run-your-protocol) the protocol
   `01_cfu_distribute_dilutant.py.` The OT-2 will distribute M9 dilutant to columns 2-11 as
   described above.

5. If you have already added dilutant to the plate manually, then you can skip running
   `01_cfu_distribute_dilutant.py` and instead continue to loading the rectangular trays onto the
   OT-2 deck as in the figure  below. Use the same number of trays as you have 96-well plates.

   <img src="images/OT-2-deck-plate-agar-pos.png" alt="Deck layout for 96-well plates" width="500"/>

6. [Import](https://support.opentrons.com/s/article/Get-started-Import-a-protocol) and
   [run](https://support.opentrons.com/s/article/Get-started-Run-your-protocol) the protocol
   `02_cfu_plate_spotting.py`. Here it is important to perform the ["Labware Position
   Check"](https://support.opentrons.com/s/article/How-positional-calibration-works-on-the-OT-2#LPC)
   which will allow you to [set
   offsets](https://support.opentrons.com/s/article/How-Labware-Offsets-work-on-the-OT-2) specific
   for the rectangular trays with agar. **MOST IMPORTANT** is to set the "z" offset for the agar plates so that the OT-2
   considers the "top of the well" as when the pipette tips are just barely touching the agar. 
