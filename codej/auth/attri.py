from collections import namedtuple

USER_PATTERN = r'^[A-ZА-ЯЁa-zа-яё][A-ZА-ЯЁa-zа-яё0-9\-_.]{2,15}$'
Group = namedtuple(
        'Group',
        ['pariah',
         'reader',
         'commentator_',
         'commentator',
         'commentatorpro',
         'blogger',
         'bloggerpro',
         'keeper',
         'keeperpro',
         'root'])
groups = Group(pariah="Изгои",
               reader="Читатели",
               commentator_="Комментаторы",
               commentator="Комментаторы+",
               commentatorpro="Комментаторы++",
               blogger="Писатели",
               bloggerpro="Писатели+",
               keeper="Хранители",
               keeperpro="Хранители+",
               root="Администраторы")
defaultg = groups.blogger
dgroups = (groups.reader, groups.commentator_, groups.commentator,
           groups.commentatorpro, groups.blogger, groups.bloggerpro)
kgroups = (groups.pariah, groups.reader, groups.commentator_,
           groups.commentator, groups.commentatorpro,
           groups.blogger, groups.bloggerpro)


async def weigh(group):
    if group == groups.pariah:         # Запрет на вход в сервис
        return 0
    if group == groups.reader:         # Чтение, Профиль, Лента
        return 30
    if group == groups.commentator_:   #+ Комментарии
        return 45
    if group == groups.commentator:    #+ Дизлайки, Приваты
        return 50
    if group == groups.commentatorpro: #+ Ссылки
        return 55
    if group == groups.blogger:        #+ Свой блог, Объявления
        return 100
    if group == groups.bloggerpro:     #+ Хостинг картинок
        return 150
    if group == groups.keeper:         #+ Смена группы другим
        return 200
    if group == groups.keeperpro:      #+ Литовка блогов других авторов
        return 250
    if group == groups.root:           # Без ограничений
        return 255
