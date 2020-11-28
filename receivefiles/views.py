from django.shortcuts import render
from django.shortcuts import HttpResponse
 
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

def chack_new_mission():
    for f in os.listdir(HWFILES):
        if '.new' in f:
            return f
    return None

def no_names():
    if not os.path.exists(HWFILES):
        os.mkdir(HWFILES)

    if not os.path.exists('static/18物二.NameList'):
        return 'NoClass'
    subNames = chack_new_mission()
    if subNames == None:
        return 'NoMission'

    with open('static/18物二.NameList', encoding='utf-8') as f:
        allNames = [i[:-1] for i in f.readlines() if len(i) > 1]
    with open(f'{HWFILES}/{subNames}', encoding='utf-8') as f:
        zyType,fileType = f.readline()[:-1].split(H_ONSIGN)
        subNames = [i[:-1] for i in f.readlines() if len(i) > 1]
    noNames = [n for n in allNames if n not in subNames]

    rdata = {
        'names': noNames,
        'zyType': zyType,
        'fileType': fileType,
    }
    return rdata

def index(request):
    rdata = no_names()
    backc = dict(BACKC)

    if rdata == 'NoClass':
        backc['ps'] = '你访问的班级好像并不存在'
        return render(request, 'back.html', context=backc)
    if rdata == 'NoMission':
        backc['ps'] = '你访问的任务好像并不存在'
        return render(request, 'back.html', context=backc)

    rdata['fileType'] = FILETYPES[rdata['fileType']]['suffix'][0]
    return render(request, 'index.html', context=rdata)

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

def close_homework(request):
    fn = chack_new_mission()
    backc = dict(BACKC)
    if fn == None:
        backc['ps'] = '现在没有进行中的作业'
        return render(request, 'back.html', context=backc)
    os.rename(f'{HWFILES}/{fn}', f'{HWFILES}/{fn[:-4]}/{fn[:-4]+".log"}')
    backc['ps'] = '旧的任务已经关闭了哦，现在你可以发布新任务了'
    return render(request, 'back.html', context=backc)

# --------------------------------------------------------------------------- #

def task_exists(tid):
    if not os.path.exists(HONFILES):
        os.mkdir(HONFILES)
        return False
    if not os.path.exists(f'{HONFILES}/{tid}'):
        return False
    return True

def get_info(tid, fild):
    with open(f'{HONFILES}/{tid}', encoding='utf-8') as f:
        taskInfo = json.loads(f.readline()[:-1])
    return taskInfo[fild]

def task_page(request, task_id):
    backc = dict(BACKC)

    if not task_exists(task_id):
        backc['ps'] = '现在没有进行中的任务'
        return render(request, 'back.html', context=backc)

    className = get_info(task_id, 'className')
    classFile = f'{HONCLASS}/{className}.NameList'
    if not os.path.exists(classFile):
        backc['ps'] = '你的组织是真实存在的吗，联系一下管理员吧'
        return render(request, 'back.html', context=backc)

    with open(classFile, encoding='utf-8') as f:
        names = [i[:-1] for i in f.readlines() if len(i) > 1]
    names = dict(zip(names, ['balck']*len(names)))
    with open(f'{HONFILES}/{task_id}', encoding='utf-8') as f:
        for i in f.readlines()[1:]:
            if len(i) < 2:
                continue
            if i[:-1] in names:
                names[i[:-1]] = 'green'
    names = [{'name': _, 'state': names[_]} for _ in names]
    # print(f'cn = {names}')
    taskData = {
            'taskCode': task_id,
            'fileType': FILETYPES[get_info(task_id, 'fileType')]['suffix'][0],
            'taskName': get_info(task_id, 'taskName'),
            'members': names,
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
            'tasks': [{'className':'','taskName':'','fileType':'',},],
            }
    adminData['classes'] = [_[:_.rfind('.')] for _ in os.listdir(HONCLASS)]
    adminData['fileTypes'] = [{'type': _, 'cnn': FILETYPES[_]['cnn']} for _ in FILETYPES]
    adminData['tasks'] = []
    for fn in os.listdir(HONFILES):
        dfn = f'{HONFILES}/{fn}'
        if os.path.isdir(dfn):
            continue
        with open(dfn, encoding='utf-8') as f:
            adminData['tasks'].append(json.loads(f.readline()[:-1]))
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

