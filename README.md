# hw05_final

# Cоциальная сеть для публикации личных дневников.
Это сайт, на котором можно создать свою страницу, предварительно пройдя регистрацию. Если на нее зайти, то можно посмотреть все записи автора.
Пользователи смогут заходить на чужие страницы, подписываться на авторов и комментировать их записи.

# Настройка и запуск на ПК
Клонируем проект:

`git clone https://github.com/Enh404/hw05_final.git`

или

`git clone git@github.com:Enh404/hw05_final.git`

Переходим в папку с проектом:

`cd hw05_final`

Устанавливаем виртуальное окружение:

`python -m venv venv`

Активируем виртуальное окружение:

`source venv/Scripts/activate`

Для деактивации виртуального окружения выполним (после работы):

`deactivate`

Устанавливаем зависимости:

`python -m pip install --upgrade pip`
`pip install -r requirements.txt`

Применяем миграции:

`python yatube/manage.py makemigrations`
`python yatube/manage.py migrate`

Создаем супер пользователя:

`python yatube/manage.py createsuperuser`

При желании делаем коллекцию статики (часть статики уже загружена в репозиторий в виде исключения):

`python yatube/manage.py collectstatic`
