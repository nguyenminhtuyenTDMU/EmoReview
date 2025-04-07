import time
from flask import Flask, render_template, request, jsonify
import re
import random
from getNewReview import scrape_amazon_reviews
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd
from tqdm import tqdm
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

app = Flask(__name__)

def is_valid_amazon_url(url):
    # pattern = r"^https?://(www\.)?amazon\.[a-z]{2,3}/[\w-]+/dp/\w+"
    pattern = r"^https?://(www\.)?amazon\.[a-z]{2,3}/(product-reviews|[\w-]+/dp)/\w+"
    return re.match(pattern, url)

# Hàm tính toán điểm số cảm xúc
def analyze1(text):
    score = sia.polarity_scores(text)["compound"]
    if score > 0.05:
        return "positive"
    elif score < -0.05:
        return "negative"
    else:
        return "neutral"

def analyze_sentiment():
    # Tải dữ liệu đánh giá sản phẩm từ file CSV
    data = pd.read_csv('amazon_reviews.csv')
    reviews = data['Text'].dropna()
    # Áp dụng phân tích cảm xúc cho từng đánh giá
    tqdm.pandas(desc="Đang phân tích cảm xúc...")
    reviews_sentiment = pd.DataFrame(reviews)
    reviews_sentiment["sentiment"] = reviews.apply(analyze1)

    # 🎯 **Vẽ biểu đồ tròn thể hiện tỷ lệ 3 nhóm cảm xúc**
    sentiment_counts = reviews_sentiment["sentiment"].value_counts()

    return {
        "positive":  int(sentiment_counts.get("positive", 0)),  # Chuyển thành int
        "neutral": int(sentiment_counts.get("neutral", 0)),# Chuyển thành int
        "negative": int(sentiment_counts.get("negative", 0))   # Nếu không có giá trị "negative" thì mặc định là 0
    }


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get("url", "")
    scrape_amazon_reviews(url)
    if not is_valid_amazon_url(url):
        return jsonify({"error": "URL không hợp lệ. Vui lòng nhập một URL sản phẩm Amazon hợp lệ."}), 400
    time.sleep(5)
    result = analyze_sentiment()
    print(result)
    return jsonify({
        "positive": result["positive"],
        "neutral": result["neutral"],
        "negative": result["negative"],
    })

if __name__ == '__main__':
    app.run(debug=True)