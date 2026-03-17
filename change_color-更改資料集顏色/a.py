from PIL import Image
import numpy as np
import sys
import os

def strToTuple( s:str ):
    return tuple( map( int , s.split(',') ) )


def replaceColor( img, dict ):
    arr = np.asarray( img )
    res = arr.copy()
    for i in range( res.shape[0] ):
        for j in range( res.shape[1] ):
            rgb = tuple( res[i][j] )
            if rgb in dict:
                res[i][j] = np.array(dict[ rgb ])
    
    return res

def main():

    settingFile = 'setting.txt'
    colorDict = {}
    
    with open( settingFile ) as sf:
        for line in sf:
            temp = line.split()
            colorDict[strToTuple( temp[0] ) ] = strToTuple( temp[1] )
            
    print( colorDict )
    
    if len( sys.argv ) == 2:
        dir = sys.argv[1]
        print(sys.argv)
        if dir[-1] != '/': dir += '/'
        fileList = [ f for f in os.listdir( dir ) ]
        print( fileList )
        for file in fileList:
            if file.endswith( '.png' ) or file.endswith( '.jpg' ):
                print( 'Processing ' + file + '...' )
                img = Image.open( dir + file ).convert( 'RGB')
                resArr = replaceColor( img, colorDict )
                resImg = Image.fromarray( resArr )
                try:
                    os.mkdir( dir + 'output/' )
                except:
                    pass
                resImg.save( dir + 'output/' + file )

# print( sys.argv )
main()
