#!/bin/env python

import mechanize
import re
import os
import requests
from bs4 import BeautifulSoup

url_92148="https://www.google.com.tw/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=0ahUKEwjzpvbBr8jYAhUCXrwKHaHEC3QQFggmMAA&url=http%3A%2F%2Fwww.92148.com%2F2014%2F09%2F59_14.html&usg=AOvVaw3hbtlrPj3sm-lGDJk_HmHM"

def generate_download_url(file_id) :
    return "https://drive.google.com/uc?export=download&id=" + file_id

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
 
def get_confirm_key_value(response) :    
    for key, value in response.cookies.items() :
        if key.startswith("download_warning") :
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 1024
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)

def save(download_url, directory) :
    print download_url

    session = requests.Session()
    response = session.get(download_url, params = {'id':id}, stream = True)

    print response.content

    confirm_key_value = get_confirm_key_value(response)

    response = session.get(download_url, params = {'id': id, 'confirm': confirm_key_value}, stream = True)

    save_response_content(response, directory)

def main() :
    dom = get_web_page(url_92148)
        
    redirect_url = get_redirect_url(dom)    
    if (redirect_url) != "" :
        print "Redirect to new url"
        dom = get_web_page(redirect_url)
        
        print redirect_url
        
        file_id = get_driver_viewer_url(dom)
        download_url = generate_download_url(file_id)
        save(download_url, "")
    else :
        print "Url not found"    
    
if __name__ == "__main__" :
    main()