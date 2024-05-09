from collections import namedtuple

USER_PATTERN = r'^[A-ZА-ЯЁa-zа-яё][A-ZА-ЯЁa-zа-яё0-9\-_.]{2,15}$'
Group = namedtuple('Group', ['pariah', 'root'])
groups = Group(pariah="Изгои", root="Администраторы")
