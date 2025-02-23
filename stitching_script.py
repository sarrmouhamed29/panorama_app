import cv2
import numpy as np
import imutils

def stitching_images(image_paths):
    images = []
    for image_path in image_paths:
        img = cv2.imread(image_path)
        if img is not None:
            images.append(img)
            
    if len(images) < 2 :
        raise ValueError("Pas assez d'images pour effectuer un stitching.")
    
    imageStitching = cv2.Stitcher_create()
    error, stitched_img = imageStitching.stitch(images)
    
    if error != cv2.STITCHER_OK:
        raise ValueError ("Impossibles d'assembler les images!")
    
    # Ajouter une bordure
    stitched_img = cv2.copyMakeBorder(stitched_img, 10,10,10,10,
                                      cv2.BORDER_CONSTANT, (0,0,0))
    
    # Traitement post-stitching
    gray = cv2.cvtColor(stitched_img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY)[1]
    
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
    
    contours = imutils.grab_contours(contours)
    areaOI = max(contours, key=cv2.contourArea)
    
    mask = np.zeros(thresh.shape, dtype="uint8")
    x, y, w, h = cv2.boundingRect(areaOI)
    cv2.rectangle(mask, (x,y), (x + w, y + h), 266, -1)
    
    minRectangle = mask.copy()
    sub = mask.copy()
    while cv2.countNonZero(sub) > 0 :
        minRectangle = cv2.erode( minRectangle, None)
        sub = cv2.subtract(minRectangle, thresh)
        
    contours = cv2.findContours(minRectangle.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
    
    x, y, w, h = cv2.boundingRect(areaOI)
    stitched_img = stitched_img[y:y + h, x:x + w]
    
    return stitched_img, "Success"
    

    