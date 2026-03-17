def Recent_info() :
    with open('output/routePlan.txt', 'r',encoding="utf-8") as f:
        last_line = f.readlines()[-1][:-1]
        info_list = [x for x in last_line.split('~')]
        #f.truncate(0)
        f.close()
        return int(info_list[0]), info_list[1], int(info_list[2]), int(info_list[3]), info_list[4]
                #distance       #Road name      #turn angel         #Orientation   #turn to

def Recent_hand_info() :
    try :
        with open('handRecognition.txt', 'r',encoding="utf-8") as f:
            last_line = f.readlines()[-1][:-1]
            #f.truncate(0)
            f.close()
            return last_line
    except:
        print( "HandRecogintion.txt is null\n" )
