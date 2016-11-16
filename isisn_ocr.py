# -*- coding:utf-8 -*-

'''
Created on 20 juil. 2012

@author: robin
'''

from generic_ocr_operations import *
from isisn_api import *


def crack(tocrack, withContourImage=False):
    # Function that intent to release all characters on the image so that the ocr can detect them

    # We just apply 4 filters but with multiples rounds

    # 转化为灰度图
    imgry = cv.CreateImage(cv.GetSize(tocrack), cv.IPL_DEPTH_8U, 1)
    cv.CvtColor(tocrack, imgry, cv.CV_RGB2GRAY)

    resized = resizeImage(imgry, (tocrack.width * 6, tocrack.height * 6))

    dilateImage(resized, 4)

    erodeImage(resized, 4)

    thresholdImage(resized, 180, cv.CV_THRESH_BINARY)

    if withContourImage:  # If we want the image made only with contours
        contours = getContours(resized, 5)
        contourimage = cv.CreateImage(cv.GetSize(resized), 8, 3)
        cv.Zero(contourimage)
        cv.DrawContours(contourimage, contours, cv.Scalar(255), cv.Scalar(255), 2, cv.CV_FILLED)

        contourimage = resizeImage(contourimage, cv.GetSize(tocrack))
        resized = resizeImage(resized, cv.GetSize(tocrack))

        return resized, contourimage

    resized = resizeImage(resized, cv.GetSize(tocrack))

    res = pytesser.iplimage_to_string(resized, psm=pytesser.PSM_SINGLE_WORD)  # Do characters recognition
    res = res[:-2]  # Remove the two \n\n always put at the end of the result

    return res.replace(" ", "")


def process_all(dir, results):
    for file, r in zip(os.listdir(dir), results):
        im = cv.LoadImage(os.path.join(dir, file))
        res = crack(im)

        if res == r:
            print file + ": " + res + " | " + r + " OK"
        else:
            print file + ": " + res + " | " + r + " NO"

        cv.WaitKey(0)


def getValidateCode():
    img = api.getValidateCodeImg()
    code = crack(img)

    while not api.checkCode(code):
        img = api.getValidateCodeImg()
        code = crack(img)
    return code


if __name__ == "__main__":

    # 下载图片准备训练
    # dir = "Isisn"
    # url = 'https://isisn.nsfc.gov.cn/egrantindex/funcindex/prjsearch-list'
    # pattern = "validatecode"
    # setup_Benchtest(dir, url, pattern, "utf-8")

    # 测试识别是否准确
    results = ["a845", "eene", "268g", "mwbm", "awf4", "5yfn", "68wa", "nya2", "fxxa", "mf6e", "xw45", "7fcm",
               "74yb", "cpny", "g4p7", "pdfw", "pnb4", "wmc6", "cdb5", "cep3"]
    process_all('Isisn-', results)


    # 测试抓取文件
    # domain = 'https://isisn.nsfc.gov.cn'
    # api = IsisnApi(domain)
    # years = ['1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011',
    #          '2012', '2013', '2014', '2015', '2016']
    #
    # for year in years:
    #     code = getValidateCode()
    #     total = api.retriveFirstPage(code, year)
    #
    #     if total >= 2:
    #         for page in range(2, total + 1):
    #             code = getValidateCode()
    #             api.retriveOtherPage(code, year, str(page))
