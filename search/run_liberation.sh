#! /bin/bash
/root/miniconda3/etc/profile.d/conda.sh
cd /root/liberation/search
echo $PWD
/root/miniconda3/bin/python naver/NaverCrawler.py > application.log

