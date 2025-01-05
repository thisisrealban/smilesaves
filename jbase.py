import json
import os
import shutil

BASE_DIR = 'jbfiles/datastores'
BACKUP_DIR = 'jbfiles/backups'
AUTO_BACKUP_DIR = 'jbfiles/auto'

# Создание необходимых директорий
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(AUTO_BACKUP_DIR, exist_ok=True)


def _get_next_id(store):
    """Получить следующий ID для нового объекта."""
    file_path = os.path.join(BASE_DIR, f'{store}.json')
    if not os.path.exists(file_path):
        return 1
    with open(file_path, 'r') as f:
        data = json.load(f)
        if not data:
            return 1
        return max(obj['id'] for obj in data) + 1


def create(store, **kwargs):
    """Создать новый объект в указанном хранилище."""
    file_path = os.path.join(BASE_DIR, f'{store}.json')
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump([], f)  # Инициализация пустого списка

    obj_id = _get_next_id(store)
    new_object = {'id': obj_id, **kwargs}

    try:
        with open(file_path, 'r+') as f:
            data = json.load(f)
            data.append(new_object)
            f.seek(0)
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Ошибка при записи в файл {file_path}: {e}")
        return False

    return True


def backup_all():
    """Создать резервную копию всех данных в папке auto."""
    for filename in os.listdir(BASE_DIR):
        if filename.endswith('.json'):
            source_file = os.path.join(BASE_DIR, filename)
            backup_file = os.path.join(AUTO_BACKUP_DIR, filename)
            try:
                shutil.copy(source_file, backup_file)
                print(f"Резервная копия {filename} создана в {AUTO_BACKUP_DIR}.")
            except Exception as e:
                print(f"Ошибка при создании резервной копии {filename}: {e}")


def clear_all_files():
    """Очистить все файлы в директории datastores и backups."""
    for folder in [BASE_DIR, BACKUP_DIR, AUTO_BACKUP_DIR]:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Файл {file_path} удалён.")


def clear_backup_files():
    """Очистить файлы восстановления в директории backups и auto."""
    for folder in [BACKUP_DIR, AUTO_BACKUP_DIR]:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Файл восстановления {file_path} удалён.")


def mass_restore():
    """Массовое восстановление файлов из папки auto."""
    for filename in os.listdir(AUTO_BACKUP_DIR):
        if filename.endswith('.json'):
            auto_file = os.path.join(AUTO_BACKUP_DIR, filename)
            datastore_file = os.path.join(BASE_DIR, filename)

            # Восстановление или создание файла
            if os.path.exists(auto_file):
                with open(auto_file, 'r') as f:
                    data = json.load(f)

                # Восстановление файла в datastores
                with open(datastore_file, 'w') as f:
                    json.dump(data, f, indent=4)
                print(f"Файл {filename} восстановлен.")
            else:
                print(f"Файл {filename} не найден в auto.")

    # Удаление файлов в datastores, которые отсутствуют в auto
    for filename in os.listdir(BASE_DIR):
        if filename.endswith('.json'):
            if not os.path.exists(os.path.join(AUTO_BACKUP_DIR, filename)):
                os.remove(os.path.join(BASE_DIR, filename))
                print(f"Файл {filename} удалён из datastores, так как он отсутствует в auto.")


def get_object_from_id(store, obj_id):
    """Получить объект по ID."""
    file_path = os.path.join(BASE_DIR, f'{store}.json')
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r') as f:
        data = json.load(f)
        for obj in data:
            if obj['id'] == obj_id:
                return obj
    return None


def get_objects_from_args(store, **kwargs):
    """Получить объекты по заданным аргументам."""
    file_path = os.path.join(BASE_DIR, f'{store}.json')
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r') as f:
        data = json.load(f)
        results = [obj for obj in data if all(obj.get(k) == v for k, v in kwargs.items())]
    return results if results else None


def remove(store, obj_id):
    """Удалить объект по ID."""
    file_path = os.path.join(BASE_DIR, f'{store}.json')
    if not os.path.exists(file_path):
        return False
    with open(file_path, 'r+') as f:
        data = json.load(f)
        data = [obj for obj in data if obj['id'] != obj_id]
        f.seek(0)
        f.truncate()
        json.dump(data, f, indent=4)
    return True


def remove_store(store):
    """Удалить хранилище."""
    file_path = os.path.join(BASE_DIR, f'{store}.json')
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


def backup(store):
    """Создать резервную копию хранилища."""
    file_path = os.path.join(BASE_DIR, f'{store}.json')
    backup_path = os.path.join(BACKUP_DIR, f'{store}.json')
    if os.path.exists(file_path):
        shutil.copy(file_path, backup_path)
        return True
    return False


def restore(store):
    """Восстановить хранилище из резервной копии."""
    backup_path = os.path.join(BACKUP_DIR, f'{store}.json')
    file_path = os.path.join(BASE_DIR, f'{store}.json')
    if os.path.exists(backup_path):
        shutil.copy(backup_path, file_path)
        return True
    return False
