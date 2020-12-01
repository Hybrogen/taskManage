from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import FileResponse
from django.utils.encoding import escape_uri_path

import os
import time
import json

import hashlib

def hon_code(data):
    code1 = hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()
    data = code1*233
    code2 = hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()
    return code2

HONFILES = 'static/files'
HONCLASS = 'static/class'
H_ONSIGN = '->honsplitsignal<-'
FILETYPES = {
    'pic': {
        'cnn': '图片',
        'suffix': ['.jpg', '.jpeg', '.png', '.PNG', '.JPG', '.JPEG'],
    },
    'doc': {
        'cnn': 'word文档',
        'suffix': ['.docx', '.doc'],
    },
    'zip': {
        'cnn': '压缩包',
        'suffix': ['.zip', '.7z', '.rar'],
    },
}
BACKC = {
        'ps': '你在干什么啊！',
        'buts': [
            {'name': '返回上一页', 'fun': 'javascript:history.back(-1)'},
            ]
        }
SUFFIXINFO = {
            'md': {'typen': 'Markdown文档', 'ctype': 'text/plain',},
            'zip': {'typen': '压缩文件', 'ctype': 'application/x-zip-compressed',},
            'rar': {'typen': '压缩文件', 'ctype': 'application/octet-stream'},
            '7z': {'typen': '压缩文件', 'ctype': 'text/plain',},
            'exe': {'typen': '应用程序', 'ctype': 'application/x-msdownload',},
            'ino': {'typen': 'Arduino源码', 'ctype': 'text/plain',},
            'tif': {'typen': '图片', 'ctype': 'image/tiff',},
            'png': {'typen': '图片', 'ctype': 'image/png',},
            'txt': {'typen': '文本文档', 'ctype': 'text/plain',},
            'docx': {'typen': 'Word文档', 'ctype': 'application/msword',},
            'py': {'typen': 'Python源码', 'ctype': 'text/plain',},
        }

def index(request):
    backc = dict(BACKC)

    backc['ps'] = '你访问的班级好像并不存在'
    return render(request, 'back.html', context=backc)

def publish_homework(request):
    taskInfo = {
            'className': '',
            'taskName': '',
            'fileType': '',
            'fileDir': '',
            }

    try:
        publishTime = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
        className = request.POST['className']
        taskName = request.POST['taskName']
        fileDir = f'{HONFILES}/{publishTime}_{className}_{taskName}'
        taskCode = hon_code(fileDir)

        taskInfo['className'] = className
        taskInfo['taskName'] = request.POST['taskName']
        taskInfo['fileType'] = request.POST['fileType']
        taskInfo['fileDir'] = fileDir

        with open(f'{HONFILES}/{taskCode}', 'w', encoding='utf-8') as f:
            f.write(json.dumps(taskInfo) + '\n')
        if not os.path.exists(fileDir):
            os.mkdir(fileDir)

        backc = dict(BACKC)
        backc['ps'] = '作业发布成功',
        backc['buts'][0]['name'] = '返回任务发布页'
        backc['buts'].append({'name': '查看任务页', 'fun': f"/task/{taskCode}"})
        return render(request, 'back.html', context=backc)
    except Exception as e:
        # print(e)
        backc = dict(BACKC)
        return render(request, 'back.html', context=backc)

def task_exists(tid):
    if not os.path.exists(HONFILES):
        os.mkdir(HONFILES)
        return False
    if not os.path.exists(f'{HONFILES}/{tid}'):
        return False
    return True

def get_info(tid, fild):
    with open(f'{HONFILES}/{tid}', encoding='utf-8') as f:
        _info = f.readline()
        if _info[-1] == '\n':
            _info = _info[:-1]
        taskInfo = json.loads(_info)
    return taskInfo[fild]

def close_task(request, taskId):
    backc = dict(BACKC)

    if not task_exists(taskId):
        backc['ps'] = '这个任务好像已经关闭了哦'
        return render(request, 'back.html', context=backc)

    os.rename(f'{HONFILES}/{taskId}', f'{get_info(taskId, "fileDir")}/任务信息.log')
    backc['ps'] = '旧的任务已经关闭了哦'
    return render(request, 'back.html', context=backc)

def suffix_info(fn, fild):
    return SUFFIXINFO[fn[fn.rfind('.'):]][fild]

def download_task(request, taskId, memberName=''):
    backc = dict(BACKC)

    if not task_exists(taskId):
        backc['ps'] = '已经关闭的任务是不能下载的'
        return render(request, 'back.html', context=backc)

    if memberName == '':
        zipName = get_info(taskId, 'taskName') + '.zip'
        fileDir = get_info(taskId, 'fileDir')
        os.system(f'zip -r {fileDir}/{zipName} {fileDir}')
    else:
        fileDir = get_info(taskId, 'fileDir')
        for fn in os.listdir(fileDir):
            if fn.find(memberName) == 0:
                zipName = fn
                break
        else:
            backc['ps'] = '这个成员好像还没有在此任务提交文件'
            return render(request, 'back.html', context=backc)

    zipFile = open(f'{fileDir}/{zipName}','rb')
    response = FileResponse(zipFile)
    # response['Content-Type'] = suffix_info(zipName, 'ctype')
    response['Content-Type'] = 'application/x-zip-compressed'
    response['Content-Disposition'] = f'attachment;filename={escape_uri_path(zipName)}'
    return response

def task_page(request, task_id):
    backc = dict(BACKC)

    try:
        order = hon_code(request.GET['order'])
        # print(request.GET['order'])
        if order == '87fa6649f00cd4ae700c3a4ebde5536c':
            return close_task(request, task_id)
        if order == '398c84a8351070ad3a1a1a98835adcff':
            try:
                memberName = request.GET['memberName']
                return download_task(request, task_id, memberName)
            except:
                pass
            return download_task(request, task_id)
        raise Exception('Unknown order')
    except Exception as e:
        # print(e)
        pass

    if not task_exists(task_id):
        backc['ps'] = '这个任务好像没有再进行中呢'
        return render(request, 'back.html', context=backc)

    className = get_info(task_id, 'className')
    classFile = f'{HONCLASS}/{className}.NameList'
    if not os.path.exists(classFile):
        backc['ps'] = '你的组织是真实存在的吗，联系一下管理员吧'
        return render(request, 'back.html', context=backc)

    with open(classFile, encoding='utf-8') as f:
        names = [i[:-1] if i[-1]=='\n' else i for i in f.readlines() if len(i) > 1]
    names = dict(zip(names, ['balck']*len(names)))
    notSubmitedNum = len(names)
    with open(f'{HONFILES}/{task_id}', encoding='utf-8') as f:
        for i in f.readlines()[1:]:
            if len(i) < 2:
                continue
            n = i[:-1] if i[-1]=='\n' else i
            if n in names:
                names[n] = '#73EB2D'
                notSubmitedNum -= 1
    names = [{'name': _, 'state': names[_]} for _ in names]
    # print(f'cn = {names}')
    taskData = {
            'taskCode': task_id,
            'fileType': FILETYPES[get_info(task_id, 'fileType')]['suffix'][0],
            'taskName': get_info(task_id, 'taskName'),
            'members': names,
            'nsn': notSubmitedNum,
            }
    return render(request, 'task.html', context=taskData)

def admin_page(request):
    backc = dict(BACKC)

    try:
        passwd = request.GET['passwd']
        # print(f'passwd = |{passwd}|')
        if hon_code(passwd) != 'db341bc7054f1312cdd6f6b324b9cd18':
            raise Exception('Wrong password')
    except:
        backc['ps'] = '不是辣个蓝人还想来这里，这都像话吗'
        return render(request, 'back.html', context=backc)

    # backc['ps'] = '恭喜主人登陆成功'
    # return render(request, 'back.html', context=backc)

    adminData = {
            'classes': ['',],
            'fileTypes': [{'type':'','cnn':'',},],
            'tasks': [{'className':'','taskName':'','fileType':'','url':'',},],
            }
    adminData['classes'] = [_[:_.rfind('.')] for _ in os.listdir(HONCLASS)]
    adminData['fileTypes'] = [{'type': _, 'cnn': FILETYPES[_]['cnn']} for _ in FILETYPES]
    adminData['tasks'] = []
    # print(os.listdir(HONFILES))
    for fn in os.listdir(HONFILES):
        if os.path.isdir(f'{HONFILES}/{fn}'):
            continue
        taskData = {
                'url': f'/task/{fn}',
                'className': get_info(fn, 'className'),
                'taskName': get_info(fn, 'taskName'),
                'fileType': FILETYPES[get_info(fn, 'fileType')]['cnn'],
                }
        adminData['tasks'].append(dict(taskData))
        # print('TEST')
    return render(request, 'admin.html', context=adminData)

def upload_file(request):
    backc = dict(BACKC)
    # backc['ps'] = f'获取的链接: {request.GET["taskCode"]}'
    # return render(request, 'back.html', context=backc)

    obj = request.FILES.get('submit_file')
    taskId = request.GET['taskCode']
    try:
        objName = obj.name
    except AttributeError:
        backc['ps'] = '宁还没有选择文件呢！'
        backc['buts'][0]['name'] = '返回任务页面'
        return render(request, 'back.html', context=backc)

    if not task_exists(taskId):
        backc['ps'] = '你访问的任务好像并不存在'
        return render(request, 'back.html', context=backc)

    with open(f'{HONFILES}/{taskId}', encoding='utf-8') as f:
        subName = [i[:-1] for i in f.readlines()[1:] if len(i) > 1]
    with open(f'{HONCLASS}/{get_info(taskId, "className")}.NameList', encoding='utf-8') as f:
        lefName = [i[:-1] for i in f.readlines() if len(i) > 1 and i[:-1] not in subName]
    fileType = get_info(taskId, 'fileType')

    for n in lefName:
        if objName.find(n) == 0 and objName[objName.rfind('.'):] in FILETYPES[fileType]['suffix']:
            with open(f'{HONFILES}/{taskId}', 'a', encoding='utf-8') as f:
                f.write(n + '\n')
            break
    else:
        backc['ps'] = '上传失败！文件名/文件格式不正确！或是已经上传过了哦，请回到主页刷新看看未交名单里有没有你'
        backc['buts'][0]['name'] = '返回任务页面'
        return render(request, 'back.html', context=backc)

    fileDir = get_info(taskId, 'fileDir')
    if not os.path.exists(fileDir):
        os.mkdir(fileDir)
    with open(os.path.join(fileDir, objName), 'wb') as f:
        for line in obj.chunks():
            f.write(line)

    backc['ps'] = '上传成功'
    backc['buts'][0]['name'] = '返回任务页面'
    return render(request, 'back.html', context=backc)

# 配置异常页面
def page_400(request, e):
    return render(request, '404.html', status=400)

def page_403(request, e):
    return render(request, '404.html', status=403)

def page_404(request, e):
    return render(request, '404.html', status=404)

def page_500(request):
    return render(request, '404.html', status=500)

