import os

FIELD_SEPARATOR = '~'   # 與 Android 端 MapFragmentView.java 組字串時一致

def last_line( path, blockSize = 1024 ) :
    """只讀檔尾最後一行（routePlan.txt 會持續 append，每幀整檔 readlines 會愈來愈慢）。

    檔案不存在、空檔、或全部是空白行時回傳 None；
    最後一行沒有結尾換行時也能完整取回（不會像 [:-1] 那樣把 END 截成 EN）。
    """
    try :
        with open( path, 'rb' ) as f :
            f.seek( 0, os.SEEK_END )
            fileSize = f.tell()
            offset = 0
            while offset < fileSize :
                offset = min( offset + blockSize, fileSize )
                f.seek( fileSize - offset )
                chunk = f.read( offset ).rstrip( b'\r\n' )   # 容忍檔尾有無換行兩種情況
                if not chunk : return None
                pos = chunk.rfind( b'\n' )
                if pos >= 0 : return chunk[pos + 1:].decode( 'utf-8', 'replace' ).strip()
                if offset >= fileSize : return chunk.decode( 'utf-8', 'replace' ).strip()
            return None                                     # 空檔
    except FileNotFoundError :
        return None
    except OSError as error :
        print( "Read %s failed : %s\n"%( path, error ) )
        return None

def Recent_info() :
    """回傳最新一筆路線資訊，尚未收到／格式不符時回傳 None（由呼叫端決定畫面怎麼呈現）。"""
    line = last_line( 'output/routePlan.txt' )
    if line is None :
        print( "routePlan.txt is not ready\n" )
        return None
    info_list = [x for x in line.split( FIELD_SEPARATOR )]
    if len( info_list ) < 5 :
        print( "routePlan.txt has a malformed line : %s\n"%line )
        return None
    try :
        return int(info_list[0]), info_list[1], int(info_list[2]), int(info_list[3]), info_list[4]
                #distance       #Road name      #turn angel         #Orientation   #turn to
    except ValueError :
        print( "routePlan.txt has a malformed line : %s\n"%line )
        return None

def Recent_hand_info() :
    line = last_line( 'handRecognition.txt' )
    if line is None :
        print( "HandRecogintion.txt is null\n" )
        return None
    return line
