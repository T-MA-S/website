from requests import get, post

print(post('http://127.0.0.1:5000/api/users',
           json={'name': 'Тест',
                 'surname': 'Тестовый',
                 'email': 'test@test.com',
                 'password': 'testpassword',
                 'is_admin': 1}).json())

print(post('http://127.0.0.1:5000/api/goods',
           json={'name': 'Процессор',
                 'producer': 'Intel',
                 'category_id': '1',
                 'info': 'good',
                 'price': '150'}).json())
