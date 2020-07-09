from appium import webdriver
import time

desired_caps = {
                "platformName": "Android",
                "deviceName": "MHA_AL00",
                "appPackage": "com.eg.android.AlipayGphone",
                "appActivity": "AlipayLogin",
                "noReset": "true",
                "fullReset": "false"
}

server = 'http://localhost:4723/wd/hub'
driver = webdriver.Remote(server, desired_caps)
time.sleep(1)
driver.find_element_by_xpath("//*[@text='蚂蚁森林']").click() #蚂蚁森林要在首页
time.sleep(1)

def Swipe(driver):
    size = driver.get_window_size()
    for i in range(4):
        driver.swipe(size['width'] * 0.5, size['height'] * 0.9, size['width'] * 0.5, size['height'] * 0.2)
    driver.find_element_by_xpath("//*[@text='查看更多好友']").click() #点击查看更多好友

def run(driver):
    Swipe(driver)
    n = 1
    #获取用户框大小
    usersize = driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.RelativeLayout[2]/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.FrameLayout/com.uc.webview.export.WebView/com.uc.webkit.az/android.webkit.WebView/android.view.View/android.view.View/android.view.View[2]/android.view.View[1]').size
    while True:
        time.sleep(0.5)
        #分别进入每个人的主页
        xpathfile = '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.RelativeLayout[2]/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.FrameLayout/com.uc.webview.export.WebView/com.uc.webkit.az/android.webkit.WebView/android.view.View/android.view.View/android.view.View[2]/android.view.View[{0}]/android.view.View[3]/android.view.View[1]/android.view.View'.format(n)
        namelist = driver.find_elements_by_xpath(xpathfile)
        if(len(namelist) > 0):
            name = namelist[0].text
            namelist[0].click()#点击该用户名称并进入
        if(len(driver.find_elements_by_xpath("//*[@text='邀请']")) > 0 or len(namelist) == 0):#用户为邀请状态或最后一个即返回到蚂蚁森林主页
            #driver.find_element_by_id("com.alipay.mobile.nebula:id/h5_tv_nav_back").click()
            driver.keyevent(4)  # 键盘返回
            break
        print('正在查看{0}的蚂蚁森林'.format(name))

        #个人主页收能量
        #向上滑动激活页面能量元素
        windowssize = driver.get_window_size()
        driver.swipe(windowssize['width'] * 0.5, windowssize['height'] * 0.9, windowssize['width'] * 0.5, windowssize['height'] * 0.7)
        items = driver.find_elements_by_class_name("android.widget.Button")
        if len(items) >6: #另有6个页面中的固定元素
            for i in items:
                if '能量' in i.text:
                    print('收取{0}的{1}'.format(name,i.text.replace('收集','')))
                    i.click()

        #主页中退出
        if name != 'JingweiZhu1990': #排除个人的号进不了主页
            #driver.find_element_by_id('com.alipay.mobile.nebula:id/h5_tv_nav_back').click() #左上角回退
            driver.keyevent(4) #键盘返回
        driver.swipe(windowssize['width'] * 0.5, windowssize['height'] * 0.9, windowssize['width'] * 0.5, windowssize['height'] * 0.9 - usersize['height'])

        n = n+1

if __name__ == '__main__':
    run(driver)
    driver.quit()