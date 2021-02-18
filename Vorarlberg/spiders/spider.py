import scrapy
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from ..items import VorarlbergItem

pattern = r'(\r)?(\n)?(\t)?(\xa0)?'


class SpiderSpider(scrapy.Spider):
    name = 'spider'

    start_urls = ['https://www.hypovbg.at/hypo-vorarlberg/news']

    def parse(self, response):
        links = response.xpath('//div[@class="hlv-news__list-item"]//a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//div[@class="hlv-news__pagination"]/a[@class="hlv-button hlv-button_link hlv-button_arrow"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(VorarlbergItem())
        item.default_output_processor = TakeFirst()
        date = response.xpath('//time/@datetime').get()
        title = response.xpath('//h1//text()').get().strip()
        content = response.xpath('//div[@class="hlv-news-content__text hlv-typeset"]//text()').getall()
        content = re.sub(pattern, "", ' '.join(content))
        category = response.xpath('//div[@class="hlv-news-content__date"]//text()[not (ancestor::time)]').get().strip().split(' ')[1]

        item.add_value('date', date)
        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('category', category)
        return item.load_item()