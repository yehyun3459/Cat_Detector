import cv2,dlib
import numpy as np
from imutils import face_utils

detector = dlib.simple_object_detector("detector.svm")
predictor = dlib.shape_predictor("cat_predictor.dat")

SCALE_FACTOR = 0.7
    
###cat face information###
LEFT_EYE = 0
RIGHT_EYE = 1
MOUTH = 2
LEFT_EAR_1 = 3
LEFT_EAR_2 = 4
LEFT_EAR_3 = 5
RIGHT_EAR_1 = 6
RIGHT_EAR_2 = 7
RIGHT_EAR_3 = 8
###

##overlay image type##
LANDMARK_TYPE = 0
HAT_TYPE = 1
GLASSES_TYPE = 2
MOUTH_TYPE = 3
###
    
def image_resize(img,img_size):
   
    old_size = img.shape[:2] 
    ratio = float(img_size) / max(old_size)
    new_size = tuple([int(x*ratio) for x in old_size])
    
    img= cv2.resize(img, (new_size[1], new_size[0]))
        
    return img
    
def print_landmarks(img_result,dets,scale):
    
    for i,d in enumerate(dets):
        print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}"
              .format(i,d.left(),d.top(),d.right(),d.bottom()))
        x1,y1 = int(d.left()/scale), int(d.top()/scale)
        x2,y2 = int(d.right()/scale),int(d.bottom()/scale)
            
        #draw bounding box
        cv2.rectangle(img_result,pt1=(x1,y1),pt2=(x2,y2),thickness=2,color=(255,0,0),lineType=cv2.LINE_AA)
        
        #draw face detail info
        shape = predictor(img_result,d)
        shape = face_utils.shape_to_np(shape)
        for k,p in enumerate(shape):
            cv2.circle(img_result,center=tuple((p/scale).astype(int)),radius=2,color=(0,0,255),thickness=2)
            cv2.putText(img_result,str(k),tuple((p/scale).astype(int)),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),1,cv2.LINE_AA)
            
    return img_result
        
def angle_between(p1,p2):
    dx = p2[0]-p1[0]
    dy = p2[1]-p1[1]
    
    return np.degrees(np.arctan2(dy,dx))

def overlay_transparent(bg_img,img_to_overlay_t,x,y,overlay_size=None):

    #convert 3 channels to 4 channels
    if bg_img.shape[2]==3:
        bg_img = cv2.cvtColor(bg_img,cv2.COLOR_BGR2BGRA) #BGR이미지에 Alpha채널 추가
        #Alpha채널은 투명도를 의미함
        
    if overlay_size is not None:
        img_to_overlay_t = cv2.resize(img_to_overlay_t,overlay_size)
        #입력받은 사이즈로 재조정
    
    b, g, r, a = cv2.split(img_to_overlay_t)
    
    mask = cv2.medianBlur(a,5)
    
    h,w,_=img_to_overlay_t.shape
    roi = bg_img[int(y-h/2):int(y+h/2),int(x-w/2):int(x+w/2)]
    
    img1_bg = cv2.bitwise_and(roi.copy(),roi.copy(),mask=cv2.bitwise_not(mask))
    img2_fg = cv2.bitwise_and(img_to_overlay_t,img_to_overlay_t,mask=mask)
    #bitwise_and : 이미지 합성
    
    bg_img[int(y-h/2):int(y+h/2),int(x-w/2):int(x+w/2)] = cv2.add(img1_bg,img2_fg)
        
    #convert 4 channels to 3 channels
    bg_img = cv2.cvtColor(bg_img, cv2.COLOR_BGRA2BGR)
    
    return bg_img
    
def overlay_to_img(overlay_img,img_type,o_image,dets,scale=1.0,resize_rate=1):
    #shape는 리스트 형태로 읽는다(np)
    

    for i, d in enumerate(dets):
        shape = predictor(overlay_img,d)
        shape = face_utils.shape_to_np(shape) 
        shape = (shape/scale).astype(int)
            
            
        #만약 코에만 장식을 붙이는거라면
        if img_type == MOUTH_TYPE: 
            image_center = shape[MOUTH]
            image_size = np.linalg.norm(shape[LEFT_EYE]-shape[RIGHT_EYE])*1.5
     
        else:
            if img_type == HAT_TYPE:
                roi = LEFT_EAR_3
                roi2 = RIGHT_EAR_1
                image_size = np.linalg.norm(shape[roi]-shape[roi2])*resize_rate
            elif img_type == GLASSES_TYPE:
                #resize_rate = resize_rate*2
                roi = LEFT_EYE
                roi2 = RIGHT_EYE
                image_size = np.linalg.norm(shape[roi]-shape[roi2])*2
            image_center = np.mean([shape[roi],shape[roi2]],axis=0)
            
                        
            angle = -angle_between(shape[roi],shape[roi2])
            M=cv2.getRotationMatrix2D((o_image.shape[1]/2,o_image.shape[0]/2),angle,1.0)
            o_image = cv2.warpAffine(o_image,M,(o_image.shape[1],o_image.shape[0]))
                        
        try:
            overlay_img =overlay_transparent(overlay_img,o_image,image_center[0],image_center[1],overlay_size=(int(image_size),int(o_image.shape[0]*image_size/o_image.shape[1])))
        except Exception as ex:
            print('failed overlay img : ',ex)
                
    return overlay_img
                