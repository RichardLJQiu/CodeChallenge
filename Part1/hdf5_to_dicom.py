import pydicom
import os
import numpy as np
import h5py
import random
import sys

# reverse the process, convert hdf5 and json to dicom
def hdf5_to_dicom(hdf5_path, temp_dicom_path, out_dicom_path): 
	template = pydicom.read_file(temp_dicom_path)
	hdf5_file = h5py.File(hdf5_path, "r")
	# get pixel_data from hdf5 file
	pixel_data_grp = hdf5_file["pixel_data"]
	inverse_convert_pixelscale = np.iinfo(template.pixel_array.dtype).max
	i = 0
	for pixel_data_index in pixel_data_grp:
	    pixel_array = pixel_data_grp[pixel_data_index][()]
	    # convert the pixel data scale to original range
	    inverse_convert_pixel_array = [[np.int16(num * inverse_convert_pixelscale) for num in row] for row in pixel_array]
	    dicom_pixel_array = np.asarray(inverse_convert_pixel_array)
	    # replace pixel data of template
	    template.PixelData = dicom_pixel_array
	    # I know for this series Instance UID, it is generated base many attribtes, like date etc, 
	    # due to time limited, I choose to give a fix UID for it.
	    template.SeriesInstanceUID = "1.3.6.1.4.1.9590.100.1.1.369231118011061003403421859172643143649"
	    # In order to generate different UID, I know we can implement in other ways, if time enough, '
	    # I can add more code for UID generation
	    template.SOPInstanceUID = "1.3.6.1.4.1.9590.100.1.1.369231118011061003403421859172643143" + "{:03}".format(random.randrange(1, 10**3))
	    template.save_as(out_dicom_path + "image" + str(i) + ".dcm")
	    i = i + 1
	hdf5_file.close()

if __name__ == "__main__":
    usage = "usage: hdf5_to_dicom.py [-h] [-d] [-o]\n\
                optional arguments:\n\
                -h, --input-hdf5  path to input hdf5 file\n\
                -d, --input-dicom  path to the template DICOM directory\n\
                -o, --output-dicom path to output DICOM directory\n"

    if len(sys.argv) == 1:
        print(usage)
    else: 
        hdf5_path = ""
        temp_dicom_path = ""
        out_dicom_path = ""
        for i in range(1, len(sys.argv), 2):
            if sys.argv[i] == "-h" or sys.argv[i] == "--input-hdf5":
                hdf5_path = sys.argv[i + 1]
            elif sys.argv[i] == "-d" or sys.argv[i] == "--input-dicom":
                temp_dicom_path = sys.argv[i + 1]
            elif sys.argv[i] == "-o" or sys.argv[i] == "--output-dicom":
                out_dicom_path = sys.argv[i + 1]

        if hdf5_path != "":
            hdf5_to_dicom(hdf5_path, temp_dicom_path, out_dicom_path)