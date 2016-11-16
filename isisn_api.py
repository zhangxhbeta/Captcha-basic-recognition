# -*- coding:utf-8 -*-

import urllib
import urllib2
from StringIO import StringIO
from PIL import Image
import cv2.cv as cv
import os
from gzip import GzipFile
import zlib
from cookielib import CookieJar
try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et


class IsisnApi():
    def __init__(self, domain, dir='Isisn', encoding=None):
        self.domain = domain
        self.dir = dir
        self.encoding = encoding
        self.image_url = None
        self.imagestr = None
        self.image = None

        cj = CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)

    def urlopen(self, url, data=None):
        request = urllib2.Request(self.domain + url)
        request.add_header('Accept-encoding', 'gzip,deflate')

        if data is None:
            response = urllib2.urlopen(request)
        else:
            response = urllib2.urlopen(request, urllib.urlencode(data))
        content = response.read()
        encoding = response.info().get('Content-Encoding')

        if encoding == 'gzip':
            txt = self.gzip(content)
        elif encoding == 'deflate':
            txt = self.deflate(content)
        else:
            txt = content
        return txt

    def getValidateCodeImg(self):
        self.imagestr = self.urlopen('/egrantindex/validatecode.jpg?date=')
        self.string_to_iplimage(self.imagestr)  # Convert image
        return self.image

    def checkCode(self, code):
        result = self.urlopen('/egrantindex/funcindex/validate-checkcode', {'checkCode': code})
        print '校验验证码:{} | {}'.format(code, result)
        return result == 'success'

    def getXml(self, code, year, page):
        searchStr = 'resultDate^:prjNo%3A%2Cctitle%3A%2CpsnName%3A%2CorgName%3A%2CsubjectCode%3A%2Cf_subjectCode_hideId%3A%2CsubjectCode_hideName%3A%2CkeyWords%3A%2Ccheckcode%3Apnxd%2CgrantCode%3A429%2CsubGrantCode%3A%2ChelpGrantCode%3A%2Cyear%3A' + year + '[tear]sort_name1^:psnName[tear]sort_name2^:prjNo[tear]sort_order^:desc'
        data = {
            'searchString': searchStr,
            'rows': '100',
            'page': page,
            'sidx': '',
            'sord': 'desc',
            '_search': 'false'
        }

        txt = self.urlopen('/egrantindex/funcindex/prjsearch-list?flag=grid&checkcode=' + code, data)

        # 保存起来
        with open('{}/{}-{}.xml'.format(self.dir, year, page), "w") as xmlFile:
            xmlFile.write(txt)
        print 'Saved to file {}/{}-{}.xml'.format(self.dir, year, page)
        return txt

    def retriveOtherPage(self, code, year, page):
        self.getXml(code, year, page)

    def retriveFirstPage(self, code, year):
        # 获取第一页数据
        txt = self.getXml(code, year, '1')

        # 解析返回的数据
        if self.encoding is not None:
            txt = txt.decode(self.encoding)

        try:
            root = et.fromstring(txt)
        except Exception, e:
            print "Error:cannot parse result xml."
            return
        total = int(root.find('total').text)
        return total


    def gzip(self, data):
        buf = StringIO(data)
        f = GzipFile(fileobj=buf)
        return f.read()

    def deflate(self, data):
        try:
            return zlib.decompress(data, -zlib.MAX_WBITS)
        except zlib.error:
            return zlib.decompress(data)

    def string_to_iplimage(self, im):
        # Convert the image return by urllib into an OpenCV image
        pilim = StringIO(im)
        source = Image.open(pilim).convert("RGB")

        self.image = cv.CreateImageHeader(source.size, cv.IPL_DEPTH_8U, 3)
        cv.SetData(self.image, source.tobytes())
        cv.CvtColor(self.image, self.image, cv.CV_RGB2BGR)


# 设定目录
def setupDir(dir):
    if os.path.exists(dir):
        for file in os.listdir(dir):
            os.remove(os.path.join(dir, file))
        os.removedirs(dir)
    os.mkdir(dir)
