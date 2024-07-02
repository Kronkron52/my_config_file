import os
import re
import subprocess
 
# Функция для чтения значения переменной из файла build.env
def read_env_variable(file_path, variable_name):
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith(variable_name):
                return line.split('=')[1].strip()
    return None
 
# Функция для извлечения полного имени образа
def get_image_name(image_value):
    # Извлекаем имя образа из значения переменной
    match = re.search(r'lds-docker\.artifacts\.tn\.tngrp\.ru/([^:]+:[^\s]+)', image_value)
    if match:
        return match.group(1)
    return None
 
# Функция для определения имени микросервиса из значения образа
def get_service_name(image_name):
    # Извлекаем имя микросервиса из полного имени образа и заменяем дефисы на подчеркивания
    match = re.search(r'lds-([a-zA-Z0-9-]+)', image_name)
    if match:
        return match.group(1).replace('-', '_')
    return None
 
# Функция для обновления значений в файле .env
def update_env_file(file_path, service_name, image_name):
    with open(file_path, 'r') as file:
        content = file.read()
 
    # Регулярное выражение для поиска значений образа
    pattern = re.compile(rf'{service_name.upper()}_IMAGE=[^\s]+')
 
    # Замена строки для соответствующего микросервиса
    new_content = pattern.sub(f'{service_name.upper()}_IMAGE={image_name}', content)
 
    if new_content == content:
        print(f"Паттерн не найден для замены: {pattern.pattern}")
    else:
        print(f"Паттерн найден и заменен: {pattern.pattern}")
 
    # Сохранение изменений в файл
    with open(file_path, 'w') as file:
        file.write(new_content)
 
    # Дополнительные выводы о замене
    matches = pattern.findall(content)
    for match in matches:
        print(f"Меняем: {match} на {service_name.upper()}_IMAGE={image_name}")
 
# Определение имени файла .env в зависимости от текущей папки
def get_env_file():
    current_dir = os.getcwd()
    if 'node1' in current_dir:
        return '/data/node1/env_file/.env.test1'
    elif 'node2' in current_dir:
        return '/data/node2/env_file/.env.test2'
    elif 'node3' in current_dir:
        return '/data/node3/env_file/.env.test3'
    else:
        raise ValueError("Неизвестная папка, не могу определить соответствующий .env файл")
 
# Путь к файлу build.env
env_file_path = 'build.env'
 
# Имя переменной в файле build.env
variable_name = 'CREATED_DOCKER_IMAGE'
 
# Чтение значения переменной из файла build.env
variable_value = read_env_variable(env_file_path, variable_name)
 
if variable_value:
    print(f"Значение переменной {variable_name}: {variable_value}")
    
    # Извлечение полного имени образа
    image_name = get_image_name(variable_value)
    
    if image_name:
        print(f"Извлеченное имя образа: {image_name}")
        
        # Определение имени микросервиса
        service_name = get_service_name(image_name)
        
        if service_name:
            print(f"Имя микросервиса: {service_name}")
            
            # Определение имени файла .env
            env_file = get_env_file()
            print(f"Используемый .env файл: {env_file}")
            
            # Обновление файла .env
            update_env_file(env_file, service_name, image_name)
            
            # Подготовка команды docker-compose
            docker_compose_cmd = [
                'docker-compose',
                '--env-file', env_file,
                '-f', 'docker-compose-lds.yml',
                'up', '-d'
            ]
            print(f"Команда docker-compose: {' '.join(docker_compose_cmd)}")
            
            # Запуск docker-compose up -d с использованием нужного .env файла
            subprocess.run(docker_compose_cmd)
        else:
            print("Имя микросервиса не найдено в значении образа")
    else:
        print("Имя образа не найдено в значении переменной CREATED_DOCKER_IMAGE")
else:
    print(f"Переменная {variable_name} не найдена в файле {env_file_path}")
