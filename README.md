# Position Annotated BLE RSSI Dataset for Indoor Localization
## Introduction
This dataset is intended for the researchers that work in indoor positioning domain and want to use positioning parameters that are labeled with highly precise ground truth positions. We provide signal parameters collected while navigating an emitter at different paces in an indoor environment, and their position labels collected using a more precise method \(with a median precision of ~0.04 m\) and registered to the signal parameters rigorously.

We collect the data using a specially designed setup of cameras and a Bluetooth beacon. A network of distributed Bluetooth sensors collect the received signal strength indicators \(RSSI\) of the captured packages emitted by a navigated Bluetooth beacon. Simultaneously, a two camera system captures videos from the environment that is decorated with a dense set of augmented reality \(AR\) tags. The AR-based visual system provides highly precise position information. These precise positions can be used as the ground truth for positioning. Any wireless-based inference about the positions can now be evaluated accurately using these precise position labels.

## Top Level Directory Descriptions
The directories in the dataset include different levels of information that are used to infer the positions that the beacon is on. Each directory has its own README.md that describe the data format and other assistive information.

### hst: fingerprint histogram files
The directory comprises of RSSI data collected by multiple sensors from stationary points \(reference points\) that are used afterwards to estimate a probabilistic radio frequency map of the area.

### grd: grid files
Grid files are composed of the probabilistic radio frequency maps of the area estimated via our Wasserstein Interpolation based method that uses the fingerprint files as input. See [\[Daniş _et al_, Sensors, 2017\]](#sensors) for details.

### trk: track files
Track files include RSSI data collected by multiple sensors while navigating the beacon in the area. The files also include the ground truth positions so that that a direct evaluation of the inference becomes possible.

### occ: occupancy files
Occupancy information of the area. Passable and occluded areas can be easily introduced into localization algorithms and the accuracy can be increased with light tweaks. See [\[Daniş _et al_, Access, 2021\]](#access) for further details.

### cnf: configuration files
Configuration files that describe the positions of the sensors and various parameters that can be used to do conversions between pixel coordinates on the maps and the coordinate frame of the area.

### map: images of area maps
Images of the area map that include the stationary sensors, furnitures, walls and columns.

## Corresponding research
- To make inferences on positions using Bayesian forward algorithm (a.k.a. Forward Filter or HMM filter), please refer to [\[Daniş _et al_, PEVA, 2023\]](#peva).
- For a complete introduction to the distributed sensing setup and the method that collects and synchronizes the data, please refer to [\[Daniş _et al_, PMC, 2022\]](#pmc).
- In order to see how to build a Sequential Monte Carlo \(Particle Filter\) based algorithm that employs these data to infer the positions of a navigated emitter, please see [\[Daniş _et al_, Access, 2021\]](#access).
- To estimate probabilistic radio frequency maps using Affine Wasserstein Combination that takes stationary information, please refer to [\[Daniş _et al_, Sensors, 2017\]](#sensors).
- To infer probabilistic radio frequency maps using neural networks, please refer to [\[Güler _et al_, IPIN, 2019\]](#ipin2019).

## References
**<a id="peva">\[Daniş _et al._, PEVA, 2023\]</a>**
FS Daniş and AT Cemgil, “Probabilistic indoor tracking of Bluetooth Low-Energy beacons,” *Performance Evaluation*, vol. 162, p. 102374, Oct. 2023.

**<a id="pmc">\[Daniş _et al._, PMC, 2022\]</a>**
F. Serhan Daniş and A. Teoman Naskali and A. Taylan Cemgil and Cem Ersoy. An Indoor Localization Dataset and Data Collection Framework with High Precision Position Annotation, Pervasive and Mobile Computing,Volume 81,2022.

**<a id="access">\[Daniş _et al._, Access, 2021\]</a>**
F. S. Daniş, A. T. Cemgil, and C. Ersoy. Adaptive sequential monte carlo filter for indoor positioning and tracking with bluetooth low energy beacons. _IEEE Access_, 9:37022–37038, 2021.

**<a id="sensors">\[Daniş and Cemgil, Sensors, 2017\]</a>**
FS Daniş and AT Cemgil, “Model-Based Localization and Tracking Using Bluetooth Low-Energy Beacons,” *Sensors*, vol. 17, no. 11, p. 2484, Oct. 2017.

**<a id="ipin2019">\[Güler _et al._, IPIN, 2019\]</a>**
Sila Guler, F. Serhan Danis, and Ali Taylan Cemgil. Radio map estimation with neural networks and active learning for indoor localization. In Francesco Potorti, Valérie Renaudin, Kyle O’Keefe, and Filippo Palumbo, editors, _Proceedings of the Tenth International Conference on Indoor Positioning and Indoor Navigation - Work-in-Progress Papers_, number 2498 in CEUR Workshop Proceedings, pages 25–31, Aachen, 2019.
