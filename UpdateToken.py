# -*- coding: UTF-8 -*-
import requests as req
import json
import os
from base64 import b64encode
from nacl import encoding, public

app_num=os.getenv('APP_NUM')
if app_num == '':
    app_num='1'
gh_token=os.getenv('GH_TOKEN')
gh_repo=os.getenv('GH_REPO')
#ms_token=os.getenv('MS_TOKEN')
#client_id=os.getenv('CLIENT_ID')
#client_secret=os.getenv('CLIENT_SECRET')
Auth=r'token '+gh_token
geturl=r'https://api.github.com/repos/'+gh_repo+r'/actions/secrets/public-key'
#puturl=r'https://api.github.com/repos/'+gh_repo+r'/actions/secrets/MS_TOKEN'
key_id='wangziyingwen'

#公钥获取 
def getpublickey(Auth,geturl):
    headers={
            'Accept': 'application/vnd.github.v3+json','Authorization': Auth
            }
    for retry_ in range(4):
        html = req.get(geturl,headers=headers)
        if html.status_code < 300:
            print("公钥获取成功")
            break
        else:
            if retry_ == 3:
                print("公钥获取失败，请检查secret里 GH_TOKEN 格式与设置是否正确")
    jsontxt = json.loads(html.text)
    public_key = jsontxt['key']
    global key_id 
    key_id = jsontxt['key_id']
    return public_key

#微软refresh_token获取
def getmstoken(ms_token,appnum):
    headers={
            'Content-Type':'application/x-www-form-urlencoded'
            }
    data={
         'grant_type': 'refresh_token',
         'refresh_token': ms_token,
         'client_id':client_id,
         'client_secret':client_secret,
         'redirect_uri':'http://localhost:53682/'
         }
    for retry_ in range(4):
        html = req.post('https://login.microsoftonline.com/common/oauth2/v2.0/token',data=data,headers=headers)
        #json.dumps失败
        if html.status_code < 300:
            print(r'账号/应用 '+str(appnum)+' 的微软密钥获取成功')
            break
        else:
            if retry_ == 3:
                print(r'账号/应用 '+str(appnum)+' 的微软密钥获取失败'+'\n'+'请检查secret里 CLIENT_ID , CLIENT_SECRET , MS_TOKEN 格式与内容是否正确，然后重新设置')
    jsontxt = json.loads(html.text)
    refresh_token = jsontxt['refresh_token']
    access_token = jsontxt['access_token']
    return refresh_token
#是否要保存access，以降低微软token刷新率???

#token加密
def createsecret(public_key,secret_value):
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")

#token上传
def setsecret(encrypted_value,key_id,puturl,appnum):
    headers={
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': Auth
            }
    data={
         'encrypted_value': encrypted_value,
         'key_id': key_id
         }
    #data_str=r'{"encrypted_value":"'+encrypted_value+r'",'+r'"key_id":"'+key_id+r'"}'
    for retry_ in range(4):
        putstatus=req.put(puturl,headers=headers,data=json.dumps(data))
        if putstatus.status_code < 300:
            print(r'账号/应用 '+str(appnum)+' 的微软密钥上传成功')
            break
        else:
            if retry_ == 3:
                print(r'账号/应用 '+str(appnum)+' 的微软密钥上传失败，请检查secret里 GH_TOKEN 格式与设置是否正确')        
    return putstatus
    
#调用 
for a in range(1, int(app_num)+1):
    client_id=os.getenv('CLIENT_ID_'+str(a))
    client_secret=os.getenv('CLIENT_SECRET_'+str(a))
    ms_token=os.getenv('MS_TOKEN_'+str(a))
    if a == 1:
        puturl=r'https://api.github.com/repos/'+gh_repo+r'/actions/secrets/MS_TOKEN'
    else:
        puturl=r'https://api.github.com/repos/'+gh_repo+r'/actions/secrets/MS_TOKEN_'+str(a)
    encrypted_value=createsecret(getpublickey(Auth,geturl),getmstoken(ms_token,a))
    setsecret(encrypted_value,key_id,puturl,a)
