import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from nltk.sentiment import SentimentIntensityAnalyzer
from tqdm import tqdm
from sklearn.decomposition import PCA
import nltk

nltk.download('vader_lexicon')

# Tải dữ liệu đánh giá sản phẩm từ file CSV
data = pd.read_csv('amazon_reviews.csv')  # Đổi tên file nếu cần

# Giả sử dữ liệu có cột 'review_text' chứa đánh giá
reviews = data['review_text'].dropna()

# Khởi tạo công cụ phân tích cảm xúc từ NLTK
sia = SentimentIntensityAnalyzer()

# Hàm tính toán điểm số cảm xúc
def analyze_sentiment(text):
    score = sia.polarity_scores(text)["compound"]
    if score > 0.05:
        return "Tích cực"
    elif score < -0.05:
        return "Tiêu cực"
    else:
        return "Trung tính"

# Áp dụng phân tích cảm xúc cho từng đánh giá
tqdm.pandas(desc="Đang phân tích cảm xúc...")
reviews_sentiment = pd.DataFrame(reviews)
reviews_sentiment["sentiment"] = reviews.apply(analyze_sentiment)

# 🎯 **Vẽ biểu đồ tròn thể hiện tỷ lệ 3 nhóm cảm xúc**
sentiment_counts = reviews_sentiment["sentiment"].value_counts()

plt.figure(figsize=(8, 6))
plt.pie(
    sentiment_counts, 
    labels=sentiment_counts.index, 
    autopct='%1.1f%%', 
    colors=['lightblue', 'lightgreen', 'lightcoral'], 
    startangle=140
)
plt.title("Tỷ lệ cảm xúc trong các đánh giá")
plt.show()
