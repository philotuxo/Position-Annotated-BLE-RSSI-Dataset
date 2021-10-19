# Videos for Precise Positioning with Augmented Reality Tags

The videos are uploaded to another location because of the storage constraints of Github. Videos can be accessible through [this link](https://drive.google.com/drive/folders/1Y3kJfj9mhoQ0mNMHxqaMi2P9q51MvVDZ).

## marker_positions.dat

The markers are generated using the ArUco Dictionary "DICT_6X6_50". When a proper camera matrix is obtained after camera calibration, markers can be detected in the videos. When a marker is detected, the ArUco suite provides its label, position and orientation with respect to the camera. 

Each marker has an AR-code and a pose (position and orientation) already defined with respect to the world frame. With this information in hand, we can estimate the camera pose when a marker is detected.

The file contains the labels and the poses of the markers installed in the area in the following format:
<pre>&lt;marker_label&gt;:&lt;3D_position_in_world_frame&gt;:&lt;3D_orientation_in_world_frame&gt;</pre>

For a detailed information on how precise positioning is possible, please refer to (Daniş _et_al_., PMC, ?).
