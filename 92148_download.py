#!/usr/bin/env python

import mechanize
import re
import os
import sys
import requests
from bs4 import BeautifulSoup

list_url="http://www.92148.com/search/label/%E5%8B%95%E6%BC%AB%E7%B7%A3%E4%B9%8B%E7%A9%BA"
MAX_RESULT = 500
CHUNK_SIZE = 32768

def generate_download_url(file_id) :
    return "https://drive.google.com/uc?export=download&id=" + file_id

def get_driver_viewer_url(dom) :
    soup = BeautifulSoup(dom, 'html.parser')
    
    iframe = soup.find('iframe')
    
    print iframe
    
    if iframe != None :
        tmp_url = iframe.attrs['src']
    
        regx = re.compile("https://docs.google.com/file/d/(.+)/preview")
        regx_result = regx.findall(tmp_url)
        
        if regx_result != [] :   
            return regx_result[0]
        else :
            return ""
    else :
        return ""
  

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
    global CHUNK_SIZE
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)
    f.close()

def save(download_url, directory) :
    print download_url

    session = requests.Session()
    response = session.get(download_url, params = {'id':id}, stream = True)

    confirm_key_value = get_confirm_key_value(response)

    response = session.get(download_url, params = {'id': id, 'confirm': confirm_key_value}, stream = True)
    
    get_file_extension_format = "video/(.+)"
    regx = re.compile(get_file_extension_format)
    regx_result = regx.findall(response.headers['Content-Type'])
    
    if (regx_result != []) :
        print regx_result[0]
        save_response_content(response, directory + "." + regx_result[0])
    else :
        print "Unknown video type " + response.headers['Content-Type']

def download_from_web_page(episode_url, directory) :
    dom = get_web_page(episode_url)
        
    redirect_url = get_redirect_url(dom)    
    if (redirect_url) != "" :
        print "Redirect to new url"
        dom = get_web_page(redirect_url)
        
        print redirect_url
        
        file_id = get_driver_viewer_url(dom)
        if file_id != "" :
            download_url = generate_download_url(file_id)
            save(download_url, directory)
    else :
        print "Url not found"

def generate_file_name_from_url(url) :
    get_html_name_format = "http://.+/(.+)\.html"
    
    regx = re.compile(get_html_name_format)
    regx_result = regx.findall(url)
    
    if regx_result != [] :
        return regx_result[0]
    
def batch_download(download_list, start_episode, end_episode) :
    for download_task in download_list:
        if (download_task['episode'] >= start_episode) :
            if  (end_episode == 0) or (download_task['episode'] <= end_episode) :
                print "Downloading episode: " + str(download_task['episode'])
                download_from_web_page(download_task['link'], download_task['directory'])
    print "done"
    
def get_episode_from_name(file_name) :
    episode_format = "(\d+).*"
    
    regx = re.compile(episode_format)
    regx_result = regx.findall(file_name)
    
    if regx_result != [] :
        return int(regx_result[0])
        
def download_video_from_list(list_url, directory, start_episode = 1, end_episode = 0, count = 0) :
    dom = get_web_page(list_url)
    download_list = []
    
    if count != 0 :
        end_episode = start_episode + count - 1
    
    soup = BeautifulSoup(dom, 'html.parser')
    h3_list = soup.find_all('h3')
    
    for h3 in h3_list :
        a = h3.find('a')
        if a != None :
            link = a['href']
            file_name = generate_file_name_from_url(link)
            episode = get_episode_from_name(file_name)
            download_list.append({'episode': episode, 'directory': os.path.join(directory, file_name), 'link': link})
    
    batch_download(download_list, start_episode, end_episode)
    
def append_max_result(url) :
    global MAX_RESULT
    regx = re.compile("[&]*max-results=[\d]+")
    regx_result = regx.findall(url)
    
    if regx_result != [] :
        url = url.replace(regx_result[0], "")
    
    if url[-1] != '?' :
        url += '?'
    
    return url + "&max-results=" + str(MAX_RESULT)
    
if __name__ == "__main__" :
    url = append_max_result(list_url)
    print url
    download_video_from_list(url, "I:\\videos\\tmp")