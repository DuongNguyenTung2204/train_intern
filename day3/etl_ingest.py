import argparse
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from sqlalchemy import text
from database import engine, create_table_if_not_exists
from dotenv import load_dotenv

load_dotenv()


def crawl_cafef(max_articles=20):
    """=== SCRIPT CRAWL CỦA BẠN ĐÃ ĐƯỢC TÍCH HỢP ==="""
    print("🌐 Đang khởi tạo Selenium crawl cafef.vn...")

    # === PHẦN THIẾT LẬP CHROME OPTIONS (giữ nguyên của bạn) ===
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    url = "https://cafef.vn/tai-chinh-quoc-te.chn"
    print(f"Đang truy cập: {url}")
    driver.get(url)

    # Chờ trang load (tăng thời gian lên 15s vì trang nặng)
    print("Đang đợi trang load hoàn tất...")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "h3 a[href$='.chn']"))
    )

    # === SELECTOR MỚI (đã update cho năm 2026) ===
    articles = driver.find_elements(By.CSS_SELECTOR, "h3 a[href$='.chn']")

    # Thử selector thay thế nếu không tìm thấy (giữ nguyên logic của bạn)
    if not articles:
        print("Không tìm thấy với selector mới, thử XPath...")
        articles = driver.find_elements(By.XPATH, "//h3/a[contains(@href, '.chn')]")

    print(f"Tìm thấy {len(articles)} bài báo.")

    titles, links = [], []
    for i, article in enumerate(articles[:max_articles]):
        try:
            title = article.text.strip()
            link = article.get_attribute("href")

            if link and not link.startswith("http"):
                link = "https://cafef.vn" + link

            if title and link:
                titles.append(title)
                links.append(link)
                print(f"{i+1}. Title: {title[:50]}... | Link: {link}")

            time.sleep(0.5)  # Delay nhỏ tránh detection
        except Exception as e:
            print(f"Lỗi extract bài {i+1}: {e}")
            continue

    driver.quit()

    # === LƯU VÀO EXCEL ===
    if titles and links:
        df = pd.DataFrame({"Title": titles, "Link": links})
        output_file = "cafef_articles.xlsx"
        df.to_excel(output_file, index=False, engine="openpyxl")
        print(f"\n✅ Đã lưu {len(df)} bài vào file: {output_file}")
        print(df.head())
    else:
        print("❌ Không tìm thấy bài báo nào!")

    # === LƯU VÀO DATABASE ===
    if titles and links:
        with engine.connect() as conn:
            for title, link in zip(titles, links):
                conn.execute(text("""
                    INSERT INTO articles (title, link, crawled_at)
                    VALUES (:title, :link, :crawled_at)
                    ON CONFLICT (link) DO NOTHING
                """), {
                    "title": title,
                    "link": link,
                    "crawled_at": datetime.now()
                })
            conn.commit()
        print(f"✅ Đã lưu {len(titles)} bài viết vào Database bảng 'articles'!")
    else:
        print("Không có dữ liệu để lưu vào DB.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl cafef.vn → Excel + Database")
    parser.add_argument("--max", type=int, default=20, help="Số bài tối đa (mặc định 20)")
    args = parser.parse_args()

    create_table_if_not_exists()
    crawl_cafef(max_articles=args.max)