# -*- coding: utf-8 -*-
import scrapy
from lxml import etree
from amazon.items import AmazonItem
import requests
from fake_useragent import UserAgent
import re, datetime


class AmazonspiderSpider(scrapy.Spider):
    name = 'amazonSpider'
    allowed_domains = ['www.amazon.com']
    keyword='earbuds'
    start_urls = [f'https://www.amazon.com/s?k=earbuds&page={page}' for page in range(1, 51)]
    headers = {'user-agent': UserAgent().chrome,'referer': 'https://www.amazon.com/'}

    # start
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    # html
    def parse(self, response):
        print(f'{response.url} 请求成功')
        retry_num = 1
        html = response.text

        try:
            if 'Enter the characters you see below' in html:
                print('需输入验证码：{}'.format(response.url))
                raise requests.exceptions.RequestException
        except Exception as e:
            print(e)
            if response.status == 404:
                print('404错误：{}'.format(response.url))

            if retry_num <= 10:
                print(f'{response.url}重试第{retry_num}次')
                self.retry(url=response.url)
                retry_num += 1

            else:
                print(f'重试失败{response.url}')
                html = ''
        return self.parse_page(html=html)

    def retry(self, url):

        yield scrapy.Request(
            url=url,
            headers=self.headers,
            callback=self.parse
        )

    # get asin
    def parse_page(self,html):
        if html == '':
            print('页面获取失败')
        else:
            print('获取页面成功')
            mytree = etree.HTML(html)
            asin_box = mytree.xpath('//*[@id="search"]/div[1]/div[2]/div/span[3]/div[1]/div[contains(@data-asin,"B")]/@data-asin')

            for asin in asin_box:
                url = 'https://www.amazon.com/dp/' + asin

                try:
                    yield scrapy.Request(url=url, callback=self.get_detail, headers=self.headers)
                except Exception as e:
                    print(e)
                    self.retry_asin_url(url=url)

    def retry_asin_url(self,url):
        retry_num = 1
        try:
            print(f'{url}回调重试第{retry_num}次')
            yield scrapy.Request(url=url, callback=self.get_detail, headers=self.headers)
        except Exception as e:
            print(e)

            if retry_num <= 11:
                self.retry_asin_url(url)
                print(f'详情页{url}回调出错重试第{retry_num}次')
                retry_num += 1
            else:
                print(f'{url}详情页获取失败')

    def get_detail(self,res):

        print(f'{res.url} 请求成功')

        retry_num = 1
        html_text = res.text

        try:
            if 'Enter the characters you see below' in html_text:
                print('需输入验证码：{}'.format(res.url))
                raise requests.exceptions.RequestException
        except Exception as e:
            print(e)
            if res.status == 404:
                print('404错误：{}'.format(res.url))

            if retry_num <= 10:
                self.retry_asin_url(url=res.url)
                print(f'{res.url}重试第{retry_num}次')
                retry_num += 1
            else:
                print(f'爬取失败{res.url}')

        print(f'解析详情页面{res.url}')

        item = {}
        keyword = self.keyword
        item['keyword'] = keyword
        url = res.url
        item['url'] = url
        item['asin'] = url.split('/')[-1]
        html = etree.HTML(html_text)

        # title
        try:
            item['title'] = html.xpath('//span[@id="productTitle"]/text()')[0].strip().replace('\xa0', ' ')
        except Exception as e:
            item['title'] = ''

        # brand
        if html.xpath('//a[@id="bylineInfo"]/text()') and html.xpath('//a[@id="bylineInfo"]/text()'):
            item['brand'] = html.xpath('//a[@id="bylineInfo"]/text()')[0].replace('by','').strip()
        elif html.xpath('//a[contains(@class,"contributorNameID")]/text()'):
            item['brand'] = html.xpath('//a[contains(@class,"contributorNameID")]/text()')[0].strip()
        else:
            item['brand'] = ''

        # price
        if html.xpath('//span[@id="priceblock_ourprice"]/text()'):
            price = html.xpath('//span[@id="priceblock_ourprice"]/text()')[0]
            item['price'] = price[1:]
        else:
            item['price'] = ''

        # main pic
        if html.xpath('//div[@id="imgTagWrapperId"]/img/@data-old-hires'):
            if html.xpath('//div[@id="imgTagWrapperId"]/img/@data-old-hires')[0]:
                item['picture'] = html.xpath('//div[@id="imgTagWrapperId"]/img/@data-old-hires')[0]
            else:
                item['picture'] = re.findall('"(https.*?\.jpg)"',html.xpath('//div[@id="imgTagWrapperId"]/img/@data-a-dynamic-image')[0])[0]
        elif re.findall('"mainUrl":"(https.*?\.jpg)"', html_text):
            item['picture'] = re.findall('"mainUrl":"(https.*?\.jpg)"', html_text)[0]
        elif html.xpath('//div[@id="digitalMusicProductImage_feature_div"]/img/@src'):
            item['picture'] = html.xpath('//div[@id="digitalMusicProductImage_feature_div"]/img/@src')[0]
        else:
            item['picture'] = ''
        item['picture'] = re.sub('\._[A-Z]{2}\d{4}_', '', item['picture'])

        # stars
        try:
            item['stars'] = float(html.xpath('//span[@id="acrPopover"]/@title')[0].split(' ')[0])
        except:
            item['stars'] = 0.0

        # reviews
        try:
            item['reviews'] = int(html.xpath('//span[@id="acrCustomerReviewText"]/text()')[0].split(' ')[0].replace(',', ''))
        except:
            item['reviews'] = 0

        # father bsr
        if re.findall('#(.*?) in (.*?) \(.*?See Top 100 in.*?\)', html_text):
            item['rank'] = re.findall('#(.*?) in (.*?) \(.*?See Top 100 in.*?\)', html_text)[0]
        else:
            item['rank'] = ''

        item['ranks'] = []

        # son bsr
        if html.xpath('//li[@class="zg_hrsr_item"]'):
            ranks_no = html.xpath('//li[@class="zg_hrsr_item"]/span[@class="zg_hrsr_rank"]/text()')
            ranks_name = html.xpath('//li[@class="zg_hrsr_item"]/span[@class="zg_hrsr_ladder"]/a/text()')
            item['ranks'] = [(no.replace('#', ''), name) for no, name in zip(ranks_no, ranks_name)]

        if not item['ranks']:
            item['ranks'] = re.findall("<span>#(.*?) in <a.*?>(.*?)<\/a>", html_text)

        item['time'] = datetime.date.today()

        yield item

