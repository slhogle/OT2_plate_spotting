
# Introduction

This is a protocol to perform high-throughput CFU spotting of bacteria for colony forming unit (CFU) quantification. The user should manually set up bacterial samples in a series of serial dilutions in a 96-well plate. Then select dilutions are aspirated and spotted onto a rectangular agar plate such as the [Nunc OmniTray](https://www.sigmaaldrich.com/FI/en/product/sigma/o0764) or something similar. These plates are incubated for some duration of time and the resulting colonies are counted at different dilutions. Plates may also be imaged using an instrument like the Evos m7000 or using the [Reshape Biotech Imaging device](https://www.reshapebiotech.com/). The protocol can process up to 24 bacterial samples at a time (3 plates x 8 wells (1 column) per plate). This protocol was inspired by the protocol [available here](https://protocols.opentrons.com/protocol/33y0f3).

# Reagents

- Rectangular tray (e.g., the [Nunc OmniTray](https://www.sigmaaldrich.com/FI/en/product/sigma/o0764) or something similar) with *30 ml* of the selective agar of choice, sterile. Agar trays should be dried on as flat a surface as possible to ensure consistent heights across the plate.
- Sterile M9 for dilution

# Equipment/Consumables

- Standard lab 1-well reservoir (the kind that can be autoclaved) for M9 dilutant (e.g., axygen_1_reservoir_90ml)
- 96 well plates for the serial dilution

- [Opentrons P20 8 Channel Electronic Pipette (GEN2)](https://shop.opentrons.com/8-channel-electronic-pipette/)
- [Opentrons OT-2 96 Tip Racks - 20 µL](https://shop.opentrons.com/opentrons-20-l-tips-160-racks-800-refills/)
- [Opentrons P300 8 Channel Electronic Pipette (GEN2)](https://shop.opentrons.com/8-channel-electronic-pipette/)
- [Opentrons OT-2 96 Tip Rack - 300 µL](https://shop.opentrons.com/opentrons-300ul-tips-1000-refills/)

# IMPORTANT: Editing scripts and tip management
If you need to change defaults in this script you will need to edit the script directly before importing it into the Opentrons app. The main variables that need to be changed are in the "Global Vars" section of the script, which include the deck locations for the different plates, the dilution volumes to be used, and the position of the pipettes on the robot (e.g., left or right).

**Important!** We will always need to start the protocol from column A of a tip box. With the multichannel you cannot specify a different column to start with. The pipette will always start at A1.

# Procedure

The main process is divided into three steps/scripts

## 1) Manually distribute dilutant and perform serial dilution

This should be performed in a Biosafety cabinet using a multichannel pipette. (NOTE: earlier we had the robot perform the dilution step but we learned through experience that it is significantly slower and more cumbersome than manually doing the dilution in a biosafety cabinet)

Steps:
1. 8 different samples should be transfered at full concentration in Column 1.
2. Add 180 µL of the dilutant to columns 2-8 using a multichannel pipette and a reservoir.
3. For columns n = {1,2,3,4,5,6,7,8} starting from 1:
    Perform a serial dilution of 20 µL from column *n* to column *n+1* (e.g., transfer 20 µL from column 1 to column 2). Make sure to aspirate up and down to mix thoroughly. Discard tips between dilutions.

The end product should look as in Figure 1 below.

| <img src="images/96-Well_plate.png" alt="Deck layout for 96-well plates" width="500"/> |
| - |
| **Figure 2:** Concentrations for the serial dilution series in a plate |

## 2) Agar spotting

Load dilution plate and agar trays in the required orientation. For example, if you have dilution plates in deck positions 1, 2, and 3 and want to replicate spot each plate into rows 4-6 and 7-9 as in Figure 2 below.

| <img src="images/OT-2-deck-step2.png" alt="Deck layout for 96-well plates" width="500"/> |
| - |
| **Figure 2:** Deck layout for performing the serial dilutions |

You would edit the dictionary in the script so that the variable at line 19 is:

```python
PLATE_DICTIONARY = {1: [4,7], 2: [5,8], 3: [6,9]}
```

The python dictionary above would specify that the dilution plate at deck position 1 is spotted in duplicate onto agar trays in deck positions 4 and 7, dilution plate 2 into deck positions 5 and 8, and so on...

However, you could also just as easily write the dictionary as:

```python
PLATE_DICTIONARY = {1: [4,5,6,7,7,9]}
```

where the robot will replicate spot from deck position 1 into agar trays in deck psoitions 4 through 9.

After editing the script to your specifications, [import](https://support.opentrons.com/s/article/Get-started-Import-a-protocol) and [run](https://support.opentrons.com/s/article/Get-started-Run-your-protocol) the python script in Opentrons app. It is very important to perform the ["Labware Position Check"](https://support.opentrons.com/s/article/How-positional-calibration-works-on-the-OT-2#LPC) which will allow you to [set offsets](https://support.opentrons.com/s/article/How-Labware-Offsets-work-on-the-OT-2) specific for the rectangular trays with agar. **MOST IMPORTANT** is to set the "z" offset for the agar plates so that the OT-2 considers the "top of the well" as when the pipette tips are just barely above the agar. The robot will record and reload the labware offsets from the last time the script was run. From my experience, it works best to always delete the offsets and start from the begininig each time because the height of the agar in different trays can be highly variable. 

The script will spot 2 µL from the 1E-7, 1E-6, 1E-5, and 1E-4 dilutions in triplicate onto the agar trays in columns 1E-7 = {12,11,10}, 1E-6 = {9,8,7}, 1E-5 = {6,5,4} and 1E-4 = {3,2,1}
