from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


def save_fullpage_screenshot(chromeDriver, pidInfo=None, url=None):
    '''take screenshot and return screenshot file name'''

    chromeDriver.get(url)
    time.sleep(5)
    
    filename = str(time.strftime("%Y-%m-%d_%H-%M-%S")) + "_pid-" + str(pidInfo) + ".png"
    direcoty = "/shared/image/"
    filename = direcoty + filename
    try:
        chromeDriver.save_screenshot(filename)
        return filename
    except:
        return ""

def open_chrome_driver(path = None):
    '''open chrome driver with options'''

    path = 'chromedriver'
    #path = 'c:\\bin\\chromedriver.exe'
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f"--window-size=1200,4300")
    d = webdriver.Chrome(path,chrome_options=chrome_options)    
    return d


"""
d = open_chrome_driver()
print(save_fullpage_screenshot(d))
d.close()
"""
