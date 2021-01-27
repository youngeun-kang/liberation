import sys
import os
import json
import subprocess
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
import psycopg2

sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('../..'))


from ExcelFileReader import ExcelFileReader
from util.util import findUrl
from NaverScreenshot import open_chrome_driver, save_fullpage_screenshot


class NaverCrawlerCurl:

    def _get_json_data_(self, curl_command):
        curl_command = curl_command.replace("\n", "")
        curl_command = curl_command.replace("\\", "")
        curl_command = curl_command.replace("\'", "\"")
        curl_command = curl_command.replace("--compressed", "")
        #print(curl_command)
        result = subprocess.check_output(f"{curl_command}", shell=True)
        result = result.decode('utf-8')
        json_obj = json.loads(result)
        return json_obj

    def _read_template_(self):
        data = ExcelFileReader.load('../../data/naver_url.pkl')
        curl_list = []
        for row in data.values:
            pid = row[0]
            barcode = row[3]  # P&G Product barcode
            ncurl_pg = row[12]  # P&G Product curl url
            curl_list.append([pid, barcode, ncurl_pg])
        return curl_list

    def __parse_json__obj__(self, json_obj, pid):
        """
        To-do : Json object를 파싱해서 dataframe로 만든다.
        """
        try:
            naver_df = pd.DataFrame({})

            #json -> result -> products
            result = self._parse_element(json_obj, 'result')
            products = self._parse_element(result, 'products')
                              
            #for loop products list, 1 product level
            rank = 0
            while rank < len(products):                            
                product_df = pd.DataFrame(products[rank], index=[0])
                #filter columns
                product_df = product_df[['nvMid', 'productName', 'mallName', 'channelName', 'pcPrice', 'mobilePrice', 'deliveryFee', 'pcProductUrl']]
                #add rank of the product from the main list
                product_df['pcRank'] = rank + 1
                naver_df = pd.concat([naver_df, product_df], axis=0, ignore_index=True)
                rank += 1

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

    def process(self):
        curl_list = self._read_template_()
        for pid, barcode, curl in curl_list[:1]:  #excel template이 완성되면 제거할것.
            json = self._get_json_data_(curl)
            print(json)
            curl_df = self.__parse_json__obj__(json, pid)
            curl_df['Barcode'] = barcode
            print(curl_df)
            print(curl_df.columns)

    def run_craweler(self, pid, curl, result_df, info_type, d):
        '''Check input is vaild url and extract key data'''

        if "https://search.shopping.naver.com/" in str(curl):
            #get page source
            json = self._get_json_data_(curl)
            #parse page source
            naver_df = self.__parse_json__obj__(json, pid)
            #pid
            naver_df['pid'] = pid
            #extract url
            url_found= findUrl(curl)[0]
            # take a screenshot of it and add file name to screenshot col
            #naver_df['screenshot'] = save_fullpage_screenshot(d, str(pid)+"_"+str(info_type), url_found)
            #concatenate crawled procudt info
            result_df = pd.concat([result_df, naver_df], axis = 0,  ignore_index=True)
        return result_df

if __name__ == '__main__':
    naver = NaverCrawlerCurl()
    naver.process()

