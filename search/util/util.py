import pickle
#Binary로 변경하는 패키지
import re
import os

def writePickle(obj, pickle_file):
    with open(pickle_file, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

 
def readPickle(pickle_file):
    with open(pickle_file, 'rb') as input:
        obj = pickle.load(input)
        return obj

def findUrl(string): 
    # findall() has been used  
    # with valid conditions for urls in string 
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)       
    return [x[0] for x in url]