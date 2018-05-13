import pydicom
import os
import numpy as np
import h5py
from matplotlib import pyplot, cm

PathDicom = "./dicom_data/"
dslist = []
volume = []
rescaled_pixel_array = []

for dirName, subdirList, fileList in os.walk(PathDicom):
    for filename in fileList:
        if ".dcm" in filename.lower():  # check whether the file's DICOM
            dslist.append(pydicom.read_file(os.path.join(dirName,filename)))

dslist.sort(key=lambda ds: ds.SliceLocation, reverse=False)
input_pixel_data_scale = float(1 / np.iinfo(dslist[0].pixel_array.dtype).max)

for ds in dslist:
    pixel_array = [[float(num * input_pixel_data_scale) for num in row] for row in ds.pixel_array]
    rescaled_pixel_array.append(np.asarray(pixel_array))

# convert to hdf5 file
import h5py
hdf5_file = h5py.File("mytestfile.hdf5", "w")
pixel_data_grp = hdf5_file.create_group("pixel_data")

# write ds pixel data into hdf5 
for i in range(len(rescaled_pixel_array)):
    pixel_data_grp.create_dataset("pixel_data" + str(i), dtype='f4', data=rescaled_pixel_array[i])

# write pixel spacing in all dimension into hdf5
if len(dslist) > 0:
    # Load dimensions based on the number of rows, columns, and slices (along the Z axis)
    ConstPixelDims = (int(dslist[0].Rows), int(dslist[0].Columns), len(dslist))
    # ConstPixelDims = (256, 256, 180)
    
    # Load spacing values
    ConstPixelSpacing = (float(dslist[0].PixelSpacing[0]), float(dslist[0].PixelSpacing[1]), float(dslist[0].SpacingBetweenSlices))
    # ConstPixelSpacing = (0.703125, 0.703125, 2.0)
    
    x = numpy.arange(0.0, (ConstPixelDims[0]+1)*ConstPixelSpacing[0], ConstPixelSpacing[0])
    y = numpy.arange(0.0, (ConstPixelDims[1]+1)*ConstPixelSpacing[1], ConstPixelSpacing[1])
    z = numpy.arange(0.0, (ConstPixelDims[2]+1)*ConstPixelSpacing[2], ConstPixelSpacing[2])
    
    pixel_spacing_grp = hdf5_file.create_group("pixel_spacing")
    pixel_spacing_grp.create_dataset("pixel_spacing_x", dtype='f4', data=x)
    pixel_spacing_grp.create_dataset("pixel_spacing_y", dtype='f4', data=y)
    pixel_spacing_grp.create_dataset("pixel_spacing_z", dtype='f4', data=z)

hdf5_file.close()

# write Series description and imaging modality name to json file
import json
meta_data = dict()
for i in range(len(dslist)):
    sub_meta = dict()
    sub_meta["seriesdescription"] = dslist[i].SeriesDescription
    sub_meta["modality"] = dslist[i].Modality                    
    meta_data["image" + str(i)] = sub_meta
    
json_file = open("myJson.json", "w")
json.dump(meta_data, json_file)
json_file.close()