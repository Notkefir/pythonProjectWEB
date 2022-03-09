from requests import get, post, delete

#print(get('http://localhost:8080/api/news/1').json())

# print(post('http://localhost:8080/api/news',
#            json={'title': 'Заголовок',
#                  'content': 'Текст новости',
#                  'user_id': 1,
#                  'is_private': False}).json())

#print(delete('http://localhost:8080/api/news/1').json())

print(get('http://localhost:8080/api/v2/news/e').json())