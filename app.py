from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time
import re
import os

# --- TELEGRAM DETAILS (ENV VARS USE KARO) ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "8653423304:AAFbr1w_6k-dCNqVJq2YpFp_tfflXQjlZuE")
CHAT_ID = os.getenv("CHAT_ID", "-1003872883285")
AFFILIATE_TAG = os.getenv("AFFILIATE_TAG", "dealbot91-21")

# --- TARGET DISCOUNT RANGE ---
MIN_DISCOUNT = 50   # Kam se kam 50%
MAX_DISCOUNT = 75   # Zyada se zyada 75%

PRODUCTS_TO_TRACK = [
    {"url": "https://www.amazon.in/GOBOULT-Smartwatch-Brightness-Watchfaces-Monitoring/dp/B0FB8VPKQK/"},
    {"url": "https://www.amazon.in/GOBOULT-Mustang-Racer-Smartwatch-AMOLED/dp/B0CX9279D2/"},
    {"url": "https://www.amazon.in/GOBOULT-Newly-Launched-Smartwatch-Watchfaces/dp/B0D5Y8S6QM/"},
    {"url":"https://www.amazon.in/Imsa-Moda-Polycotton-Loose-Comfortable/dp/B0GWVFLGFD"},
    {"url":"https://www.amazon.in/dp/B0DGDC59NV"}
]

def send_telegram_message(product_title, current_price, discount, url):
    affiliate_url = f"{url}&tag={AFFILIATE_TAG}" if "?" in url else f"{url}?tag={AFFILIATE_TAG}"
    message = f"🔥 **LOOT DEAL: {discount}% OFF!** 🔥\n\n" \
              f"📦 **Product:** {product_title[:60]}...\n" \
              f"💰 **Deal Price:** ₹{current_price}\n" \
              f"📉 **Discount:** {discount}% OFF\n\n" \
              f"🔗 **Buy Before Price Up:** {affiliate_url}"

    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}

    for attempt in range(3):  # retry logic
        try:
            requests.post(telegram_url, json=payload, timeout=10)
            print(f"🎉 Success! Alert posted for: {product_title[:30]}...")
            break
        except Exception as e:
            print("Telegram Error:", e)
            time.sleep(2)

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def check_discount(driver, url):
    try:
        driver.get(url)
        time.sleep(5)

        # Title
        try:
            title = driver.find_element(By.ID, "productTitle").text.strip()
        except:
            title = "Unknown Product"

        # Price
        price = 0
        try:
            p_el = driver.find_element(By.CLASS_NAME, "a-price-whole")
            price = float(p_el.text.replace(',', '').replace('₹', '').strip())
        except:
            pass

        # Discount
        discount = 0
        try:
            d_el = driver.find_element(By.XPATH, "//span[contains(text(),'%')]")
            discount = int(re.findall(r'\d+', d_el.text)[0])
        except:
            pass

        print(f"Checking: {title[:30]}... | Price: ₹{price} | Discount: {discount}%")

        if MIN_DISCOUNT <= discount <= MAX_DISCOUNT:
            print(f"-> Loot Mili! {discount}% range me hai. Telegram bhej raha hoon...")
            send_telegram_message(title, price, discount, url)
        else:
            print(f"-> Discount ({discount}%) range me nahi hai.")

    except Exception as e:
        print("Error:", e)

# --- MAIN LOOP ---
driver = get_driver()
while True:
    print(f"\n--- Cycle Started at {time.strftime('%X')} ---")
    for product in PRODUCTS_TO_TRACK:
        check_discount(driver, product["url"])
        time.sleep(6)
    print("\nSaare products check ho gaye. Agle cycle ke liye 1 ghante ka wait...")
    time.sleep(3600)
