import pydicom
import os
import numpy as np
import h5py
import random

# reverse the process, convert hdf5 and json to dicom
template = pydicom.read_file("./template.dcm")
hdf5_file = h5py.File("mytestfile.hdf5", "r")
pixel_data_grp = hdf5_file["pixel_data"]
# template.pixel_array
# pixel_data_grp

inverse_convert_pixelscale = np.iinfo(template.pixel_array.dtype).max
i = 0
for pixel_data_index in pixel_data_grp:
    pixel_array = pixel_data_grp[pixel_data_index][()]
    inverse_convert_pixel_array = [[np.int16(num * inverse_convert_pixelscale) for num in row] for row in pixel_array]
    dicom_pixel_array = np.asarray(inverse_convert_pixel_array)
    template.PixelData = dicom_pixel_array
    template.SeriesInstanceUID = "1.3.6.1.4.1.9590.100.1.1.369231118011061003403421859172643143649"
    template.SOPInstanceUID = "1.3.6.1.4.1.9590.100.1.1.369231118011061003403421859172643143" + "{:03}".format(random.randrange(1, 10**3))
    template.save_as("./dicom_output/image" + str(i) + ".dcm")
    i = i + 1
hdf5_file.close()