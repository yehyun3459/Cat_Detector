import sys,os
import cv2,dlib
import glob
import numpy as np
import datetime
import catDetect
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from imutils import face_utils

class MyApp(QDialog):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
    
    def initUI(self):
        
        tabWidget = QTabWidget()
        tabWidget.addTab(takePicture(),'New Picture/Movie')
        tabWidget.addTab(maskImage(),'Existing Picture/Movie')
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(tabWidget)
        self.setLayout(mainLayout)
        
        self.setWindowTitle("Cat Detect Program")
        
        self.setWindowIcon(QIcon('titlethumb.png')) #어플리케이션 아이콘 넣기
        self.center()
        self.resize(400,400)
        self.show()
        
    def center(self):
        
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
        
class takePicture(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
    
    def initUI(self):
        
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.openCam())
        vbox.addWidget(self.selectOption())
        vbox.addWidget(self.mainFunction())
        self.setLayout(vbox)
    
    def openCam(self):
        

        groupbox = QGroupBox()
        self.open_cb = QCheckBox('Open Camera',self)
        self.open_cb.setToolTip('quit button is \'q\'')
        self.open_cb.clicked.connect(self.openWebCam)
       
            
        vbox = QVBoxLayout()
        vbox.addWidget(self.open_cb)
        groupbox.setLayout(vbox)
        
        return groupbox
    
    def selectOption(self):
        
        self.draw_type=[]
        self.o_image=[-1,
                      'images\hat.png',
                      'images\glasses.png',
                      'images\mustache.png']
        
        groupbox = QGroupBox()
        self.land_cb = QCheckBox('Face Landmark',self)
        
        self.image_cb1 = QCheckBox('head',self)
        self.image_cb2 = QCheckBox('eye',self)
        self.image_cb3 = QCheckBox('nose',self)
        
        self.image1_type = QComboBox(self)
        self.image1_type.addItem('hat')
        self.image1_type.addItem('ham1')
        self.image1_type.addItem('ham2')
        self.image1_type.addItem('ribbon')
        self.image1_type.activated[str].connect(self.changeType1)
        
        
        self.image2_type = QComboBox(self)
        self.image2_type.addItem('glasses')
        self.image2_type.addItem('sunglasses')
        self.image2_type.activated[str].connect(self.changeType2)
        
        self.image3_type = QComboBox(self)
        self.image3_type.addItem('mustache')
        self.image3_type.activated[str].connect(self.changeType3)      
        
        self.land_cb.stateChanged.connect(self.changeList)
        self.image_cb1.stateChanged.connect(self.changeList)
        self.image_cb2.stateChanged.connect(self.changeList)
        self.image_cb3.stateChanged.connect(self.changeList)
        
        
        
        grid = QGridLayout()
        grid.addWidget(self.land_cb,0,0)
       
        grid.addWidget(self.image_cb1,1,0)
        grid.addWidget(self.image1_type,1,1)
        grid.addWidget(self.image_cb2,2,0)
        grid.addWidget(self.image2_type,2,1)
        grid.addWidget(self.image_cb3,3,0)
        grid.addWidget(self.image3_type,3,1)
    
        groupbox.setLayout(grid)
        
        return groupbox
    
     
    def changeList(self,state):
        
        if state==Qt.Checked:
            if self.land_cb.checkState()==2 and catDetect.LANDMARK_TYPE not in self.draw_type:
                self.draw_type.append(catDetect.LANDMARK_TYPE)
            elif self.image_cb1.checkState()==2 and catDetect.HAT_TYPE not in self.draw_type:
                self.draw_type.append(catDetect.HAT_TYPE)
            elif self.image_cb2.checkState()==2 and catDetect.GLASSES_TYPE not in self.draw_type:
                self.draw_type.append(catDetect.GLASSES_TYPE)
            elif self.image_cb3.checkState()==2 and catDetect.MOUTH_TYPE not in self.draw_type:
                self.draw_type.append(catDetect.MOUTH_TYPE)    
        
        else:
            if self.land_cb.checkState()==0 and catDetect.LANDMARK_TYPE in self.draw_type:
                self.draw_type.remove(catDetect.LANDMARK_TYPE)
            elif self.image_cb1.checkState()==0 and catDetect.HAT_TYPE in self.draw_type:
                self.draw_type.remove(catDetect.HAT_TYPE)
            elif self.image_cb2.checkState()==0 and catDetect.GLASSES_TYPE in self.draw_type:
                self.draw_type.remove(catDetect.GLASSES_TYPE)
            elif self.image_cb3.checkState()==0 and catDetect.MOUTH_TYPE in self.draw_type:
                self.draw_type.remove(catDetect.MOUTH_TYPE)  
        
    
    def changeType1(self,text):
        self.o_image[1]='images\\'+text+'.png'
    
    def changeType2(self,text):
        self.o_image[2]='images\\'+text+'.png'
        
    def changeType3(self,text):
        self.o_image[3]='images\\'+text+'.png'
    
    def mainFunction(self):
        
        groupbox = QGroupBox()
        
        tp_button = QPushButton('Take Picture')
        tp_button.clicked.connect(self.captureFrame)
        
        self.tv_button = QPushButton('Start video')
        self.tv_button.setToolTip('Saved in C:\CatCam_MY folder')
        self.tv_button.clicked.connect(self.captureVideo)
        
        
        hbox = QHBoxLayout()
        
        hbox.addWidget(tp_button)
        hbox.addWidget(self.tv_button)
    
        groupbox.setLayout(hbox)
        
        return groupbox
    
    ##action!

    def captureFrame(self):
        
        self.getFrame = True
        
    def captureVideo(self):
        
        print(self.tv_button.text())
        if self.tv_button.text() == 'Start video':
            self.video_path = "C:\CatCam_MY\\"
            if not os.path.isdir(self.video_path):
                os.mkdir(self.video_path)
            
            self.getVideo = True
            self.videoStart = True
            self.tv_button.setText('Stop video')
        
        elif self.tv_button.text() == 'Stop video':
            self.getVideo = False
            self.videoStop = True
            self.tv_button.setText('Start video')
            
    def openWebCam(self):
        self.getFrame = False
        self.getVideo = False
        self.videoStart = False
        self.videoStop = False

        cap = cv2.VideoCapture(0)
        scale = 0.5
        while cap.isOpened():
            ret,img = cap.read()
            
            if not ret:
                break
            
            img_result = img.copy()
            
            img = cv2.resize(img,dsize=None,fx=scale,fy=scale)
            dets = catDetect.detector(img)
            
            for dt in self.draw_type:
                if dt==0: #LANDMARK
                    img_result = catDetect.print_landmarks(img_result,dets,scale)
                    
                else:
                    o_img = cv2.imread(self.o_image[dt],cv2.IMREAD_UNCHANGED)
                    img_result = catDetect.overlay_to_img(img_result,dt,o_img,dets,scale)
                    
            cv2.imshow('result',img_result)
            
            if cv2.waitKey(1)==ord('q'):
                break
            
            
            if self.videoStart==True:
                self.videoStart=False
                now = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
                save_path = self.video_path+'CatVideo_'+now+'.mp4'
                fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
                out = cv2.VideoWriter(save_path,fourcc,cap.get(cv2.CAP_PROP_FPS),(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
            
            if self.getVideo==True:
                out.write(img_result)
                
            if self.videoStop==True:
                self.videoStop=False
                out.release()
                msg = QMessageBox.about(self,'*0*','Saved!')
            
            if self.getFrame==True:
                cv2.imshow('Frame',img_result)
                self.getFrame = False
                file_name = None
                msg = QMessageBox.question(self,'*^_^*','Save?',QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
                if msg == QMessageBox.Yes:
                
                    file_name = QFileDialog.getSaveFileName(self,'Save file','C:\\','JPEG(*.jpg)')
                if file_name is not None:
                    print(file_name)
                    cv2.imwrite(file_name[0],img_result)
                    msg = QMessageBox.about(self,'*0*','Saved!')
                
                cv2.destroyWindow('Frame')
                    
            
        cap.release()
        cv2.destroyAllWindows()
        self.open_cb.toggle()
    
class maskImage(QWidget):

    def __init__(self):
        super().__init__()
        
      
        self.initUI()
    
    def initUI(self):

        start_btn = QPushButton('Start') 
                
        vbox = QVBoxLayout()
        vbox.addWidget(self.selectOption())
        vbox.addWidget(self.readFile())
        vbox.addWidget(start_btn)

        
        start_btn.clicked.connect(self.inputFileType)
        
        self.setLayout(vbox)
        
    
    def readFile(self):
        
        groupbox = QGroupBox()
        
        self.isPic = True
        
        self.select_rbtn1 = QRadioButton('Picture',self)
        self.select_rbtn1.setChecked(True)
        self.select_rbtn2 = QRadioButton('Movie',self)
        
        select_filebtn = QPushButton('Open File',self)
        select_filebtn.clicked.connect(self.searchFile)
        
        
        self.nameEdit = QLineEdit()
        self.nameEdit.dragEnabled()
         
        
        
        grid = QGridLayout()
        grid.addWidget(self.select_rbtn1,0,0)
        grid.addWidget(self.select_rbtn2,0,1)
        grid.addWidget(QLabel('Select file : '),1,0)
        grid.addWidget(self.nameEdit,2,0)
        grid.addWidget(select_filebtn,2,1)
      
    
        groupbox.setLayout(grid)       
        
        return groupbox
        
    def inputFileType(self):
        
        if self.select_rbtn1.isChecked():
            self.makePicResult()
        elif self.select_rbtn2.isChecked():
            self.makeVideoResult()
    
    def searchFile(self):
        
        self.file_name = QFileDialog.getOpenFileName(self, 'Open file', 'C:\\')
        self.nameEdit.setText(self.file_name[0])
        self.fname = self.file_name[0].replace("/","\\")
        
        
    def selectOption(self):
        
        self.draw_type=[]
        self.o_image=[-1,
                      'images\hat.png',
                      'images\glasses.png',
                      'images\mustache.png']
        
        groupbox = QGroupBox()
        self.land_cb = QCheckBox('Face Landmark',self)
        
        self.image_cb1 = QCheckBox('head',self)
        self.image_cb2 = QCheckBox('eye',self)
        self.image_cb3 = QCheckBox('nose',self)
        
        self.image1_type = QComboBox(self)
        self.image1_type.addItem('hat')
        self.image1_type.addItem('ham1')
        self.image1_type.addItem('ham2')
        self.image1_type.addItem('ribbon')
        self.image1_type.activated[str].connect(self.changeType1)
        
        
        self.image2_type = QComboBox(self)
        self.image2_type.addItem('glasses')
        self.image2_type.addItem('sunglasses')
        self.image2_type.activated[str].connect(self.changeType2)
        
        self.image3_type = QComboBox(self)
        self.image3_type.addItem('mustache')
        self.image3_type.activated[str].connect(self.changeType3)      
        
        self.land_cb.stateChanged.connect(self.changeList)
        self.image_cb1.stateChanged.connect(self.changeList)
        self.image_cb2.stateChanged.connect(self.changeList)
        self.image_cb3.stateChanged.connect(self.changeList)
        
        
        
        grid = QGridLayout()
        grid.addWidget(self.land_cb,0,0)
       
        grid.addWidget(self.image_cb1,1,0)
        grid.addWidget(self.image1_type,1,1)
        grid.addWidget(self.image_cb2,2,0)
        grid.addWidget(self.image2_type,2,1)
        grid.addWidget(self.image_cb3,3,0)
        grid.addWidget(self.image3_type,3,1)
    
        groupbox.setLayout(grid)
        
        return groupbox
    
    def changeList(self,state):
        
        if state==Qt.Checked:
            if self.land_cb.checkState()==2 and catDetect.LANDMARK_TYPE not in self.draw_type:
                self.draw_type.append(catDetect.LANDMARK_TYPE)
            elif self.image_cb1.checkState()==2 and catDetect.HAT_TYPE not in self.draw_type:
                self.draw_type.append(catDetect.HAT_TYPE)
            elif self.image_cb2.checkState()==2 and catDetect.GLASSES_TYPE not in self.draw_type:
                self.draw_type.append(catDetect.GLASSES_TYPE)
            elif self.image_cb3.checkState()==2 and catDetect.MOUTH_TYPE not in self.draw_type:
                self.draw_type.append(catDetect.MOUTH_TYPE)    
        
        else:
            if self.land_cb.checkState()==0 and catDetect.LANDMARK_TYPE in self.draw_type:
                self.draw_type.remove(catDetect.LANDMARK_TYPE)
            elif self.image_cb1.checkState()==0 and catDetect.HAT_TYPE in self.draw_type:
                self.draw_type.remove(catDetect.HAT_TYPE)
            elif self.image_cb2.checkState()==0 and catDetect.GLASSES_TYPE in self.draw_type:
                self.draw_type.remove(catDetect.GLASSES_TYPE)
            elif self.image_cb3.checkState()==0 and catDetect.MOUTH_TYPE in self.draw_type:
                self.draw_type.remove(catDetect.MOUTH_TYPE)  
        
    def changeType1(self,text):
        self.o_image[1]='images\\'+text+'.png'
    
    def changeType2(self,text):
        self.o_image[2]='images\\'+text+'.png'
        
    def changeType3(self,text):
        self.o_image[3]='images\\'+text+'.png'


    def makePicResult(self):
        
        img = cv2.imread(self.fname)
        
        if img.shape[0]> 1000 or img.shape[1] > 1000:
            img = catDetect.image_resize(img,1000)
            
        dets = catDetect.detector(img)
            
        print("File name : {}".format(self.fname))
        print("{} faces are detected".format(len(dets)))
        if len(dets) > 0:
            for dt in self.draw_type:
                    
                if dt==0:
                    img = catDetect.print_landmarks(img,dets,1.0)
                        
                else:
                    o_img = cv2.imread(self.o_image[dt],cv2.IMREAD_UNCHANGED)
                    img = catDetect.overlay_to_img(img,dt,o_img,dets)
                        
            cv2.imshow("result",img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
            msg = QMessageBox.question(self,'*^_^*','Save?',QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
            if msg == QMessageBox.Yes:
                
                file_name = QFileDialog.getSaveFileName(self,'Save file','C:\\','JPEG(*.jpg)')
                if file_name is not None:
                    print(file_name)
                    cv2.imwrite(file_name[0],img)
                    msg = QMessageBox.about(self,'*0*','Saved!')
            
            self.nameEdit.setText('')
                
                
        else:
            msg = QMessageBox.about(self,'TT','Please Try again with different Pic')
            self.nameEdit.setText('')
            
    def makeVideoResult(self):
        
        msg = QMessageBox.question(self,'*0*','Please specify a path to save the video in advance!',QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
        
        if msg == QMessageBox.Yes:
            file_name = QFileDialog.getSaveFileName(self,'Save file','C:\\','MP4(*.mp4)')
            
        else:
            file_name = None
            
        cap = cv2.VideoCapture(self.fname)
        fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
        if file_name is not None:
            out = cv2.VideoWriter(file_name[0],fourcc,cap.get(cv2.CAP_PROP_FPS),(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

        while cap.isOpened():
            ret,img = cap.read()
            
            if not ret:
                break

            scale = 1.0
            if img.shape[0]>1000 or img.shape[1]>1000:
                img = catDetect.image_resize(img,1000)
                
            img_result = img.copy()
            
            img = cv2.resize(img,dsize=None,fx=scale,fy=scale)
            
            dets = catDetect.detector(img)
            if len(dets) > 0:
                for dt in self.draw_type:
                    
                    if dt==0:
                        img_result = catDetect.print_landmarks(img_result,dets,scale)
                        
                    else:
                        o_img = cv2.imread(self.o_image[dt],cv2.IMREAD_UNCHANGED)
                        img_result = catDetect.overlay_to_img(img_result,dt,o_img,dets,scale)
        
            if file_name is not None:                
                out.write(img_result)
            cv2.imshow('result',img_result)
            if cv2.waitKey(1)==ord('q'):
                break
            
        cv2.destroyAllWindows()
        cap.release()
        if file_name is not None:                
            out.release()
            msg = QMessageBox.about(self,'*0*','Saved!')
        self.nameEdit.setText('')
        
        
    
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())