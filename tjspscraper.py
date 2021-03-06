import arrow
import scrapy
from scrapy.crawler import CrawlerProcess

import os
from pathlib import Path

# `DLDIR_STRING` determina o diretorio onde serao salvos os downloads
DLDIR_STRING = "./downloads"

DLDIR        = Path(DLDIR_STRING)

def is_weekday(r: arrow.Arrow) -> bool:
    return not is_weekend(r)

def is_weekend(r: arrow.Arrow) -> bool:
    return r.format('dddd') in ["Sunday", "Saturday"]

def file_exists(fname):
    return os.path.isfile(DLDIR.joinpath(fname).as_posix())

class TJSPAranha(scrapy.spiders.Spider):
    name           = 'TJSP'
    download_delay = 1.5

    def start_requests(self):
        tjurl  = "https://dje.tjsp.jus.br/cdje/downloadCaderno.do?dtDiario={0}/{1}/{2}&cdCaderno={3}"
        cadernos = [11, 12, 13, 15, 18]
        diainicial = arrow.get(2007, 1, 1)
        diafinal   = arrow.utcnow()
        dias = list(arrow.Arrow.range('day', diainicial, diafinal))
        dias.reverse()
        for r in dias:
            if is_weekend(r):
                continue
            dia = r.format('DD')
            mes = r.format('MM')
            ano = r.format('YYYY')
            for c in cadernos:
                fname = f"{ano}{mes}{dia}c{c}.pdf"
                if file_exists(fname):
                    continue
                uri = tjurl.format(dia, mes, ano, c)
                yield scrapy.http.Request(uri, meta={'fname': fname})

    def parse(self, response):
        fhandle = open(DLDIR.joinpath(response.meta['fname']), 'wb')
        fhandle.write(response.body)
        fhandle.close()
        self.logger.info(f"{response.meta['fname']} salvo com sucesso")

def main():
    try:
        os.mkdir(DLDIR.as_posix())
    except FileExistsError:
        pass
    crawlproc = CrawlerProcess()
    crawlproc.crawl(TJSPAranha)
    crawlproc.start()

if __name__ == "__main__":
    main()

