# Grids

Interpolated fingerprint histograms on a grid map. We provide four versions with different resolutions: 0.1, 0.2, 0.5 and 1.0 meters for grid cell size. 

The directory and the file names follow the following pattern:
<pre>&lt;interpolation_type&gt;_&lt;grid_cell_size&gt;/&lt;data_set&gt;_&lt;signal_parameter&gt;_&lt;sensor_mac&gt;_&lt;grid_cell_size&gt;.grd</pre>

Sample file name:
<pre>"wassBest" _ "0.2" / "tetam_rssi" _ "000000000401" _ "0.2" .grd</pre>

The histograms on the grids estimated by using the Wasserstein interpolation method. The histograms on the grid structure  can also be regarded as an estimate for the probabilistic radio frequency map. The researchers that want to use the grid data can cite this article [1].

Header:
<pre>&lt;sensor_mac&gt;::&lt;rectangular_limits&gt;::&lt;resolution&gt;::&lt;histogram_bins&gt;</pre>
Lines:
<pre>&lt;2D_grid_coordinate&gt;::&lt;beacon_mac&gt;::&lt;histogram_measures&gt;</pre>
