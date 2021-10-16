## Configuration files

### ./tetam.par
Parameters file: a json file that includes the parameters used for conversion between the units.

"origin": (px) the position of the origin of the area in the map image
"limits: (m) the rectangular area that the algorithms are tested.
"direction": (matrix) the rotation matrix from the pixel space to pixel space
"parity": (m/px) measurement of a pixel edge in metric space

----------------------------------------------------------------------------------------------------------------
### ./tetam.dev

Devices file: file that includes the device properties.
The lines starting with 
  - Dongles: show the sensor information
  - Beacons: show the beacon information
  
The format of each device in Python dict:
<MAC Address>: [ <3D position>, <color>, <alias> ]
