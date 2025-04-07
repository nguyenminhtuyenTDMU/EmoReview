from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pickle
import csv
from dotenv import load_dotenv
import os

def scrape_amazon_reviews(product_url, output_csv="amazon_reviews.csv"):
    load_dotenv()
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")
    
    # Cấu hình Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)

    # Kiểm tra và tải lại cookies nếu có
    try:
        driver.get("https://www.amazon.com/")
        with open("amazon_cookies.pkl", "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(2)
    except:
        print("Không tìm thấy cookie, tiến hành đăng nhập...")

    # Mở trang đăng nhập nếu cần
    if "signin" in driver.current_url:
        driver.get("https://www.amazon.com/ap/signin")
        time.sleep(2)

        email_input = driver.find_element(By.ID, "ap_email")
        email_input.send_keys(EMAIL)
        email_input.send_keys(Keys.RETURN)
        time.sleep(2)

        password_input = driver.find_element(By.ID, "ap_password")
        password_input.send_keys(PASSWORD)
        password_input.send_keys(Keys.RETURN)
        time.sleep(3)

        input("Hãy nhập CAPTCHA trên trình duyệt, sau đó nhấn Enter để tiếp tục...")
        time.sleep(5)

        pickle.dump(driver.get_cookies(), open("amazon_cookies.pkl", "wb"))

    # Mở trang đánh giá sản phẩm
    driver.get(product_url)
    time.sleep(3)

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["review_text"])

        while True:
            time.sleep(3)
            try:
                review_list = driver.find_element(By.ID, "cm_cr-review_list")
                reviews = review_list.find_elements(By.CLASS_NAME, "review")
            except:
                print("Không tìm thấy danh sách đánh giá.")
                break

            for review in reviews:
                try:
                    # title = review.find_element(By.CSS_SELECTOR, "a.review-title").text
                    content = review.find_element(By.CSS_SELECTOR, "span.review-text-content").text
                    writer.writerow([content])
                except Exception as e:
                    print("Lỗi lấy dữ liệu review:", e)
                    continue

            # Kiểm tra xem có nút "Next" không, nếu không thì thoát
            try:
                next_button = driver.find_element(By.CLASS_NAME, "a-last")
                if "a-disabled" in next_button.get_attribute("class"):
                    break
                next_button.click()
                time.sleep(3)
            except:
                break

    print(f"Đã lưu tất cả đánh giá vào {output_csv}")
    driver.quit()
if __name__ == "__main__":
    product_url = "https://www.amazon.com/product-reviews/B009FUFD1C/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"
    scrape_amazon_reviews(product_url)
    # df_reviews = scrape_amazon_reviews(product_url)   