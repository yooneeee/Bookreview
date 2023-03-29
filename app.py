from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://sparta:test@cluster0.ww2tacc.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

import requests
from bs4 import BeautifulSoup

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def join_page():
    return render_template('register.html')

@app.route('/rpage')
def review_page():
    return render_template('review.html')

@app.route('/detail')
def detail_page():
    return render_template('detail.html')

@app.route("/book", methods=["POST"])
def book_post():
    url_receive = request.form['url_give']
    comment_receive = request.form['comment_give']
    star_receive = request.form['star_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    title = soup.select_one('#container > div > div > div > div > div > div > h2').text
    writer = soup.select_one('#container > div > div > div > div > div > div > ul > li:nth-child(1) > div.bookTitle_info_content__iHfCC > span').text
    publisher = soup.select_one('#container > div > div > div > div > div > div > ul > li:nth-child(2) > div.bookTitle_info_content__iHfCC > span').text
    date = soup.select_one('#container > div > div > div > div > div > div > ul > li:nth-child(3) > div.bookTitle_info_content__iHfCC > span').text
    desc = soup.select_one('#container > div> div > div > div > div.bookIntro_book_intro__BzWNC > div').text
    image = soup.select_one('meta[property="og:image"]')['content']


    doc = {
        'title':title,
        'writer':writer,
        'publisher':publisher,
        'date':date,
        'desc':desc,
        'image':image,
        'comment':comment_receive,
        'star':star_receive
    }
    
    db.books.insert_one(doc)

    return jsonify({'msg':'저장완료!'})

@app.route("/book", methods=["GET"])
def book_get():
    all_books = list(db.books.find({},{'_id':False}))
    return jsonify({'result':all_books})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)