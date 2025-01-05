import json
import hashlib
import os
import time

# Файл для хранения пользователей
USERS_FILE = 'users.json'


# Функция для загрузки пользователей из файла
def load_users():
    if not os.path.exists(USERS_FILE):
        return []  # Если файл не существует, возвращаем пустой список
    with open(USERS_FILE, 'r', encoding='utf-8') as file:
        return json.load(file)


# Функция для сохранения пользователей в файл
def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as file:
        json.dump(users, file, indent=4)


# Функция для создания пользователя
def create_user(username, display_name, password, email, cash, money, role):
    users = load_users()

    # Проверка уникальности username и email
    if any(user['username'] == username for user in users):
        return None
    if any(user['email'] == email for user in users):
        return None

    # Генерация ID
    user_id = max([user['id'] for user in users], default=0) + 1
    password_hash = hashlib.sha256(password.encode()).hexdigest()  # Хеширование пароля

    new_user = {
        'id': user_id,
        'username': username,
        'display_name': display_name,
        'password_hash': password_hash,
        'email': email,
        'cash': cash,
        'money': money,
        'role': role,
        "verifyed": False,
        "date_creation": time.time()
    }

    users.append(new_user)
    save_users(users)
    return new_user


# Функция для изменения пользователя
def update_user(user_id, **kwargs):
    users = load_users()
    for user in users:
        if user['id'] == user_id:
            for key, value in kwargs.items():
                if key in user:
                    user[key] = value
            save_users(users)
            return user
    return None


# Функция для удаления пользователя
def delete_user(user_id):
    users = load_users()
    new_users = [user for user in users if user['id'] != user_id]
    if len(users) == len(new_users):
        return False  # Не удалось удалить, пользователь не найден
    save_users(new_users)
    return True  # Успешно удален


# Функция для точного поиска по ID
def find_user_by_id(user_id):
    users = load_users()
    for user in users:
        if user['id'] == user_id:
            return user
    return None


# Функция для точного поиска по username
def find_user_by_username(username):
    users = load_users()
    for user in users:
        if user['username'] == username:
            return user
    return None


# Функция для приблизительного поиска
def approximate_search(query):
    users = load_users()
    results = []
    for user in users:
        if (str(user['id']) == query or
                user['username'].lower() == query.lower() or
                user['display_name'].lower() == query.lower()):
            results.append(user)
    return results


# Функция для проверки username и password
def verify_user(username, password):
    users = load_users()
    for user in users:
        if user['username'] == username:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if password_hash == user['password_hash']:
                return True  # Успешная проверка
    return False  # Неправильный username или пароль


# Пример использования
if __name__ == "__main__":
    # Создание пользователя
    user = create_user('johndoe', 'John Doe', 'securepassword', 'john@example.com', 100, 200, 1)
    print("Создан пользователь:", user)

    # Попытка создать пользователя с существующим username
    duplicate_user = create_user('johndoe', 'John Doe', 'anotherpassword', 'john2@example.com', 100, 200, 1)
    print("Попытка создать дубликат:", duplicate_user)

    # Проверка пользователя
    is_verified = verify_user('johndoe', 'securepassword')
    print("Пользователь проверен:", is_verified)

    # Изменение пользователя
    updated_user = update_user(user['id'], cash=150)
    print("Обновленный пользователь:", updated_user)

    # Поиск пользователя
    found_user = find_user_by_id(user['id'])
    print("Найден пользователь по ID:", found_user)

    # Приблизительный поиск
    search_results = approximate_search('johndoe')
    print("Результаты приблизительного поиска:", search_results)

    # Удаление пользователя
    deletion_result = delete_user(user['id'])
    print("Пользователь удален:", deletion_result)
