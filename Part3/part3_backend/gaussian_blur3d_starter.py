import numpy as np
import h5py

volume = []
meta_data = {}
config = {"sigma": 5}
input_3d = None
blurred_img = None

# load 3d volume from hdf5 file and stored in input_3d
def load_3dvolume(volume_path):
    global input_3d
    hdf5_file = h5py.File(volume_path, "r")
    pixel_data_grp = hdf5_file["pixel_data"]
    inverse_convert_pixelscale = np.iinfo(np.int16).max

    for pixel_data_index in pixel_data_grp:
        pixel_array = pixel_data_grp[pixel_data_index][()]
        volume.append(pixel_array)

    pixel_spacing_grp = hdf5_file["pixel_spacing"]
    meta_data["pixel_spacing_x"] = pixel_spacing_grp["pixel_spacing_x"].value
    meta_data["pixel_spacing_y"] = pixel_spacing_grp["pixel_spacing_y"].value
    meta_data["pixel_spacing_z"] = pixel_spacing_grp["pixel_spacing_z"].value

    hdf5_file.close()
    input_3d = np.asarray(volume)
    return input_3d, meta_data, config

# gaussian blured algorithm is to calculate the value of the blur point according to its neighbor pixels
# as the formula from https://en.wikipedia.org/wiki/Gaussian_blur, I made a "mask" to set its distance
# with neighbor pixels, and then mulitple the normal distribution possiblity.
def gaussian(x_space, y_space, z_space, sigma):
    gaussian = np.zeros((2 * x_space + 1, 2 * y_space + 1, 2 * z_space + 1))
    row = 0
    for x in range(-x_space, x_space + 1):
        col = 0
        for y in range(-y_space, y_space + 1):
            lay = 0
            for z in range(-z_space, z_space + 1):
                d1 = np.power(sigma, 3) * np.power(2 * np.pi, 3 / 2)
                d2 = np.exp(-(x ** 2 + y ** 2 + z ** 2) / (2 * sigma ** 2))
                gaussian[row][col][lay] = (1 / d1) * d2
                lay = lay + 1
            col = col + 1
        row = row + 1
    return gaussian

# I spent too much time on figuring the gaussian algorithm and how to extend from 2d blurrd image to 3d volume,
# this function use the mask we generate from func:gaussian to multiple with the input_3d, finally we got
# the blurred image.
def caculate_blurred_img(img, mask):
    row, col, lay = img.shape
    m, n, o = mask.shape
    new = np.zeros((row + m - 1, col + n - 1, lay + o - 1))
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

# The pixel spacing from different dimension I think we should discuss how to involve the calculation
# this is my personl idea and use fixed space to calcaute the blurred image
def gaussian_blur3d(input_3d: np.ndarray, meta_data: dict, config: dict) -> np.array:
    # Performs 3D Gaussian blur on the input volume
    mask = gaussian(10, 10, 10, config["sigma"])
    blurred_img = caculate_blurred_img(input_3d, mask)
    return blurred_img

# pre_gaussian_blur3d and post_gaussian_blur3d used for InterferencePipline test
def pre_gaussian_blur3d(input_volume_path):
    global input_3d, meta_data, config
    input_3d, meta_data, config = load_3dvolume(input_volume_path)


def run_gaussian_blur3d():
    global blurred_img, input_3d, meta_data, config
    blurred_img = gaussian_blur3d(input_3d, meta_data, config)

def post_gaussian_blur3d(output_volume_path):
    # write blurred image to hdf5 file
    hdf5_file = h5py.File(output_volume_path + "blurred_img.hdf5", "w")
    pixel_data_grp = hdf5_file.create_group("pixel_data")
    for i in range(len(blurred_img)):
        pixel_data_grp.create_dataset("pixel_data" + str(i), dtype='f4', data=blurred_img[i])
    hdf5_file.close()

