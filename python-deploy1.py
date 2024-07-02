import os
import re
 
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
    # Извлекаем имя микросервиса из полного имени образа
    match = re.search(r'lds-([a-zA-Z0-9-]+)', image_name)
    if match:
        return match.group(0)
    return None
 
# Функция для обновления значений в файле docker-compose.yml
def update_docker_compose(file_path, service_name, image_name):
    with open(file_path, 'r') as file:
        content = file.read()
 
    # Регулярное выражение для поиска значений image: для конкретного сервиса
    pattern = re.compile(rf'image:\s*\${{NEXUS_REGISTRY}}/{service_name}:[^\s]+')
 
    # Замена строки image: для соответствующего микросервиса
    new_content = pattern.sub(f'image: ${{NEXUS_REGISTRY}}/{image_name}', content)
 
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
        print(f"Меняем: {match} на image: ${{NEXUS_REGISTRY}}/{image_name}")
 
# Путь к файлу build.env
env_file_path = 'build.env'
 
# Имя переменной в файле build.env
variable_name = 'CREATED_DOCKER_IMAGE'
 
# Путь к файлу docker-compose.yml
docker_compose_file_path = 'docker-compose-lds.yml'
 
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
            
            # Обновление файла docker-compose.yml
            update_docker_compose(docker_compose_file_path, service_name, image_name)
        else:
            print("Имя микросервиса не найдено в значении образа")
    else:
        print("Имя образа не найдено в значении переменной CREATED_DOCKER_IMAGE")
else:
    print(f"Переменная {variable_name} не найдена в файле {env_file_path}")
