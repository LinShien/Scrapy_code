import scrapy
from scrapy_for_project import items

class NudeSpider(scrapy.Spider):
    name = 'NudeSpider'
    allowed_domains = ['nudepics.ws']            #爬蟲限制範圍
    start_urls = ['http://www.nudepics.ws/index.php?p=1',  'http://www.nudepics.ws/index.php?p=2', ]      #從這個url開始爬蟲, 之後的url都從這延伸
    
    def __init__(self, max_pages = 10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._max_pages = max_pages
        self._pages = 0
    

    #default callback func to process downloaded responses, when their requests don’t specify a callback   
    #in charge of processing the response and returning scraped data  or or more URLs to follow                                       
    def parse(self, response):                   
        self._pages += 1
        if self._pages > self._max_pages:
            self.logger.warning('max pages reached')
            scrapy.signals.spider_closed(self, 'max pages reached')   
        
        page = response.url.split("/")[-2]    #The response parameter is an instance of TextResponse that holds the page content and has further helpful methods to handle it
        filename = '%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        
        next_page_urls = response.xpath('.//div[@class = "topmenu"]/a/@href').extract()
        for next_url in next_page_urls:
            if next_url is not None:
                yield scrapy.Request(response.urljoin(next_url), callback = self.parse_image)
    
    def parse_image(self, response):
        item = items.ImageItem()
        
        for image_url in response.xpath('.//div[@class = "tblock"]/a/img/@data-src').extract():
            if image_url.endswith('.jpg'):
                item['image_urls'] = {image_url}
                yield item
                 