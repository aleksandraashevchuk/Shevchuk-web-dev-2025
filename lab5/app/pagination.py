class Pagination:
    def __init__(self, page, per_page, total, items):
        self.page = page # текущая страница
        self.per_page = per_page # на странице
        self.total = total # всего элементов
        self.items = items # элементы на текущей

    @property
    def pages(self): # всего страниц (с округлением вверх, как гарантия, что будет одна страница минимум)
        return max(1, (self.total + self.per_page - 1) // self.per_page)

    @property
    def has_prev(self): # есть ли предыдущая страница
        return self.page > 1

    @property
    def has_next(self): # есть ли следующая страница
        return self.page < self.pages

    @property
    def prev_num(self): # номер предыдущей страницы
        return self.page - 1 if self.has_prev else None

    @property
    def next_num(self): # номер следующей страницы
        return self.page + 1 if self.has_next else None
    # генерация номеров страниц 1, 2, None, 6, 7, 8, 9, 10, 11, 12, 13, None, 19, 20
    # left_edge: сколько страниц показывать в начале
    # left_current: сколько страниц показывать слева от текущей
    # right_current: сколько страниц показывать справа от текущей
    # right_edge: сколько страниц показывать в конце
    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if (num <= left_edge or
                (num > self.page - left_current - 1 and num < self.page + right_current) or
                num > self.pages - right_edge):
                if last + 1 != num:
                    yield None
                yield num
                last = num