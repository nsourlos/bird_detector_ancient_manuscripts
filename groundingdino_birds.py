from groundingdino.util.inference import load_model, load_image, predict, annotate
import cv2
import os
import time

start=time.time() #Takes <1sec per image

model = load_model("/home/soyrl/GroundingDINO/groundingdino/config/GroundingDINO_SwinB_cfg.py", 
                   "/home/soyrl/weights/groundingdino_swinb_cogcoor.pth")
#Alternatively we can use 'T_OGC' and 't_ogc.pth' endings for the two paths above - doesn't perform as well

path_imgs = 'pdf_saves_new/'
all_imgs=os.listdir(path_imgs)

save_imgs_path = path_imgs+'annotated/'
#If save_imgs_path doesn't exist, create it
if not os.path.exists(save_imgs_path):
    os.makedirs(save_imgs_path)

for img in sorted(all_imgs):
    IMAGE_PATH = path_imgs+img

    TEXT_PROMPT = "bird ."
    BOX_TRESHOLD = 0.4 #detection threshold confidence
    TEXT_TRESHOLD = 0.4 #if label will be shown or not - use same as above or lower

    image_source, image = load_image(IMAGE_PATH) 

    boxes, logits, phrases = predict(
        model=model,
        image=image,
        caption=TEXT_PROMPT,
        box_threshold=BOX_TRESHOLD,
        text_threshold=TEXT_TRESHOLD
    )

    print(IMAGE_PATH) #Prints the path of the image
    with open("output_dino.txt", "a") as file: #First time write the command we send to LlaVa to the output file
        file.write(IMAGE_PATH)
        file.write('\n')

    result = "yes" if any(element != "" for element in phrases) else "no"
    print(result) #Prints 'yes' if there is a bird in the image, 'no' if there isn't
    with open("output_dino.txt", "a") as file: #First time write the command we send to LlaVa to the output file
        file.write(result)
        file.write('\n')

    #Annotates image with boxes and labels 
    annotated_frame = annotate(image_source=image_source, boxes=boxes, logits=logits, phrases=phrases) 
    #Saves the annotated image in the same folder as the original image
    cv2.imwrite(save_imgs_path+IMAGE_PATH.split('/')[1], annotated_frame) 

end=time.time()
print("Took",str(end-start),'secs to process',str(len(all_imgs)),'images') #Prints the time it took to run the script

with open("output_dino.txt", "a") as file: #First time write the command we send to LlaVa to the output file
    file.write('\n')
    file.write("Took"+str(end-start)+'secs to process'+str(len(all_imgs))+'images')