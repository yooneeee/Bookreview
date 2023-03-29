from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
import certifi 
ca = certifi.where() 
client = MongoClient('mongodb+srv://sparta:test@cluster0.dg8babf.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca) 
db = client.dbsparta

import requests
from bs4 import BeautifulSoup

import jwt
# 토근 만료시간 부여를 위한 datetime 사용
import datetime
# 회원가입시 비밀번호 데이터 암호화
import hashlib
from flask_cors import CORS
SECRET_KEY = 'BOOKREVIEW'

#고유 ID 값
import uuid

#메인 홈으로
CORS(app)
@app.route("/")
def main():
    # id_receive = request.form['id_give']
    # loginId = db.users.find_one(id_receive)
    isLoggedIn = False
    return render_template("home.html", isLoggedIn=isLoggedIn)

#리뷰 등록 페이지로 이동
@app.route('/rpage')
def reviewPost_Page():
    return render_template('review.html')

#리뷰 등록
@app.route("/rbook", methods=["POST"])
def posting():
    url_receive = request.form['url_give']
    comment_receive = request.form['comment_give']
    star_receive = request.form['star_give']
    uid = uuid.uuid4()

    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive,headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    ogtitle = soup.select_one('div.bookTitle_title_area__fspvB > h2.bookTitle_book_name__JuBQ2').text
    ogdesc = soup.select_one('div.bookIntro_introduce_area__NJbWv').text
    ogimage = soup.select_one('meta[property="og:image"]')['content']

    doc = {
        'title':ogtitle,
        'desc':ogdesc,
        'image':ogimage,
        'comment':comment_receive,
        'star':star_receive,
        'keyid': str(uid)
    }
    db.breviews.insert_one(doc)
    return jsonify({'msg':'등록 완료!'})

#상세 페이지로 이동
@app.route('/detail')
def detail_Page():
    return render_template('detail.html')

#도서 상세, 리뷰 불러오기
@app.route("/bookreview", methods=["GET"])
def book_get():
    all_books = list(db.breviews.find({},{'_id':False}))
    return jsonify({'result':all_books})

#댓글 등록
@app.route("/comment", methods=["POST"])
def comment_post():
    comment_receive = request.form['comment_give']
    # nickname_receive = request.form['nickname_give']
    
    doc={
        # 'nickname':nickname_receive
        'comment':comment_receive
        #책이름도 저장..
    }
    db.comments.insert_one(doc)
    return jsonify({'msg':'댓글 쓰기 완료!'})

#댓글 읽어오기
@app.route("/comment", methods=["GET"])
def comment_get():
    all_comments = list(db.comments.find({},{'_id':False}))
    return jsonify({'result':all_comments})


#로그인 페이지로 이동
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

#회원가입 페이지로 이동
@app.route('/register')
def register():
    return render_template('register.html')

# [회원가입 API]
CORS(app)
@app.route('/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    existing_user = db.users.find_one({'id': id_receive})
    if existing_user is not None:
        return jsonify({'result': 'fail', 'msg': '이미 가입된 아이디입니다.'})
    existing_user_nickname = db.users.find_one({'nick': nickname_receive})
    if existing_user_nickname is not None:
        return jsonify({'result': 'fail', 'msg': '이미 가입된 닉네임입니다.'})
       
    
     # 패스워드 암호화 / sha256 방법(=단방향 암호화. 풀어볼 수 없음)
    pw_hash = hashlib.sha256(pw_receive.encode('UTF-8')).hexdigest()

    db.users.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})
    
    
    return jsonify({'result': 'success'})
    
# [로그인 API]
# id, pw를 받아서 맞춰 본 뒤 토큰 발급
CORS(app)
@app.route('/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('UTF-8')).hexdigest()

    result = db.users.find_one({'id': id_receive, 'pw': pw_hash})
# --------------------------------------------------------------------- 작업중>
    if result is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # token 발급
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

        
CORS(app)        
@app.route('/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    try:
        # token을 시크릿키로 디코딩
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError:
        
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)