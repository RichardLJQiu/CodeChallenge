import numpy as np

volume = []
meta_data = {}
config = {"sigma" : 3}

def load_3dvolume(volume_path):
    hdf5_file = h5py.File(volume_path, "r")
    pixel_data_grp = hdf5_file["pixel_data"]
    inverse_convert_pixelscale = np.iinfo(np.int16).max

    for pixel_data_index in pixel_data_grp:
        pixel_array = pixel_data_grp[pixel_data_index][()]
        inverse_convert_pixel_array = [[np.int16(num * inverse_convert_pixelscale) for num in row] for row in pixel_array]
        volume.append(inverse_convert_pixel_array)
        
    pixel_spacing_grp = hdf5_file["pixel_spacing"]
    meta_data["pixel_spacing_x"] = pixel_spacing_grp["pixel_spacing_x"].value
    meta_data["pixel_spacing_y"] = pixel_spacing_grp["pixel_spacing_y"].value
    meta_data["pixel_spacing_z"] = pixel_spacing_grp["pixel_spacing_z"].value
    
    hdf5_file.close()
    
# 3d gaussian blur
def caculate_blurred_img(img, mask):
    row, col, lay = img.shape
    m, n, o = mask.shape
    new = np.zeros((row + m - 1, col + n - 1, lay + o -1))
    n = n // 2
    m = m // 2
    o = o // 2
    blurred_img = np.zeros(img.shape)
    new[m:new.shape[0] - m, n:new.shape[1] - n, o:new.shape[2] - o] = img
    for i in range(m, new.shape[0] - m):
        for j in range(n, new.shape[1] - n):
            for k in range(o, new.shape[2] - o):
                temp = new[i - m:i + m + 1, j - n:j + n + 1, k - o:k + o + 1]
                result = temp * mask
                blurred_img[i - m, j - n, k - o] = result.sum()
    return blurred_img

def gaussian(x_space, y_space, z_space, sigma):
    gaussian = np.zeros((2 * x_space + 1, 2 * y_space + 1, 2 * z_space + 1))
    row = 0
    for x in range(-x_space, x_space + 1):
        col = 0
        for y in range(-y_space, y_space + 1):
            lay = 0
            for z in range(-z_space, z_space + 1):
                d1 = np.power(sigma, 3) * np.power(2 * np.pi, 3 / 2)
                d2 = np.exp(-(x**2 + y**2 + z**2) / (2 * sigma**2))
                gaussian[row][col][lay] = (1 / d1) * d2
                lay = lay + 1
            col = col + 1
        row = row + 1
    return gaussian
    
def gaussian_blur3d(input_3d: np.ndarray, meta_data: dict, config: dict) -> np.array:
    # Performs 3D Gaussian blur on the input volume

    # :param input_3d: input volume in 3D numpy array
    # :param meta_data: a dict object with the following key(s):
    #     'spacing': 3-tuple of floats, the pixel spacing in 3D
    # :param config: a dict object with the following key(s):
    #     'sigma': a float indicating size of the Gaussian kernel
    
    # :return: the blurred volume in 3D numpy array, same size as input_3d
    mask = gaussian(5, 5, 5, config["sigma"])
    blurred_img = caculate_blurred_img(input_3d, mask)
    return blurred_img
    
load_3dvolume("mytestfile.hdf5")
input_3d = np.asarray(volume)
blurred_img = gaussian_blur3d(input_3d, meta_data, config)
