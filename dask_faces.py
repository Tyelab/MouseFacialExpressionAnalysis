# import numpy as np
# from skimage.feature import hog
# import cv2
# import pims
# import dask.array as da
# import dask_image.imread
# import matplotlib.pyplot as plt
# from numcodecs import Blosc
# import zarr

# # class GreyImageIOReader(FramesSequence):
# #     class_priority = 100  # we purposefully set this very high to force pims.open() to use this reader
# #     class_exts = pims.ImageIOReader.class_exts

# #     def __init__(self, filename, **kwargs):
# #         self._reader = pims.ImageIOReader(filename, **kwargs)
# #         self.filename = self._reader.filename
    
# #     def close(self):
# #         self._reader.close()  # important since dask-image uses pims.open() as a context manager

# #     def get_frame(self, n):
# #         return pims.as_grey(self._reader.get_frame(n))

# #     def __len__(self):
# #         return self._reader.__len__()

# #     @property
# #     def frame_shape(self):
# #         return self._reader.frame_shape[:-1]

# #     @property
# #     def pixel_type(self):
# #         return self._reader.pixel_type


# def as_grey(frame):
#     """Convert a 2D image or array of 2D images to greyscale.

#     This weights the color channels according to their typical
#     response to white light.

#     It does nothing if the input is already greyscale.
#     (Copied and slightly modified from pims source code.)
#     """
#     if len(frame.shape) == 2 or frame.shape[-1] != 3:  # already greyscale
#         return frame
#     else:
#         red = frame[..., 0]
#         green = frame[..., 1]
#         blue = frame[..., 2]
#         return 0.2125 * red + 0.7154 * green + 0.0721 * blue


# def crop_frame(video_object):

#     coords = cv2.selectROI("ROI Selection", video_object)
#     cv2.destroyAllWindows()

#     return coords

# def make_hogs(frames, coords, kwargs):

#     # frames will be a chunk of elements from the dask array
#     # coords are the cropping coordinates used for selecting subset of image
#     # kwargs are the keyword arguments that hog() expects
#     # Example:
#     # kwargs = dict(
#     # orientations=8,
#     # pixels_per_cell=(32, 32),
#     # cells_per_block=(1, 1),
#     # transform_sqrt=True,
#     # visualize=True
#     # )

#     # Perform cropping procedure upon every frame, the : slice,
#     # crop the x coordinates in the second slice, and crop the y
#     # coordinates in the third slice. Save this new array as 
#     # new_frames
#     new_frames = frames[
#         :,
#         coords[1]:coords[1] + coords[3],
#         coords[0]:coords[0] + coords[2]
#     ]

#     # Get the number of frames and shape for making
#     # np.arrays of hog descriptors and images later
#     nframes = new_frames.shape[0]
#     first_frame = new_frames[0]

#     print("NEW IMAGE SHAPE: ", first_frame.shape)

#     # Use first frame to generate hog descriptor np.array and
#     # np.array of a hog image
#     hog_descriptor, hog_image = hog(
#         first_frame,
#         **kwargs
#         )

#     print("FIRST FRAME HOG SHAPE: ", hog_image.shape)

#     # Make empty numpy array that equals the number of frames passed into
#     # the function, use the fed in datatype as the datatype of the images
#     # and descriptors, and make the arrays shaped as each object's shape
#     hog_images = np.empty((nframes,) + hog_image.shape, dtype=hog_image.dtype)
#     hog_descriptors = np.empty((nframes,) + hog_descriptor.shape, dtype=hog_descriptor.dtype)

#     print("EMPTY HOG IMAGES NUMPY ARRAY SHAPE: ", hog_images.shape)

#     # Until I edit the hog code, perform the hog calculation upon each
#     # frame in a loop and append them to their respective np arrays
#     for index, image in enumerate(new_frames):
#         hog_descriptor, hog_image = hog(image, **kwargs)
#         hog_descriptors[index, ...] = hog_descriptor
#         hog_images[index, ...] = hog_image

#     print("COMPUTED HOG IMAGE NUMPY ARRAY: ", hog_images.shape)
    
#     return hog_descriptors, hog_images


# def get_ith_tuple_element(tuple_, i=0):
#     return  tuple_[i]


# video_path = "test_vid.mp4"

# pims.ImageIOReader.class_priority = 100  # we set this very high in order to force dask's imread() to use this reader [via pims.open()]

# original_video = dask_image.imread.imread(video_path)

# # Turn pims frame into numpy array that opencv will take for cropping image
# coords = crop_frame(np.array(original_video[0]))

# # kwargs to use for generating both hog images and hog_descriptors
# kwargs = dict(
#     orientations=8,
#     pixels_per_cell=(32, 32),
#     cells_per_block=(1, 1),
#     transform_sqrt=True,
#     visualize=True
#     )

# grey_frames = original_video.map_blocks(as_grey, drop_axis=-1)

# grey_frames = grey_frames.rechunk({0: 100})

# meta = np.array([[[]]])

# dtype = grey_frames.dtype

# my_hogs = grey_frames.map_blocks(
#     make_hogs,
#     coords=coords,
#     kwargs=kwargs,
#     dtype=dtype,
#     meta=meta
#     )

# my_hogs = my_hogs.persist()

# hog_images = my_hogs.map_blocks(
#     get_ith_tuple_element,
#     i = 1,
#     dtype=dtype,
#     meta=meta
# )

# first_hog_descriptor, first_hog_image = make_hogs(
#     grey_frames[:1, ...].compute(),
#     coords=coords,
#     kwargs=kwargs
# )

# hog_images = my_hogs.map_blocks(
#     get_ith_tuple_element,
#     i = 1,
#     chunks=(grey_frames.chunks[0],) + first_hog_image.shape[1:],
#     dtype=dtype,
#     meta=meta
# )

# image_axes = [1, 2]
# descriptor_axes = list(range(1, first_hog_descriptor.ndim))
# descriptors_array_chunks = (grey_frames.chunks[0],) + first_hog_descriptor.shape[1:]


# hog_descriptors = my_hogs.map_blocks(
#     get_ith_tuple_element,
#     i=0,
#     drop_axis=image_axes,
#     new_axis=descriptor_axes,
#     chunks=descriptors_array_chunks,
#     dtype=dtype,
#     meta=meta
# )

# print("DESCRIPTORS: ", type(hog_descriptors), hog_descriptors.shape, hog_descriptors)
# print("IMAGES: ", type(hog_images), hog_images.shape, hog_images)

# compressor = Blosc(cname='zstd', clevel=1)

# da.to_zarr(hog_images, "hog_images/data.zarr", compressor=compressor)

# da.to_zarr(hog_descriptors, "hog_descriptors/data.zarr", compressor=compressor)

# print("Data written to zarr! Hooray!")


# grey_frames.compute()
# da.to_zarr(grey_frames, "full_video/data.zarr", compressor=compressor)
# total_time_grey = time.perf_counter() - start_grey_compute
# print(f"As Grey Reader: {total_time_grey}")


# grey_frames = zarr.open("test/data.zarr")
# print(type(grey_frames))
# grey_array = da.from_zarr(grey_frames)

# descs = original_video.map_blocks(
#     make_hogs,
#     original_video, coords, kwargs,
#     dtype=np.uint8
#     )

# print("ready to make hogs!")

# descs.compute()

# fd, hog_image = hog(test, orientations=8, pixels_per_cell=(32,32),
#                     cells_per_block=(1,1), visualize=True,
#                     transform_sqrt=True)

# hog_image_rescale = exposure.rescale_intensity(hog_image, in_range=(0,10))

# print(type(fd), type(hog_image))

# print(len(fd))
# print(fd.shape)



# input()

# grey_frames = original_video.map_blocks(as_grey, drop_axis=-1)

# grey_frames.compute()

# grey_frames = grey_frames.rechunk({0: 100})

# my_hogs = grey_frames.map_blocks(make_hogs, coordinates, dtype=np.uint8)

# my_hogs.compute()


# import numpy as np
# from skimage.feature import hog
# import cv2
# import pims
# import dask.array as da
# import dask_image.imread
# import matplotlib.pyplot as plt
# from numcodecs import Blosc
# import zarr

# def as_grey(frame):
#     """Convert a 2D image or array of 2D images to greyscale.

#     This weights the color channels according to their typical
#     response to white light.

#     It does nothing if the input is already greyscale.
#     (Copied and slightly modified from pims source code.)
#     """
#     if len(frame.shape) == 2 or frame.shape[-1] != 3:  # already greyscale
#         return frame
#     else:
#         red = frame[..., 0]
#         green = frame[..., 1]
#         blue = frame[..., 2]
#         return 0.2125 * red + 0.7154 * green + 0.0721 * blue


# def crop_frame(video_object):

#     coords = cv2.selectROI("ROI Selection", video_object)
#     cv2.destroyAllWindows()

#     return coords

# def make_hogs(frames, coords, kwargs):

#     # frames will be a chunk of elements from the dask array
#     # coords are the cropping coordinates used for selecting subset of image
#     # kwargs are the keyword arguments that hog() expects
#     # Example:
#     # kwargs = dict(
#     # orientations=8,
#     # pixels_per_cell=(32, 32),
#     # cells_per_block=(1, 1),
#     # transform_sqrt=True,
#     # visualize=True
#     # )

#     # Perform cropping procedure upon every frame, the : slice,
#     # crop the x coordinates in the second slice, and crop the y
#     # coordinates in the third slice. Save this new array as 
#     # new_frames
#     new_frames = frames[
#         :,
#         coords[1]:coords[1] + coords[3],
#         coords[0]:coords[0] + coords[2]
#     ]

#     # Get the number of frames and shape for making
#     # np.arrays of hog descriptors and images later
#     nframes = new_frames.shape[0]
#     first_frame = new_frames[0]

#     print("NEW IMAGE SHAPE: ", first_frame.shape)

#     # Use first frame to generate hog descriptor np.array and
#     # np.array of a hog image
#     hog_descriptor, hog_image = hog(
#         first_frame,
#         **kwargs
#         )

#     print("FIRST FRAME HOG SHAPE: ", hog_image.shape)

#     # Make empty numpy array that equals the number of frames passed into
#     # the function, use the fed in datatype as the datatype of the images
#     # and descriptors, and make the arrays shaped as each object's shape
#     hog_images = np.empty((nframes,) + hog_image.shape, dtype=hog_image.dtype)
#     hog_descriptors = np.empty((nframes,) + hog_descriptor.shape, dtype=hog_descriptor.dtype)

#     print("EMPTY HOG IMAGES NUMPY ARRAY SHAPE: ", hog_images.shape)

#     # Until I edit the hog code, perform the hog calculation upon each
#     # frame in a loop and append them to their respective np arrays
#     for index, image in enumerate(new_frames):
#         hog_descriptor, hog_image = hog(image, **kwargs)
#         hog_descriptors[index, ...] = hog_descriptor
#         hog_images[index, ...] = hog_image

#     print("COMPUTED HOG IMAGE NUMPY ARRAY: ", hog_images.shape)
    
#     return hog_descriptors, hog_images


# def get_ith_tuple_element(tuple_, i=0):
#     return  tuple_[i]


# video_path = "test_vid.mp4"

# pims.ImageIOReader.class_priority = 100  # we set this very high in order to force dask's imread() to use this reader [via pims.open()]

# original_video = dask_image.imread.imread(video_path)

# # Turn pims frame into numpy array that opencv will take for cropping image
# coords = crop_frame(np.array(original_video[0]))

# # kwargs to use for generating both hog images and hog_descriptors
# kwargs = dict(
#     orientations=8,
#     pixels_per_cell=(32, 32),
#     cells_per_block=(1, 1),
#     transform_sqrt=True,
#     visualize=True
#     )

# grey_frames = original_video.map_blocks(as_grey, drop_axis=-1)

# grey_frames = grey_frames.rechunk({0: 100})

# meta = np.array([[[]]])

# dtype = grey_frames.dtype

# my_hogs = grey_frames.map_blocks(
#     make_hogs,
#     coords=coords,
#     kwargs=kwargs,
#     dtype=dtype,
#     meta=meta
#     )

# my_hogs = my_hogs.persist()

# hog_images = my_hogs.map_blocks(
#     get_ith_tuple_element,
#     i = 1,
#     dtype=dtype,
#     meta=meta
# )

# first_hog_descriptor, first_hog_image = make_hogs(
#     grey_frames[:1, ...].compute(),
#     coords=coords,
#     kwargs=kwargs
# )

# hog_images = my_hogs.map_blocks(
#     get_ith_tuple_element,
#     i = 1,
#     chunks=(grey_frames.chunks[0],) + first_hog_image.shape[1:],
#     dtype=dtype,
#     meta=meta
# )

# image_axes = [1, 2]
# descriptor_axes = list(range(1, first_hog_descriptor.ndim))
# descriptors_array_chunks = (grey_frames.chunks[0],) + first_hog_descriptor.shape[1:]



# hog_descriptors = my_hogs.map_blocks(
#     get_ith_tuple_element,
#     i=0,
#     drop_axis=image_axes,
#     new_axis=descriptor_axes,
#     chunks=descriptors_array_chunks,
#     dtype=dtype,
#     meta=meta
# )

# print("DESCRIPTORS: ", type(hog_descriptors), hog_descriptors.shape, hog_descriptors)
# print("IMAGES: ", type(hog_images), hog_images.shape, hog_images)

# compressor = Blosc(cname='zstd', clevel=1)

# da.to_zarr(hog_images, "hog_images/data.zarr", compressor=compressor)

# da.to_zarr(hog_descriptors, "hog_descriptors/data.zarr", compressor=compressor)

# print("Data written to zarr! Hooray!")

##### PARTICULAR MINER VERSION #####
import numpy as np
from pathlib import Path
from skimage.feature import hog
from numcodecs.blosc import Blosc
# import cv2
import pims
import dask.config
import dask.array as da
import dask_image.imread
import time
import warnings


def as_grey(frame):
    """Convert a 2D image or array of 2D images to greyscale.

    This weights the color channels according to their typical
    response to white light.

    It does nothing if the input is already greyscale.
    (Copied and slightly modified from pims source code.)
    """
    if len(frame.shape) == 2 or frame.shape[-1] != 3:  # already greyscale
        return frame
    else:
        red = frame[..., 0]
        green = frame[..., 1]
        blue = frame[..., 2]
        return 0.2125 * red + 0.7154 * green + 0.0721 * blue


# def crop_frame(video_object):

#     coords = cv2.selectROI("ROI Selection", video_object)
#     cv2.destroyAllWindows()

#     return coords

def make_hogs(frames, coords, kwargs):

    # frames will be a chunk of elements from the dask array
    # coords are the cropping coordinates used for selecting subset of image
    # kwargs are the keyword arguments that hog() expects
    # Example:
    # kwargs = dict(
    # orientations=8,
    # pixels_per_cell=(32, 32),
    # cells_per_block=(1, 1),
    # transform_sqrt=True,
    # visualize=True
    # )

    # Perform cropping procedure upon every frame, the : slice,
    # crop the x coordinates in the second slice, and crop the y
    # coordinates in the third slice. Save this new array as 
    # new_frames
    new_frames = frames[
        :,
        coords[1]:coords[1] + coords[3],
        coords[0]:coords[0] + coords[2]
    ]

    # Get the number of frames and shape for making
    # np.arrays of hog descriptors and images later
    nframes = new_frames.shape[0]
    first_frame = new_frames[0]

    # Use first frame to generate hog descriptor np.array and
    # np.array of a hog image
    hog_descriptor, hog_image = hog(
        first_frame,
        **kwargs
        )

    # Make empty numpy array that equals the number of frames passed into
    # the function, use the fed in datatype as the datatype of the images
    # and descriptors, and make the arrays shaped as each object's shape
    hog_images = np.empty((nframes,) + hog_image.shape, dtype=hog_image.dtype)
    hog_descriptors = np.empty((nframes,) + hog_descriptor.shape, dtype=hog_descriptor.dtype)

    # Until I edit the hog code, perform the hog calculation upon each
    # frame in a loop and append them to their respective np arrays
    # start = time.perf_counter()
    for index, image in enumerate(new_frames):
        hog_descriptor, hog_image = hog(image, **kwargs)
        hog_descriptors[index, ...] = hog_descriptor
        hog_images[index, ...] = hog_image
    # end = time.perf_counter() - start
    # print(f"MADE HOGS IN {end}")
    
    return hog_descriptors, hog_images


def get_ith_tuple_element(tuple_, i=0):
    return  tuple_[i]


def normalize_hog_desc_dims(tuple_):
    # add more dimensions (each of length 1) to the hog descriptor chunk in
    # order to match the number of dimensions of the hog_image
    descriptor = tuple_[0]
    image = tuple_[1]
    if descriptor.ndim >= image.ndim:
        return tuple_[0]
    else:
        return  np.expand_dims(
            tuple_[0], axis=list(range(descriptor.ndim, image.ndim))
        )

warnings.filterwarnings('ignore', '`nframes` does not nicely divide')

program_start = time.perf_counter()

video_path = "movies/test_vid.mp4"

pims.ImageIOReader.class_priority = 100  # we set this very high in order to force dask's imread() to use this reader [via pims.open()]

coords = (496, 174, 992, 508)

original_video = dask_image.imread.imread(video_path, nframes=16)

# Turn pims frame into numpy array that opencv will take for cropping image
# coords = crop_frame(np.array(original_video[0]))

# kwargs to use for generating both hog images and hog_descriptors
kwargs = dict(
    orientations=8,
    pixels_per_cell=(32, 32),
    cells_per_block=(1, 1),
    transform_sqrt=True,
    visualize=True
)

grey_frames = original_video.map_blocks(as_grey, drop_axis=-1)

meta = np.array([[[]]])

dtype = grey_frames.dtype

my_hogs = grey_frames.map_blocks(
    make_hogs,
    coords=coords,
    dtype=dtype,
    meta=meta,
    kwargs=kwargs,
)

# first determine the output hog shapes from the first grey-scaled image so that
# we can use them for all other images: 
first_hog_descr, first_hog_image = make_hogs(
    grey_frames[:1, ...].compute(),
    coords,
    kwargs
)

hog_images = my_hogs.map_blocks(
    get_ith_tuple_element,
    i=1,
    chunks=(grey_frames.chunks[0],) + first_hog_image.shape[1:],
    dtype=dtype,
    meta=meta
)

descr_array_chunks = (grey_frames.chunks[0],) + first_hog_descr.shape[1:]

if first_hog_descr.ndim <= first_hog_image.ndim:
    # we will recreate the missing hog_descriptor axes but give them each a size of 1
    new_axes = []
    n_missing_dims = first_hog_image.ndim - first_hog_descr.ndim
    descr_array_chunks += (1,)*n_missing_dims
else:
    new_axes = list(range(first_hog_image.ndim, first_hog_descr.ndim))

# Do not use `drop_axes` here!  `drop_axes` will attempt to concatenate the
# tuples, which is undesirable.  Instead, use `squeeze()` later to drop the
# unwanted axes.
hog_descriptors = my_hogs.map_blocks(
    normalize_hog_desc_dims,
    new_axis=new_axes,
    chunks=descr_array_chunks,
    dtype=dtype,
    meta=meta,
)

hog_descriptors = hog_descriptors.squeeze(-1)  # here's where we drop the last dimension

compressor = Blosc(cname='zstd', clevel=1)

with dask.config.set(scheduler='processes'):
    da.to_zarr(hog_images, "/scratch/snlkt_facial_expression/h.zarr")
    da.to_zarr(hog_descriptors, "/scratch/snlkt_facial_expression/d.zarr")

print("Data written to zarr! Hooray!")

program_end = time.perf_counter() - program_start

print(f"PROGRAM RUNTIME: {program_end}")