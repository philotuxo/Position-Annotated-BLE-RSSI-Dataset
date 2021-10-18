# Track files directory

We provide a set of RSSI values that are collected while navigating through some trajectories. Each sample of RSSI data is labeled with its position counterpart that is estimated via the AR-based location system.

The file names do not follow a specific pattern. The file names are self explanatory.

Each file consists of the lines that have the following pattern:
<pre>&lt;timestamp&gt;,&lt;MAC sensor&gt;,&lt;MAC beacon&gt;,&lt;RSSI&gt;,&lt;coord_x&gt;,&lt;coord_y&gt;,&lt;coord_z&gt;,&lt;9 fields of rotation matrix&gt;</pre>

The annotations are performed using a specially designed AR system. The details are given in (Daniş _et_al_., PMC, ?). The trajectories are also used in (Daniş _et_al_., Access, 2021). The researchers who want to use these data are expected to cite either of these articles.
