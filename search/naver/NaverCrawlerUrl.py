import requests
from bs4 import BeautifulSoup as soup
from datetime import datetime
from sqlalchemy import create_engine
import psycopg2
import pandas as pd
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname('../..'))))

from ExcelFileReader import ExcelFileReader
from util.util import findUrl
from NaverScreenshot import open_chrome_driver, save_fullpage_screenshot

class NaverCrawlerUrl:

    def crawl_search_page(self, url=None):
        '''Search Page Crawling by keyword'''

        html = requests.get(url, headers={'User-Agent': 'Moziilla/5.0'})
        page_soup = soup(html.text, 'html.parser')
        data = page_soup.findAll('script', {'type': 'application/json'})
        json_data = str(data[0]).replace('<script id="__NEXT_DATA__" type="application/json">','').replace('</script>','')
        json_obj = json.loads(json_data)
        return json_obj

    def parse_search_page(self, json_obj, pid):
        '''Parse Html Page, and extract key data'''
        try:
            naver_df = pd.DataFrame({})

            #json -> props -> pageProps -> initialState -> catalog -> products
            props = self._parse_element(json_obj, 'props')
            pageProps = self._parse_element(props, 'pageProps')
            initialState = self._parse_element(pageProps, 'initialState')
            catalog = self._parse_element(initialState, 'catalog')
            full_products = self._parse_element(catalog, 'products')

            #for loop full_product list
            i = 0
            while i < len(full_products):
                #full product -> element i -> productsPage -> products
                product = self._parse_element(full_products, i)
                productsPage = self._parse_element(product, 'productsPage')
                products = self._parse_element(productsPage, 'products')

                if products is not None:
                    
                    #only if this product is in main list
                    if i==3:                        
                        #for loop products list, 1 product level
                        rank = 0
                        while rank < len(products):
                            product_df = pd.DataFrame(products[rank], index=[0])
                            #add rank of the product from the main list
                            product_df['pcRank'] = rank + 1
                            naver_df = pd.concat([naver_df, product_df], axis=0, ignore_index=True)
                            rank += 1
                    i += 1
                else:
                    i += 1
                    continue

            naver_df['pid'] = pid
            naver_df['crawling_datetime'] = datetime.now()
            naver_df['crawling_date'] = pd.to_datetime(naver_df['crawling_datetime'] ).dt.date
            naver_df['crawling_hour'] = pd.to_datetime(naver_df['crawling_datetime'] ).dt.hour
            naver_df = naver_df.astype({"pcRank": int})

            return naver_df

        except ValueError as ve:
            print(ve)

    def _parse_element(self, obj, element_name):
        '''Parse obj by element'''
        if obj is not None and obj[element_name] is not None:
            return obj[element_name]
        else:
            #raise ValueError(f'Not Exist Error {element_name}')
            return None

    '''
    def _determine_case_type (i):
        #Return meaning of the product case
        return {0: 'lowest price', 1: 'official mall', 2:'summary', 3: 'main list', 4: 'need to be investigated'}.get(i, 'case not determinded')
    '''


    def run_craweler(self, pid, url, result_df, info_type, d):
        '''Check input is vaild url and extract key data'''

        if "https://search.shopping.naver.com/" in str(url):
            #extract url
            url_found= findUrl(url)[0]
            #get page source
            html = self.crawl_search_page(url_found)
            #parse page source
            naver_df = self.parse_search_page(html, pid)
            #filer_mandatory_columns
            naver_df = naver_df[['crawling_date','crawling_hour','crawling_datetime', 'pid','nvMid', 'productName', 'mallName', 'channelName', 'pcPrice', 'mobilePrice', 'deliveryFee', 'pcRank', 'pcProductUrl']]
            # take a screenshot of it and add file name to screenshot col
            #naver_df['screenshot'] = save_fullpage_screenshot(d, str(pid)+"_"+str(info_type), url_found)
            #concatenate crawled procudt info
            result_df = pd.concat([result_df, naver_df], axis = 0,  ignore_index=True)
        return result_df

if __name__ == '__main__':
    print('Naver Crawler Start')
    data = ExcelFileReader.load('../data/naver_url.pkl')
    result_df = pd.DataFrame()
    crawler = NaverCrawlerUrl    
    d = open_chrome_driver()

    origin_df = pd.DataFrame(data)
    print(origin_df)

    for row in data.values:
        pid= row[0]
        nurl_pg = row[11] #P&G Product url
        nurl_1 = row[30] #Competitor 1 url
        nurl_2 = row[47] #Competitor 2 url

        result_df = NaverCrawler.run_craweler(crawler, pid, nurl_pg, result_df, 'PG', d)
        result_df = NaverCrawler.run_craweler(crawler, pid, nurl_1, result_df, 'C1', d)
        result_df = NaverCrawler.run_craweler(crawler, pid, nurl_2, result_df, 'C2', d)

        print(pid)
    print(result_df)

    main_df = pd.merge(origin_df[['No', 'Barcode']], result_df, how='right', left_on = 'No', right_on= 'pid').drop(['pid'], axis=1)
    print(main_df)

    d.close()
