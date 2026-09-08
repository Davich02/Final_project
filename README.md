# Rental App — Final Project

Back-end приложение для системы аренды жилья на Django + DRF

# Стек
- Python 3.14
- Django 6.1
- Django REST Framework
- MySQL (production) / SQLite (development)

# Функционал
- Управление объявлениями (CRUD, статус активности)
- Поиск и фильтрация (цена, локация, комнаты, тип жилья)
- Аутентификация и роли (арендатор / арендодатель через Django Groups)
- Бронирование жилья
- Отзывы и рейтинги

# Запуск проекта

1. Клонировать репозиторий

2. Создать виртуальное окружение и установить зависимости:
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

3. Скопировать `.env.example` в `.env` и заполнить своими значениями

4. Применить миграции:
   python manage.py migrate

5. Создать суперпользователя:
   python manage.py createsuperuser

6. Запустить сервер:
   python manage.py runserver
  

# Структура проекта
- `apps/users` — пользователи и роли
- `apps/listings` — объявления и фото
- `apps/bookings` — бронирования
- `apps/reviews` — отзывы
- `apps/analytics` — история поиска и просмотров
- `config` — настройки Django-проекта