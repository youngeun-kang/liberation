import pandas as pd
import pickle

import sys
import os

sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('../..'))

#sys.path.append('C:\\Users\\kang.y.5\\OneDrive - Procter and Gamble\\Documents\\GitHub\\liberation\\search')

print(sys.path)

from util.util import readPickle, writePickle

class ExcelFileReader:

    def read (filepath):
        #Above 10 rows should be skipped in template
        template = pd.read_excel(os.path.abspath(filepath), skiprows=10)
        writePickle(template, '..data/naver_url.pkl')

    def load (filepath):
        if os.path.isfile(filepath):
            return readPickle(filepath)
        else:
            raise FileExistsError(f'{os.path.abspath(filepath)} Pickle file is not exist')

if __name__ == "__main__":
    efr = ExcelFileReader
    efr.read('../data/Liberation_Price Tracker SKU list_v1_Pampers.xlsx')
    print(efr.load('../data/naver_url.pkl'))

