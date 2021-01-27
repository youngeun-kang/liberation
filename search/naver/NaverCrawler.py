import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from ExcelFileReader import ExcelFileReader
import math
from NaverCrawlerUrl import NaverCrawlerUrl
from NaverCrawlerCurl import NaverCrawlerCurl
from NaverScreenshot import open_chrome_driver, save_fullpage_screenshot
from sqlalchemy import create_engine
import sys
import os

sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('../..'))

class NaverCrawler:
    def isNaN(self, string):
        return string != string

    def transform_template(self):
        data = ExcelFileReader.load('../data/naver_url.pkl')

        url_list = []
        for row in data.values:
            pid = row[0]
            barcode = row[3]  # P&G Product barcode
            #P&G product
            if not self.isNaN(row[12]):
                ncurl_pg = row[12]  # P&G Product curl url
                url_list.append(['curl', 'PG', pid, barcode, ncurl_pg])
            elif not self.isNaN(row[11]):
                nurl_pg = row[11]  # P&G Product url url
                url_list.append(['url', 'PG', pid, barcode, nurl_pg])                
            
            #Competitor 1
            if not self.isNaN(row[34]):
                ncurl_c1 = row[34]  # Competitor1 Product curl url
                url_list.append(['curl', 'C1', pid, barcode, ncurl_c1])
            elif not self.isNaN(row[33]):
                nurl_c1 = row[33]  # Competitor1 Product url url
                url_list.append(['url', 'C1', pid, barcode, nurl_c1])
            
            #Competitor 2
            if not self.isNaN(row[52]):
                ncurl_c2 = row[52]  # Competitor2 Product curl url
                url_list.append(['curl', 'C2', pid, barcode, ncurl_c2])
            elif not self.isNaN(row[51]):
                nurl_c2 = row[51]  # Competitor2 Product url url
                url_list.append(['url', 'C2', pid, barcode, nurl_c2])  
        url_df = pd.DataFrame(url_list)
        url_df.columns = ['urlType', 'infoType', 'pid','barcode', 'url']
        return url_df

    def insert_db(self, result_df):
        print('====================================Insert DB==============================================')
        print(result_df.sample(5))
        print(result_df.columns)
        engine = create_engine('postgresql+psycopg2://liberation:qwer1234@143.40.147.92:5432/liberation_db', echo=False)
        result_df.set_index(['crawling_date', 'crawling_hour', 'barcode', 'nvMid'])
        result_df.to_sql('naver_price', con=engine, if_exists='append')


if __name__ == '__main__':
    print('Naver Crawler Start')

    crawler = NaverCrawler()
    crawlerUrl = NaverCrawlerUrl() 
    crawlerCurl = NaverCrawlerCurl() 

    url_df = NaverCrawler.transform_template(crawler)
    print(url_df)
    
    result_df = pd.DataFrame()   
    d = open_chrome_driver()

    for i in url_df.index:
        url_type = url_df._get_value(i, 'urlType')
        info_type = url_df._get_value(i, 'infoType')
        pid = url_df._get_value(i, 'pid')
        url = url_df._get_value(i, 'url')

        if url_type == 'url':
            result_df = NaverCrawlerUrl.run_craweler(crawlerUrl, pid, url, result_df, info_type, d)
        else:
            result_df = NaverCrawlerCurl.run_craweler(crawlerCurl, pid, url, result_df, info_type, d)
    
    print(result_df)

    main_df = pd.merge(url_df, result_df, how='right', left_on = 'pid', right_on= 'pid').drop(['urlType', 'url'], axis=1)
    #main_df.to_csv('result.csv',encoding='utf-8-sig')

    crawler.insert_db(main_df)
    d.close()


    
