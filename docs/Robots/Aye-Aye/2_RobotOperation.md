---
title: "Robot Operation"
date: 2026-03-01
parent: Aye-Aye
layout: default
---
# 1. Robot Coordinate System
The robot can be controlled in a few ways:
| Mode | Meaning                                                                            |
| ---- | ---------------------------------------------------------------------------------- |
| 0    | Position control (normal movement)                                                 |
| 1    | Servo motion <br>• Must be set to use `set_servo_angle_j` or `set_servo_cartesian` |
| 2    | Joint teaching <br>• Ensures arm is identified and matched to control box          |
| 3    | Cartesian teaching (invalid)                                                       |
| 4    | Joint velocity control                                                             |
| 5    | Cartesian velocity control                                                         |
| 6    | Joint online trajectory planning                                                   |
| 7    | Cartesian online trajectory planning                                               |

## Teaching Detection Parameters (detection_param)
| Value | Meaning                   |
| ----- | ------------------------- |
| 0     | Turn on motion detection  |
| 1     | Turn off motion detection |
Notes: 
- Only available if firmware_version >= 1.10.1
- Only available when mode = 2


The syntax to set mode is:
```python 
def set_mode(self, mode: int = 0, detection_param: int = 0) -> int:
    """
    Set the xArm control mode.

    Parameters
    ----------
    mode : int, default=0
        Control mode of the xArm:
        0 : Position control (normal movement)
        1 : Servo motion (must set this mode to use `set_servo_angle_j` or `set_servo_cartesian`)
        2 : Joint teaching (ensure arm is identified)
        3 : Cartesian teaching (invalid)
        4 : Joint velocity control
        5 : Cartesian velocity control
        6 : Joint online trajectory planning
        7 : Cartesian online trajectory planning

    detection_param : int, default=0
        Motion detection parameters (only for `mode=2` and firmware >= 1.10.1):
        0 : Turn on motion detection
        1 : Turn off motion detection

    Returns
    -------
    int
        Return code from the xArm API.

    Examples
    --------
    >>> arm.set_mode(2, detection_param=0)
    """
```

Example:





The robot can be controlled in a few ways :



             Z
             ↑
             │
             │
             │
             │
             ●  ← tool position (x,y,z)
            /
           /
          /
         O────────────→ X
        /
       /
      ↓
      Y

- X → forward / away from robot
- Y → left / right
- Z → up / down


Roll pitch and yaw can be described like: 
- roll →  rotate around X (twist wrist left to right)
- pitch → rotate around y (nodding head up and down)
- yaw → rotate around z (turning your head let to right) 
