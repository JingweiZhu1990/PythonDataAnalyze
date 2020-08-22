from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import  WebDriverWait
from selenium.webdriver.support import  expected_conditions as EC
import time

gcookies = []

def login():
    # get login suning cookies
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 1}
    chrome_options.add_experimental_option("prefs", prefs)  # 不加载图片设置
    chrome_options.add_argument(
        'User-Agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36"')  # 谷歌文档提到需要加上这个属性来规避bug
    browser = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(browser, 10)  # 等待网页反应最多10秒
    browser.get('https://passport.suning.com/ids/login')
    while True:
        print("Please login in suning!")
        time.sleep(3)
        if "https://www.suning.com/" == browser.current_url:
            break

    global gcookies
    gcookies= browser.get_cookies()
    browser.close()

def scroll_down(browser): #下滑操作
    sroll_cnt = 0
    while  True:
        if (sroll_cnt) < 10:
            browser.execute_script('window.scrollBy(0, 2000)')
            time.sleep(1.5)
            sroll_cnt += 1
        else:
            break

def getProductslist(keyword):
    # login
    #login()
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 1}
    chrome_options.add_experimental_option("prefs", prefs)  # 不加载图片设置
    chrome_options.add_argument(
        'User-Agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36"')  # 谷歌文档提到需要加上这个属性来规避bug
    browser = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(browser, 10)  # 等待网页反应最多10秒
    #search list
    browser.get('https://www.suning.com/')
    for cookie in gcookies:
        browser.add_cookie(cookie)
    search_input = wait.until(EC.presence_of_element_located((By.XPATH,'//input[@id="searchKeywords"]')))
    search_input.send_keys(keyword)
    time.sleep(1)
    search_btn=wait.until(EC.presence_of_element_located((By.XPATH,'//input[@id="searchSubmit"]')))
    search_btn.click()
    productlist = []
    #翻页
    #苏宁最多50页
    count = 0
    for pagenum in range(4):
        url = browser.current_url  # 翻页后，获取当前页面url
        print('在浏览第', pagenum + 1, '页的数据')
        print("此时页面url为：", url)
        print('开始爬取第', pagenum + 1, '页的数据')
        scroll_down(browser)
        #EC.presence_of_element_located()方法传参的问题，往该方法传参数时需要将参数用“（）”括起来使其作为一个整体，而不是单独传入
        wait.until(EC.presence_of_all_elements_located((By.XPATH,"//div[contains(@class,'product-list')]/ul/li")))
        items = browser.find_elements_by_xpath("//div[contains(@class,'product-list')]/ul/li")
        for item in items:
            try:
                #在element下使用相对路径来寻找元素。".//a"是元素下的所有链接，而去掉点的"//a"就是整个元素的所有链接了。 加上“.”，问题解决
                element_temp = item.find_element_by_xpath('.//div[@class="title-selling-point"]/a')
                title = element_temp.text
                href = element_temp.get_attribute("href")
                price = item.find_element_by_xpath('.//div[@class="price-box"]').text.lstrip('¥')
                shop = item.find_element_by_xpath('.//div[@class="store-stock"]').text
                product = {
                    'productname': title,
                    'producturl': href,
                    'price': price,
                    'shop': shop,
                }
                print(str(count) +str(product))
                count += 1
                productlist.append(product)
                time.sleep(1)
            except:
                continue
        #小词没有输入框
        input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="bottomPage"]')))  # 当前界面是页码输入框
        submit = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="page-more ensure"]')))
        input.clear()  # 去掉以前的页码
        input.send_keys(pagenum + 2)  # 输入新的页码
        submit.click()
        #翻页有问题，节点会变
        #browser.find_element_by_xpath('//a[@id="nextPage"]/b').click()
        time.sleep(5)
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="search-path"]/h1')))  # 等待翻页过程
        pagenum += 1

if __name__ == '__main__':
    login()
    getProductslist('iphone x')