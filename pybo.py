
import math
from flask import Flask, render_template, request, redirect, url_for
import pymysql
import utils.utils as utils
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# 데이터 베이스 연동
db = pymysql.connect(host="localhost", 
                     user="root", password="passwd", 
                     db="test3",
                     charset="utf8")

cursor = db.cursor()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdf'

# @app.route('/', defaults={'page':1})
@app.route('/')
def list() :

    cursor.execute("SELECT b.boardId, b.title, u.ID, b.location, date_format(b.createAt, '%Y-%m-%d') FROM board as b LEFT OUTER JOIN user as u on u.userId = b.userId ORDER BY b.createAt DESC LIMIT 0, 3;")
    data_list = cursor.fetchall()

    return render_template("index.html", data_list = data_list)

@app.route('/list', defaults={'page':1})
@app.route('/list/<int:page>')

def paging(page) :
    print(page)

    perpage = 10
    startat=(page-1)*perpage
    cursor.execute("SELECT b.boardId, b.title, u.ID, b.location, date_format(b.createAt, '%Y-%m-%d') FROM Board as b LEFT OUTER JOIN User as u on u.userId = b.userId WHERE b.status = 'active' ORDER BY b.createAt DESC LIMIT "+str(startat)+", "+str(perpage)+";")
    data_list = cursor.fetchall()

    return render_template("list.html", data_list = data_list)

@app.route('/listview/<int:id>')    
def view2(id) :
    print("id = ", id)
    cursor.execute("SELECT b.boardId, b.title, u.ID, b.content, b.location, date_format(b.createAt, '%Y-%m-%d') FROM Board as b LEFT OUTER JOIN User as u on u.userId = b.userId WHERE boardId = {} ORDER BY b.createAt DESC;".format(id))
    data = cursor.fetchall()
    print(data)

    return render_template("view.html", data = data)


@app.route('/edit/')
def edit() :
    return render_template("edit.html")

@app.route('/view')
def view() :
    print(request.method)
    
    cursor.execute("SELECT b.boardId, b.title, u.ID, b.content, b.location, date_format(b.createAt, '%Y-%m-%d') FROM Board as b LEFT OUTER JOIN User as u on u.userId = b.userId WHERE boardId = (SELECT MAX(boardId) FROM Board) ORDER BY b.createAt DESC;",)
    data = cursor.fetchall()
    print(data)

    return render_template("view.html", data = data)

@app.route('/write/', methods=['GET', 'POST'])
def write() :
    print(request.method)
    if request.method == 'GET' :
        return render_template("write.html")
    elif request.method == 'POST' :
        
        title = request.form['title']
        user = request.form['username']
        location = request.form['userlocation']
        contents = request.form['body']
        
        cursor.execute("INSERT INTO Board (userId, title, content, location) VALUES ((SELECT userId FROM User WHERE ID = %s), %s, %s, %s);", (user, title, contents, location))
        cursor.connection.commit()

        return redirect(url_for('view'))

@app.route('/signup')
def signup() :
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def createUser():
    try:

        name = str(request.form.get('name'))
        ID = str(request.form.get('ID'))
        password = str(request.form.get('password'))
        phoneNumber = str(request.form.get('phoneNumber'))

        password_confirm = str(request.form.get('password_confirm'))
        print(name, ID, password, password_confirm, phoneNumber)
        
        if len(ID) < 4 or len(ID) > 16 :
            return '''
                <script> alert("회원 가입에 실패했습니다.\\n  - 아이디는 4~16자로 작성하세요.");
                location.href="/signup"
                </script>
                '''
        if not utils.onlyalphanum(ID) :
            return '''
                <script> alert("회원 가입에 실패했습니다.\\n - 아이디는 영문 대소문자와 숫자로 작성하세요");
                location.href="/signup"
                </script>
                '''
        if not phoneNumber.isdecimal() :
            return '''
                <script> alert("회원 가입에 실패했습니다.\\n -  전화번호는 숫자만 작성하세요. ");
                location.href="/signup"
                </script>
                '''
        if  not name.isalpha():
            return '''
                <script> alert("회원 가입에 실패했습니다.\\n  - 이름은 한글 또는 영어로만 작성하세요");
                location.href="/signup"
                </script>
                '''
        if  password != password_confirm:
            return '''
                <script> alert("회원 가입에 실패했습니다.\\n  - 비밀번호 확인 란에 동일한 비밀번호를 입력하세요.");
                location.href="/signup"
                </script>
                '''
            

        hashed_password = utils.hash_password(str(password))

        user_info = [ name , ID , hashed_password, phoneNumber ]
        
        # a = userdao.createUser(user_info)

        cursor.execute("INSERT INTO User(name, ID, password, phoneNumber) VALUES (%s, %s, %s, %s)", 
                      (user_info[0], user_info[1], user_info[2], user_info[3]))
        
        print("before commit")
        cursor.connection.commit()
        print("after commit")


        return '''
                <script> alert("환영합니다. 회원가입에 성공했습니다 :) ");
                location.href="/"
                </script>
                '''
    
    except Exception as e :
        return {'error': str(e)}

@app.route('/complete')
def display_user_login_form():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # 로그인 버튼 클릭
    if request.method == 'POST':
        id_receive = request.form.get('username')
        pw_receive = request.form.get('password')
        
        # 입력 x
        if len(id_receive) == 0 or len(pw_receive) == 0:
            return redirect(url_for('display_user_signup_form'))
        
        # 입력 o
        else:
            # 입력받은 id에 해당하는 row 가져옴
            cursor = db.cursor()
            sql = sql = "select * from user where ID=%s and status=%s"
            cursor.execute(sql, (id_receive, 'active')) #none / user정보 한줄
             
            # 입력받은 user가 db에 있으면 해당 row 한줄을 가져옴 
            row = cursor.fetchone()
        
            
            # id, pw 체크 (row[2] = ID정보, row[3] = password정보)
            if row and id_receive == row[2] and pw_receive == row[3]:
                
                # session id, userid 오브젝트 생성*저장
                session['logFlag'] = True
                session['id'] = id_receive
                session['userid'] = row[0]
                
                
                # 로그인 성공 메시지 출력 후 /sesesion 이동 
                return '''
                    <script> alert("안녕하세요, {}님 :)");
                    location.href="/session"
                    </script>
                '''.format(id_receive)      
                # return redirect(url_for('login'))
            
            else:
                return redirect(url_for('display_user_signup_form'))
    else:
        return 'wrong access'      
        
        
# 로그인 성공자만 이동
@app.route('/session')
def session_():
    if 'id' in session:
        return render_template('login.html', a = session['id'])
    
    return redirect(url_for('login'))

@app.route('/create_user')
def create_user():
    try:
        parser = reqparse.RequestParser()

        name = str(request.form.get('name'))
        ID = str(request.form.get('ID'))
        password = str(request.form.get('password'))
        phoneNumber = str(request.form.get('phoneNumber'))

        password_confirm = str(request.form.get('password_confirm'))
        
        # args = parser.parse_args()

        if len(ID) < 4 or len(ID) > 16 or not utils.onlyalpha(ID) or not phoneNumber.isdecimal() or not name.isalpha() or password != password_confirm:
           return redirect(url_for('signup_fail'))


        hashed_password = utils.hash_password(str(password))

        user_info = [ name , ID , hashed_password, phoneNumber ]
        
        a = userdao.create_user(user_info)

        return redirect(url_for('signup_complete'))
    
    except Exception as e :
        return {'error': str(e)}

@app.route('/delete_user')
def delete_user():
    try:
        parser = reqparse.RequestParser()

        name = str(request.form.get('name'))
        ID = str(request.form.get('ID'))
        password = str(request.form.get('password'))
        phoneNumber = str(request.form.get('phoneNumber'))

        password_confirm = str(request.form.get('password_confirm'))
        
        # args = parser.parse_args()

        if len(ID) < 4 or len(ID) > 16 or not utils.onlyalpha(ID) or not phoneNumber.isdecimal() or not name.isalpha() or password != password_confirm:
           return redirect(url_for('signup_fail'))


        hashed_password = utils.hash_password(str(password))

        user_info = [ name , ID , hashed_password, phoneNumber ]
        
        a = userdao.createUser(user_info)

        return redirect(url_for('signup_complete'))
    
    except Exception as e :
        return {'error': str(e)}

@app.route('/create_post')
def create_post():
    try:
        parser = reqparse.RequestParser()

        # boardId = str(request.form.get('name'))
        userId = str(request.form.get('ID'))
        title = str(request.form.get('title'))
        content = str(request.form.get('content'))
        location = str(request.form.get('location'))
        
        # args = parser.parse_args()
    

        # hashed_password = utils.hash_password(str(password))

        post_info = [ userId ,title ,content, location ]
        
        a = userdao.create_post(post_info)

        return redirect(url_for('signup_complete'))
    
    except Exception as e :
        return {'error': str(e)}
    
@app.route('/delete_post')
def delete_post():
    try:
        parser = reqparse.RequestParser()

        name = str(request.form.get('name'))
        ID = str(request.form.get('ID'))
        password = str(request.form.get('password'))
        phoneNumber = str(request.form.get('phoneNumber'))

        password_confirm = str(request.form.get('password_confirm'))
        
        # args = parser.parse_args()

        if len(ID) < 4 or len(ID) > 16 or not utils.onlyalpha(ID) or not phoneNumber.isdecimal() or not name.isalpha() or password != password_confirm:
           return redirect(url_for('signup_fail'))


        hashed_password = utils.hash_password(str(password))

        user_info = [ name , ID , hashed_password, phoneNumber ]
        
        a = userdao.create_user(user_info)

        return redirect(url_for('signup_complete'))
    
    except Exception as e :
        return {'error': str(e)}

def main() :
    app.run(debug=True, port=5000)

if __name__ == '__main__' :
    main()



