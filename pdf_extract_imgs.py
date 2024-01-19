#pip install PyMuPDF

import fitz  # PyMuPDF
import os

# Specify the path to the PDF file
pdf_path = '/home/soyrl/pdf_birds.pdf'

# Specify the directory to save the images
output_dir = '/home/soyrl/pdf_saves_new' 

if not os.path.exists(output_dir): #Create directory if it doesn't exist
    os.makedirs(output_dir)

# Open the PDF file
doc = fitz.open(pdf_path)

# Iterate over each page in the PDF
for page_num in range(len(doc)):
    page = doc[page_num]
    image_list = page.get_images(full=True)

    # Save each image
    image_counter = 1
    for img_index, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]

        # Construct image save path
        image_filename = f"page_{page_num+1}_{image_counter}.png"
        image_save_path = os.path.join(output_dir, image_filename)

        with open(image_save_path, "wb") as image_file:
            image_file.write(image_bytes)

        image_counter += 1

# Close the document
doc.close()