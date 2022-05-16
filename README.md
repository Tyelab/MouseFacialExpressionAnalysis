# MouseFacialExpressionAnalysis
Extracting emotions from facial expressions in mice


## Notes from the Tye Lab

Updating the README so it includes notes from Jeremy Delahanty, Research Technician in the Tye Lab, for expanding the capabilities of this repository. Graduate student Deryn LeDuke is also working on enhancing the repository as well.

### Purpose
This repository is meant to expand upon the original work of Nate Dolensek and the Gogolla Lab by incorporating Dask for performing HOG analyses
upon recordings of a mouse's face from H264 encoded video.

#### Original Codebase
The original codebase, hosted [here](https://zenodo.org/record/3618395#.Ym9-AdpKiUk) took in individual `.jpeg`
images collected from an industrial camera. These files would have the HOG calculations run on them individually in parallel asynchronously. This workflow was possible
because the order in which images were computed was irrelevant since the resulting arrays written to disk had the same naming convention that the original images used.
Therefore, the results were able to be sorted into the correct order post-processing, where they would then be assembled into a movie.

#### This Codebase
This codebase is meant to expand upon the original set of scripts to enable the use of the parallelization abilities of [Dask](https://docs.dask.org/en/stable/) for
video data via [Dask-Image](https://image.dask.org/en/latest/quickstart.html) and [PIMS](http://soft-matter.github.io/pims/v0.5/).
Many video readers, like those in `opencv` and `scikit-image` try and load the entirety of video data into memory. For longer videos, unless you have an enormous amount
of RAM in your machine, you are very unlikely to be able to fit the entirety of the video into a `numpy` array that the machine can compute HOGs upon.

PIMS and Dask-Image solve this problem by letting you load frames into memory only as needed by slicing the video. The magic of Dask's scheduling abilities let you
read the video into chunks which will then be iterated upon using the HOG function for your video slices!

These file reads can happen very quickly sequentially and the HOG computations and writing to zarr all happen in parallel. This is the ideal case for this repo.

Performing HOG calculations via Dask and writing data to Zarr is now complete!
On a machine with a 64 Thread Xeon processor with 252GB RAM, the code `dask_faces.py` ran to completion in just over 8 minutes!
