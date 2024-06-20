## Описание
Код, который останавливает ВМ в YandexCloud если у них есть label expired_date, значение даты которого истекло. При запуске без дополнительных ключей `-c`, `-f` и `-i` сканирует все instances аккаунта во всех облаках и каталогах, после чего останавливает все ВМ, подходящих под условие. 
## Необходимые пакеты
Программа использует библиотеку `requests`, которая не является стандартной, поэтому ее предварительно необходимо установить:
```
pip install requests
```
## Запуск
Для запуска программы необходимо в качестве аргумента передать [IAM-token](https://yandex.cloud/ru/docs/iam/operations/iam-token/create#api_1) для аккаунта Yandex Cloud. Также можно указать ID облака, каталога и определенного экземпляра ВМ.
```
python stopcloudVMs.py -t <IAM-token> [-c <cloudId> [-f <folderId> [-i <instanceId>]]]
```
После выполнения программа выводит instanceId каждой ВМ, которая была выключена.
## Пример запуска
<center>
  
![image](https://github.com/NaNColor/stopVMonYandex/assets/55803598/fe3acb5a-c439-4d00-bba0-a02d8ee66880)

</center>
