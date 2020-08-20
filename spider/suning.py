import requests
from requests.exceptions import RequestException
import re
from lxml import etree
import json

head = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36 Edg/84.0.522.52'}

def getProductsList(Keyword,MAXPAGES):
    baseURL = 'http://search.suning.com/emall/searchV1Product.do?'
    productsList = []
    for pagenum in range(MAXPAGES):
        for inpagenum in range(3):
            params ={
                'keyword':Keyword,
                'ci':'0',
                'pg':'01',
                'cp':pagenum, #翻页
                'il':'0',
                'st':'0',
                'iy':'0',
                'isNoResult':'0',
                'n':'1',
                'id':'IDENTIFYING',
                'cc':'579',
                'paging':inpagenum, #同页加载序号0-3，每次30个，共120个
                'sub':'1'
            }
            try:
                response = requests.get(baseURL,params=params,headers = head)
                if response.status_code == 200:
                    responsetext = response.text
                    selector = etree.HTML(responsetext)
                    for href in selector.xpath('//*[@class="title-selling-point"]/a/@href'):
                        if 'http:'+href not in productsList:
                            #判断重复链接
                            productsList.append('http:'+href)
                else:
                    return productsList
            except RequestException:
                return None
    return productsList

def getUsefulComment(commentID):
    # https: // review.suning.com / ajax / useful_count / 737122242 - usefulCnt.htm
    usefullcommenturl = 'https://review.suning.com/ajax/useful_count/'+str(commentID)+'-usefulCnt.htm'
    try:
        usefullcommenttext = requests.get(usefullcommenturl, headers=head).text
        commenttext = re.findall('\((.*)\)', usefullcommenttext)[0]
        usefullcommentjson = json.loads(commenttext)
        return usefullcommentjson['reviewUsefuAndReplylList'][0]['usefulCount']
    except Exception:
        print("评论评论有用数失败",usefullcommenturl)

def geProductReviews(clusterId,productid2,productid1,MAXREVIEWSPAGES):
    commenturls = ["https://review.suning.com/ajax/cluster_review_lists/cluster-" + str(clusterId) + "-" + "0" * (
                18 - len(productid2)) + productid2 + "-" + productid1 + "-total-{0}-default-10-----reviewList.htm?callback=reviewList".format(
        i+1) for i in range(MAXREVIEWSPAGES)]
    try:
        commentslist = []
        for commenturl in commenturls:
            commenttext = requests.get(commenturl, headers=head).text
            if('成功取得评价列表' not in commenttext):
                break
            commenttext = re.findall('\((.*)\)', commenttext)[0]
            commentjson = json.loads(commenttext)
            for index in range(len(commentjson['commodityReviews'])):
                commentsdict = {}
                commentsdict["commentname"] = commentjson['commodityReviews'][index]['userInfo']['nickName'] #评论姓名
                commentsdict["commentcontent"] = commentjson['commodityReviews'][index]['content'] # 评论内容
                commentsdict["commentqualitystar"] = commentjson['commodityReviews'][index]['qualityStar']  # 星级
                commentsdict["commenttime"] = commentjson['commodityReviews'][index]['publishTime'] #发表时间
                commentsdict["commentuseful"] = getUsefulComment(commentjson['commodityReviews'][index]['commodityReviewId'])  # 评论有用数
                #追评
                if commentjson['commodityReviews'][index]['againFlag']:
                    commentsdict["commentagaincontent"] = commentjson['commodityReviews'][index]['againReview']['againContent']
                    commentsdict["commentagaintime"] = commentjson['commodityReviews'][index]['againReview']['publishTime']

                # 图片地址
                commentpics = []
                if commentjson['commodityReviews'][index]['picVideoFlag']:
                    commentstr = str(commentjson['commodityReviews'][index])
                    if 'imageInfo' in commentstr:
                        for picindex in range(len(commentjson['commodityReviews'][index]['picVideInfo']['imageInfo'])):
                            commentpics.append('https:'+commentjson['commodityReviews'][index]['picVideInfo']['imageInfo'][picindex]['url']+'.jpg')
                    if 'imgId' in commentstr:
                        for picindex in range(len(commentjson['commodityReviews'][index]['againReviewImgList'])):
                            commentpics.append('https:' + commentjson['commodityReviews'][index]['againReviewImgList'][0]['imgId'] + '.jpg')
                    commentsdict["commentpics"] = commentpics
                commentslist.append(commentsdict)
                #print(commentsdict)
        return commentslist
    except Exception:
        print("评论获取失败",commenturl)

def getOneProductPage(producturl,maxcommentpages):
    try:
        productdict = {}
        ProductPagehtml = requests.get(producturl, headers=head)
        if ProductPagehtml.status_code == 200:
            ProductPagetext = ProductPagehtml.text
            # get product_id
            product_id1 = str(producturl.split('/')[3])
            product_id2 = str(producturl.split('/')[4].split('.')[0])
            # get cluster_id
            clusterIdRE = re.compile(r'clusterId":"(.*?)"', re.S)
            clusterId = re.findall(clusterIdRE, ProductPagetext)
            # 商品名
            selector = etree.HTML(ProductPagetext)
            product_name = ''.join(selector.xpath('//*[@id="itemDisplayName"]/text()')).strip()
            productdict["product_name"] ="".join(product_name.split())
            # 价格 难点
            #原始标头 https://pas.suning.com/nspcsale_0_000000011346320883_000000011346320883_0000000000_130_579_5790199_20089_1000331_9323_12570_Z001___R1901001_0.45_0___000060021____0___826.072_2_01_20002_20006_.html?callback=pcData&_=1597221286134
            saleinfourl = 'https://pas.suning.com/nspcsale_0' + ('_'+'0' * (18 - len(
                product_id2))+ product_id2 )*2 + '_' + product_id1 + '_130_579.html'
            saleinforespone = requests.get(saleinfourl,headers = head).text
            PriceRE = re.compile(r'promotionPrice":"(.*?)"', re.S)
            productprice = re.findall(PriceRE, saleinforespone)
            productdict["productprice"] = productprice[0]
            comments = geProductReviews(clusterId[0],product_id2,product_id1,maxcommentpages)
            productdict["comments"] = comments
            return productdict
    except RequestException:
        return None


def main():
    keywords = input("pls input search keyword:")
    MAXSEARCHLISTPAGES = 1
    MAXCOMMENTPAGES = 1
    urllist = getProductsList(keywords,MAXSEARCHLISTPAGES)
    #urllist = ['http://product.suning.com/0000000000/11346320883.html']
    productslist = []
    for urlindex in urllist:
        print(urlindex + '  start')
        productdict = {}
        productdict['product'] = getOneProductPage(urlindex,MAXCOMMENTPAGES)
        productslist.append(productdict)
        print(urlindex + '  finished')
    #get products json
    productsdict = {"keywords":keywords,"productslist":productslist}
    #productsstr = str(productsdict)
    #productsjson = json.loads(productsstr.replace("'",'"'))
    with open('data.json', 'w') as f:
        f.write(json.dumps(productsdict, indent=2, ensure_ascii=False))
if __name__ == '__main__':
    main()

