# Project Title: ds-kr-liberation
This projecy aims to detect an abnormal price for P&G Products in Coupang website. Coupang collects product & price information from other eCommerce websites, match it with their products, and modifies the price information. Therefore, we use Naver price tracker site to collect other eCommerce websites and compare it with the Coupang price data.

## Structure of the code
Folders:
Data: include template and pickle file
Helper: DB related python code
Search: naver (naver crawling python code) and util (defined useful functions)

Main folder: naver
NaverCrawler file refers NaverCrawlerUrl and NaverCrawlerCurl to read url and curl. 
ExflefileReader file read Excel template and turn it to pickle
NaverScreenshot file take screenshot and save the screenshot to folder, return location