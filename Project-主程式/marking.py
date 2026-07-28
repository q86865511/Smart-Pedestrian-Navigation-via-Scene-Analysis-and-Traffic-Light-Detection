from PIL import Image, ImageDraw, ImageFont
import sys
from collections import deque
import cv2
import numpy as np

targetColors = [(128,64,128)]
thresholdPixel = 300 
dy = [0,1,0,-1]
dx = [1,0,-1,0]

circleRadius = 5
centerColors = [(0,255,0)]
smallCircleRadius = 0

def analyzeRegions(img):
    """一次掃描算出所有目標色連通區域（重心、面積），並找出畫面底部中央所屬區域。

    回傳 ( regions, floorRegion )：regions 為 [(色號, 重心, 面積), ...]，
    floorRegion 為底部中央那塊的 (重心, 面積)，不在目標色上時為 None。
    原本 judgeFloor / drawCenter / drawArrow 各跑一次 BFS，共用本結果只需跑一次。
    """
    pix = img.load()
    w,h = img.size
    vis = [[False for i in range(h)] for j in range(w) ]
    fx, fy = w//2, h-1
    regions = []
    floorRegion = None
    for i in range(w):
        for j in range(h):
            if vis[i][j]: continue;
            for t in range( len( targetColors ) ):
                if pix[i,j] != targetColors[t]: continue
                floorWasVisited = vis[fx][fy]
                pos, area = calcCenterPos( img, (i,j), vis )
                regions.append( (t, pos, area) )
                if not floorWasVisited and vis[fx][fy]: floorRegion = ( pos, area )
    return regions, floorRegion

def drawCenter(img, regions = None):
    if regions == None: regions, _ = analyzeRegions( img )
    for t, pos, area in regions:
        if area >= thresholdPixel:
            drawCircle( img, pos, circleRadius, centerColors[t] )

def drawCircle(img, pos, radius, color ):
    w,h = img.size
    for i in range( -radius, radius+1 ) :
        for j in range( -radius, radius+1 ) :
            if i*i + j*j <= radius**2:
                x = pos[0]+i
                y = pos[1]+j;
                if x >= 0 and y >= 0 and x < w and y < h: img.putpixel( (x,y), color )
    

def drawEdge(img):
    pix = img.load()
    w,h = img.size
    for t in range( len( targetColors ) ):
        for i in range(w):
            j = 0
            while j < h:
                while j < h and pix[i,j] != targetColors[t]: j += 1
                if j == h: break
                temp = (i,j)
                while j < h and pix[i,j] == targetColors[t]: j += 1
                drawCircle( img, *temp, smallCircleRadius, centerColors[t] )
                if j < h: drawCircle( img,i,j,smallCircleRadius, centerColors[t] )

def judgeFloor(img, floorRegion = None):
    if floorRegion == None:
        pix = img.load()
        w,h = img.size
        if pix[w//2, h-1] != targetColors[0]: return False
        floorRegion = calcCenterPos( img, (w//2, h-1) )
    _, area = floorRegion
    return area >= thresholdPixel

def calcCenterPos(img, pos, vis = None):
    pix = img.load()
    w,h = img.size
    clr = pix[pos]
    q = deque()                 # 單執行緒 BFS 不需要 queue.Queue 的鎖
    q.append( pos )
    if vis == None: vis = [[False for i in range(h)] for j in range(w) ]
    vis[pos[0]][pos[1]] = True
    sumw = 0
    sumh = 0
    sump = 0
    while q:
        x,y = q.popleft()
        sumw += x
        sumh += y
        sump += 1
        for k in range(4):
            nx = x+dx[k]
            ny = y+dy[k]
            if nx >= 0 and ny >= 0 and nx < w and ny < h and not vis[nx][ny] and pix[nx,ny] == clr :
                q.append( (nx,ny ) )
                vis[nx][ny] = True
    return ( sumw // sump, sumh // sump ), sump

arrowImg = Image.open("arrow.png").convert('RGBA').resize( (50,50) )
def drawArrow(img, angle, floorRegion = None):
    pix = img.load()
    # print(angle)
    rotatedArrowImg = arrowImg.rotate( angle )
    w,h = img.size
    if floorRegion != None: pos, _ = floorRegion
    elif pix[w//2, h-1] == targetColors[0]: pos, _ = calcCenterPos(img, (w//2, h-1) )
    else: pos = ( w//2, h-1 )
    centerPos = ( pos[0] - arrowImg.size[0] // 2, pos[1] - arrowImg.size[1] // 2 )
    offsetPos = ( centerPos[0], centerPos[1] - 25 )
    img.paste(rotatedArrowImg,offsetPos,rotatedArrowImg.convert('RGBA'))


fontSize = 24
markFont = None
def getFont():
    global markFont       # 字型只從磁碟載入一次，不必每幀 truetype
    if markFont == None: markFont = ImageFont.truetype( 'TaipeiSansTCBeta-Regular.ttf', fontSize )
    return markFont

def drawInfo( img, dist, name, turn, ori, is_walkable, info ):

    draw = ImageDraw.Draw( img )
    font = getFont()
    if name == 'null' : name = 'The Road has no name'
    if dist == None :   # 手機端路線資訊尚未送達或格式不符
        draw.text( (5,5), "Waiting for route information", font = font, align = 'left' )

    elif dist <= 15 and turn != 'END' :
        draw.text( (5,5), "This Road is head to %d°"%ori, font = font, align = 'left' )
        draw.text( (5,30), "Distance %dm"%dist, font = font, align = 'left' )
        draw.text( (5,55), "Next Road's Name : %s"%name, font = font, align = 'left' )
        draw.text( (5,80), "Next Turn is %s"%turn, font = font, align = 'left' )

    elif turn == 'END' :
        draw.text( (5,5), "This Road is head to %d°"%ori, font = font, align = 'left' )
        draw.text( (5,30), "Distance %dm"%dist, font = font, align = 'left' )
        draw.text( (5,55), "Next Road's Name : No next road", font = font, align = 'left' )
        draw.text( (5,80), "Your about to the Destination", font = font, align = 'left' )

    else :
        draw.text( (5,5), "This Road is head to %d°"%ori, font = font, align = 'left' )
        draw.text( (5,30), "Distance %dm"%dist, font = font, align = 'left' )
        draw.text( (5,55), "Next Road's Name : %s"%name, font = font, align = 'left' )
        draw.text( (5,80), "Next Turn is %s"%turn, font = font, align = 'left' )
    
    if is_walkable :
        draw.text( (5,105), "You are on road area", font = font, align = 'left' )
    else :
        draw.text( (5,105), "You are not on road area", font = font, align = 'left' )

    draw.text( (5,130), "Gesture : %s"%info, font = font, align = 'left' )
#    draw.text( (5,130), "Traffic light : %s"%traffic_light, font = font, align = 'left' )

import read_txt as rt

def drawAndSave(img, info):
    img = img[:,:,::-1]
    img = Image.fromarray(img)
    regions, floorRegion = analyzeRegions( img )    # 三處共用同一次連通區域分析
    is_walkable = judgeFloor( img, floorRegion )
    drawCenter( img, regions )

    route = rt.Recent_info() #read navigation informations
    if route == None :
        dist, name, angel, ori, turn = None, 'null', 0, 0, 'UNKNOWN'
    else :
        dist, name, angel, ori, turn = route

    if dist != None and dist <= 15 and turn != 'END' :
        drawArrow(img, angel, floorRegion)
    else :
        drawArrow(img, 0, floorRegion)

    drawInfo( img, dist, name, turn, ori, is_walkable, info )
    img.save("output/output_pred_marked.png")
    img = np.array(img)
    img = img[:, :, ::-1].copy()
    return img
                 
        
def test():
    img = cv2.imread( sys.argv[1] )     # drawAndSave 收的是 numpy array，不是路徑
    if img is None :
        print( "Cannot read image %s"%sys.argv[1] )
        return
    drawAndSave( img, "" )

if __name__ == '__main__':
    test()
