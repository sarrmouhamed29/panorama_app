import cv2 as cv
import numpy as np
import imutils

class ImageStitcher:
    def __init__(self):
        self.stitcher = cv.Stitcher_create()
        
    def stitch_images(self, image_paths):
        """
        Assemble plusieurs images en une seule panoramique 
        Args:
            image_paths (list): Liste des chemins des images a assembler
            
        Returns : tuple: (image assemblee ou None, message de statut)
        """
        result_img, message, _ = self.stitch_images_with_process(image_paths)
        return result_img, message
        
    def stitch_images_with_process(self, image_paths):
        """
        Assemble plusieurs images en une seule panoramique et capture le processus
        Args:
            image_paths (list): Liste des chemins des images a assembler
            
        Returns : tuple: (image assemblee ou None, message de statut, liste des images du processus)
        """
        
        # charger les images
        images = []
        process_images = []
        
        for image_path in image_paths: 
            img = cv.imread(image_path)
            if img is not None:
                images.append(img)
                
        if len(images) < 2:
            return None, "Pas assez d'images", []
        
        # Étape 1: Visualiser les images source avec les points clés
        detector = cv.SIFT_create()
        keypoints_image = images[0].copy()
        for img in images:
            kp = detector.detect(img, None)
            temp = cv.drawKeypoints(img.copy(), kp, None, color=(0,255,0))
            if len(process_images) == 0:
                process_images.append(temp)
            else:
                # Redimensionner pour avoir la même hauteur
                h, w = process_images[0].shape[:2]
                aspect = w / h
                new_h = h
                new_w = int(img.shape[1] * (new_h / img.shape[0]))
                resized = cv.resize(temp, (new_w, new_h))
                combined = np.hstack([process_images[0], resized])
                process_images[0] = combined
        
        # Étape 2: Correspondance des points clés (simulée)
        if len(images) >= 2:
            img1, img2 = images[0], images[1]
            kp1, des1 = detector.detectAndCompute(img1, None)
            kp2, des2 = detector.detectAndCompute(img2, None)
            
            matcher = cv.BFMatcher()
            matches = matcher.knnMatch(des1, des2, k=2)
            
            good_matches = []
            for m, n in matches:
                if m.distance < 0.75 * n.distance:
                    good_matches.append(m)
            
            match_img = cv.drawMatches(img1, kp1, img2, kp2, good_matches[:50], None, flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
            process_images.append(match_img)
        
        # effectuez le stitching
        error, stitched_img = self.stitcher.stitch(images)
        
        if error != cv.STITCHER_OK:
            return None, "Echec du stitching, nombre d'images a assembler < 2 ou images non correspondantes", process_images
        
        # Étape 3: Estimation homographique (résultat intermédiaire)
        # Simuler une visualisation de l'homographie
        warped_image = stitched_img.copy()
        h, w = warped_image.shape[:2]
        process_images.append(warped_image)
        
        # Étape 4: Alignement des images
        aligned_img = stitched_img.copy()
        # Ajouter un cadre pour visualiser l'alignement
        aligned_img = cv.copyMakeBorder(aligned_img, 20, 20, 20, 20, cv.BORDER_CONSTANT, (0, 0, 255))
        process_images.append(aligned_img)
        
        # Étape 5: Fusion des images
        gray = cv.cvtColor(stitched_img, cv.COLOR_BGR2GRAY)
        thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY)[1]
        fusion_img = cv.cvtColor(thresh, cv.COLOR_GRAY2BGR)
        process_images.append(fusion_img)
        
        # post-traitement et étape finale
        processed_img = self._post_process(stitched_img)
        process_images.append(processed_img)
        
        return processed_img, "Success", process_images
    
    def _post_process(self, stitched_img):
        """
        Effectur le post-traitement de l'image assemblee

        Args:
            stitched_img : Image Assemblee
            
        Returns: Image Traitee
        """
        # ajouter une bordure
        stitched_img = cv.copyMakeBorder(
            stitched_img, 10, 10, 10, 10,
            cv.BORDER_CONSTANT, (0,0,0)
        )
        
        # convertir en niveau de gris
        gray = cv.cvtColor(stitched_img, cv.COLOR_BGR2GRAY)
        blurred = cv.GaussianBlur(gray, (5, 5), 0)
        thresh = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY)[1]
        
        # trouver les contours 
        contours = cv.findContours(
            thresh.copy(),
            cv.RETR_EXTERNAL,
            cv.CHAIN_APPROX_SIMPLE
        )
        
        contours = imutils.grab_contours(contours)
        areaOI = max(contours, key=cv.contourArea)
        
        # creer un masque
        mask = np.zeros(thresh.shape, dtype="uint8")
        
        x, y, w, h = cv.boundingRect(areaOI)
        cv.rectangle(mask, (x,y), (x+w, y+h), 255, -1)
        
        # erosion du rectangele
        minRectangle = mask.copy()
        sub = mask.copy()
        
        while cv.countNonZero(sub) > 0:
            minRectangle= cv.erode(minRectangle, None)
            sub = cv.subtract(minRectangle, thresh)
            
        # trouver le contours final
        
        contours = cv.findContours(
            minRectangle.copy(),
            cv.RETR_EXTERNAL,
            cv.CHAIN_APPROX_SIMPLE
        )
        
        contours = imutils.grab_contours(contours)
        areaOI = max(contours, key=cv.contourArea)
        
        # decouper l'image final
        x, y, w, h = cv.boundingRect(areaOI)
        return stitched_img[y:y + h, x: x + w]