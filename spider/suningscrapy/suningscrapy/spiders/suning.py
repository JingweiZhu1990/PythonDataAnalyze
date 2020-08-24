import scrapy
import re
import datetime
from suningscrapy.items import SuningscrapyItem
from suningscrapy.items import CommentsItem

class SuningSpider(scrapy.Spider):
    name = 'suning'
    allowed_domains = ['suning.com']
    #start_urls = ['http://suning.com/']
    MAXREVIEWSPAGES = 2
    keyword = 'iphone 11'
    # 商品列表页的 初始页
    page = 0
    # 商品列表页的 层数
    layer = 0
    # 商品列表页的 地址
    searchlisturl ='https://search.suning.com/emall/searchV1Product.do?keyword={0}&ci=0&pg=01&cp=%d&il=0&st=0&iy=0&isNoResult=0&n=1&id=IDENTIFYING&cc=579&paging=%d&sub=1'.format(keyword)
    def start_requests(self):
        yield scrapy.Request(url=self.searchlisturl % (self.page, self.layer), callback=self.parse)

    def parse(self, response):
        productslist = response.xpath('//li[contains(@class,"item-wrap")]')
        for product in productslist:
            url = ''.join(['https:',product.xpath('.//div[@class="title-selling-point"]/a/@href').extract()[0]])
            # 回调去处理 parseproductdetailpage（处理商品详情页）
            yield scrapy.Request(url=url, callback=self.parseproductdetailpage)
        if self.layer < 3 and self.page < 50:
            self.layer += 1
            yield scrapy.Request(url=self.searchlisturl%(self.page,self.layer), callback=self.parse)  # meta={'download_timeout':3}（设置超时时间）
        if self.layer == 3 and self.page < 49:
            self.layer = 0
            self.page += 1
            yield scrapy.Request(url=self.searchlisturl%(self.page,self.layer), callback=self.parse)

    #product detail page
    def parseproductdetailpage(self, response):
        # 商品价格页的 地址
        responestext = response.text
        url = response.url
        producttitle = ''.join(response.xpath('//h1[@id="itemDisplayName"]/text()').extract()).strip()
        shopname = response.xpath('//div[@class="si-intro-list"]/dl/dd/a/text()').extract_first().strip()
        product_id1 = url.split('/')[3]
        product_id2 = url.split('/')[4].split('.')[0]
        productdetialurl = 'https://pas.suning.com/nspcsale_0' + ('_' + '0' * (18 - len(product_id2)) + product_id2) * 2 + '_' + product_id1 + '_130_579.html'
        yield scrapy.Request(url=productdetialurl, callback=self.parseproductprice,meta={'url':url,'producttitle':producttitle,'shopname':shopname})
        # get cluster_id
        clusterIdRE = re.compile(r'clusterId":"(.*?)"', re.S)
        clusterId = re.findall(clusterIdRE, responestext)[0]
        print(clusterId)
        commenturls = ["https://review.suning.com/ajax/cluster_review_lists/cluster-" + str(clusterId) + "-" + "0" * (18 - len(product_id2)) + product_id2 + "-" + product_id1 + "-total-{0}-default-10-----reviewList.htm?callback=reviewList".format(i + 1) for i in range(self.MAXREVIEWSPAGES)]
        for commenturl in commenturls:
            yield scrapy.Request(url=commenturl, callback=self.parsecomments,meta={'url':url})

    #product info incluede price
    def parseproductprice(self,response):
        productitem = SuningscrapyItem()
        saleinforespone = response.text
        PriceRE = re.compile(r'promotionPrice":"(.*?)"', re.S)
        productprice = re.findall(PriceRE, saleinforespone)
        productitem['price'] = productprice[0]
        productitem['title'] = response.meta['producttitle']
        productitem['url'] = response.meta['url']
        productitem['shopname'] = response.meta['shopname']
        productitem['crawldate'] = datetime.datetime.now()
        yield productitem

    def parsecomments(self,response):
        commenttext = re.findall('\((.*)\)', response.text)[0]
        commentitem = CommentsItem()
        commentitem['url'] = response.meta['url']
        commentitem['commentstext'] = commenttext
        yield commentitem