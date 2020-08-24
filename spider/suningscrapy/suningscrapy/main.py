# 先导入一个包
from scrapy import cmdline
# 在cmdline里面，去执行一些命令
cmdline.execute("scrapy crawl suning -o suning.json".split())  # 进行一个字符串的处理