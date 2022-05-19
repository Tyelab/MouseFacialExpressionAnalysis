# Open zarr, perform correlation across entire dataset frame by frame

import zarr
import numpy as np
import time
import dask.array as da
import dask.config
# Use Blosc as compressor for zarrs written to disk
from numcodecs.blosc import Blosc
from tqdm import tqdm


# data = zarr.open("/snlkt/lvhome/jdelahanty/facial_expression_demo_data/CSE020/data.zarr")

# data = data.descriptors

def chunk_corrcoef(first, second):
    assert first.shape == second.shape
    n_zarrs = first.shape[0]
    first_out = np.corrcoef(first[0], second[0])
    out = np.empty((n_zarrs,) + first_out.shape)
    out[0] = first_out
    for i in range(1, n_zarrs):
        out[i] = np.corrcoef(first[i], second[i])
    return out


input_file = "/snlkt/lvhome/jdelahanty/facial_expression_demo_data/CSE020/data.zarr/descriptors"
output_file = "/snlkt/lvhome/jdelahanty/facial_expression_demo_data/corrs/data.zarr"

z = da.from_zarr(input_file)  # 2d array

# To prepare for ``map_blocks()``, ensure the same chunking for both input arrays
# (Not necessary if using ``blockwise()`` instead.)
new_chunks = {0: z.chunks[0][0], 1: -1}
firsts = z[0:-1, :].rechunk(new_chunks)
seconds = z[1:, :].rechunk(new_chunks)

delayed_results = da.map_blocks(
    chunk_corrcoef, firsts, seconds, new_axis=2, chunks=(firsts.chunks[0], 2, 2)
)
with dask.config.set(scheduler='threading'):  # compare to ``scheduler='processes'``?
    delayed_results.to_zarr(output_file, overwrite=True)

