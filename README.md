# Position Annotated BLE RSSI Dataset for Indoor Localization
## Introduction
This dataset is intended for the researchers that work in indoor positioning domain and want to use RSSI parameters that are labeled with highly precise ground truth positions. The data are collected from a setup of multiple Bluetooth sensors that track a Bluetooth beacon that navigate in the environment. 

- For a complete introduction to the setup and the method that collects and synchronizes the data, please refer to [(Daniş _et al_, ?)](#1). 
- In order to see how to build a Sequential Monte Carlo (Particle Filter) based algorithm that employs these data to infer the positions of a navigated emitter, please see [(Daniş _et al_, 2021)](#2).
- To estimate probabilistic radio frequency maps using Affine Wasserstein Combination that takes stationary information, please refer to [(Daniş _et al_, 2017)](#3).
- To infer probabilistic radio frequency maps using neural networks, please refer to [(Güler _et al_, 2019)](#4).
- To make inferences on positions using Bayesian forward algorithm, please refer to [(Daniş _et al_, 2021b)](#5).

## Top Level Directory Descriptions
The files in the dataset include different levels of information that are used to infer the positions that the beacon is on.

### fpt: fingerprint files
The directory comprises of RSSI data collected by multiple sensors from stationary points (reference points) that are used afterwards to estimate a probabilistic radio frequency map of the area.

### grd: grid files
Grid files are composed of the probabilistic radio frequency maps of the area estimated via our Wasserstein Interpolation based method that uses the fingerprint files as input. See [[2]](#2) for details.

### trk: track files
Track files include RSSI data collected by multiple sensors while navigating the beacon in the area. The files also include the ground truth positions so that that a direct evaluation of the inference becomes possible.

### occ: occupancy files
Occupancy information of the area. Passable and occluded areas can be easily introduced into localization algorithms and the accuracy can be increased with light tweaks. See [[3]](#3) for further details.


conf: configuration files
maps: area images

# References

**<a id="1">(Daniş et al, ?)</a>**
F. Serhan Daniş and A. Teoman Naskali and A. Taylan Cemgil and Cem Ersoy. An Indoor Localization Dataset and Data Collection Framework with High Precision Position Annotation, *Submitted to Pervasive and Mobile Computing.*

**Abstract:**
We introduce a novel technique and an associated dataset for high resolution evaluation of wireless indoor positioning algorithms. The technique makes use of an Augmented Reality (AR) based positioning system to annotate the wireless signal parameter data samples with high precision position data. We track the position of a practical and low cost navigable setup of cameras and a Bluetooth Low Energy (BLE) beacon in an area decorated with AR markers. We maximize the performance of the AR-based localization by using a redundant number of markers. Video streams captured by the cameras are subjected to a series of marker recognition, subset selection and filtering operations to yield highly precise pose estimations. Our results show that we can reduce the positional error of AR localization system to a rate under 0.05 meters. The position data are then used to annotate the unreliable BLE data that are captured simultaneously by the sensors stationed in the environment, hence, constructing a wireless signal data set with the ground truth, which allows a wireless signal based localization system to be evaluated accurately.

**Bibtex**
<pre>@ARTICLE{danis2021pmc,
  author={F. Serhan Daniş and A. Teoman Naskali and A. Taylan Cemgil and Cem Ersoy},
  journal={SUBMITTED to Pervasive and Mobile Computing},
  title={An Indoor Localization Dataset and Data Collection Framework with High Precision Position Annotation}, 
  year={?},
  volume={},
  number={},
  pages={},
}</pre>

**<a id="2">(Daniş et al, 2021)</a>**
F. S. Daniş, A. T. Cemgil, and C. Ersoy. Adaptive sequential monte carlo filter for indoor positioning and tracking with bluetooth low energy beacons. _IEEE Access_, 9:37022–37038, 2021.

**Abstract:**
We model the tracking of Bluetooth low-energy (BLE) transmitters as a three layer hidden Markov model with joint state and parameter estimation. We are after a filtering distribution by Bayesian approximation using Monte Carlo sampling techniques. In a test environment decorated with multiple BLE sensors, the tracking relies only on the naturally unreliable received signal strength indicator (RSSI) of the captured signals. We assume that the tracked BLE transmitter does not provide any other motion or position related information. Hence, the transition density is designed to be merely a diffusion where the probability measures are diffused into the neighboring space. This makes the diagonal error covariance factor of the prediction density, namely the diffusion factor, the most important parameter to be tuned on the fly. We first show an experimental proof of concept using synthetic data on real trajectories by comparing three parameter estimation approaches: static, decaying and adaptive diffusion factors. We then obtain the results on real data which show that online parameter sampling adapts to the observed data and yields lower error means and medians, but more importantly steady error distributions with respect to a large range of parameters.

**Bibtex**
<pre>@ARTICLE{danis2021access,
  author={F. S. {Daniş} and A. T. {Cemgil} and C. {Ersoy}},
  journal={IEEE Access}, 
  title={Adaptive Sequential Monte Carlo Filter for Indoor Positioning and Tracking With Bluetooth Low Energy Beacons}, 
  year={2021},
  volume={9},
  number={},
  pages={37022-37038},
  doi={10.1109/ACCESS.2021.3062818}
}</pre>


**<a id="3">(Daniş and Cemgil, 2017)</a>**
FS Daniş and AT Cemgil, “Model-Based Localization and Tracking Using Bluetooth Low-Energy Beacons,” *Sensors*, vol. 17, no. 11, p. 2484, Oct. 2017.

**Abstract:**
We introduce a high precision localization and tracking method that makes use of cheap Bluetooth low-energy (BLE) beacons only. We track the position of a moving sensor by integrating highly unreliable and noisy BLE observations streaming from multiple locations. A novel aspect of our approach is the development of an observation model, specifically tailored for received signal strength indicator (RSSI) fingerprints: a combination based on the optimal transport model of Wasserstein distance. The tracking results of the entire system are compared with alternative baseline estimation methods, such as nearest neighboring fingerprints and an artificial neural network. Our results show that highly accurate estimation from noisy Bluetooth data is practically feasible with an observation model based on Wasserstein distance interpolation combined with the sequential Monte Carlo (SMC) method for tracking.

**Bibtex**
<pre>@Article{danis2017sensors,
AUTHOR = {Daniş, F. Serhan and Cemgil, A. Taylan},
TITLE = {Model-Based Localization and Tracking Using Bluetooth Low-Energy Beacons},
JOURNAL = {Sensors},
VOLUME = {17},
YEAR = {2017},
NUMBER = {11},
ARTICLE--NUMBER = {2484},
URL = {http://www.mdpi.com/1424-8220/17/11/2484},
ISSN = {1424-8220},
DOI = {10.3390/s17112484}
}</pre>

**<a id="4">(Güler et al, 2019)</a>** 
Sila Guler, F. Serhan Danis, and Ali Taylan Cemgil. Radio map estimation with neural networks and active learning for indoor localization. In Francesco Potorti, Valérie Renaudin, Kyle O’Keefe, and Filippo Palumbo, editors, _Proceedings of the Tenth International Conference on Indoor Positioning and Indoor Navigation - Work-in-Progress Papers_, number 2498 in CEUR Workshop Proceedings, pages 25–31, Aachen, 2019.

**Abstract:**
Practical indoor localization, by exploiting electromagnetic scattering properties of local area networks, can be formulated as a tracking problem using a Hidden Markov model with a radio map as the observation model. Accurate estimation of the radio map is key in accurate indoor localization but this requires dense sampling of the electromagnetic field, also named as fingerprinting. To decrease the time consuming fingerprinting process, we represent the observation model by a neural network and train it using an active learning strategy based on uncertainty sampling aided by a Gaussian process. Our results indicate that the same localization performance can be maintained with less fingerprint measurements using our approach.

**Bibtex**
<pre>@inproceedings{guler2019ipin,
  author = {Sila Guler and F. Serhan Danis and Ali Taylan Cemgil},
  title = {RADIO MAP ESTIMATION WITH NEURAL NETWORKS AND ACTIVE  LEARNING FOR INDOOR LOCALIZATION},
  pages = {25--31},
  year = 2019,
  editor = {Francesco Potorti and Valérie Renaudin and Kyle O'Keefe and Filippo Palumbo},
  number = 2498,
  series = {CEUR Workshop Proceedings},
  address = {Aachen},
  issn = {1613-0073},
  url = {http://ceur-ws.org/Vol-2498},
  venue = {Pisa, Italy},
  eventdate = {2019-09-30},
  booktitle = {Proceedings of the Tenth International Conference on Indoor Positioning and Indoor Navigation - Work-in-Progress Papers}
}</pre>

**<a id="5">(Daniş et al, 2021b)</a>**
F. Serhan Daniş, A. Taylan Cemgil, and Cem Ersoy. Tracking a mobile beacon: A pure probabilistic approach. In 2021 International Conference on Indoor Positioning and Indoor Navigation (IPIN) (ACCEPTED),Lloret de Mar, Spain, 2021.

**Abstract:**
We construct a practical and real-time probabilistic framework for fine target tracking. The practicality comes from the application of the forward algorithm and the small parameter set used to build the state space model (SSM). A Bluetooth Low-Energy (BLE) beacon navigating in the environment publishes BLE packets which are captured by the stationary sensors. Fingerprints are formed by collecting received signal strength indicators (RSSI) of these packets, which are then processed into high resolution emission matrix using a histogram combination technique. We convert the map of the area into a grid structure, the resolution of which is controlled by the grid cell size. The transition matrices are built by Gaussian blur masks parametrized by the size and diffusion extent. As the transition matrix is highly sparse, we make the exact inference tractable by adopting a sparse matrix representation and by intelligently controlling the mask size, diffusion factor and grid cell size. Filtering can then be directly performed by the forward algorithm given a series of real RSSI measurements along real trajectories. We measure the performance of the system by comparing the most likely positions at each step with the ground truth positions. We achieve promising results and evaluate the approach also by the runtime and memory usage.

**Bibtex**
<pre>@INPROCEEDINGS{danis2021ipin,
  author={F. Serhan Daniş and A. Taylan Cemgil and Cem Ersoy},
  booktitle={2021 International Conference on Indoor Positioning and Indoor Navigation (IPIN) (ACCEPTED)},
  title={Tracking a Mobile Beacon: A Pure Probabilistic Approach},
  year={2021},
  venue = {Lloret de Mar, Spain},
  eventdate = {2021-11-29},
  volume={},
  number={},
  doi={10.1109/IPIN.2019.8911800}
}</pre>
