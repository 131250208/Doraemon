import scrapy
import re
import json

class CommentsSpider(scrapy.Spider):
    name = 'comments'
    start_urls = [
        'http://music.163.com/discover/playlist/?order=hot',
    ]

    def parse(self, response):
        cat_url_list = response.css("a.s-fc1::attr(href)").extract()
        for cat_url in cat_url_list:
            # self.log('cat_url %s' % cat_url)
            yield response.follow(cat_url, callback=self.process_cat)

    # 遍历每个cat的所以page
    def process_cat(self, response):
        page_end = int(response.css("a.zpgi::text").extract()[-1])
        self.log("%d pages in this category!" % page_end)

        for p in range(page_end):
            url = response.url + "&limit=35&offset=" + str(p * 35)
            yield scrapy.Request(url, callback=self.parse_cat)

    # 处理每一页的歌单
    def parse_cat(self, response):
        songslist_a_list = response.css("a.tit")

        for songslist_a in songslist_a_list:
            songslist_title = songslist_a.css("::attr(title)").extract_first()
            songslist_url = songslist_a.css("::attr(href)").extract_first()

            self.log("song-list %s " % songslist_title)
            yield response.follow(songslist_url, callback=self.parse_songslist)

    # process songslist
    def parse_songslist(self, response):
        song_a_list = response.css("ul.f-hide > li > a")

        param = {'params': 'wxLqdGgw16OHb6UwY/sW16VtLqAhGaDMeI2F4DaESDplHA+CPsscI4mgiKoVCPuWW8lcd9eY0YWR/iai0sJqs0NmtLubVCkG\
                                dpNTN3mLhevZpdZy/XM1+z7L18InFz5HbbRkq230i0aOco/3jVsMWcD3/tzzOCLkGuu5xdbo99aUjDxHwDSVfu4pz4spV2KonJ47Rt6vJhOorV7LfpIVmP/qeZghfaXXuKO2chlqU54=',
                 'encSecKey': '12d3a1e221cd845231abdc0c29040e9c74a47ee32eb332a1850b6e19ff1f30218eb9e2d6d9a72bd797f75fa115b769ad580fc51128cc9993e51276043ccbd9ca4e1f589a2ec479ab0323c973e7f7b1fe1a7cd0a02ababe2adecadd4ac93d09744be0deafd1eef0cfbc79903216b1b71a82f9698eea0f0dc594f1269b419393c0', }

        for song_a in song_a_list:
            song_href = song_a.css("::attr(href)").extract_first()
            song_name = song_a.css("::text").extract_first()

            song = {
                "song_id": int(re.match("\/song\?id=([0-9]+)", song_href).group(1)),
                "song_name": song_name,
            }

            url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_%s?csrf_token=c0f6bfdcd0526ec0ba6c207051a08960' % \
                  song["song_id"]

            yield scrapy.FormRequest(url=url,
                                     formdata=param,
                                     callback=lambda response=response, song=song: self.parse_comments_json(response,
                                                                                                            song))

    def parse_comments_json(self, response, song):
        jsonob = json.loads(response.text)
        hotComments = jsonob["hotComments"]

        if len(hotComments) == 0: return

        comments = []
        for com in hotComments:
            likedCount = com["likedCount"]
            if likedCount < 100: continue

            comments.append({
                "likedCount": likedCount,
                "content": com["content"],
            })

        if len(comments) == 0: return

        yield {
            "id": song["song_id"],
            "name": song["song_name"],
            "comments": comments,
        }
