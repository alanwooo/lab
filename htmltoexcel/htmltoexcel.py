#! /usr/bin/python

import bs4 # yum install python-beautifulsoup4
import json
import urllib
import urllib2
import httplib
import cookielib
import pyquery

LOGINURL = 'https://xxxx.com/atlas_login.php'

def getLoginInfo():
    return { 'user' : 'xxxxxx',
             'password' : 'xxxxx',
             'login' : 'loginUser'
           }

def getWebPage(opener, url, data={}):
    headers = {'Connection': 'keep-alive',
        'Adf-Ads-Page-Id': '2',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'Adf-Rich-Message': 'true',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept-Encoding': 'gzip, deflate'
        }
    entrydata = urllib.urlencode(data)
    if entrydata:
        req = urllib2.Request(url, entrydata, headers=headers)
    else:
        req = urllib2.Request(url,headers=headers)

    res = opener.open(req)
    con = res.read()
    #print ron
    return con

def getFormValue(page):
    """
    get the login page, parser it, get all the inputs in form(submit),
    fill the name input and password input
    """
    data = {}
    soup = bs4.BeautifulSoup(page)
    inputs = soup.find('form').findAll('input')
    for input in inputs:
        name = input.get('name')
        value = input.get('value')
        data[name] = value

    return data

def getCookies():
    cookiejar=cookielib.CookieJar()
    cj=urllib2.HTTPCookieProcessor(cookiejar)
    opener=urllib2.build_opener(cj)

    print cookiejar
    getWebPage(opener, LOGINURL) # login once to get the cookies
    print cookiejar
    return opener

def getTargetWebPage(opener, url):
    """
    data = getFromValue(LOGINURL)
    data['user'] = 'xxxxxxx'
    data['password'] = 'xxxxxxx'
    con = getWebPage(opener, url, data)
    """
    con = getWebPage(opener, url, getLoginInfo())
    pq = pyquery.PyQuery(con)

    for tr in pq('tr'):
        element = [pyquery.PyQuery(td).text() for td in pyquery.PyQuery(tr)("td")]
        if len(element) < 3 or element[1] != getLoginInfo()['user']:
            continue
        print json.dumps(element)

if __name__ == "__main__":
    url = 'http://xxxxx/xxxx' # the web page you want to get
    getTargetWebPage(getCookies(), url) 
