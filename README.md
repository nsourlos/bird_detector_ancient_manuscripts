# Automatic detection of birds in ancient manuscripts

<!-- ![Alt text](./semi-automated-exe-and-msi-file-installation-windows-10.svg) -->

[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![forthebadge](https://forthebadge.com/images/badges/uses-badges.svg)](https://forthebadge.com)

[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-no-red.svg)](https://github.com/nsourlos/automatic_bird_detection_in_ancient_manuscripts)

> This tool is used to detect birds in ancient manuscripts. There are two different approaches:
1. Using [**Llava**](https://llava-vl.github.io/) (Large Language Model with vision), as in the file [llava_imgs_tcli.py](./llava_imgs_tcli.py).
2. Using [**GroundingDINO**](https://github.com/IDEA-Research/GroundingDINO), a state of the art object detector, as in the file [groundingdino_birds.py](./groundingdino_birds.py)

The second method is the one we prefer due to being faster, allowing us to modify the detection threshold, and having better Negative Predictive Value (NPV). By using it we can exclude all images without birds, and therefore save time from manually checking all images in a manuscript. Both methods have a lot of extra FPs.

An example of a TP, FP, FN, and TN image is shown below:

![Alt text](./pics/86_TP.png)
- Example of an image with a correct bird detection (TP)

![Alt text](./pics/31_FP.png)
- Example of an image with incorrect bird detections (FPs). A correct bird is also detected.

![Alt text](./pics/104_FN.png)
- Example of an image of a bird not detected (FN)

![Alt text](./pics/21_TN.png)
- Example of an image with no detections while there was no bird (TN)

# [groundingdino_birds.py](./groundingdino_birds.py)

This Python script is used for object detection in images, specifically for bird detection in our case. It uses a pre-trained model from the [GroundingDINO](https://github.com/IDEA-Research/GroundingDINO) project. Installation of dependencies can also be found in the project link. Model weights should be downloaded as well from the git repository above. 

It returns a file named `output_dino.txt` with the name of each image, its page number in the pdf, and if it contains a bird or not (yes or no). It also returns the total processing time for all images (<1sec/image). 

## Key Variables

- `model`: The pre-trained model loaded from a path (needs to be specified by the user).
- `path_imgs`: The directory path where the images to be processed are stored (should be specified by user)
- `all_imgs`: List of all images in the `path_imgs` directory.
- `save_imgs_path`: The directory path where the annotated images will be saved.
- `IMAGE_PATH`: The path of the current image being processed.
- `TEXT_PROMPT`: The label for the object of interest (in our case **bird**).
- `BOX_TRESHOLD`: The confidence threshold for object detection (in our case **0.4**).
- `TEXT_TRESHOLD`: The confidence threshold for displaying the label (in our case **0.4**).
- `image_source, image`: The original and processed image.

## Workflow

1. Load the pre-trained model.
2. Get the list of all images in the specified directory.
3. Create a directory for saving the annotated images if it doesn't exist.
4. For each image in the directory:
   - Load the image.
   - Predict the bounding boxes, confidence scores, and labels.
   - Annotate the image with the predictions.
   - Save the annotated image.

## Usage

This script is meant to be run as a standalone script. It does not take any command-line arguments. All configurations are done within the script itself.


# [llava_imgs_tcli.py](./llava_imgs_tcli.py)

This script is created based on the issue in https://github.com/haotian-liu/LLaVA/issues/540.

The files [tcli](./tcli.py) and [cli](./cli.py) should be placed inside the `LLaVA\llava\serve` folder (will be cloned from git below).

If errors occur, consider changing `time.sleep(25)` to `30`.

It returns a file named `output_llava.txt` with the name of each image, its page number in the pdf, and if it contains a bird or not (yes or no). It also returns the time it took to process one image (the final one), and the total processing time for all images (~35secs/image). 

Dependencies:
-------------
<!-- These lines (---) same as ## -->
To run this script, you need to clone the LLaVA repository and set up the environment as follows:

1. Clone the LLaVA repository:
```bash
git clone https://github.com/haotian-liu/LLaVA.git
```

2. Navigate to the LLaVA directory:
```bash
cd LLaVA 
```


3. Create a new conda environment named `llava` with Python 3.10:
```bash
conda create -n llava python=3.10 -y
```
4. Activate the `llava` environment:
```bash
conda activate llava
```

5. Upgrade pip to enable PEP 660 support:
```bash
pip install --upgrade pip
```
6. Install the LLaVA package:
```bash
pip install -e .
```


Modules:
--------
Below some important libraries that are used along with a simple explanation of them:

- `subprocess`: Allows you to spawn new processes, connect to their input/output/error pipes, and obtain their return codes.
- `select`: Allows high-efficiency I/O multiplexing.
- `fcntl`: The fcntl module performs file control and I/O control on file descriptors.
- `errno`: Defines symbolic names for the errno numbers.
- `selectors`: High-level I/O multiplexing.

Key Variables:
----------
- `img_path`: The path where the images are stored (needs to be specified by the user).
- `all_imgs`: A sorted list of all images in the directory specified by img_path.
- `all_paths`: A list of paths for each image in all_imgs.
- `commands`: A list of commands to be executed. In this case, it's a command to run the `tcli` module of the `llava.serve` package with specified model path and load-4bit option.


# [pdf_extract_imgs.py](./pdf_extract_imgs.py)

This script is used to extract images from a PDF file.

## Modules

- `PyPDF2`: A Python library to extract document information and content, split documents page by page, merge documents page by page, and decrypt PDF files.
This should be installed with:
```bash
pip install PyMuPDF
```

## Variables

- `pdf_path`: The path to the PDF file from which images are to be extracted (needs to be specified by the user).
- `output_dir`: The directory where the extracted images will be stored (needs to be specified by the user).