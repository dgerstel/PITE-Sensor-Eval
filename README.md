# PITEml
Machine learning project for PITE classes

## Catalogue structure

### ./code
 - preprocessData.C -- is a ROOT framework macro that from the raw data (./data/165527) (1) extracts parametrisation of sensors (output: ./data/sensorData.dat) and (2) saves png figures of 2D and 1D noise histograms (./fig)

### ./docs
 - stores report and may hold other materials if feel appropriate

### ./fig
 - original 2D histograms representing noise among 2048 channels (41 files for 41 sensors)
 - extracted noise 1D distributions (for all 41 sensors)

### ./data
 - 165527 -- directory with all raw data (perhaps needn't be shared, but to store all in one place I just put it there)
 - sensorData.dat -- parametrisation for all sesnsors where the columns read: {mean, RMS, skewness, kurtosis, quality}.
   quality is assumed 1.0 for all, but it might be [0.0, 100.0] value if we figure out how to come up with it.


