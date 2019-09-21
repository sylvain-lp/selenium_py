from selenium import webdriver

#For Explicit Wait:
from selenium.webdriver.common.by  import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support    import expected_conditions as EC

#To Send to Domoticz
import urllib2
 
print("1. Setting Driver Options (Mobile)")
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')         # Bypass OS security model, MUST BE THE VERY FIRST OPTION
options.add_argument('--headless')           # Seems deprecated, replaced with "headless = True" below
options.headless = True
options.add_argument('start-maximized')      # open Browser in maximized mode
options.add_argument('disable-infobars')     # disabling infobars
options.add_argument('--disable-extensions') #disabling extensions
options.add_argument('--disable-dev-shm-usage') # overcome limited resource problem
options.add_argument('--disable-gpu')        # applicable to windows os only
#Configure WebDriver Options to Emulate Chrome on Mobile Device Nexus 5 / 360x640
mobile_emulation = {
    "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19" }

options.add_experimental_option('mobileEmulation', mobile_emulation)
options.add_experimental_option('useAutomationExtension', False) 
#Start Chrome WebDriver
print("2. Starting WebDriver Chrome")
chrome = webdriver.Chrome(chrome_options=options)

#Prevent code from executing before the page fully loads.
#chrome.implicitly_wait(10)

#Open Target URL and check Title 
print("3. Open Web Site")
chrome.get("http://teleray.irsn.fr")
#chrome.get("http://www.google.com")

print("4. Page Result Title: {}".format(chrome.title.encode('utf-8')))
#chrome.save_screenshot('screenshot.png')

#Search #1 Element to Click on Page (Region)
#Wait Map to be Clickable + Display Index + Click on Element (France Map)

elem = WebDriverWait(chrome, 10).until(
    EC.element_to_be_clickable((By.XPATH, u'//*[@id="map"]/div[1]/div[2]/div[3]/img[103]')))
print("z-index: "+ elem.value_of_css_property("z-index"))

#fav = "{'list':[{'id':1036,'name':'LYON'}]}"
#fav = '{\'name\':\'LYON\'}'
#fav = "LYON5"
#favscript = "window.localStorage.setItem('favorites', '{}');".format(fav)
print("5 Setting Favorites") # to: '{}'".format(fav) #"{\'list\':[{\"id\":1036,\"name\":\"LYON\"}]}"))
# chrome.execute_script(favscript)
# chrome.execute_script("window.localStorage.setItem('favorites'," + fav + ");")
# FAIL: chrome.execute_script("""window.localStorage.setItem('favorites',{"list":[{"id":1036,"name":"LYON"}]});""")
# FAIL2: chrome.execute_script("window.localStorage.setItem('favorites',\"{\'list\':[{\"id\":1036,\"name\":\"LYON\"}]}\")")
# TARGET UNESCAPED: localStorage.setItem("favorites","{'list':[{\"id\":1036,\"name\":\"LYON\"}]}")
# TARGET ATTEMPT: fav = "{'list':[{\"id\":1036,\"name\":\"LYON\"}]}"
# TARGET OK !!! fav = "{\\\"name\\\":\\\"LYON\\\"}"
fav = "{\\\"list\\\":[{\\\"id\\\":1036,\\\"name\\\":\\\"LYON\\\"}]}"
scr = "window.localStorage.setItem(\"favorites\",\"{}\")".format(fav)
print("  Running Script: {}".format(scr))
chrome.execute_script(scr)
# chrome.execute_script("window.localStorage.setItem(\"favorites\",\"{\'list\':[{\\\"id\\\":1036,\\\"name\\\":\\\"LYON\\\"}]}\" ")

#chrome.execute_script("window.localStorage.setItem('favorites',\"{\'list\':[{\"id\":1036,\"name\":\"LYON\"}]}\")")
print("Favorites Set")
# chrome.execute_script("window.localStorage.setItem('favorites','{'list':[{'id':1036,'name':'LYON'}]}');")
# fav = chrome.execute_script("window.localStorage.getItem('favorites');")
fav = 'empty' 
#fav = chrome.execute_script("""return window.localStorage.getItem('favorites');""")

print("6 Getting ALL Local Storage Data")
lng = chrome.execute_script("return window.localStorage.length")
i = 0
while i < lng:
    scr = "return window.localStorage.key({})".format(i)
    ky0 = chrome.execute_script(scr)
    # print '  {}: {}'.format(i,ky0)
    scr = "return window.localStorage.getItem(\"{}\")".format(ky0)
    itm = chrome.execute_script(scr)
    print("  {}. Item: {}\t Value: {}".format(i,ky0,itm)) 
    i+=1

print("7. Opening Favorites Page...with LYON")
#USING URL chrome.get("http://teleray.irsn.fr/#favoritespage")

#USING "CLICK"
clickfav = WebDriverWait(chrome, 10).until(
    EC.element_to_be_clickable((By.XPATH, u'//*[@id="favorite"]')))
print("   FOUND Favorite Icon to Click: {}".format(clickfav.get_attribute("href")))
print("   CLICKING!")
clickfav.click()
print("   Done")
print("   Page Result Title: {}".format(chrome.title.encode('utf-8')))
#html = chrome.page_source
#print(html)
#Search #3 Element to Display Results (Lyon?)
print("8. Reading LYON Metrics from Favorites Page")
#lyon = WebDriverWait(chrome, 10).until(
#EC.presence_of_element_located((By.XPATH, u'//*[@id="fav1036measure"]')))

lyon = WebDriverWait(chrome, 10).until(
    EC.presence_of_element_located((By.XPATH, u'//*[@id="fav1036measure"]')))

#EC.presence_of_element_located((By.ID("fav1036measure"))))
#lyon = chrome.find_element_by_xpath(u'//*[@id="fav1036measure"]')
print("   LYON Fav: "+ lyon.get_attribute("innerText").encode('utf-8'))
# SELECTOR: #fav1036measure
#lyon = chrome.find_element_by_xpath(u'//*[@id="fav1036measure"]')
print("  1 --> {}".format(lyon))
metric=lyon.get_attribute("innerText").encode('utf-8')
print("  2 --> {}".format(metric))
final=metric.split(" ")
print("  3 --> FINAL: {} nSv/h - TIME:{}".format(final[0], final[3]))
print("  4 --> Sending to DOMOTICZ")

url_dom = 'http://192.168.1.30:8084/json.htm?type=command&param=udevice&idx=52&nvalue=0&svalue=' + final[0]
print("  5 --> URL: {}".format(url_dom))
f = urllib2.urlopen(url_dom)
f.close()

#elem.click()
print("Done")
""" 
#Search #2 Element to Click on Page (Cities)
#Wait Map to be Clickable + Display Index + Click on Element (City Map)
elem2 = WebDriverWait(chrome, 90).until(
EC.element_to_be_clickable((By.XPATH, u'//*[@id="map"]/div[1]/div[2]/div[3]/img[20]')))
print("8. Clicking on City")
print("z-index: "+ elem2.value_of_css_property("z-index"))
print("Clicking City...")
elem2.click()
print("Done")

#Search #3 Element to Display Results (Lyon?)
city = chrome.find_element_by_xpath(u'//*[@id="markerpage"]/div[1]/h1')
radio = chrome.find_element_by_xpath(u'//*[@id="details-list"]/li[2]')

#Display City and Data for Element (Lyon Data?)
print("City  : "+ city.value_of_css_property("innerText"))
print("Radio : "+ radio.value_of_css_property("innerText"))
print("End") """

#Closing Browser (need QUIT instead to close ALL Windows) 
chrome.quit()
