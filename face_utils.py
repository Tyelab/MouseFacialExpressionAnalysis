# For the first recording of a video, the best neutral face must be selected from ITIs for comparison against
# each trial type (for now, airpuff, sucrose).
# So what needs to happen is:
# Go from timestamp to frame number start/stop for ITIs
# Go from framenumber to parsing out trial sets
# For each section of trials, output highest correlation value, save as temporary "best" face
# Iterate through event type, save correlation value, save frame number, HOG image, HOG descriptor, and original image to it's own file

# Deryn LeDuke, Jeremy Delahanty

# Import things
import numpy as np
from pathlib import Path
import zarr
import pandas as pd
import pims
import matplotlib.pyplot as plt

pims.ImageIOReader.class_priority = 100  # we set this very high in order to force dask's imread() to use this reader [via pims.open()]

def convert_ms_to_frame(fps, timestamp):

    # timestamps are collected in milliseconds, convert to seconds
    # so FPS to Frame # makes sense
    seconds = timestamp/1000

    # Multipliy fps and seconds to get frame number
    # Round down to get earliest possible frame
    frame_number = np.around((fps * seconds), decimals=0).astype(int)
    
    return frame_number


csv_path = Path("/snlkt/lvhome/jdelahanty/facial_expression_demo_data/20211105_CSE020_plane1_-587.325_raw-013_Cycle00001_VoltageRecording_001_events.csv")
descriptor_path = Path("/snlkt/lvhome/jdelahanty/facial_expression_demo_data/CSE020/data.zarr/descriptors")
initial_corrs_path = Path("/snlkt/lvhome/jdelahanty/facial_expression_demo_data/corrs/data.zarr")
vid_path = Path("/snlkt/lvhome/jdelahanty/facial_expression_demo_data/20211105_CSE020_plane1_-587.325.mp4")

timestamps = pd.read_csv(csv_path, index_col=0)

first_iti_end = convert_ms_to_frame(29.42, timestamps["Speaker_on"][0])

initial_corrs = zarr.open(initial_corrs_path)

first_iti_corrs = initial_corrs[0:first_iti_end]

first_iti_vals = np.empty((first_iti_corrs.shape[0],))

# Make a list of the actual correlation values from the correlation matrices
for correlation in range(0, len(first_iti_corrs)):

    # The max value in these is always 1. The min values are the actual correlations
    # which are always less than 1.
    first_iti_vals[correlation] = np.min(first_iti_corrs[correlation][0][1])

neutral_max_corr = np.max(first_iti_vals)
neutral_max_corr_frame = first_iti_vals.argmax(axis=0)

vid = pims.open(str(vid_path))

my_frame = np.array(vid[neutral_max_corr_frame])

plt.imshow(my_frame)
plt.show()

