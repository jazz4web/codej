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
               commentator_="Комметаторы",
               commentator="Комментаторы+",
               commentatorpro="Комментаторы++",
               blogger="Писатели",
               bloggerpro="Писатели+",
               keeper="Хранители",
               keeperpro="Хранители+",
               root="Администраторы")
defaultg = groups.blogger
kgroups = (groups.pariah, groups.reader, groups.commentator_,
           groups.commentator, groups.commentatorpro,
           groups.blogger, groups.bloggerpro)


async def weigh(group):
    if group == groups.pariah:
        return 0
    if group == groups.reader:
        return 30
    if group == groups.commentator_:
        return 45
    if group == groups.commentator:
        return 50
    if group == groups.commentatorpro:
        return 55
    if group == groups.blogger:
        return 100
    if group == groups.bloggerpro:
        return 150
    if group == groups.keeper:
        return 200
    if group == groups.keeperpro:
        return 250
    if group == groups.root:
        return 255
