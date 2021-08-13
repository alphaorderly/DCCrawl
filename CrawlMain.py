import urllib

import pdfkit
import requests
from urllib import request
from information import *
import bs4
import time
import os
import random
import urllib

def mainCrawl(BASE_URL, am):
    while(1):
        # 기본 Response
        response = requests.get(BASE_URL, headers=headers)
        soup = bs4.BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')

        article_list = soup.find('tbody').find_all('tr')

        # 공지 넘기기
        place = 0
        while(1):
            if not article_list[place].find_all('em', class_='icon_img icon_txt') and not article_list[place].find_all('em', class_='icon_img icon_pic') and not article_list[place].find_all('em', class_='icon_img icon_movie'):
                place += 1
            else:
                break

        item_recent = article_list[place:place + 2] # 가장 최근글 가져오기

        # 글 제목 / 글 주소 / 글 넘버 받아오기
        for item in item_recent:
            title_tag = item.find('a', href=True)
            address = title_tag['href']
            title = title_tag.text

            #폴더에 사용하면 안되는 문자 제거 및 공백 제거
            for char in invalid:
                title = title.replace(char, ' ')

            title = title.strip(' ')

            # 글 번호 받아오기
            address_number = address.split('&')[1].split("=")[1]

            # 사진 있으면 사진 받아오고, 없으면 받지 않기.
            if item.find_all('em', class_='icon_img icon_pic'):
                directory_name = "%s/img %s %s"%(SAVE_DIRECTORY, address_number, title)
            else:
                directory_name = "%s/%s %s" % (SAVE_DIRECTORY, address_number, title)

            if not os.path.isdir(directory_name):
                os.makedirs(directory_name)
                if item.find_all('em', class_='icon_img icon_pic') or item.find_all('em', class_='icon_img icon_movie'):
                    img_download(DCINSIDE_URL + address, directory_name)
                str_download(DCINSIDE_URL + address, directory_name, title)
            else:
                print(directory_name + " 는 이미 받아온 글입니다.")

        timeset = random.uniform(1.0, 1.5)
        time.sleep(timeset)

# 이미지 다운로드
def img_download(dcurl, directory):

    try:
        response = requests.get(dcurl, headers=headers)
        soup = bs4.BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
        if soup.find_all('div', class_='appending_file_box'): image_download_contents = soup.find('div', class_='appending_file_box').find('ul').find_all('li')
    except Exception as e :
        print(6)
        print(e)

    try:
        for li in image_download_contents:
            img_url = li.find('a', href=True)['href']

            # 저장될 파일명
            savename = img_url.split("no=")[2]
            # 파일 이름에 % 제거
            savename = savename.replace('%', '')
            # 레퍼러 => 이미지 다운로드
            headers['Referer'] = dcurl
            response = requests.get(img_url, headers=headers)

            path = "/%s"%savename

            #다운로드
            file = open(directory + path, "wb")
            file.write(response.content)
            file.close()
    except Exception as e :
        print(5)
        print(e)

# HTML 생성
def str_download(dcurl, directory, title):
    # 테스트용
    #dcurl = "https://gall.dcinside.com/mgallery/board/view/?id=destiny&no=1775239&page=1"

    response = requests.get(dcurl, headers=headers)
    soup = bs4.BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
    article_contents = soup.find('div', class_='writing_view_box').find('div', class_='write_div')

    savename = list()
    image_available = 0
    image_count = 0

    # 이미지 첨부파일이 있는지 확인하기
    try:
        if soup.find_all('div', class_='appending_file_box') and soup.find('div', class_='appending_file_box').find('ul').find_all('li'):
            image_download_contents = soup.find('div', class_='appending_file_box').find('ul').find_all('li')
            image_available = 1

            for i in image_download_contents:
                img_url = i.find('a', href=True)['href']
                savename.append(img_url.split("no=")[2].replace('%', ''))

    except Exception as e :
        print(1)
        print(e)

    # out of index 방지 ( 동일 파일 여러개 업로드시 )
    if savename.__len__() >= 1:
        for i in range(10):
            savename.append(savename[0])

    file = open(directory + "/%s.html"%title, "w", encoding='UTF-8')
    file.write(r"""
    <!DOCTYPE html>

    <html>

    <head>

    <meta charset="utf-8">

    <title>""")

    file.write(title)

    file.write(r"""</title>

    </head>
    
    <body>
    
    <p>""")

    file.write('<a href="%s">원글 보러가기</a>'%dcurl)

# 본격적인 HTML 코딩 부분, 움짤 / 디시콘 / 비디오 예외처리 및 video 움짤 처리 과정
    try:
        for item in article_contents:
            if str(type(item)) != "<class 'bs4.element.NavigableString'>":
                for i in item:
                    if str(type(i)) != "<class 'bs4.element.NavigableString'>":
                        if(i.name == 'img'):                 # 이미지 관리
                            if i.has_attr('class'): continue # 디시콘 이미지 -> 넘기기
                                # index 넘지 않게
                            if (image_count >= len(savename)): continue

                            i['src'] = savename[image_count]
                            i['width'] = "75%"
                            image_count += 1
                        if(i.name == 'video'):
                            if i.has_attr('class'): # 움직이는 디시콘 -> 따로 img로 뽑아야 작동함
                                imgsrc = i['data-src']
                                i.name = 'img'  # img로 바꾸고, attribute 다 지우고 src 추가하기
                                i.attrs.clear()
                                i['src'] = imgsrc
                                continue
                                # index 넘지 않게
                            if (image_count >= len(savename)): continue

                            i.name = 'img'                   # img로 바꾸고, attribute 다 지우고 src 추가하기
                            i.attrs.clear()
                            i['src'] = savename[image_count]
                            image_count += 1
            file.write(str(item))
    except Exception as e :
        print(2)
        print(e)

    file.write(r"""</p>

    </body>
    
    </html>""")

    file.close()


