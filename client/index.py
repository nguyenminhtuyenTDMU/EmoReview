import time
from flask import Flask, render_template, request, jsonify
import re
from getNewReview import scrape_amazon_reviews
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd
from tqdm import tqdm
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

app = Flask(__name__)

def is_valid_amazon_url(url):
    if not url.startswith("https://www.amazon.com"):
        return False
    return True

def get_product_id(url):
    # Trích xuất product_id từ URL
    match = re.search(r'/dp/(\w+)', url)
    if match:
        return match.group(1)
    return None

def preprocess_text(text):
    # Loại bỏ dấu câu và emoji
    text = re.sub(r'[^\w\s,]', '', text)  
    # Chuyển văn bản thành chữ thường
    text = text.lower()
    return text

# Hàm tính toán điểm số cảm xúc
def analyze_sentiment(text):
    # Tiền xử lý văn bản
    text = preprocess_text(text)
    # Tính toán điểm số cảm xúc
    score = sia.polarity_scores(text)["compound"]
    if score > 0.05:
        return "positive"
    elif score < -0.05:
        return "negative"
    else:
        return "neutral"

def handle_analyze_sentiment():
    # Tải dữ liệu đánh giá sản phẩm từ file CSV
    data = pd.read_csv('amazon_reviews.csv')
    reviews = data['Text'].dropna()

    # Áp dụng phân tích cảm xúc cho từng đánh giá
    reviews_sentiment = pd.DataFrame(reviews)
    reviews_sentiment["sentiment"] = reviews.apply(analyze_sentiment)

    # Vẽ biểu đồ tròn thể hiện tỷ lệ 3 nhóm cảm xúc
    sentiment_counts = reviews_sentiment["sentiment"].value_counts()

    return {
        "positive":  int(sentiment_counts.get("positive", 0)),
        "neutral": int(sentiment_counts.get("neutral", 0)),
        "negative": int(sentiment_counts.get("negative", 0))
    }


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get("url", "")
    if not url:
        return jsonify({"error": "URL không được để trống."}), 400
    if not is_valid_amazon_url(url):
        return jsonify({"error": "URL không hợp lệ. Vui lòng nhập một URL sản phẩm Amazon hợp lệ."}), 400
    id = get_product_id(url)
    url_review = f"https://www.amazon.com/product-reviews/{id}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"
    # Gọi hàm scrape_amazon_reviews để lấy dữ liệu đánh giá từ Amazon
    scrape_amazon_reviews(url_review)
    time.sleep(5)
    result = handle_analyze_sentiment()
    print(result)
    return jsonify({
        "positive": result["positive"],
        "neutral": result["neutral"],
        "negative": result["negative"],
    })

if __name__ == '__main__':
    app.run(debug=True)