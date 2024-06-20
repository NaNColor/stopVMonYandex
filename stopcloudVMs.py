import requests
import sys
import argparse
import datetime

header = {}

def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token')
    parser.add_argument('-c', '--cloud')
    parser.add_argument('-f', '--folder')
    parser.add_argument('-i', '--instance')
 
    return parser


def getJsonAPI(URL, headers, params=None):
    # Делаем запрос
    response = None
    try:
        if not params:
            response = requests.get(URL, headers=headers)
        else:
            response = requests.get(URL, headers=headers, params=params)
    except Exception as e:
        print(e)
        return None
    return response.json()

def getIDsfromNextPageYandex(field, URL, nextPageToken, params = {}):
    # Получаем следующую страницу ответа и собираем данные
    list = []
    params['pageToken'] = nextPageToken
    data = getJsonAPI(URL, header, params)
    for item in data[field]:
        list.append(item['id'])
    while "nextPageToken" in data:
        params['pageToken'] = nextPageToken
        data = getJsonAPI(URL, header, params)
        for item in data[field]:
            list.append(item['id'])
    return list

def getYandexClouds():
    # Находим все облака
    URL = "https://resource-manager.api.cloud.yandex.net/resource-manager/v1/clouds"
    clouds = []
    data = getJsonAPI(URL, header)
    for item in data['clouds']:
        clouds.append(item['id'])
    if "nextPageToken" in data:
        clouds.extend("clouds", getIDsfromNextPageYandex(URL, data['nextPageToken']))
    return clouds

def getYandexFolders(cloudId):
    # находим все каталоги облака
    params = {
        'cloudId': cloudId
    }
    URL = "https://resource-manager.api.cloud.yandex.net/resource-manager/v1/folders"
    folders = []
    data = getJsonAPI(URL, header, params)
    if not data:
        return None
    for item in data['folders']:
        folders.append(item['id'])
    if "nextPageToken" in data:
        folders.extend("folders", getIDsfromNextPageYandex(URL, data['nextPageToken'], params))
    return folders


def getYandexInstances(folderId):
    # Находим все ВМ каталога
    params = {
        'folderId': folderId
    }
    URL = "https://compute.api.cloud.yandex.net/compute/v1/instances"
    instances = []
    data = getJsonAPI(URL, header, params)
    if not data:
        return None
    for item in data['instances']:
        instances.append(item)
    # Если есть следующая страница, то ищем информацию из нее
    if "nextPageToken" in data:
        params['pageToken'] = data['nextPageToken']    
        while "nextPageToken" in data:
            params['pageToken'] = data['nextPageToken']
            data = getJsonAPI(URL, header, params)
            for item in data['instances']:
                instances.append(item)
    return instances


def getYandexInstance(instanceId):
    # информация о ВМ
    URL = f"https://compute.api.cloud.yandex.net/compute/v1/instances/{instanceId}"
    data = getJsonAPI(URL, header)
    if not data:
        return None
    return data

def stopYandexVM(instanceId):
    # Остановить ВМ
    URL = f"https://compute.api.cloud.yandex.net/compute/v1/instances/{instanceId}:stop"
    try:
        response = requests.post(URL, headers=header)
    except Exception as e:
        print(e)
        return None
    return response.json()


def main():
    parser = createParser()
    args = parser.parse_args(sys.argv[1:])
    if (not args.token) or (not args.cloud and args.folder) or (args.instance and not args.folder):
        print("Вы ввели не правильные ключи. Пожалуйста, ознакомтесь с файлом README.md.")
        return
    
    global header
    header = {
        'Authorization': f"Bearer {args.token}"
    }
    instances = []
    try:
        if not args.cloud:
            clouds = getYandexClouds()
            if not clouds:
                print("Cloud error")
                return
            for cloud in clouds:
                folders = getYandexFolders(cloud)
                if not folders:
                    print("Folder error")
                    return
                for folder in folders:
                    i = getYandexInstances(folder)
                    if not i:
                        print("Instance error")
                        return
                    instances.extend(i)
        elif not args.folder:
            folders = getYandexFolders(args.cloud)
            if not folders:
                print("Folder error")
                return
            for folder in folders:
                i = getYandexInstances(folder)
                if not i:
                    print("Instance error")
                    return
                instances.extend(i)
        elif not args.instance:
            i = getYandexInstances(args.folder)
            if not i:
                print("Instance error")
                return
            instances.extend(i)
        else:
            i = getYandexInstance(args.instance)
            if not i:
                print("Instance error")
                return
            instances.append(i)
    except Exception as e:
        print("Error", e)
        return
    today = datetime.datetime.now().date()
    for item in instances:
        if item['status'] != 'RUNNING':
            continue

        if "labels" in item:
            if "expired_date" in item['labels']:
                #d.m.y=12.06.2024
                try:
                    expired_date = datetime.datetime.strptime(item['labels']['expired_date'], "%d.%m.%Y").date()
                except Exception:
                    print(f"ВМ {item['id']} имеет неправильный формат тега.")
                    continue
                if today > expired_date:
                    responce = stopYandexVM(item['id'])
                    if "error" in responce:
                        print(f"Ошибка при выключении ВМ {responce['id']}. {responce['error']['code']} {responce['error']['message']}")
                    else:
                        print(f"ВМ {responce['id']} выключена.")



if __name__ == '__main__':
    main()