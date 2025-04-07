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
    # options.add_argument("--headless=new")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
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
        driver.get("https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3F%26tag%3Dgoogleglobalp-20%26ref%3Dnav_signin%26adgrpid%3D159651196451%26hvpone%3D%26hvptwo%3D%26hvadid%3D675114638556%26hvpos%3D%26hvnetw%3Dg%26hvrand%3D11681921992439922994%26hvqmt%3De%26hvdev%3Dc%26hvdvcmdl%3D%26hvlocint%3D%26hvlocphy%3D9207678%26hvtargid%3Dkwd-10573980%26hydadcr%3D2246_13649807&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0")

    # Mở trang đăng nhập nếu cần
    if "signin" in driver.current_url:
        print("Đang đăng nhập vào tài khoản Amazon...")
        driver.get("https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3F%26tag%3Dgoogleglobalp-20%26ref%3Dnav_signin%26adgrpid%3D159651196451%26hvpone%3D%26hvptwo%3D%26hvadid%3D675114638556%26hvpos%3D%26hvnetw%3Dg%26hvrand%3D11681921992439922994%26hvqmt%3De%26hvdev%3Dc%26hvdvcmdl%3D%26hvlocint%3D%26hvlocphy%3D9207678%26hvtargid%3Dkwd-10573980%26hydadcr%3D2246_13649807&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0")
        time.sleep(2)

        email_input = driver.find_element(By.ID, "ap_email")
        email_input.send_keys(EMAIL)
        email_input.send_keys(Keys.RETURN)
        time.sleep(2)

        password_input = driver.find_element(By.ID, "ap_password")
        password_input.send_keys(PASSWORD)
        password_input.send_keys(Keys.RETURN)
        time.sleep(3)

        pickle.dump(driver.get_cookies(), open("amazon_cookies.pkl", "wb"))

    # Mở trang đánh giá sản phẩm
    print("Đang mở trang sản phẩm...")
    driver.get(product_url)
    time.sleep(1)

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ProfileName", "Text"])

        while True:
            time.sleep(1)
            try:
                review_list = driver.find_element(By.ID, "cm_cr-review_list")
                reviews = review_list.find_elements(By.CLASS_NAME, "review")
            except:
                print("Không tìm thấy danh sách đánh giá.")
                break

            for review in reviews:
                try:
                    author = review.find_element(By.CLASS_NAME, "a-profile-name").text
                    content = review.find_element(By.CSS_SELECTOR, "span.review-text-content").text
                    writer.writerow([author, content])
                except Exception as e:
                    print("Lỗi lấy dữ liệu review:", e)
                    continue

            # Kiểm tra xem có nút "Next" không, nếu không thì thoát
            try:
                next_button = driver.find_element(By.CLASS_NAME, "a-last")
                if "a-disabled" in next_button.get_attribute("class"):
                    break
                next_button.click()
                time.sleep(1)
            except:
                break

    print(f"Đã lưu tất cả đánh giá vào {output_csv}")
    driver.quit()
