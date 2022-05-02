# visualize dask_faces_output

import zarr
import numpy as np
import matplotlib.pyplot as plt
import pims
import dask_image
import dask_image.imread
from skimage.feature import hog

d = zarr.open('hog_images/data.zarr', mode='r')

o = zarr.open('hog_descriptors/data.zarr', mode='r')

print(o)

t = d[0]

# video_path = "test_vid.mp4"

# pims.ImageIOReader.class_priority = 100  # we set this very high in order to force dask's imread() to use this reader [via pims.open()]

# original_video = dask_image.imread.imread(video_path)

# kwargs = dict(
#     orientations=8,
#     pixels_per_cell=(32, 32),
#     cells_per_block=(1, 1),
#     transform_sqrt=True,
#     visualize=True
#     )

# desc, im = hog(np.array(original_video[0]), **kwargs)

plt.imshow(t)
plt.show()