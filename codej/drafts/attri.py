from collections import namedtuple

Status = namedtuple('Status', ['pub', 'priv', 'ffo', 'draft', 'cens'])
status = Status(
    pub="публичный",
    priv="сообществу",
    ffo="для друзей",
    draft="черновик",
    cens="закрыто")
