# -*- coding: utf-8 -*-
import os
import re
import time
from tool import Tools
from log import LogMgr

class GMP(Tools):
    """
    GMP证书的识别
    """
    def __init__(self, imgpath):
        Tools.__init__(self)
        self.imgpath = imgpath
        self.logmgr = LogMgr()

    def _recognize(self,datas, nums):
        """
        识别GMP证书, 程序的主逻辑
        """
        keylist = []
        datadict = dict()
      
        for (word, i) in zip(datas, range(0, nums)):
            '''
            循环读识别出的数据，然后根据judge_keywords函数是否提取到了关键信息；
            若提取到了，则保存到datadict中。
            若未提取到，list_result为空。有两种情况，
                1.这段信息不是我们所需要的。
                2.这段信息是上个关键字的值。
                然后执行else，进行更精确的判别。若是需归到上个字段，则循环递减，根据
                keylist[1],也就是list_reault[2]是否出现再上面的某个字段。若有则追加。
            '''
            list_result = self._judge_keywords(word['words'])
            if list_result != None:
                if list_result[0] in datadict and keylist[-1][0] != list_result[0]:
                    datadict[list_result[0]] += list_result[1]
                    flag = 1
                else:
                    datadict[list_result[0]] = list_result[1]
                    flag = 1
                #保存关键字段的信息，以及这段信息原本关键字段的信息
                keylist.append([list_result[0],list_result[2]])
            else:
                j = i
                while j > 0:
                    if not keylist:
                        break
                    #FIXMEED:逻辑问题  4/10 DONE
                    if re.match(r'\s[a-zA-Z]+', word['words']):
                        break
                    #提取"有效期至"与"发证日期"字段
                    if re.match(r'\d{4}|\d{2}', word['words']):
                        if len(word['words']) <= 4:
                            break
                        elif '/' in word['words']:
                            if keylist[-1][0] == '发证机关':
                                datadict['发证日期'] = word['words']
                                keylist.append(['杂', '杂'])
                                break
                            if '有效期至' in datadict:
                                if re.search(r'\d{4}|\d{2}', datadict['有效期至']):
                                    break
                            else:
                                datadict['有效期至'] = word['words']
                                break
                    if flag:
                        if keylist[-1][0] == '地址':
                            if i + 1 >= nums:
                                break
                            is_scope = self._judge_keywords(datas[i + 1]['words'])
                            if is_scope != None and is_scope[0] == '认证范围':
                                datadict['认证范围'] = word['words']
                                break
                        if keylist[-1][0] == '有效期至':
                            break
                        if keylist[-1][1] in datas[j]['words']:
                            datadict[keylist[-1][0]] += word['words']
                            break
                    j -= 1  
        return datadict

    def _judge_keywords(self, strword):
        '''
        判断关键字,若识别到关键字，返回一个包含关键字的list。
        $resultlist[0] -----要入库的关键字
        $resultlist[1] -----提取到内容
        $resultlist[2] -----需判断的信息中本来的关键字
        如:'证书编号:H12345',resultlist = ['证书编号', 'H12345', '证书编号']
           '证书号:H123', resultlist = ['证书编号', 'H123', '证书号']
        '''
        re_coname = re.compile(r"企业*名称*|企*业名*称")
        re_cernum = re.compile(r"证书*编号*|证*书编*号")
        re_addr = re.compile(r"地址")
        re_cerscope = re.compile(r"认证*范围*|认*证范*围")
        re_valid = re.compile(r"有效期至*|有效*期至")
        re_liceauth = re.compile(r"发证*机关*|发*证机*关")
        re_licedate = re.compile(r"发证*日期*|发*证日*期")
        re_abandon = re.compile(r"经审*查")

        if len(strword) >= 8: 
            index = 6
        else:
            index = len(strword)

        if(re.match(r'.+?(?:\:)', strword[:index])):
            if re_coname.search(strword[:index]):
                return ['企业名称_GMP', strword[re_coname.search(strword).span()[1]:], re_coname.search(strword).group()]
            elif re_cernum.search(strword[:index]):
                return ['证书编号' , strword[re_cernum.search(strword).span()[1] + 1:], re_cernum.search(strword).group()]
            elif re_addr.search(strword[:self._sort_index(strword)]):
                return ['地址' , strword[re_addr.search(strword).span()[1]:],re_addr.search(strword).group()]
            elif re_cerscope.search(strword[:index]):
                return ['认证范围' , strword[re_cerscope.search(strword).span()[1]:],re_cerscope.search(strword).group()]
            elif re_valid.search(strword[:index]):
                return ['有效期至' , strword[re_valid.search(strword).span()[1]:],re_valid.search(strword).group()]
            elif re_liceauth.search(strword[:index]):
                return ['发证机关' , strword[re_liceauth.search(strword).span()[1]:],re_liceauth.search(strword).group()]
            elif re_licedate.search(strword[:index]):
                return ['发证时间' , strword[re_licedate.search(strword).span()[1]:],re_licedate.search(strword).group()]
            else:
                return None
        else: 
            if re_coname.search(strword[:index]):
                return ['企业名称_GMP', strword[re_coname.search(strword).span()[1]:], re_coname.search(strword).group()]
            elif re_cernum.search(strword[:index]):
                return ['证书编号' , strword[re_cernum.search(strword).span()[1] + 1:], re_cernum.search(strword).group()]
            elif re_addr.search(strword[:self._sort_index(strword)]):
                return ['地址' , strword[re_addr.search(strword).span()[1]:],re_addr.search(strword).group()]
            elif re_cerscope.search(strword[:index]):
                return ['认证范围' , strword[re_cerscope.search(strword).span()[1]:],re_cerscope.search(strword).group()]
            elif re_valid.search(strword[:index]):
                return ['有效期至' , strword[re_valid.search(strword).span()[1]:],re_valid.search(strword).group()]
            elif re_liceauth.search(strword[:index]):
                return ['发证机关' , strword[re_liceauth.search(strword).span()[1]:],re_liceauth.search(strword).group()]
            elif re_licedate.search(strword[:index]):
                return ['发证时间' , strword[re_licedate.search(strword).span()[1]:],re_licedate.search(strword).group()]
            elif re_abandon.search(strword[:index]):
                return ['经审查', strword[re_abandon.search(strword).span()[1]:], re_abandon.search(strword).group()]
            else:
                return None

    def gmp_delploy(self, imgs, idcode):
        flag = 0
        tmp = ''
        #datas = []
        for file in imgs:
            file_name = file['imgpath'].split('/')[-1]
            id = file['imgpath'].split('/')[-2]
            if re.search(r'[\u4e00-\u9fa5]+', id):
                dragname = re.search(r'[\u4e00-\u9fa5]+', id).group()
            else:
                dragname = re.search(r'[\u4e00-\u9fa5]+', file_name).group()

            if dragname.find('(') > 0:
                dragname = dragname[:dragname.find('(')]

            if 'error_code' in file['imgjson']:
                self.logmgr.error(file['imgpath'] + " : Img Size Error!")
                continue
            
            datas = file['imgjson']['words_result']
            nums = file['imgjson']['words_result_num']
            
        if len(datas) > 0 and nums > 0:
            datadicttmp = self._recognize(datas, nums)
            datadict = dict()
            if '企业名称_GMP' in datadicttmp:
                if re.match('[:：]',datadicttmp['企业名称_GMP']):
                    datadict['企业名称_GMP'] = datadicttmp['企业名称_GMP'][1:]
                else:
                    datadict['企业名称_GMP'] = datadicttmp['企业名称_GMP']
            if '证书编号' in datadicttmp:
                if re.match('[:：]',datadicttmp['证书编号']):
                    datadict['证书编号'] = datadicttmp['证书编号'][1:]
                else:
                    datadict['证书编号'] = datadicttmp['证书编号']
            if '地址' in datadicttmp:
                if re.match('[:：]',datadicttmp['地址']):
                    datadict['地址'] = datadicttmp['地址'][1:]
                else:
                    datadict['地址'] = datadicttmp['地址']
            if '认证范围' in datadicttmp:
                if re.match('[:：]',datadicttmp['认证范围']):
                    datadict['认证范围'] = datadicttmp['认证范围'][1:]
                else:
                    datadict['认证范围'] = datadicttmp['认证范围']

            if '有效期至' in datadicttmp:
                if re.match('[:：]',datadicttmp['有效期至']):
                    datadict['有效期至'] = datadicttmp['有效期至'][1:]
                else:
                    datadict['有效期至'] = datadicttmp['有效期至']


            if '发证机关' in datadicttmp:
                if re.match('[:：]',datadicttmp['发证机关']):
                    datadict['发证机关'] = datadicttmp['发证机关'][1:]
                else:
                    datadict['发证机关'] = datadicttmp['发证机关']

            if '发证日期' in datadicttmp:
                if re.match('[:：]',datadicttmp['发证日期']):
                    datadict['发证日期'] = datadicttmp['发证日期'][1:]
                else:
                    datadict['发证日期'] = datadicttmp['发证日期']
            if '地址' not in datadict:
                datadict['地址'] = ''
            if '企业名称_GMP' not in datadict:
                datadict['企业名称_GMP'] = ''
            if re.search(r'.+公司.+',datadict['企业名称_GMP']):
                datadict['地址'] = datadict['地址']+datadict['企业名称_GMP'].split('公司')[1]
                datadict['企业名称_GMP'] = datadict['企业名称_GMP'].split('公司')[0]+'公司'

            if not datadict:
                nums = self._cleandata(datadict, datas, nums)
                return datadict
            return datadict
                #try:
                #    #self._data_to_db('GMPCERT', datadict)
                #    nums = self._cleandata(datadict, datas, nums)
                #except Exception as e:
                #    print('Error: ', e)
                #    #self._update_item('OCRWORKFILE','JOB_ID', jobid,'IS_TO_DB','F')
                #    self.logmgr.error(file[0] + '\\' + file_name + "insert error!! : " + str(e))
                #    nums = self._cleandata(datadict, datas, nums)
                #    return 'None'


    def gmp(self, datapath, id_code):
        flag = 0
        temp = ''
        for file in os.walk(datapath):
            jobdict = {}
            for file_name in file[2]:
                page = 1
                if 'GMP证书' in file_name:
                    imgname = file_name.split('.')[0]
                    curpath = file[0].split('data')[1]
                    index = imgname.rfind('_')
                    id = curpath[curpath.rfind('\\') + 1:]
                    if re.search(r'[\u4e00-\u9fa5]+', id):
                        dragname = re.search(r'[\u4e00-\u9fa5]+', id).group()
                    else:
                        dragname = re.search(r'[\u4e00-\u9fa5]+', file_name).group()

                    if dragname.find('(') > 0:
                        dragname = dragname[:dragname.find('(')]
                    #id_code = id[name_index_e - 1:]
                    datajson = self._load_json(file[0] + '\\' + file_name)
                    original_path = self.imgpath + '\\' + curpath + '\\' + imgname[:index - 2] + '.' + 'pdf'

                    #服务器
                    jobdict['SER_IP'] = '10.67.28.8'
                    #job id
                    jobdict['JOB_ID'] = self._generatemd5(file[0] + imgname)
                    jobid = jobdict['JOB_ID']
                    jobdict['SRC_FILE_NAME'] = imgname[:index - 2] + '.' + 'pdf'
                    jobdict['SRC_FILE_PATH'] = original_path
                    # jobdict['JOB_ID'] = self._generatemd5(jobdict[])
                    #原文件
                    jobdict['CUT_FILE_NAME'] = imgname[:index] + '.' + imgname[index:].split('_')[1]
                    #原路径
                    jobdict['CUT_FILE_PATH'] = 'G:\\IMG' + '\\' + curpath
                    #时间
                    jobdict['HANDLE_TIME'] = time.strftime("%Y-%m-%d %X", time.localtime())
                    #药品名
                    jobdict['DRUG_NAME'] = dragname
                    #影像件类型
                    jobdict['FILE_TYPE'] = 'GMP证书'
                    #同一套影像件识别码
                    jobdict['ID_CODE'] = id_code
                    #分公司
                    jobdict['SRC_CO'] = curpath.split('\\')[1]
                    #源文件相对路径
                    jobdict['FILE_REL_PATH'] = '\\' + imgname[:index] + '.' + imgname[index:].split('_')[1]
                    #文件服务器域名
                    jobdict['SYS_URL'] = '10.67.28.8'
                    #页数
                    jobdict['PAGE_NUM'] = page
                    #文件ocr解析识别状态 fk sysparams
                    jobdict['OCR_STATE'] = 'T'
                    #备注说明
                    jobdict['REMARK'] = ''
                    #创建用户
                    jobdict['ADD_USER'] = 'DevinChang'
                    #图片过大或者一些原因，没有识别出来就会有error_code字段
                    if 'error_code' in datajson:
                        jobdict['IS_TO_DB'] = 'F'
                        self.job.job_add(jobdict)
                        self.job.job_todb()
                        self.job.job_del()
                        self.logmgr.error(file[0] + '\\' + file_name + ": img size error!")
                        continue
                    #source_img_path = imgpaht_root_desktop + '\\' + curpath + '\\' + imgname[:index] + '.' + imgname[index:].split('_')[1]
                    #try:
                    #    kindict = hmc.kinds(source_img_path, datajson)
                    #except Exception as e:
                    #    logmgr.error(file[0] + '\\' + file_name + ':' + str(e))
                    #    continue
                    #print('Current processing: {}'.format(imgpaht_root_desktop + '\\' + curpath + 
                    #                        '\\' + imgname[:index] + 
                    #                        '.' + imgname[index:].split('_')[1], 
                    #                        file[0] + '\\' + file_name))
                    datas = datajson['words_result']
                    nums = datajson['words_result_num']
                    flag = 1

                    #中间文件
                    jobdict['MID_FILE_NAME'] = file_name
                    #中间文件路径
                    jobdict['MID_FILE_PATH'] = file[0]
                    #评分
                    jobdict['OCR_SCORE'] = int(self._getscore(datas, nums))
                    #影像件内容是否入库
                    if len(datas) > 0 and nums > 0:
                        jobdict['IS_TO_DB'] = 'T'
                    else:
                        jobdict['IS_TO_DB'] = 'F'
                    
                    #文件文本内容
                    jobdict['FILE_TEXT'] = self._middict(datas, self.codepath + '\\middata\\' + curpath, imgname)
                    ###############
                    temp = jobdict['FILE_TEXT']
                    #jobdict['JOB_ID'] = self._generatemd5(jobdict['FILE_TEXT'])
                    ###############
                    
                    try:
                        self.job.job_add(jobdict)
                    except Exception:
                        self.job.update_item('JOB_ID', jobid, 'IS_TO_DB', 'F')
                    self.job.job_todb()
                    self.job.job_del()
            if flag:
                if len(datas) > 0 and nums > 0:
                    datadicttmp = self._recognize(datas, nums)
                    datadict = dict()
                    if '企业名称_GMP' in datadicttmp:
                        if re.match('[:：]',datadicttmp['企业名称_GMP']):
                            datadict['企业名称_GMP'] = datadicttmp['企业名称_GMP'][1:]
                        else:
                            datadict['企业名称_GMP'] = datadicttmp['企业名称_GMP']
                    if '证书编号' in datadicttmp:
                        if re.match('[:：]',datadicttmp['证书编号']):
                            datadict['证书编号'] = datadicttmp['证书编号'][1:]
                        else:
                            datadict['证书编号'] = datadicttmp['证书编号']
                    if '地址' in datadicttmp:
                        if re.match('[:：]',datadicttmp['地址']):
                            datadict['地址'] = datadicttmp['地址'][1:]
                        else:
                            datadict['地址'] = datadicttmp['地址']
                    if '认证范围' in datadicttmp:
                        if re.match('[:：]',datadicttmp['认证范围']):
                            datadict['认证范围'] = datadicttmp['认证范围'][1:]
                        else:
                            datadict['认证范围'] = datadicttmp['认证范围']

                    if '有效期至' in datadicttmp:
                        if re.match('[:：]',datadicttmp['有效期至']):
                            datadict['有效期至'] = datadicttmp['有效期至'][1:]
                        else:
                            datadict['有效期至'] = datadicttmp['有效期至']


                    if '发证机关' in datadicttmp:
                        if re.match('[:：]',datadicttmp['发证机关']):
                            datadict['发证机关'] = datadicttmp['发证机关'][1:]
                        else:
                            datadict['发证机关'] = datadicttmp['发证机关']

                    if '发证日期' in datadicttmp:
                        if re.match('[:：]',datadicttmp['发证日期']):
                            datadict['发证日期'] = datadicttmp['发证日期'][1:]
                        else:
                            datadict['发证日期'] = datadicttmp['发证日期']

                    ######################################增加部分###########################################
                    datadict['ID_CODE']=id_code
                    datadict['REMARK']=''
                    datadict['ADD_USER']='shuai'
                    datadict['JOB_ID'] = self._generatemd5(temp)
                    if '地址' not in datadict:
                        datadict['地址'] = ''
                    if '企业名称_GMP' not in datadict:
                        datadict['企业名称_GMP'] = ''
                    if re.search(r'.+公司.+',datadict['企业名称_GMP']):
                        datadict['地址'] = datadict['地址']+datadict['企业名称_GMP'].split('公司')[1]
                        datadict['企业名称_GMP'] = datadict['企业名称_GMP'].split('公司')[0]+'公司'

                    ######################################增加部分###########################################
                    print(datadict)
                    if not datadict:
                        nums = self._cleandata(datadict, datas, nums)
                        continue
                    try:
                        self._data_to_db('GMPCERT', datadict)
                        nums = self._cleandata(datadict, datas, nums)
                    except Exception as e:
                        print('Error: ', e)
                        self._update_item('OCRWORKFILE','JOB_ID', jobid,'IS_TO_DB','F')
                        self.logmgr.error(file[0] + '\\' + file_name + "insert error!! : " + str(e))
                        nums = self._cleandata(datadict, datas, nums)
                        continue 



if __name__ == '__main__':
    datapath = os.path.dirname(__file__) + '\data'
    testpath = 'f:\DevinChang\Code\Python\ocr\data\国控盐城\西药\酮康唑乳膏A000060628'
    gmptest = GMP(datapath)
    gmptest.gmp(testpath, '12345')