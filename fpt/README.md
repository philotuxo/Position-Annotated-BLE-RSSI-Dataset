## Fingerprints

Data directory for the fingerprints (or stationary reference points): we provide two fingerprint data sets collected from the area: "set_1" and "set_2" collected at different dates. 

### mbd files: multi ble data 
(_multi_ for multiple sensors)

The data sets consist of the files whose names have the following pattern:
<pre>&lt;sensor_alias&gt;_&lt;pos_x&gt;_&lt;pos_y&gt;_&lt;pos_z&gt;.mbd</pre>

Each file consists of lines that have the following pattern:
<timestamp>,<MAC sensor>,<MAC beacon>,<RSSI>
