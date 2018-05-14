# CodeChallenge
Part1: DICOM Input and Output<br>
1. Test dicom convert to hdf5 and json file:<br>
python3 dicom_to_hdf5_json.py -i ../dicom_data -h ../hdf5_data/hdf5_data.hdf5 -j ../json_data/json_data.json<br>
-i path to input DICOM directory<br>
-h path to output hdf5 file<br>
-j path to output JSON file<br>
2. Test hdf5 convert to dicom file<br>

python3 hdf5_to_dicom.py -h ../hdf5_data/hdf5_data.hdf5 -d ../template.dcm -o ../dicom_output/<br>
