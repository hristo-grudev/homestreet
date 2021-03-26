import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import HomestreetItem
from itemloaders.processors import TakeFirst


class HomestreetSpider(scrapy.Spider):
	name = 'homestreet'
	start_urls = ['http://ir.homestreet.com/feed/PressRelease.svc/GetPressReleaseList?apiKey=BF185719B0464B3CB809D23926182246&LanguageId=1&bodyType=3&pressReleaseDateFilter=3&categoryId=1cb807d2-208f-4bc3-9133-6a9ad45ac3b0&pageSize=-1&pageNumber=0&tagList=&includeTags=true&year=-1&excludeSelection=1']

	def parse(self, response):
		json_response = json.loads(response.text)
		articles = json_response["GetPressReleaseListResult"]
		for article in articles:
			link = response.urljoin(article['LinkToDetailPage'])
			date = article["PressReleaseDate"]
			yield response.follow(link, self.parse_post, cb_kwargs=dict(date=date))

	def parse_post(self, response, date):
		if 'pdf' in response.url:
			return
		title = response.xpath('//h2[@class="module-details_title"]//text()[normalize-space()]').get()
		description = response.xpath('//div[@class="module_body"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=HomestreetItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
