# Проект "Yatube"

- Социальная сеть для блогеров.

## Описание проекта:

- Yatube это социальная сеть для публикации личных дневников.

- Это сайт, на котором можно создать свою страницу. Если на нее зайти, то можно посмотреть все записи автора.
    Пользователи смогут заходить на чужие страницы, подписываться на авторов и комментировать их записи.

## Технологии:

- Python 3.7
- Django 2.2.28

## Установка:
 **Как развернуть проект на локальной машине**:
 
Клонировать репозиторий и перейти в него в командной строке:


```
git clone https://github.com/carden-code/yatube
```

```
cd yatube
```

Cоздать и активировать виртуальное окружение:


```
python3 -m venv venv
```

```
source venv/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
cd yatube/
```

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
# Авторы:
- Вячеслав (GitHub: https://github.com/carden-code)

# Лицензия
Этот проект лицензируется в соответствии с лицензией MIT

![](https://miro.medium.com/max/156/1*A0rVKDO9tEFamc-Gqt7oEA.png "1")