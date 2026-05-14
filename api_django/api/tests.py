import json

import requests

# # answer = requests.get("http://127.0.0.1:8000/api/v1/user/1/") #Обычный гет запрос
# # answer = requests.post("http://127.0.0.1:8000/api/v1/auth/users/", {"username":"thirduser","password":"asdasdaweqwedsfa321","email":"321@mail.ru"}) #Пост запрос на добавление юзера
# answer = requests.post("http://127.0.0.1:8000/auth/token/login/", {"username":"thirduser","password":"asdasdaweqwedsfa321"}) #Пост запрос на авторизацию возвращает токен
#
# # Схема для пост и пут запросов. Ссылка для пост заканчивается таблицей т.е. user/ , а для пут запроса строкой таблицы т.е. user/2/
# url = 'http://127.0.0.1:8000/api/v1/user/'
# param = {"title": "12345    "}
# headers = {"Authorization": "Token 5147798c182fc8b9bd0f62b2e5fb08251d467b5a"}
# # answer = requests.post(url, json=param, headers=headers)
# print(answer.json())
# my_list = [1, 2, 3, 4, 5]
# for i in my_list[:-1]:
#     print(i)