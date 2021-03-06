# -*- coding: utf-8 -*-

from config import *
from aip import AipOcr
import json
import csv
import os
#from wand.image import Image
#from introduction import format_introduction
#import introduction
#from baiduai import *
import re
from log import LogMgr
import base64
"""
__version__: 1.0
__application__: ocr识别说明书，药品许可证等证件
__author__: DevinChang
__date__: 2018/1/23
"""

"""
__version__: 1.1
__application__: ocr识别说明书，药品许可证等证件
__author__: DevinChang
__date__: 2018/1/27
__modify__: 1).增加提取药品说明书关键信息模块
            2).支持选择多个精度识别
            3).整合pdf转jpg模块
__bug__: 仅支持一些常见的说明书文件;提取的字段精度不高，时有混乱的字段。
"""






class MyOcr(object):
    """
    文字识别
    @app_id @api_key @secret_key 为百度ai平台上申请的值
    @typeid 精度的选择
            1--调用通用文字识别
            2--含位置信息的通用文字识别
            3--高精度的文字识别
            4--含位置信息的高精度文字识别
    """
    def __init__(self, typeid, app_id = APP_ID, api_key = API_KEY, secret_key = SECRET_KEY):
        self.client = AipOcr(app_id, api_key, secret_key)
        #self.client = AipOcr(appid[1], apikey[1], secretkey[1])
        self.typeid = typeid
        self.codepath = os.path.dirname(__file__)
        self.datapath = self.codepath + '\data'
        os.makedirs(self.datapath, exist_ok=True)
        self.log = LogMgr()
    

    def _get_file_content(self, filePath):
        """读取图片"""
        with open(filePath, 'rb') as fp:
            return fp.read()

    def _write_json_file(self, filepath, data):
        """写入json文件"""
        with open(filepath, 'w', encoding = 'utf-8') as fw:
            fw.write(json.dumps(data, ensure_ascii=False))
        
    def _list_custom(self, path):
        root = os.listdir(path)
        return os.listdir(path + '\\' + root[0]), path + '\\' + root[0]

    def ocr_deploy(self, rec_dict):
        files = rec_dict['files']
        #ocr所需的参数
        options = {}
        options["detect_direction"] = "true" 
        options["detect_language"] = "true"
        options["probability"] = "true"
        
        #dirlist = os.listdir(imgpath)
        #dirlist, root = self._list_custom(imgpath)
        for file in files:
            if re.search(r'进口注册证|GMP|说明书|药品再注册批件|营业执照|生产许可证|进口药品许可证|进口药品注册证', file['type']):
                for img in file['imgs']:
                    print('Current img: {}'.format(img['imgpath']))
                    try:
                        data = self.client.accurate(base64.b64decode(bytes(img['base64'], encoding='utf-8')), options)
                    except Exception as e:
                        print('Error: ', e)
                        self.log.error(img['imgpath'] + "Error! : " + str(e))
                        continue
                    img.update({"imgjson" : data})
        return rec_dict

    def _ocr(self, imgpath):
        """
        识别img文件下的图片
        @输出json数据，保存到data文件夹下
        """
        #imgpath = self.codepath + '\IMG'+'\国控天星'
        #FIXME:电脑环境不同，路径也不一样，切换环境的话要修改路径
        #imgpath = 'F:\IMG'
        #imgpath = r'D:\IMG'

        options = {}
        options["detect_direction"] = "true" 
        options["detect_language"] = "true"
        options["probability"] = "true"
        
        #FIXME:图片路径需改
        dirlist = os.listdir(imgpath)
        root = imgpath
        #dirlist, root = self._list_custom(imgpath)
        for file in os.walk(imgpath):
            for file_name in file[2]:
                if re.search(r'进口注册证|GMP|说明书|药品再注册批件|营业执照|生产许可证|进口药品许可证', file_name):
                    if '备案' in file_name:
                        continue
                    if os.path.isdir(file[0] + '\\' + file_name):
                        continue
                    if not re.match(r'[jJ][pP][gG]', file_name[-3:]):
                        continue
                    datafilepath = self.datapath + file[0].split('IMG')[1]
                    if not os.path.exists(datafilepath):
                        os.makedirs(datafilepath)
                    img = self._get_file_content(file[0] + '\\' + file_name)
                    if file_name[:-4].find('.'):
                        file_name = file_name[:-4].replace('.', '') + file_name[-4:]
                    try:
                        prefix,suffix = file_name.split('.')
                    except Exception as e:
                        print('split error: {}\ncurrent file: {}'.format(e, file[0] + '\\' + file_name))
                        self.log.error(file[0] + '\\' + file_name + " Error!! : " + str(e))
                        continue
                    #判断文件是否存在
                    if os.path.isfile((datafilepath +'\{}.json').format(prefix + '_' + suffix)):
                        continue
                    print('Current img: {}'.format(file[0] + '\\' + file_name))
                    #FIXME:
                    testdict = dict()
                    testdict['base64'] = str(base64.b64encode(img), 'utf-8')
                   #img_test = str.encode(testdict['base64'])
                    #self._write_json_file('F:\\IMG\\11A0015\\test.json', str(img))
                    try: 
                        if self.typeid == 1:
                            data = self.client.basicGeneral(img, options)
                        elif self.typeid == 2:
                            data = self.client.general(img, options)
                        elif self.typeid == 3:
                            data = self.client.basicAccurate(base64.b64decode(bytes(testdict['base64'], encoding='utf-8')), options)
                        elif self.typeid == 4:
                            data = self.client.accurate(img, options)
                    except Exception as e:
                        print('Error: ', e)
                        self.log.error(file[0] + '\\' + file_name + " Error!! : " + str(e))
                        continue
                    
                    self._write_json_file((datafilepath +'\{}.json').format(prefix + '_' + suffix), data)       


                
    def _write_dict(self):
        files = os.listdir(self.datapath)
        for file in files:
            format_data = introduction.introduction(self.datapath + '\\' + file)
            print(format_data)

    def pdf2img(self):
        """pdf转jpg"""
        file_dir = self.codepath + '/PDF/说明书/'
        save_dir = self.codepath + '/IMG/图片/'
        for files in os.walk(file_dir):
            for file_name in files[2]:
                file_path = file_dir
                [file_name_prefix, file_name_suffix] = file_name.split('.')
                file = file_dir + file_name
                with(Image(filename=file, resolution=300)) as img:
                    images = img.sequence
                    pages = len(images)
                    for i in range(pages):
                        images[i].type = 'truecolor'
                        save_name = save_dir + file_name_prefix + str(i) + '.jpg'
                        Image(images[i]).save(filename=save_name)
    
    def run(self, imgpath):
        """入口函数"""
        print('********Start Identify********')
        self._ocr(imgpath)
        print('********End********')
        #print('=================Format Data================')
        #self._write_dict()
        #print('======================End===================')


if __name__ == '__main__':
    ocr = MyOcr(3)
    ocr.run('F:\\IMG\\11A0015')    
    with open(r'F:\IMG\11A0015\testnet.json', 'rb') as f:
        json_data = json.loads(f.read())
    
    ocr.ocr_deploy(json_data)