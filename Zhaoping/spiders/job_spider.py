# -*- coding: utf-8 -*-
import scrapy
import json
from Zhaoping.items import ZhaopingItem
import re

class ZhaopinSpider(scrapy.Spider):
    name = 'job_spider'
    # allowed_domains = ['sou.zhaopin.com']

    baseUrl='https://fe-api.zhaopin.com/c/i/sou?start={0}&pageSize=90&cityId=489' \
            '&workExperience=-1&education=-1&companyType=-1&employmentType=-1' \
            '&jobWelfareTag=-1&kw={1}&kt=3'

    offset=0 #偏移量

    # start_urls = []

    '''
    初始换爬取地址，取关键词组成爬取初始地址
    '''
    def start_requests(self):
        with open('keywords.json', 'r') as f:
            keywords_list = json.load(f)

        start_urls=[]
        for item in keywords_list:
            for job_key in item['Job_keywords']:
               start_urls.append(self.baseUrl.format(str(self.offset),job_key))
        if start_urls is not None:
            for url in start_urls:
                print("start_url:",url)
                yield scrapy.Request(url=url,callback=self.parse,meta={'start_url':url})

    def parse(self, response):
        #将json数据加载成字节数据
        data_list=json.loads(response.body)['data']['results']
        if len(data_list)==0:
            return
        #迭代遍历
        for data in data_list:
            #实例化对象
            item=ZhaopingItem()
            item['jobType']=data['jobType']['display']     #职位所属种类
            item['jobName']=data['jobName']                 #职位名称
            item['emplType']=data['emplType']               #工作类型(兼职、全职)
            item['eduLevel']=data['eduLevel']['name']      #学历要求
            item['companyName']=data['company']['name']    #公司名称
            item['salary']=data['salary']                   #薪资
            item['welfare']=data['welfare']                 #员工福利
            item['city']=data['city']['display']            #工作城市
            item['workingExp']=data['workingExp']['name']  #工作经验
            item['infoComLink']=data['company']['url']     #公司详情连接

            yield item

        '''
        获取start_request函数传递过来的url，爬取第一页结束之后，
        使用正则匹配，替换url中的起始页，拼接新的url，
        增加偏移量offset，达到翻页的效果。
        '''
        print("调试：输入response中的meta参数：",response.meta['start_url'])
        init_url=response.meta['start_url']
        self.offset += 90
        str_offset = str(self.offset)
        pattern = 'start=(.*?)&'
        replace_str = 'start=' + str_offset + '&'
        url = re.sub(pattern=pattern, repl=replace_str, string=init_url)

        yield scrapy.Request(url=url,callback=self.parse)










