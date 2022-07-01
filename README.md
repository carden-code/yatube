# Проект "Yatube"

- Социальная сеть для блогеров.

## Описание проекта:

- Проект **Yatube** - это полноценный сайт, где пользователи могут: 
зарегистрироваться, создавать посты, редактировать посты, комментировать посты, читать посты других авторов, подписываться на авторов.


# Установка
 **Как развернуть проект на локальной машине**:
 
Клонировать репозиторий и перейти в него в командной строке:


    git clone https://github.com/carden-code/yatube
    cd yatube
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

# Лицензия
Этот проект лицензируется в соответствии с лицензией MIT

![](https://miro.medium.com/max/156/1*A0rVKDO9tEFamc-Gqt7oEA.png "1")