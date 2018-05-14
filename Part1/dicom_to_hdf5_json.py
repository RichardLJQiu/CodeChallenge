import os
import sys
import pydicom
import numpy as np
import h5py
import json

dslist = []

# get all dicoms file under current directory and store them in dslist
def load_dataset(dicom_path):
    global dslist    
    for dir_name, subdir_list, file_list in os.walk(dicom_path):
        for filename in file_list:
            if ".dcm" in filename.lower():  # check whether the file's DICOM
                dslist.append(pydicom.read_file(os.path.join(dir_name,filename)))
    # sort dicom based on each file’s Slice Location DICOM tag in ascending order
    dslist.sort(key=lambda ds: ds.SliceLocation, reverse=False)

# store pixel data in "pixel_data_group", and store pixel spacing in "pixel_spacing_group"
def convert_to_hdf5(hdf5_path):
    global dslist
    rescaled_pixel_array = []
    if len(dslist) == 0:
        return
    input_pixel_data_scale = float(1 / np.iinfo(dslist[0].pixel_array.dtype).max)

    for ds in dslist:
        # convert 3D volume data to the range from 0 to 1(float 32)
        pixel_array = [[float(num * input_pixel_data_scale) for num in row] for row in ds.pixel_array]
        rescaled_pixel_array.append(np.asarray(pixel_array))

    # write to hdf5 file
    hdf5_file = h5py.File(hdf5_path, "w")
    pixel_data_grp = hdf5_file.create_group("pixel_data")

    # write ds pixel data into hdf5 
    for i in range(len(rescaled_pixel_array)):
        pixel_data_grp.create_dataset("pixel_data" + str(i), dtype='f4', data=rescaled_pixel_array[i])

    # write pixel spacing in all dimension into hdf5, select PixelSpacing as z dimension spacing
    if len(dslist) > 0:
        pixel_spacing_grp = hdf5_file.create_group("pixel_spacing")
        pixel_spacing_grp.create_dataset("pixel_spacing_x", dtype='f4', data=float(dslist[0].PixelSpacing[0]))
        pixel_spacing_grp.create_dataset("pixel_spacing_y", dtype='f4', data=float(dslist[0].PixelSpacing[1]))
        pixel_spacing_grp.create_dataset("pixel_spacing_z", dtype='f4', data=float(dslist[0].SpacingBetweenSlices))

    hdf5_file.close()
    print("Converted to hdf5 successfully!")

# store series description and image modality name in json file for each dicom file
def convert_to_json(json_path):
    global dslist
    meta_data = dict()
    for i in range(len(dslist)):
        sub_meta = dict()
        sub_meta["seriesdescription"] = dslist[i].SeriesDescription
        sub_meta["modality"] = dslist[i].Modality                    
        meta_data["image" + str(i)] = sub_meta
        
    json_file = open(json_path, "w")
    json.dump(meta_data, json_file)
    json_file.close()
    print("Converted to json successfully!")

if __name__ == "__main__":
    usage = "usage: dicom_to_hdf5_json.py [-i] [-h] [-j]\n\
                optional arguments:\n\
                -i, --input-dicom  path to input DICOM directory\n\
                -h, --output-hdf5  path to output hdf5 file\n\
                -j, --output-json  path to output JSON file\n"
    if len(sys.argv) == 1:
        print(usage)
    else: 
        dicom_path = ""
        hdf5_path = ""
        json_path = ""
        for i in range(1, len(sys.argv), 2):
            if sys.argv[i] == "-i" or sys.argv[i] == "--input-dicom":
                dicom_path = sys.argv[i + 1]
            elif sys.argv[i] == "-h" or sys.argv[i] == "--output-hdf5":
                hdf5_path = sys.argv[i + 1]
            elif sys.argv[i] == "-j" or sys.argv[i] == "--output-json":
                json_path = sys.argv[i + 1]

        if dicom_path != "":
            load_dataset(dicom_path)
            if hdf5_path != "":
                convert_to_hdf5(hdf5_path)
            if json_path != "":
                convert_to_json(json_path)
                