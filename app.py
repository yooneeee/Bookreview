from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
import certifi 
ca = certifi.where() 
client = MongoClient('mongodb+srv://sparta:test@cluster0.vozxpm9.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

import requests
from bs4 import BeautifulSoup

#메인 페이지
@app.route('/')
def home():
    return render_template('home.html')

#리뷰 등록 페이지로 이동
@app.route('/rpage')
def reviewPost_Page():
    return render_template('review.html')
@app.route('/detail')
def detail_Page():
    return render_template('detail.html')
#리뷰 등록
@app.route("/book", methods=["POST"])
def review_post():
    url_receive = request.form['url_give']
    comment_receive = request.form['comment_give']
    star_receive = request.form['star_give']
    # ***아이디 또는 닉네임 값 받기***
    #nickname_receive = request.form['nickname_give']

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
        'star':star_receive
        #'nickname':nickname_receive
    }
    db.breviews.insert_one(doc)
    return jsonify({'msg':'등록 완료!'})
@app.route("/bookreview", methods=["GET"])
def book_get():
    all_books = list(db.breviews.find({},{'_id':False}))
    return jsonify({'result':all_books})

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
@app.route("/comment", methods=["GET"])
def comment_get():
    all_comments = list(db.comments.find({},{'_id':False}))
    return jsonify({'result':all_comments})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)

# mongodbautoincrement














