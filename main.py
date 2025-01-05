import asyncio

import flet as ft
import threading
import random
import time
import users
import re
import jbase as jb

def is_valid_email(email):
    email_pattern = r'^[^@]+@[^@]+\.[a-z]{2,}$'
    return re.match(email_pattern, email) is not None

host = "Blazer"


class SmileCoinGenerator(threading.Thread):
    def __init__(self, min_value=1.00, max_value=999.99, min_amplitude=-0.2, max_amplitude=0.2):
        super().__init__()
        self.current_value = 1.00
        self.min_value = min_value
        self.max_value = max_value
        self.min_amplitude = min_amplitude
        self.max_amplitude = max_amplitude
        self.lock = threading.Lock()

    def run(self):
        while True:
            change = random.uniform(self.min_amplitude, self.max_amplitude)
            with self.lock:
                self.current_value += change
                self.current_value = max(self.min_value, min(self.current_value, self.max_value))

            print(f"Сгенерированное значение: {self.current_value:.2f}")
            time.sleep(5)

    def get_current_value(self):
        with self.lock:
            return self.current_value

    def get_min_amplitude(self):
        with self.lock:
            return self.min_amplitude

    def get_max_amplitude(self):
        with self.lock:
            return self.max_amplitude

    def get_min_value(self):
        with self.lock:
            return self.min_value

    def get_max_value(self):
        with self.lock:
            return self.max_value

    def set_current_value(self, new_value):
        with self.lock:
            self.current_value = new_value

    def set_min_value(self, new_min):
        with self.lock:
            self.min_value = new_min

    def set_max_value(self, new_max):
        with self.lock:
            self.max_value = new_max

    def set_min_amplitude(self, new_min_amplitude):
        with self.lock:
            self.min_amplitude = new_min_amplitude

    def set_max_amplitude(self, new_max_amplitude):
        with self.lock:
            self.max_amplitude = new_max_amplitude


smile_coin_generator = SmileCoinGenerator()
smile_coin_generator.start()



def main(page: ft.Page):
    page.title = "Смайл Сейвы"
    page.theme = ft.Theme(#color_scheme_seed="#FFCC00",
                          font_family="Medium")
    page.fonts = {
        "HeadlineBold": "/fonts/HeadlineBold.ttf",
        "Bold": "/fonts/Bold.ttf",
        "Medium": "/fonts/Medium.ttf",
        "Regular": "/fonts/Regular.ttf",
    }
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    def nav_changed(e):
        if page.navigation_bar.selected_index == 0:
            page.route = "/home"
        elif  page.navigation_bar.selected_index == 1:
            page.route = "/chat"
        elif  page.navigation_bar.selected_index == 2:
            page.route = "/my"
        #elif  page.navigation_bar.selected_index == 3:
        #    page.route = "/settings"
        page.update()

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Главная"),
            ft.NavigationBarDestination(icon=ft.Icons.CHAT_BUBBLE, label="Общение"),
            ft.NavigationBarDestination(icon=ft.Icons.ACCOUNT_CIRCLE, label="Моё"),
            #ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Настройки"),
        ],
        on_change=nav_changed,
        bgcolor=ft.Colors.ON_INVERSE_SURFACE
    )
    page.appbar = ft.AppBar(
        title=ft.Row(controls=[ft.Image(src="/icons/MiniLogotype.png", height=24),
                               ft.Text(value="Смайл Сейвы", font_family="HeadlineBold",
                                       color=ft.Colors.ON_SURFACE, size=20),],
                     spacing=10),
        center_title=False,
        bgcolor=ft.Colors.ON_INVERSE_SURFACE,

    )

    def home_page():
        def update_course(e):
            course_text.value = (f"{smile_coin_generator.get_current_value():.2f}".replace('.', ',') + " ₽")
            page.update()

        def commit_course(e):
            if len(new_course.value) != 0:
                new_course.error_text = None
                new_course.update()
                smile_coin_generator.set_current_value(float(new_course.value))
                update_course(None)
                page.close(us)
            else:
                new_course.error_text = "Значение не может быть пустым"
                new_course.update()

        def commit_amp(e):
            if len(minamp.value) != 0:
                minamp.error_text = None
                minamp.update()
                if len(maxamp.value) != 0:
                    maxamp.error_text = None
                    maxamp.update()
                    smile_coin_generator.set_max_amplitude(float(maxamp.value))
                    smile_coin_generator.set_min_amplitude(float(minamp.value))
                    update_course(None)
                    page.close(amp)
                else:
                    maxamp.error_text = "Значение не может быть пустым"
                    maxamp.update()
            else:
                minamp.error_text = "Значение не может быть пустым"
                minamp.update()

        def commit_vals(e):
            if len(minval.value) != 0:
                minval.error_text = None
                minval.update()
                if len(maxval.value) != 0:
                    maxval.error_text = None
                    maxval.update()
                    smile_coin_generator.set_max_value(float(maxval.value))
                    smile_coin_generator.set_min_value(float(minval.value))
                    update_course(None)
                    page.close(vals)
                else:
                    maxval.error_text = "Значение не может быть пустым"
                    maxval.update()
            else:
                minval.error_text = "Значение не может быть пустым"
                minval.update()

        def commit_buy(e):
            try:
                if len(to_buy.value) > 0:
                    user = users.find_user_by_username(page.client_storage.get("login"))
                    if users.verify_user(user['username'], page.client_storage.get("password")) == True and user['verifyed'] == True:
                        if user['money'] >= smile_coin_generator.get_current_value()*float(to_buy.value):
                            users.update_user(user['id'], cash=user['cash']+round(float(to_buy.value), 2))
                            users.update_user(user['id'], money=user['money']-round(float(to_buy.value)*smile_coin_generator.get_current_value(), 2))
                            to_buy.error_text = None
                            to_buy.update()
                            page.close(buy)
                        else:
                            to_buy.error_text = "Недостаточно средств"
                            to_buy.update()
                    else:
                        to_buy.error_text = "Не авторизован"
                        to_buy.update()
                else:
                    to_buy.error_text = "Поле не может быть пустым"
                    to_buy.update()
            except:
                to_buy.error_text = "Неверное значение"
                to_buy.update()

        def update_buy(e):
            try:
                to_buy_txt.title.value = f"~{round(float(to_buy.value) * smile_coin_generator.get_current_value(), 2)} ₽"
                to_buy_txt.update()
            except:
                pass

        def commit_sell(e):
            try:
                if len(to_sell.value) > 0:
                    user = users.find_user_by_username(page.client_storage.get("login"))
                    if users.verify_user(user['username'], page.client_storage.get("password")) == True and user['verifyed'] == True:
                        if user['money'] >= smile_coin_generator.get_current_value()*float(to_sell.value):
                            users.update_user(user['id'], cash=user['cash']-round(float(to_sell.value), 2))
                            users.update_user(user['id'], money=user['money']+round(float(to_sell.value)*smile_coin_generator.get_current_value(), 2))
                            to_sell.error_text = None
                            to_sell.update()
                            page.close(sell)
                        else:
                            to_sell.error_text = "Недостаточно средств"
                            to_sell.update()
                    else:
                        to_sell.error_text = "Не авторизован"
                        to_sell.update()
                else:
                    to_sell.error_text = "Поле не может быть пустым"
                    to_sell.update()
            except:
                to_sell.error_text = "Неверное значение"
                to_sell.update()

        def update_sell(e):
            try:
                to_sell_txt.title.value = f"~{round(float(to_sell.value) * smile_coin_generator.get_current_value(), 2)} ₽"
                to_sell_txt.update()
            except:
                pass

        def open_us(e):
            new_course.value = f"{smile_coin_generator.get_current_value():.2f}"
            page.open(us)

        def open_amp(e):
            maxamp.value = str(smile_coin_generator.get_max_amplitude())
            minamp.value = str(smile_coin_generator.get_min_amplitude())
            page.open(amp)

        def open_vals(e):
            maxval.value = str(smile_coin_generator.get_max_value())
            minval.value = str(smile_coin_generator.get_min_value())
            page.open(vals)

        def open_buy(e):
            to_buy.value = 0
            page.open(buy)

        def open_sell(e):
            to_sell.value = 0
            page.open(sell)

        def handle_dismissal_us(e):
            page.close(us)

        def handle_dismissal_amp(e):
            page.close(amp)

        def handle_dismissal_vals(e):
            page.close(vals)

        def handle_dismissal_buy(e):
            page.close(buy)

        def handle_dismissal_sell(e):
            page.close(sell)

        new_course = ft.TextField(label="Новый курс", input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$", replacement_string=""))

        us = ft.BottomSheet(
            on_dismiss=handle_dismissal_us,
            content=ft.Container(
                padding=16,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.MONEY),
                            title=ft.Text("Изменение курса", font_family="HeadlineBold"),
                            subtitle=ft.Text(
                                "Иногда курс бывает весьма неудовлетворителен потребностям"),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE
                        ),
                        new_course,
                        ft.Row([
                            ft.TextButton("Отмена", on_click=handle_dismissal_us),
                            ft.TextButton("Изменить", on_click=commit_course),
                        ], alignment=ft.MainAxisAlignment.END),
                    ],
                ),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                border_radius=24,
                width=400
            ),
        )

        minamp = ft.TextField(label="Минимальная",
                                  input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$",
                                                              replacement_string=""))
        maxamp = ft.TextField(label="Максимальная",
                              input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$",
                                                          replacement_string=""))

        amp = ft.BottomSheet(
            on_dismiss=handle_dismissal_amp,
            content=ft.Container(
                padding=16,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.FORMAT_LINE_SPACING),
                            title=ft.Text("Изменение амплитуды", font_family="HeadlineBold"),
                            subtitle=ft.Text(
                                "Изменяет экстремальные отклонения курса"),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE
                        ),
                        minamp,
                        maxamp,
                        ft.Row([
                            ft.TextButton("Отмена", on_click=handle_dismissal_amp),
                            ft.TextButton("Изменить", on_click=commit_amp),
                        ], alignment=ft.MainAxisAlignment.END),
                    ],
                ),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                border_radius=24,
                width=400
            ),
        )

        minval = ft.TextField(label="Минимальное",
                                  input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$",
                                                              replacement_string=""))
        maxval = ft.TextField(label="Максимальное",
                              input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$",
                                                          replacement_string=""))

        vals = ft.BottomSheet(
            on_dismiss=handle_dismissal_vals,
            content=ft.Container(
                padding=16,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.LINE_WEIGHT),
                            title=ft.Text("Изменение лимита", font_family="HeadlineBold"),
                            subtitle=ft.Text(
                                "Изменяет экстремальные точки курса"),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE
                        ),
                        minval,
                        maxval,
                        ft.Row([
                            ft.TextButton("Отмена", on_click=handle_dismissal_vals),
                            ft.TextButton("Купить", on_click=commit_vals),
                        ], alignment=ft.MainAxisAlignment.END),
                    ],
                ),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                border_radius=24,
                width=400
            ),
        )

        to_buy = ft.TextField(suffix_text="₲", on_change=update_buy,
                              input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$",
                                                          replacement_string=""),
                              label="Единицы"
                              )
        to_buy_txt = ft.ListTile(
                            title=ft.Text("~0.0 ₽", theme_style=ft.TextThemeStyle.HEADLINE_LARGE, font_family="HeadlineBold"),
                            subtitle=ft.Text(
                                f"Доступно {users.find_user_by_username(page.client_storage.get("login"))['money']}₽"),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE
                        )

        buy = ft.BottomSheet(
            on_dismiss=handle_dismissal_buy,
            content=ft.Container(
                padding=16,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.LINE_WEIGHT),
                            title=ft.Text("Купить ₲", font_family="HeadlineBold"),
                            subtitle=ft.Text(
                                "Покупаем смайл-коины"),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE
                        ),
                        to_buy_txt,
                        to_buy,
                        ft.Row([
                            ft.TextButton("Отмена", on_click=handle_dismissal_buy),
                            ft.TextButton("Оплатить", on_click=commit_buy),
                        ], alignment=ft.MainAxisAlignment.END),
                    ],
                ),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                border_radius=24,
                width=400
            ),
        )

        to_sell = ft.TextField(suffix_text="₲", on_change=update_sell,
                              input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$",
                                                          replacement_string=""),
                              label="Единицы"
                              )
        to_sell_txt = ft.ListTile(
            title=ft.Text("~0.0 ₽", theme_style=ft.TextThemeStyle.HEADLINE_LARGE, font_family="HeadlineBold"),
            subtitle=ft.Text(
                f"Доступно {users.find_user_by_username(page.client_storage.get("login"))['cash']}₲"),
            bgcolor=ft.Colors.ON_INVERSE_SURFACE
        )

        sell = ft.BottomSheet(
            on_dismiss=handle_dismissal_sell,
            content=ft.Container(
                padding=16,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.LINE_WEIGHT),
                            title=ft.Text("Продать ₲", font_family="HeadlineBold"),
                            subtitle=ft.Text(
                                "Продаём смайл-коины"),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE
                        ),
                        to_sell_txt,
                        to_sell,
                        ft.Row([
                            ft.TextButton("Отмена", on_click=handle_dismissal_sell),
                            ft.TextButton("Продать", on_click=commit_sell),
                        ], alignment=ft.MainAxisAlignment.END),
                    ],
                ),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                border_radius=24,
                width=400
            ),
        )

        def open_jbsave(e):
            jb_mode.value = "auto"
            jb_datastore.value = ""
            jb_datastore.visible = False
            page.open(jbase_save)

        def open_jbrecovery(e):
            jb_mode.value = "auto"
            jb_datastore.value = ""
            jb_datastore.visible = False
            page.open(jbase_recovery)

        def open_jbclear(e):
            page.open(jbase_clear)

        def update_jbsm(e):
            if jb_mode.value == "auto":
                jb_datastore.visible = False
            else:
                jb_datastore.visible = True
            jb_datastore.update()

        def update_jbdel(e):
            if jbdel_mode.value == "recovery":
                jbd_mode.visible = False
            else:
                jbd_mode.visible = True
            page.update()

        def commit_jbdel(e):
            if jbdel_mode.value == "datastores":
                jb.clear_all_files()
            else:
                jb.clear_backup_files()

        def commit_jbsave(e):
            if jb_mode.value == "auto":
                jb.backup_all()
                page.close(jbase_save)
            else:
                ds = jb_datastore.value
                if not jb.backup(ds):
                    jb_datastore.error_text = "Хранилище не существует"
                    jb_datastore.update()
                else:
                    jb_datastore.error_text = None
                    jb_datastore.update()
                    page.close(jbase_save)

        def commit_jbrecovery(e):
            if jb_mode.value == "auto":
                jb.mass_restore()
                page.close(jbase_recovery)
            else:
                ds = jb_datastore.value
                if not jb.restore(ds):
                    jb_datastore.error_text = "Хранилище не существует"
                    jb_datastore.update()
                else:
                    jb_datastore.error_text = None
                    jb_datastore.update()
                    page.close(jbase_save)

        def commit_jbclear(e):
            jb.clear_backup_files()
            page.close(jbase_clear)

        def handle_dismissal_jbsave(e):
            page.close(jbase_save)

        def handle_dismissal_jbrecovery(e):
            page.close(jbase_recovery)

        def handle_dismissal_jbclear(e):
            page.close(jbase_clear)

        jb_mode = ft.Dropdown(label="Режим",
                                  options=[ft.dropdown.Option(text="Массовый (авто)", key="auto"),
                                           ft.dropdown.Option(text="Точечный", key="manual"),],
                                  value="auto", on_change=update_jbsm)

        jbd_mode = ft.Dropdown(label="Режим",
                                  options=[ft.dropdown.Option(text="Массовый (авто)", key="auto"),
                                           ft.dropdown.Option(text="Точечный", key="manual"),],
                                  value="auto", on_change=update_jbdel)

        jbdel_mode = ft.Dropdown(label="Очистка",
                                  options=[ft.dropdown.Option(text="Файлы восстановления", key="recovery"),
                                           ft.dropdown.Option(text="Все файлы", key="datastores")],
                                  value="recovery", on_change=update_jbdel)

        jb_datastore = ft.TextField(label="Название хранилища", visible=False)

        jbase_save = ft.BottomSheet(
            on_dismiss=handle_dismissal_jbsave,
            content=ft.Container(
                padding=16,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.DATA_ARRAY),
                            title=ft.Text("JBase: копирование", font_family="HeadlineBold"),
                            subtitle=ft.Text(
                                "Создание резервных копий"),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE
                        ),
                        jb_mode,
                        jb_datastore,
                        ft.Row([
                            ft.TextButton("Отмена", on_click=handle_dismissal_jbsave),
                            ft.TextButton("Копировать", on_click=commit_jbsave),
                        ], alignment=ft.MainAxisAlignment.END),
                    ],
                ),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                border_radius=24,
                width=400
            ),
        )

        jbase_recovery = ft.BottomSheet(
            on_dismiss=handle_dismissal_jbrecovery,
            content=ft.Container(
                padding=16,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.DATA_ARRAY),
                            title=ft.Text("JBase: восстановление", font_family="HeadlineBold"),
                            subtitle=ft.Text(
                                "Восстановление баз данных"),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE
                        ),
                        jb_mode,
                        jb_datastore,
                        ft.Row([
                            ft.TextButton("Отмена", on_click=handle_dismissal_jbrecovery),
                            ft.TextButton("Восстановить", on_click=commit_jbrecovery),
                        ], alignment=ft.MainAxisAlignment.END),
                    ],
                ),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                border_radius=24,
                width=400
            ),
        )

        jbase_clear = ft.BottomSheet(
            on_dismiss=handle_dismissal_jbclear,
            content=ft.Container(
                padding=16,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.DATA_ARRAY),
                            title=ft.Text("JBase: очистка", font_family="HeadlineBold"),
                            subtitle=ft.Text(
                                "Очистка баз данных"),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE
                        ),
                        jbdel_mode,
                        ft.Row([
                            ft.TextButton("Отмена", on_click=handle_dismissal_jbclear),
                            ft.TextButton("Очистить", on_click=commit_jbclear, style=ft.ButtonStyle(color=ft.Colors.ERROR)),
                        ], alignment=ft.MainAxisAlignment.END),
                    ],
                ),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                border_radius=24,
                width=400
            ),
        )

        course_text = ft.Text(f"{smile_coin_generator.get_current_value():.2f}".replace('.', ',') + " ₽", theme_style=ft.TextThemeStyle.HEADLINE_LARGE, font_family="HeadlineBold")
        course = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.ListTile(
                                #leading=ft.Icon(ft.Icons.MONEY),
                                title=course_text,
                                subtitle=ft.Text("Текущий курс"),
                                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                                trailing=ft.PopupMenuButton(icon=ft.Icons.MORE_VERT, tooltip="Дополнительно", items=[
                                    ft.PopupMenuItem("Обновить курс", icon=ft.Icons.REFRESH, on_click=update_course)
                                ])
                            ),
                        ]
                    ),
                    width=400,
                    padding=10,
                ),
            color=ft.Colors.ON_INVERSE_SURFACE
            )

        buy_cash = ft.TextButton("Купить", on_click=open_buy)
        sell_cash = ft.TextButton("Продать", on_click=open_sell)
        activate = ft.Image(src="banners/ActivateNow.png", width=400)

        cash_manipulations = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.WALLET),
                            title=ft.Text("Кошелёк", font_family="HeadlineBold"),
                            subtitle=ft.Text(
                                "Денежные массы управляются здесь"
                            ),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                        ),
                        ft.Row([
                            buy_cash,
                            sell_cash,
                        ], alignment=ft.MainAxisAlignment.END),
                    ]
                ),
                width=400,
                padding=10,
            ),
            color=ft.Colors.ON_INVERSE_SURFACE
        )

        devtools = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.DEVELOPER_MODE),
                                title=ft.Text("Инструменты разработчика", font_family="HeadlineBold"),
                                subtitle=ft.Text(
                                    "API, веселье и многое другое"
                                ),
                                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                            ),
                            ft.TextButton(text="Изменить курс", width=400, on_click=open_us),
                            ft.TextButton(text="Изменить амплитуду", width=400, on_click=open_amp),
                            ft.TextButton(text="Изменить лимиты", width=400, on_click=open_vals),
                        ]
                    ),
                    width=400,
                    padding=10,
                ),
            color=ft.Colors.ON_INVERSE_SURFACE
            )
        jbaseblock = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.DATA_ARRAY),
                            title=ft.Text("JBase", font_family="HeadlineBold"),
                            subtitle=ft.Text(
                                "База данных"
                            ),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                        ),
                        ft.TextButton(text="Резервное копирование", width=400, on_click=open_jbsave),
                        ft.TextButton(text="Восстановление данных", width=400, on_click=open_jbrecovery),
                        ft.TextButton(text="Удаление данных и очистка", width=400, on_click=open_jbclear),
                    ]
                ),
                width=400,
                padding=10,
            ),
            color=ft.Colors.ON_INVERSE_SURFACE,
            visible=False
        )

        def reg(e):
            page.route = "/signup"
            page.update()

        gift = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.WALLET_GIFTCARD),
                            title=ft.Text("Дарим подарки всем!", font_family="HeadlineBold"),
                            subtitle=ft.Text(
                                "За регистрацию подарим 50₽ на счёт"
                            ),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                        ),
                        ft.FilledButton("Зарегистрироваться", width=400, on_click=reg)
                    ]
                ),
                width=400,
                padding=10,
            ),
            color=ft.Colors.ON_INVERSE_SURFACE
        )

        if page.client_storage.get("valid_user") == True:
            gift.visible = False
            user = users.find_user_by_username(page.client_storage.get("login"))
            if user != None and user['role'] >= 200:
                devtools.visible = True
                if user['role'] >= 240:
                    jbaseblock.visible = True
            else:
                devtools.visible = False
            if user != None and user['verifyed'] == False:
                sell_cash.disabled = True
                buy_cash.disabled = True
                activate.visible = True
            else:
                activate.visible = False
        else:
            cash_manipulations.visible = False
            activate.visible = False
            devtools.visible = False
            gift.visible = True
        page.add(ft.Image(src="icons/SeasonBanner.png", width=400),
            course,
            cash_manipulations,
            activate,
            gift,
            devtools,
            jbaseblock
        )

    def register():
        def validate(e):
            password.error_text = None
            email.error_text = None
            username.error_text = None
            if is_valid_email(email.value) == True:
                if not users.find_user_by_username(username.value):
                    if not len(password.value) < 8:
                        user = users.create_user(username=username.value, password=password.value, email=email.value,
                                                 cash=0, money=50, role=0, display_name=username.value)
                        if user == None:
                            email.error = "Почта занята"
                        else:
                            page.client_storage.set("login", username.value)
                            page.client_storage.set("password", password.value)
                            password.error_text = None
                            email.error_text = None
                            username.error_text = None
                            page.route = "/my"
                            page.update()
                    else:
                        password.error_text = "Должно быть хотя бы 8 знаков"
                        page.update()
                else:
                    username.error_text = "Имя пользователя занято"
                    page.update()
            else:
                email.error_text = "Неверный адрес почты"
                page.update()

        def login(e):
            page.route = "/signin"
            page.update()

        username = ft.TextField(
            label="Имя пользователя",
            max_length=14,
            prefix_text="@",
            input_filter=ft.InputFilter(regex_string=r"^[A-Za-z0-9-]*$", allow=True, replacement_string=""),
            autofill_hints=ft.AutofillHint.USERNAME
        )
        password = ft.TextField(label="Пароль", password=True, can_reveal_password=True)
        email = ft.TextField(label="Почта", autofill_hints=ft.AutofillHint.EMAIL)

        register = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.MANAGE_ACCOUNTS),
                                title=ft.Text("Регистрация аккаунта", font_family="HeadlineBold"),
                                subtitle=ft.Text("Создать новую учётную запись"),
                                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                            ),
                            username,
                            email,
                            password,
                            ft.Row([
                                ft.TextButton("Войти в свой аккаунт", on_click=login),
                                ft.FilledButton("Создать", on_click=validate),
                            ], alignment=ft.MainAxisAlignment.END)
                        ]
                    ),
                    width=400,
                    padding=10,
                ),
            color=ft.Colors.ON_INVERSE_SURFACE
            )

        page.add(
            register
        )

    def signin():
        def validate(e):
            username.error_text = None
            password.error_text = None
            if users.find_user_by_username(username.value):
                if users.verify_user(username.value, password.value) == True:
                    page.client_storage.set("login", username.value)
                    page.client_storage.set("password", password.value)
                    page.route = "/my"
                    username.error_text = None
                    password.error_text = None
                    page.update()
                else:
                    password.error_text = "Неверный пароль"
                    page.update()
            else:
                username.error_text = "Пользователь не существует"
                page.update()

        def signup(e):
            page.route = "/signup"
            page.update()

        username = ft.TextField(
            label="Имя пользователя",
            max_length=14,
            prefix_text="@",
            input_filter=ft.InputFilter(regex_string=r"^[A-Za-z0-9-]*$", allow=True, replacement_string=""),
            autofill_hints=ft.AutofillHint.USERNAME
        )
        password = ft.TextField(label="Пароль", password=True, can_reveal_password=True)

        register = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.MANAGE_ACCOUNTS),
                                title=ft.Text("Вход", font_family="HeadlineBold"),
                                subtitle=ft.Text("Вход в свою учётную запись"),
                                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                            ),
                            username,
                            password,
                            ft.Row([
                                ft.TextButton("Создать аккаунт", on_click=signup),
                                ft.FilledButton("Войти", on_click=validate),
                            ], alignment=ft.MainAxisAlignment.END)
                        ]
                    ),
                    width=400,
                    padding=10,
                ),
            color=ft.Colors.ON_INVERSE_SURFACE
            )

        page.add(
            register
        )

    def my():
        user = users.find_user_by_username(page.client_storage.get('login'))

        def reload(e):
            user = users.find_user_by_username(page.client_storage.get('login'))
            dispnametext.value = f"{user['display_name']}"
            usernametext.value = f"@{user['username']}"
            avatar.content.value = f"{user['display_name'][:2]}"
            page.update()

        def reload_cash(e):
            user = users.find_user_by_username(page.client_storage.get('login'))
            cash_text_bal.value = f"{user['cash']} ₲"
            money_text_bal.value = f"{user['money']} ₽"
            page.update()

        def open_edit(e):
            username.value = user['username']
            page.open(bs)

        def open_sm(e):
            username.value = None
            page.open(sm)

        def open_ss(username, count):
            rgif.src = f"/gifs/{random.randint(1,16)}.gif"
            stext.title.value = f"-{count} ₲"
            stext.subtitle.value = f"Вы перевели {count}₲ на аккаунт @{username}!"
            page.open(ss)

        def commit_changes(e):
            if len(dispname.value) >= 3:
                dispname.error_text = None
                page.update()
                page.close(bs)
                users.update_user(user['id'], display_name=dispname.value)
                reload(None)
                if len(username.value) >= 3:
                    if users.find_user_by_username(username.value) == None and user["username"] != username.value:
                        page.open(us)
                    else:
                        if user["username"] != username.value:
                            page.open(ue)
                else:
                    username.error_text = "Нужно хотя бы 3 символа"
                    page.update()
            else:
                dispname.error_text = "Нужно хотя бы 3 символа"
                page.update()

        def commit_send(e):
            user = users.find_user_by_username(page.client_storage.get("login"))
            if len(cash_val.value) >= 1:
                if user['cash'] >= float(cash_val.value):
                    cash_val.error_text = None
                    page.update()
                    if len(username.value) >= 1:
                        user1 = users.find_user_by_username(username.value)
                        if user1 != None:
                            if user['username'] != user1['username']:
                                if user1['verifyed'] == True:
                                    username.error_text = None
                                    page.update()

                                    page.close(sm)
                                    users.update_user(user['id'], cash=user['cash'] - float(cash_val.value))
                                    reload_cash(None)
                                    users.update_user(user1['id'], cash=user1['cash'] + float(cash_val.value))
                                    jb.create("transfers", sender_id=user["id"], recipient_id=user1["id"], quantity=float(cash_val.value), date=time.time(), message=None, picture=None)
                                    open_ss(user1['username'], round(float(cash_val.value), 2))
                                else:
                                    username.error_text = "Аккаунт не активирован"
                                    page.update()
                            else:
                                username.error_text = random.choice(["Зачем ты это делаешь?",
                                                                     "Зачем ты переводишь себе?",
                                                                     "Так нельзя!",
                                                                     "Что за мошеннические схемы?",
                                                                     "Нигамозг вышел из чата",
                                                                     "Это меня бесит",
                                                                     "01011010 01000001 00110100 01000101 01001101?",
                                                                     "Я устал",
                                                                     "Переводишь на меня пере.. ой",
                                                                     f"Лучше на @{users.find_user_by_id(1)['username']} переведи"])
                                page.update()
                        else:
                            username.error_text = "Пользователь не существует"
                            page.update()
                    else:
                        username.error_text = "Это поле не может быть пустым"
                        page.update()
                else:
                    cash_val.error_text = "Недостаточно средств"
                    page.update()
            else:
                cash_val.error_text = "Это поле не может быть пустым"
                page.update()

        def commit_username(e):
            if len(password.value) > 0:
                if users.verify_user(username=user["username"], password=password.value) == True:
                    users.update_user(user["id"], username=username.value, cash=user["cash"]-100)
                    if stay_logged_in.value == True:
                        page.client_storage.set("login", username.value)
                        reload(None)
                    else:
                        page.go("/signin")
                    page.close(us)
                else:
                    password.error_text = "Неверный пароль"
            else:
                password.error_text = "Необходимо заполнить это поле"

        def handle_dismissal_bs(e):
            page.close(bs)

        def handle_dismissal_ue(e):
            page.close(ue)

        def handle_dismissal_us(e):
            page.close(us)

        def handle_dismissal_sm(e):
            page.close(sm)

        def handle_dismissal_ss(e):
            page.close(ss)

        username = ft.TextField(
    label="Имя пользователя",
    max_length=14,
    value=user['username'],
    prefix_text="@",
    input_filter=ft.InputFilter(regex_string=r"^[A-Za-z0-9-]*$", allow=True, replacement_string="")
)
        dispname = ft.TextField(label="Отображаемое имя", max_length=24, value=user['display_name'], helper_text="Желательно имя с инициалами, например: Александр К.")
        password = ft.TextField(label="Пароль", max_length=24, password=True, can_reveal_password=True)
        stay_logged_in = ft.Checkbox(label="Остаться в аккаунте")

        us = ft.BottomSheet(
            on_dismiss=handle_dismissal_us,
            content=ft.Container(
                padding=16,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.QUESTION_MARK),
                            title=ft.Text("Смена имени пользователя", font_family="HeadlineBold"),
                            subtitle=ft.Text("При смене имени пользователя с виртуального счёта спишется 100₲. Чтобы продолжить, введите свой пароль."),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE
                        ),
                        password,
                        stay_logged_in,
                        ft.Row([
                            ft.TextButton("Отмена", on_click=handle_dismissal_us),
                            ft.TextButton("Сменить имя пользователя", on_click=commit_username),
                        ], alignment=ft.MainAxisAlignment.END),
                    ],
                ),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                border_radius=24,
                width=400
            ),
        )

        ue = ft.BottomSheet(
            on_dismiss=handle_dismissal_ue,
            content=ft.Container(
                padding=16,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.ACCOUNT_CIRCLE),
                            title=ft.Text("Конфликт", font_family="HeadlineBold"),
                            subtitle=ft.Text(
                                f"Указанное имя пользователя уже используется другим человеком. Игнорируя конфликт, отображаемое имя было изменено."),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE
                        ),
                        ft.Row([
                            ft.TextButton("Ок", on_click=handle_dismissal_ue),
                        ], alignment=ft.MainAxisAlignment.END),
                    ],
                ),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                border_radius=24,
                width=400
            ),
        )

        rgif = ft.Image(src=f"/gifs/{random.randint(1,6)}.gif", width=400, fit=ft.ImageFit.FIT_WIDTH, border_radius=12, height=200)
        stext = ft.ListTile(
                            title=ft.Text("-0 ₲", font_family="HeadlineBold", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
                            subtitle=ft.Text(
                                f"Вы перевели 0₲ на аккаунт @none"),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE
                        )

        ss = ft.BottomSheet(
            on_dismiss=handle_dismissal_ss,
            content=ft.Container(
                padding=16,
                content=ft.Column(
                    tight=True,
                    controls=[
                        rgif,
                        stext,
                        ft.Row([
                            ft.TextButton("Ок", on_click=handle_dismissal_ss),
                        ], alignment=ft.MainAxisAlignment.END),
                    ],
                ),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                border_radius=24,
                width=400,
            ),
        )

        bs = ft.BottomSheet(
            on_dismiss=handle_dismissal_bs,
            content=ft.Container(
                padding=16,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.EDIT),
                            title=ft.Text("Изменение профиля", font_family="HeadlineBold"),
                            subtitle=ft.Text("Персонализация аккаунта"),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE
                        ),
                        #ft.Divider(),
                        username,
                        dispname,
                        ft.Row([
                            ft.TextButton("Отмена", on_click=handle_dismissal_bs),
                            ft.TextButton("Сохранить", on_click=commit_changes),
                        ], alignment=ft.MainAxisAlignment.END),
                    ],
                ),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                border_radius=24,
                width=400
            ),
        )

        cash_val = ft.TextField(suffix_text="₲",
                                input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]{0,2}$",
                                                            replacement_string=""),
                                label="Единицы"
                            )

        sm = ft.BottomSheet(
            on_dismiss=handle_dismissal_sm,
            content=ft.Container(
                padding=16,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.SEND),
                            title=ft.Text("Перевод", font_family="HeadlineBold"),
                            subtitle=ft.Text("Отправим смайл-коины"),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE
                        ),
                        username,
                        cash_val,
                        ft.Row([
                            ft.TextButton("Отмена", on_click=handle_dismissal_sm),
                            ft.TextButton("Отправить", on_click=commit_send),
                        ], alignment=ft.MainAxisAlignment.END),
                    ],
                ),
                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                border_radius=24,
                width=400
            ),
        )

        def logout(e):
            page.route = "/signout"
            page.update()

        display_name = users.find_user_by_username(page.client_storage.get('login'))['display_name']
        dispnametext = ft.Text(f"{display_name}", theme_style=ft.TextThemeStyle.HEADLINE_LARGE, font_family="HeadlineBold")
        usernametext = ft.Text(f"@{user['username']}")
        avatar = ft.CircleAvatar(
                                foreground_image_src="https://avatars.githubusercontent.com/u/_5041459?s=88&v=4",
                                content=ft.Text(f"{display_name[:2]}"),
                            )

        account = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=avatar,
                            title=dispnametext,
                            subtitle=usernametext,
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE
                        ),
                        ft.Row([
                            ft.IconButton(ft.Icons.EDIT, on_click=open_edit, tooltip="Изменить профиль"),
                            ft.IconButton(ft.Icons.REFRESH, on_click=reload, tooltip="Обновить блок"),
                        ], alignment=ft.MainAxisAlignment.END),
                    ]
                ),
                width=400,
                padding=10,
            ),
            color=ft.Colors.ON_INVERSE_SURFACE
        )

        cash_text_bal = ft.Text(f"{user['cash']} ₲", theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                                          font_family="HeadlineBold")

        money_text_bal = ft.Text(f"{user['money']} ₽", theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                                          font_family="HeadlineBold")

        send_cash = ft.TextButton("Отправить смайл-коины",
                                          on_click=open_sm)

        balance = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            title=cash_text_bal,
                            subtitle=ft.Text(
                                f"Виртуальный счёт"),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE
                        ),
                        ft.ListTile(
                            title=money_text_bal,
                            subtitle=ft.Text(
                                f"Рублёвый счёт"),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE
                        ),
                        ft.Row([
                            send_cash,
                            ft.IconButton(ft.Icons.REFRESH, on_click=reload_cash, tooltip="Обновить блок"),
                        ], alignment=ft.MainAxisAlignment.END)
                    ]
                ),
                width=400,
                padding=10,
            ),
            color=ft.Colors.ON_INVERSE_SURFACE
        )

        activate = ft.Image(src="banners/NotActivated.png", width=400, visible=False)
        if user["verifyed"] == False:
            activate.visible = True
            send_cash.disabled = True

        accounting = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.MANAGE_ACCOUNTS),
                            title=ft.Text("Мой аккаунт", font_family="HeadlineBold"),
                            subtitle=ft.Text(
                                "Действия с аккаутом"
                            ),
                            bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                        ),
                        ft.FilledButton("Выйти", width=400, icon=ft.Icons.LOGOUT, on_click=logout)
                    ]
                ),
                width=400,
                padding=10,
            ),
            color=ft.Colors.ON_INVERSE_SURFACE
        )

        page.add(
            account,
            activate,
            balance,
            accounting
        )

    def settings():
        if page.client_storage.get_async("theme_mode") != None:
            page.client_storage.set("theme_mode", "system")

        appstyle = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.SUNNY),
                                title=ft.Text("Внешний вид"),
                                subtitle=ft.Text(
                                    "Преображаем приложение"
                                ),
                                bgcolor=ft.Colors.ON_INVERSE_SURFACE,
                            ),
                        ]
                    ),
                    width=400,
                    padding=10,
                ),
            color=ft.Colors.ON_INVERSE_SURFACE
            )

        page.add(
            appstyle,
            ft.Text(f"Работает на {host}", opacity=0.3),
        )

    def route_change(route):
        if users.verify_user(username=page.client_storage.get("login"), password=page.client_storage.get("password")) == True:
            page.client_storage.set("valid_user", True)
        else:
            page.client_storage.set("valid_user", False)
        page.controls.clear()
        if page.route == "/home" or page.route == "/":
            home_page()
        elif page.route == "/chat":
            page.add(ft.Text("Чат"))
        elif page.route == "/my":
            if page.client_storage.get("valid_user"):
                my()
            else:
                page.route = "/signup"
        #elif page.route == "/settings":
        #    settings()
        elif page.route == "/admin":
            settings()
        elif page.route == "/signup":
            register()
        elif page.route == "/signin":
            signin()
        elif page.route == "/signout":
            page.route = "/my"
            page.client_storage.set("login", "0")
            page.client_storage.set("password", "0")
            page.update()

        page.update()

    page.on_route_change = route_change

    page.update()
    route_change(None)


ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="192.168.0.10", port=80)
