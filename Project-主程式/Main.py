import os,time,cv2, sys, math
import tensorflow.compat.v1 as tf
import argparse
import numpy as np
import time
import marking
import app
import read_txt as rt
import client
import pyscreenshot as ImageGrab
from playsound import playsound
from PIL import Image

from utils import utils, helpers
from builders import model_builder

tf.compat.v1.disable_eager_execution()
parser = argparse.ArgumentParser()
parser.add_argument('--inputVideo', type=str, default='no', required=False, help='The video you want to predict on. ')
parser.add_argument('--image', type=str, default='output/output.jpg', required=False, help='The image you want to predict on. ')
parser.add_argument('--checkpoint_path', type=str, default='BDD-512-640/Checkpoint/latest_model_FC-DenseNet103_CamVid.ckpt', required=False, help='The path to the latest checkpoint weights for your model.')
parser.add_argument('--crop_height', type=int, default=480, help='Height of cropped input image to network')
parser.add_argument('--crop_width', type=int, default=640, help='Width of cropped input image to network')
parser.add_argument('--model', type=str, default='FC-DenseNet103', required=False, help='The model you are using')
parser.add_argument('--dataset', type=str, default="CamVid", required=False, help='The dataset you are using')
args = parser.parse_args()

class_names_list, label_values = helpers.get_label_info(os.path.join(args.dataset, "class_dict.csv"))

num_classes = len(label_values)

print("\n***** Begin prediction *****")
print("Video -->", args.inputVideo)
print("Dataset -->", args.dataset)
print("Model -->", args.model)
print("Crop Height -->", args.crop_height)
print("Crop Width -->", args.crop_width)
print("Num Classes -->", num_classes)
print("Image -->", args.image)

# Initializing network
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess=tf.Session(config=config)

net_input = tf.placeholder(tf.float32,shape=[None,None,None,3])
net_output = tf.placeholder(tf.float32,shape=[None,None,None,num_classes]) 

network, _ = model_builder.build_model(args.model, net_input=net_input,
                                        num_classes=num_classes,
                                        crop_width=args.crop_width,
                                        crop_height=args.crop_height,
                                        is_training=False)

sess.run(tf.global_variables_initializer())

print('Loading model checkpoint weights')
saver=tf.train.Saver(max_to_keep=1000)
saver.restore(sess, args.checkpoint_path)

def predict() :
    print("Testing image " + args.image)

    loaded_image = utils.load_image(args.image)
    resized_image =cv2.resize(loaded_image, (args.crop_width, args.crop_height))
    input_image = np.expand_dims(np.float32(resized_image[:args.crop_height, :args.crop_width]),axis=0)/255.0

    st = time.time()
    output_image = sess.run(network,feed_dict={net_input:input_image})

    run_time = time.time()-st

    output_image = np.array(output_image[0,:,:,:])
    output_image = helpers.reverse_one_hot(output_image)

    out_vis_image = helpers.colour_code_segmentation(output_image, label_values)
    file_name = utils.filepath_to_name(args.image)
    img = cv2.cvtColor(np.uint8(out_vis_image), cv2.COLOR_RGB2BGR)
    cv2.imwrite("output/%s_pred.png"%(file_name), img)

    print("")
    print("Finished!")
    print("Wrote image " + "%s_pred.png"%(file_name))
    return img

if args.inputVideo == 'no' :
    cap = cv2.VideoCapture(0)
else :
    cap = cv2.VideoCapture( args.inputVideo )

cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

stopIndex = 0
videoIndex = 0
videoIndexLimit = 1
if args.inputVideo != 'no' :
    videoIndexLimit = 30
while True:
    ret, frame = cap.read()             # 讀取影片的每一幀
    if not ret: 
        print("Cannot receive frame")   # 如果讀取錯誤，印出訊息
        break
    videoIndex = videoIndex + 1
    if videoIndex == videoIndexLimit :
        frame =cv2.resize( frame, ( 640, 480 ) )
        cv2.imwrite('output/output.jpg', frame )
        predictedImg = predict()
        info, handImg = app.main()
        cv2.imwrite('output/output_hand.jpg', handImg )
        if info == 'Stop':
            stopIndex = stopIndex + 1
            if stopIndex == 1 :
                playsound( './stop.mp3' )
                print( 'Stop!!' )
                stopIndex = 0
        markedImg = marking.drawAndSave( predictedImg, info )
        result = np.concatenate( ( handImg, markedImg ), axis=1 ) 
        cv2.imshow('GestureAndMark', result)     # 如果讀取成功，顯示該幀的畫面
        videoIndex = 0
    #time.sleep(2)

cap.release()                           # 所有作業都完成後，釋放資源
cv2.destroyAllWindows()                 # 結束所有視窗


'''
sendFlag = 0
while True:
    frame = ImageGrab.grab( (150, 120, 800, 600) )
    #frame.show()

    frame.save( 'output/output.jpg' )
    dImg = predict()
    
    frame = np.array( frame )   
    frame = frame[:, :, ::-1].copy()
    sendFlag += 1
    
    if sendFlag == 3 or sendFlag == 7 :
        try :
            client.sendImg( 'output/output.jpg' )
            client.sendImg( 'output/output_pred.png' )
            sendFlag %= 7
        except :
            print( 'Sending img error' )
    
    
    frame = cv2.resize(frame, (640,480), interpolation=cv2.INTER_AREA)
    result = np.concatenate((frame, dImg), axis=1)
    cv2.namedWindow('RealTime', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('RealTime', 480, 360 )
    cv2.imshow('RealTime', result)     # 如果讀取成功，顯示該幀的畫面

    cv2.waitKey(1)
cv2.destroyAllWindows()                 # 結束所有視窗
'''

'''
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

sendFlag = 0
while True:
    ret, frame = cap.read()             # 讀取影片的每一幀
    if not ret: 
        print("Cannot receive frame")   # 如果讀取錯誤，印出訊息
        break

    cv2.imwrite('output/output.jpg', frame )
    #info = app.main()
    #print( rt.Recent_hand_info() )
    dImg = predict()
    sendFlag += 1
    if sendFlag == 3 or sendFlag == 7 :
        try :
            client.sendImg( 'output/output.jpg' )
            client.sendImg( 'output/output_pred.png' )
            sendFlag %= 7
        except :
            print( 'Sending img error' )

    #marking.drawAndSave( "%s_pred.png"%(args.image.split('.')[0]), info )
    #dImg = cv2.imread( "%s_pred_marked.png"%(args.image.split('.')[0]) )
    #dImg = cv2.imread( "%s_pred.png"%(args.image.split('.')[0]) )
    result = np.concatenate((frame, dImg), axis=1)
    cv2.imshow('RealTime', result)     # 如果讀取成功，顯示該幀的畫面

    cv2.waitKey(1)
cap.release()                           # 所有作業都完成後，釋放資源
cv2.destroyAllWindows()                 # 結束所有視窗
'''
