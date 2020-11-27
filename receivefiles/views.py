from django.shortcuts import render
from django.shortcuts import HttpResponse
 
import os
import time

HWFILES = 'static/files'
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

    if rdata == 'NoClass':
        return render(request, 'back.html', context={'ps': '你访问的班级好像并不存在'})
    if rdata == 'NoMission':
        return render(request, 'back.html', context={'ps': '你访问的任务好像并不存在'})

    rdata['fileType'] = FILETYPES[rdata['fileType']]['suffix'][0]
    return render(request, 'index.html', context=rdata)

def upload(request):
    obj = request.FILES.get('zy')

    try:
        on = obj.name
        # print(on)
    except AttributeError:
        return render(request, 'back.html', context={'ps': '宁还没有选择文件呢！'})
    fn = chack_new_mission()
    if fn == None:
        return render(request, 'back.html', context={'ps': '现在好像没有任务哦'})
    datas = no_names()
    if datas == 'NoClass':
        return render(request, 'back.html', context={'ps': '你访问的班级好像并不存在'})
    if datas == 'NoMission':
        return render(request, 'back.html', context={'ps': '你访问的任务好像并不存在'})

    for n in datas['names']:
        if on.find(n) == 0 and on[on.rfind('.'):] in FILETYPES[datas['fileType']]['suffix']:
            with open(f'{HWFILES}/{fn}', 'a', encoding='utf-8') as f:
                f.write(n + '\n')
            break
    else:
        return render(request, 'back.html', context={'ps': '上传失败！文件名/文件格式不正确！或是已经上传过了哦，请回到主页刷新看看未交名单里有没有你'})

    fdir = f'{HWFILES}/{fn[:-4]}'
    if not os.path.exists(fdir):
        os.mkdir(fdir)
    with open(os.path.join(fdir, on), 'wb') as f:
        for line in obj.chunks():
            f.write(line)

    return render(request, 'back.html', context={'ps': '上传成功'})

def admin_page(request):
    datas = no_names()
    if datas == 'NoClass':
        return render(request, 'back.html', context={'ps': '你访问的班级好像并不存在'})
    if datas == 'NoMission':
        rdata = {
            'zyType': '目前没有任务',
            'fileType': '目前没有任务',
        }
    else:
        rdata = {
            'zyType': datas['zyType'],
            'fileType': FILETYPES[datas['fileType']]['cnn'],
        }
    rdata['fileTypes'] = [{'type': t, 'cnn': FILETYPES[t]['cnn']} for t in FILETYPES]
    return render(request, 'admin.html', context=rdata)

def publish_homework(request):
    if chack_new_mission():
        return render(request, 'back.html', context={'ps': '目前有正在进行的作业'})
    try:
        ptime = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
        zy = request.POST['zy']
        ftype = request.POST['ftype']
        with open(f'{HWFILES}/{ptime}_{zy}.new', 'w', encoding='utf-8') as f:
            f.write(f'{zy}{H_ONSIGN}{ftype}\n')
        fdir = f'{HWFILES}/{ptime}_{zy}'
        if not os.path.exists(fdir):
            os.mkdir(fdir)
        return render(request, 'back.html', context={'ps': '作业发布成功'})
    except:
        return render(request, 'back.html', context={'ps': '你在干什么啊！'})
    # print(f'zy = {zy} / type(zy) = {type(zy)}')
    # print(f'ftype = {ftype} / type(ftype) = {type(ftype)}')
    # from django.contrib import messages
    # messages.success(request, f'发布成功：{zy} - {ftype}')

def close_homework(request):
    fn = chack_new_mission()
    if fn == None:
        return render(request, 'back.html', context={'ps': '现在没有进行中的作业'})
    os.rename(f'{HWFILES}/{fn}', f'{HWFILES}/{fn[:-4]}/{fn[:-4]+".log"}')
    return render(request, 'back.html', context={'ps': '旧的任务已经关闭了哦，现在你可以发布新任务了'})

# 配置异常页面
def page_400(request, e):
    return render(request, '404.html', status=400)

def page_403(request, e):
    return render(request, '404.html', status=403)

def page_404(request, e):
    return render(request, '404.html', status=404)

def page_500(request):
    return render(request, '404.html', status=500)

