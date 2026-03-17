import numpy as np
import marking
import app
import argparse
import cv2
from gtts import gTTS
from playsound import playsound
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument('--image', type=str, default='output/output.jpg', required=False, help='The image you want to predict on. ')
args = parser.parse_args()

def handwhile() :
    index = 0
    while True :
        try :
          info, gImg = app.main()
          if info == 'Stop' :
              index = index + 1
              if index == 5 :
                  playsound( 'stop.mp3' )
                  index = 0
          marking.drawAndSave( "%s_pred.png"%(args.image.split('.')[0]), info )
          mImg = cv2.imread( "%s_pred_marked.png"%(args.image.split('.')[0]) )
          result = np.concatenate((gImg, mImg), axis=1)
          cv2.imshow('GestureAndMark', result)     # 如果讀取成功，顯示該幀的畫面
          # cv2.destroyWindow('GestureAndMark')
        except Exception as error:
          print( error )
          continue
        time.sleep(2)

    cv2.destroyAllWindows()                 # 結束所有視窗

def hand() :
    info, gImg = app.main()
    if info == 'Stop' :
       playsound( 'stop.mp3' )
    marking.drawAndSave( "%s_pred.png"%(args.image.split('.')[0]), info )
    mImg = cv2.imread( "%s_pred_marked.png"%(args.image.split('.')[0]) )
    result = np.concatenate((gImg, mImg), axis=1)
    cv2.imshow('GestureAndMark', result)     # 如果讀取成功，顯示該幀的畫面

def soundmake() :
    print( 'sound make start' )
    tts = gTTS( text = 'Stop the bus', lang = 'en' )
    tts.save( 'stop.mp3' )
    print( 'end' )
if __name__ == '__main__' :
    #soundmake()
    handwhile()
