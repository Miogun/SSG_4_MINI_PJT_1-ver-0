import json
import pymysql

def getConnection():
    return pymysql.connect(host="localhost", 
                     user="root", 
                     passwd="passwd", 
                     db="test3", charset="utf8")


# datetime을 포함한 데이터를 json으로 바로 바꿀 수 있도록 추가한 함수
def user_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj
# execute(OMser)
# name을 parameter로 받아 user 테이블에 추가

def create_user(user_info):
    #user_info :  name, ID, password, phoneNumber, rent
    conn = getConnection()
    curs = conn.cursor()
    ok = curs.execute("INSERT INTO User(name, ID, password, phoneNumber) VALUES (%s, %s, %s, %s)", 
                      (user_info[0], user_info[1], user_info[2], user_info[3]))
    
    conn.commit()
    conn.close()

    return json.dumps({'rows': ok})

def delete_user(user_info):
    #user_info :  name, ID, password, phoneNumber, rent
    conn = getConnection()
    curs = conn.cursor()
    ok = curs.execute("UPDATE SET user(status) VALUES (%s) WHERE name = %s",user_info[4],user_info[0])
    
    conn.commit()
    conn.close()

    return json.dumps({'rows': ok})

def create_post(post_info):
    #user_info :  name, ID, password, phoneNumber, rent
    conn = getConnection()
    curs = conn.cursor()
    ok = curs.execute("INSERT INTO User(name, ID, password, phoneNumber) VALUES (%s, %s, %s, %s)", 
                      (post_info[0], post_info[1], post_info[2], post_info[3]))
    
    conn.commit()
    conn.close()

    return json.dumps({'rows': ok})

def delete_post(post_info):
    #user_info :  name, ID, password, phoneNumber, rent
    conn = getConnection()
    curs = conn.cursor()
    ok = curs.execute("DELETE FROM board WHERE name = %s",post_info[0])
    
    conn.commit()
    conn.close()

    return json.dumps({'rows': ok})