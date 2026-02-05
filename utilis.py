
import cv2
import imutils
import os
from skimage.metrics import structural_similarity as ssim

def detect_tampering(original_path, uploaded_path):
    """
    ML Logic: Original and Uploaded image-ah compare panni 
    pixel differences-ah highlight pannum.
    """
    
    # 1. Rendu image-aiyum load panrom
    original = cv2.imread(original_path)
    uploaded = cv2.imread(uploaded_path)

    # 2. Image size mismatch aagama irukka uploaded-ah resize panrom
    uploaded = cv2.resize(uploaded, (original.shape[1], original.shape[0]))

    # 3. Grayscale-ku mathi pixel intensity-ah check panrom
    gray_org = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    gray_up = cv2.cvtColor(uploaded, cv2.COLOR_BGR2GRAY)

    # 4. SSIM Algorithm use panni similarity score calculate panrom
    # Score 1.0 na 100% match. Koraivaga irundha tampering nadandhiruku.
    (score, diff) = ssim(gray_org, gray_up, full=True)
    diff = (diff * 255).astype("uint8")

    # 5. Thresholding: Differences irukura area-va mattum isolate panrom
    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # 6. Forgery nadandha specific areas-la RED RECTANGLES draw panrom
    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(uploaded, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # 7. Final Report Image-ah save panrom
    result_filename = "tamper_analysis_report.png"
    result_path = os.path.join("static/results", result_filename)
    
    # Results folder illana create pannikko
    if not os.path.exists("static/results"):
        os.makedirs("static/results")
        
    cv2.imwrite(result_path, uploaded)
    
    # Score and image path-ah return panrom (main.py kaga)
    return score, result_path

