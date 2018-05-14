# CodeChallenge	
## Part1: DICOM Input and Output<br>	
### 1. Test dicom convert to hdf5 and json file:<br>	
#### Test case:<br>	
python3 dicom_to_hdf5_json.py -i ../dicom_data -h ../hdf5_data/hdf5_data.hdf5 -j ../json_data/json_data.json<br><br>	
"../dicom_data" ------ path to input DICOM directory<br>	
"../hdf5_data/hdf5_data.hdf5" ------ path to output hdf5 file and filename<br>	
"../json_data/json_data.json" ------ path to output JSON file<br>	
### 2. Test hdf5 convert to dicom file<br>	
#### Test case:<br>	
python3 hdf5_to_dicom.py -h ../hdf5_data/hdf5_data.hdf5 -d ../template.dcm -o ../dicom_output/<br><br>	
"../hdf5_data/hdf5_data.hdf5" ------ path to input hdf5 file<br>	
"../template.dcm" ------ path to the template DICOM directory<br>
"../dicom_output/" ------ path to output DICOM directory<br>
## Part2: Inference Pipeline and 3D Blurring Module<br>	
### Design
At first, I implement the gaussian algorithm to blur a 2D image, and then extend to blur 3D volumne, pixel data computaion is based on hdf5 file.<br> 
### 1. Test 3d blur algorithm(can run this python file directrlty)<br>	
python3 gaussian_blur3d_starter.py<br>
### 2. Test Inference Pipeline pipeline(can run this python file directrlty)<br>
python3 inference_pipeline_starter.py<br>
## Part3: A Web Backend<br>
### Design
I wrote a simple front end page can send Post and Get request through that textfield. Involve Interference Pipeline to execute background job task.<br> 
![WebPage](/webpage.png)<br>
Run server at directory of Part3<br>
./manage.py runserver<br>

### Test1: Post request(localhost:8000)
Can use postman or just type path in the post textfield, I use 3dblurr function as example in Inference Pipeline, it might take a long time to run this function at background.<br>
Example: /job/?job_name=3dblur&in_dir=./part3_backend/input_volume/mytestfile.hdf5<br>
### Test2: Get request
Can type path in the get textfield or type in broswer url field.<br> 
Example: query/601<br>
