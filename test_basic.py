# PREREQUISITES: sudo apt-get install python-selenium
from selenium import webdriver

#For Explicit Wait:
from selenium.webdriver.common.by  import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support    import expected_conditions as EC

#To Send to Domoticz
import urllib2

#Defining Specific Variables (City & Domoticz Server)
SOURCE_URL   = "http://teleray.irsn.fr"
CITY_ID      = 1036
CITY_NAME    = "LYON"
DOMOTICZ_URL = "http://192.168.1.30:8084"
DOMOTICZ_IDX = 52
 
#Setting Options for Chrome Browser (Mobile Headless)
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')         # Bypass OS security model, MUST BE THE VERY FIRST OPTION
options.add_argument('--headless')           # Seems deprecated, replaced with "headless = True" below
options.headless = True
options.add_argument('start-maximized')      # open Browser in maximized mode
options.add_argument('disable-infobars')     # disabling infobars
options.add_argument('--disable-extensions') #disabling extensions
options.add_argument('--disable-dev-shm-usage') # overcome limited resource problem
options.add_argument('--disable-gpu')        # applicable to windows os only
#WebDriver Options to Emulate Chrome on Mobile Device Nexus 5 / 360x640
mobile_emulation = {
    "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19" }

options.add_experimental_option('mobileEmulation', mobile_emulation)
options.add_experimental_option('useAutomationExtension', False) 
#Start Chrome WebDriver
chrome = webdriver.Chrome(chrome_options=options)

#Chrome Waits for Elements to be Available prior to processing
chrome.implicitly_wait(10)

#Opening Any Web Page so that "Local Storage" can be accessible
chrome.get("http://teleray.irsn.fr/#mappage")
title=chrome.title.encode('utf-8')

#Setting Local Storage to have LYON in FAVORITES
fav = "{\\\"list\\\":[{\\\"id\\\":1036,\\\"name\\\":\\\"LYON\\\"}]}"
scr = "window.localStorage.setItem(\"favorites\",\"{}\")".format(fav)
chrome.execute_script(scr)

#Opening Favorite Page BY CLICKING (open by URL is not enough)
clickfav = WebDriverWait(chrome, 10).until(
    EC.element_to_be_clickable((By.XPATH, u'//*[@id="favorite"]')))
clickfav.click()
 
#Get LYON Metrics from FAVORITES Summary
lyon = WebDriverWait(chrome, 10).until(
    EC.presence_of_element_located((By.XPATH, u'//*[@id="fav1036measure"]')))
metric=lyon.get_attribute("innerText").encode('utf-8')
final=metric.split(" ")
print("LYON: {} nSv/h - TIME:{}".format(final[0], final[3]))

#Sending Results to Domoticz
url_dom = 'http://192.168.1.30:8084/json.htm?type=command&param=udevice&idx=52&nvalue=0&svalue=' + final[0]
print("Sending to Domoticz: {}".format(url_dom))
f = urllib2.urlopen(url_dom)
f.close()

#Closing Browser (need QUIT instead to close all Windows) 
chrome.close()
chrome.quit()
