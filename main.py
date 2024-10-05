import os
import zipfile
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import lxml.html
from db import connect_to_db, insert_multiple_posts, get_all_posts, insert_user, get_all_urls
import pandas as pd


# List of proxies in the format: IP:PORT:USERNAME:PASSWORD
valid_proxies = [
    '198.23.239.134:6540:hxmlpejz:sa6vhuse1ftb',
    '207.244.217.165:6712:hxmlpejz:sa6vhuse1ftb',
    '107.172.163.27:6543:hxmlpejz:sa6vhuse1ftb',
    '173.211.0.148:6641:hxmlpejz:sa6vhuse1ftb',
    '161.123.152.115:6360:hxmlpejz:sa6vhuse1ftb',
    '216.10.27.159:6837:hxmlpejz:sa6vhuse1ftb',
    '167.160.180.203:6754:hxmlpejz:sa6vhuse1ftb',
    '154.36.110.199:6853:hxmlpejz:sa6vhuse1ftb',
    '45.151.162.198:6600:hxmlpejz:sa6vhuse1ftb',
    '206.41.172.74:6634:hxmlpejz:sa6vhuse1ftb',
]

# Select a random proxy
proxy_str = random.choice(valid_proxies)

# Extract IP, port, username, and password from the proxy string
proxy_ip, proxy_port, proxy_user, proxy_pass = proxy_str.split(":")

# Create a Chrome extension to handle proxy authentication
def create_proxy_auth_extension(proxy_host, proxy_port, username, password, scheme='http'):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """
    
    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "%s",
                host: "%s",
                port: parseInt(%s)
              },
              bypassList: ["localhost"]
            }
          };
    
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    
    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }
    
    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {urls: ["<all_urls>"]},
        ['blocking']
    );
    """ % (scheme, proxy_host, proxy_port, username, password)
    
    # Save the extension
    plugin_file = 'proxy_auth_extension.zip'
    
    with zipfile.ZipFile(plugin_file, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    
    return plugin_file

def get_posts():
    posts = []
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        doc = lxml.html.fromstring(html)
        posts = soup.find_all(class_="css-1soki6-DivItemContainerForSearch e19c29qe19")
        for item in posts:
            post = {
                'video_url': item.div.div.div.a.get('href'),
                'video_caption': item.find("h1", class_='css-6opxuj-H1Container ejg0rhn1').get_text(),
                'author_username': item.find("p", class_='css-2zn17v-PUniqueId etrd4pu6').get_text(),
            }
            posts.append(post)
            #print(post)
    except Exception as e:
        pass

    return posts


def scroll_down():
    prev_height = -1 
    max_scrolls = 100
    scroll_count = 0

    while scroll_count < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.randint(3, 7))  # give some time for new results to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == prev_height:
            break
        prev_height = new_height
        scroll_count += 1

def get_posts_by_keywords(keyword):

    driver.get("https://www.tiktok.com/")
    time.sleep(10)
    # Locate the search input element by name (Google search box)
    search_box = driver.find_element(By.NAME, "q")
    # Input text into the search field
    search_box.send_keys(keyword)
    # Press Enter to perform the search
    search_box.send_keys(Keys.RETURN)
    # Wait for a few seconds to observe the results
    time.sleep(5)

    # Locate Videos
    try:
        # Locate the element using its unique attributes (you can use other locators if needed)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="search-tabs"]/div[1]/div[1]/div[1]/div[3]')
                )
        )
        video_element = driver.find_element(By.XPATH, '//*[@id="search-tabs"]/div[1]/div[1]/div[1]/div[3]')
        print("Video Element found!")
        # Click the tab element
        video_element.click()
        print("Video Tab clicked successfully!")
        time.sleep(10)
    except NoSuchElementException:
        print("Video element not found on the page.")
    except ElementClickInterceptedException:
        print("Element is not clickable at the moment.")

    scroll_down()
    return get_posts()
    


def get_posts_by_hastag(hastag):

    driver.get("https://www.tiktok.com/")
    time.sleep(10)
    # Locate the search input element by name (Google search box)
    search_box = driver.find_element(By.NAME, "q")
    # Input text into the search field
    search_box.send_keys("#"+hastag)
    # Press Enter to perform the search
    search_box.send_keys(Keys.RETURN)
    # Wait for a few seconds to observe the results
    time.sleep(5)

    # Locate Videos
    try:
        # Locate the element using its unique attributes (you can use other locators if needed)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="search-tabs"]/div[1]/div[1]/div[1]/div[3]')
                )
        )
        video_element = driver.find_element(By.XPATH, '//*[@id="search-tabs"]/div[1]/div[1]/div[1]/div[3]')
        print("Video Element found!")
        # Click the tab element
        video_element.click()
        print("Video Tab clicked successfully!")
        time.sleep(10)
    except NoSuchElementException:
        print("Video element not found on the page.")
    except ElementClickInterceptedException:
        print("Element is not clickable at the moment.")

    scroll_down()
    return get_posts()

def get_user(url):

    driver.get(url)
    time.sleep(10)
    user = driver.find_element(By.XPATH, '//*[@id="main-content-video_detail"]/div/div[2]/div[1]/div[1]/div[2]/div[1]/div/a[2]').click()
    time.sleep(random.randint(5, 10))
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    try:
        username = soup.find("h1", class_="css-11ay367-H1ShareTitle e1457k4r8").text
    except:
        username = None
    try:
        f = soup.find_all("div", class_="css-1ldzp5s-DivNumber e1457k4r1") # Followers and following
    except:
        f = [None, None]
    try:
        likes = soup.find("div", class_="css-pmcwcg-DivNumber e1457k4r1").text
    except:
        likes = None

    return {
        'username' : username,
        'follower_count' : f[0],
        'following_count' : f[1],
        'like_count' : likes
    }


def get_driver(proxy_auth_plugin_path):

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server={proxy_ip}:{proxy_port}')
    chrome_options.add_extension(proxy_auth_plugin_path)

    # Path to ChromeDriver
    webdriver_service = Service(executable_path='/Users/rittique/Python/chrome-mac-arm64/Google Chrome for Testing.app')

    # Launch the WebDriver with the proxy settings
    return webdriver.Chrome(options=chrome_options)

if __name__=="__main__":

    # Create the proxy authentication extension
    keywords = ["beautiful destinations",
                "places to visit",
                "places to travel",
                "places that don't feel real",
                "travel hacks"]

    hashtags = ["traveltok", "wanderlust", "backpackingadventures", 
                "luxurytravel", "hiddengems", "solotravel", "roadtripvibes", 
                "travelhacks", "foodietravel", "sustainabletravel"]
    
    all_posts_by_keywords = []
    all_posts_by_hashtags = []
    driver = uc.Chrome()

    conn = connect_to_db()

    nb_retries = 10

    # Visit a website
    try:
        try:
            driver = uc.Chrome()
            for keyword in keywords:
                time.sleep(random.randint(5, 10))
                session_posts_keyword = get_posts_by_keywords(keyword)
                for post in session_posts_keyword:
                    all_posts_by_keywords.append(post)
            print("Posts through Keywords: ", len(all_posts_by_keywords))
        except:
            pass

        try:
            driver = uc.Chrome()
            for hastag in hashtags:
                time.sleep(random.randint(5, 10))
                session_posts_hashtags = get_posts_by_keywords(hashtag)
                for post in session_posts_hashtags:
                    all_posts_by_keywords.append(post)
            print("Posts through Hastags", len(all_posts_by_hashtags))
        except:
            pass

    except Exception as e:
        print(f"Scrapping ended for: \n {e}")
    
    finally:
        insert_multiple_posts(conn, all_posts_by_keywords)
        insert_multiple_posts(conn, all_posts_by_hashtags)
        # Retrieving all posts to verify insertion
        all_posts = get_all_posts(conn)
        print("Posts:", len(all_posts))
        dummy_url = "https://www.tiktok.com/@tring_biring_ghost/video/7272750125674482945"
        insert_user(conn, get_user(dummy_url).values()[0], get_user(dummy_url).values()[1], get_user(dummy_url).values()[2])

        conn.close()

    







