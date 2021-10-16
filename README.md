# Position Annotated BLE RSSI dataset for indoor localization
## Introduction
This dataset is intended for the researchers that work in indoor positioning domain and want to use RSSI parameters that are labeled with highly precise ground truth positions. The data are collected from a setup of multiple Bluetooth sensors that track a Bluetooth beacon that navigate in the environment. For a complete introduction to the setup and the method that collects and synchronizes the data, please cite and refer to [[1]](#1).

## Top Level Directory Descriptions
The files in the dataset include different levels of information that are used to infer the positions that the beacon is on.

### fpt: fingerprint files
The directory comprises of RSSI data collected by multiple sensors from stationary points (reference points) that are used afterwards to estimate a probabilistic radio frequency map of the area.

### grd: grid files
Grid files are composed of the probabilistic radio frequency maps of the area estimated via our Wasserstein Interpolation based method that uses the fingerprint files as input. See [[2]](#2) for details.

### trk: track files
Track files include RSSI data collected by multiple sensors while navigating the beacon in the area. The files also include the ground truth positions so that that a direct evaluation of the inference becomes possible.

### occ: occupancy files
Occupancy information of the area.

conf: configuration files
maps: area images

## References
<a id="1">[1]</a> 
F. Serhan Daniş and A. Teoman Naskali and A. Taylan Cemgil and Cem Ersoy
An Indoor Localization Dataset and Data Collection Framework with High Precision Position Annotation
Submitted to Pervasive and Mobile Computing.

### bibtex
@ARTICLE{danis2021pmc,
  author={F. Serhan Daniş and A. Teoman Naskali and A. Taylan Cemgil and Cem Ersoy},
  journal={SUBMITTED to Pervasive and Mobile Computing},
  title={An Indoor Localization Dataset and Data Collection Framework with High Precision Position Annotation}, 
  year={2021},
  volume={},
  number={},
  pages={},
}

<a id="2">[2]</a> 
F. Serhan Daniş and A. Taylan Cemgil (2017)
Model-Based Localization and Tracking Using Bluetooth Low-Energy Beacons, 
Sensors. 2017; 17(11):2484

### bibtex
@Article{danis2017sensors,
AUTHOR = {Daniş, F. Serhan and Cemgil, A. Taylan},
TITLE = {Model-Based Localization and Tracking Using Bluetooth Low-Energy Beacons},
JOURNAL = {Sensors},
VOLUME = {17},
YEAR = {2017},
NUMBER = {11},
ARTICLE--NUMBER = {2484},
URL = {http://www.mdpi.com/1424-8220/17/11/2484},
ISSN = {1424-8220},
ABSTRACT = {We introduce a high precision localization and tracking method that makes use of cheap Bluetooth low-energy (BLE) beacons only. We track the position of a moving sensor by integrating highly unreliable and noisy BLE observations streaming from multiple locations. A novel aspect of our approach is the development of an observation model, specifically tailored for received signal strength indicator (RSSI) fingerprints: a combination based on the optimal transport model of Wasserstein distance. The tracking results of the entire system are compared with alternative baseline estimation methods, such as nearest neighboring fingerprints and an artificial neural network. Our results show that highly accurate estimation from noisy Bluetooth data is practically feasible with an observation model based on Wasserstein distance interpolation combined with the sequential Monte Carlo (SMC) method for tracking.},
DOI = {10.3390/s17112484}
}
