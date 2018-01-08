#!/bin/env python

import mechanize
import re
import os
import urllib
from bs4 import BeautifulSoup

url_92148="https://www.google.com.tw/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=0ahUKEwjzpvbBr8jYAhUCXrwKHaHEC3QQFggmMAA&url=http%3A%2F%2Fwww.92148.com%2F2014%2F09%2F59_14.html&usg=AOvVaw3hbtlrPj3sm-lGDJk_HmHM"

def generate_download_url(url_core) :
    return "https://drive.google.com/uc?export=download&confirm=us-z&id=" + url_core

def get_driver_viewer_url(dom) :
    soup = BeautifulSoup(dom, 'html.parser')
    
    iframe = soup.find('iframe')
    
    tmp_url = iframe.attrs['src']
    
    regx = re.compile("https://docs.google.com/file/d/(.+)/preview")
    regx_result = regx.findall(tmp_url)
       
    return regx_result[0]
  

def get_web_page(url) :
    br = mechanize.Browser()
    
    br.set_handle_robots(False)
    br.addheaders = [("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36")]
    
    return br.open(url).get_data()

def get_redirect_url(dom) :
    url_pattern = "http://www.92148.com/.+\.html"
    regx = re.compile(url_pattern)
    regx_result = regx.findall(dom)
    
    if regx_result != [] :
        return regx_result[0]
    else :
        return ""

def click_download_anyway(download_url) :
    dom = get_web_page(download_url)
    
    soup = BeautifulSoup(dom, 'html.parser')
    hyperlinks = soup.find_all('a')
    
    for h in hyperlinks :
        if h.has_attr('class') :
            if any("jfk-button-action" in s for s in h.attrs['class']) :
                print "found"
                return "https://drive.google.com" + h['href']
 
#def save(download_url, directory) :    
    
def main() :
    dom = get_web_page(url_92148)
        
    redirect_url = get_redirect_url(dom)    
    if (redirect_url) != "" :
        print "Redirect to new url"
        dom = get_web_page(redirect_url)
        
        print redirect_url
        
        url_core = get_driver_viewer_url(dom)
        warning_page_url = generate_download_url(url_core)
        download_url = click_download_anyway(warning_page_url)
    else :
        print "Url not found"    
    
if __name__ == "__main__" :
    main()