---
title: "Opentron Flex Python API"
date: 2025-06-01
parent: Capy
layout: default
---

All api are sourced from [Opentron Python API][https://docs.opentrons.com/python-api/]

# Basic 
```Python
from opentrons import protocol_api

metadata = {
    "protocolName": "My Protocol",
    "description": "This protocol uses the Flex",
}

requirements = {"robotType": "Flex", "apiLevel": "2.27"}
```


