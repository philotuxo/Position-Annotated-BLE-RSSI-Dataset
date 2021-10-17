## Configuration files

### tetam.par
Parameters file: a json file that includes the parameters used for conversion between the units. The pixel measurements belong to the map "tetam.png".
- "origin": (px) the position of the origin of the area in the map image.
- "limits: (m) the rectangle where the algorithms are to be performed.
- "direction": (matrix) the rotation matrix from 2D real world to 2D pixel space.
- "parity": (m/px) measurement of a pixel edge in metric space.

### tetam.dev

Devices file: file that includes the device properties.
The lines that begin with 
- Dongles: show the sensor information
- Beacons: show the beacon information
  
The format of each device in Python dict:
<pre>&lt;MAC Address&gt;: [ &lt;3D position&gt;, &lt;color&gt;, &lt;alias&gt; ]</pre>
