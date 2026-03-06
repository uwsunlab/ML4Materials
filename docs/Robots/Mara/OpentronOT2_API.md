---
title: "Opentron OT2 Python API"
date: 2025-06-01
parent: Mara
layout: default
---

All api are sourced from [Opentron Python API][https://docs.opentrons.com/python-api/]

# Basic

def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware("opentrons_96_tiprack_300ul", 1)
    left_pipette = protocol.load_instrument(
        "p300_single_gen2", "left", tip_racks=[tips]
    )

## Deck slot labels
On the OT2 there are 12 decks labeled by number


# Pipet Functions
The OT2 can use Gen1 and Gen2 single channel pipets. 
Multi channel pipets (8 channel) also compatible. (However partial pipetting is a function of the Flex not OT2)

For Mara, most common configurations are:
```Python
# 20 ul Gen2 Single Channel 
tiprack_20 = protocol.load_labware('opentrons_96_tiprack_20ul', 'Deck Slot')
pip20 = protocol.load_instrument('p20_single_gen2', mount='left or left', tip_racks=[tiprack_20])

# 300 ul Gen2 Single Channel 
tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 'Deck Slot')
pip300 = protocol.load_instrument('p300_single_gen2', mount='right or left', tip_racks=[tiprack_300])

# 1000 ul Gen2 Single Channel 
tiprack_1000 = protocol.load_labware('opentrons_96_tiprack_1000ul', 'Deck Slot')
pip1000 = protocol.load_instrument('p1000_single_gen2', mount='right or left', tip_racks=[tiprack_300])

```

Apsiration and dispensing speeds can be controlled when necessary
```Python
    # Set pipette transfer speeds
    pip300.flow_rate.aspirate = 50
    pip300.flow_rate.dispense = 50
    pip300.flow_rate.blow_out = 100
```


# Common functions

