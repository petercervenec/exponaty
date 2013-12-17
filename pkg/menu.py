# vim: set expandtab:

import urwid
import json
import sqlite3
import general


class Config:
    def __init__(self):
        self.db = sqlite3.connect('expo.db')

        cur = self.db.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS config(key TEXT PRIMARY KEY NOT NULL, value TEXT)')

    def get(self, key):
        cur = self.db.cursor()
        for row in cur.execute('SELECT key, value FROM config WHERE key = ?', (key,)):
            return json.loads(row[1])
        return None

    def set(self, key, value):
        cur = self.db.cursor()
        cur.execute('INSERT OR REPLACE INTO config VALUES(?, ?)', (key, json.dumps(value)))
        self.db.commit()


class Menu:
    """ Opens a menu, in which the user can select an exhibit and its level to run. If there is no
        user input within 5 seconds, the last used exhibit and level are selected automatically.
    """
    def __init__(self, exhibits):
        self.exhibits = exhibits
        self.config = Config()
        self.result = (None, None)
        self.preselected_timer_handle = None

    def get_preselected(self):
        preselected = self.config.get('preselected')
        exhibit_id = preselected['exhibit'] if preselected and 'exhibit' in preselected else None
        level_id = preselected['level'] if preselected and 'level' in preselected else None

        for exhibit in self.exhibits:
            if exhibit.name == exhibit_id:
                for level in exhibit.levels:
                    if level.name == level_id:
                        return exhibit, level
        return None, None

    def run(self):
        self.main = urwid.Padding(None, left=2, right=2)
        self.top = urwid.Overlay(self.main, urwid.SolidFill(u'\N{MEDIUM SHADE}'), align='center',
                width=('relative', 60), valign='middle', height=('relative', 60),
                min_width=20, min_height=9)
        self.loop = urwid.MainLoop(self.top, palette=[('reversed', 'standout', '')],
                unhandled_input=self.loop_unhandled_input, input_filter=self.loop_input_filter)

        exhibit, level = self.get_preselected()
        general.logger.info("Preselected: " + str((exhibit, level)))
        if exhibit and level:
            self.preselected_timer(exhibit, level)
            self.level_menu(exhibit, level)
        else:
            self.exhibit_menu()

        self.loop.run()

    def loop_unhandled_input(self, input):
        if input == 'E':
            self.config.set('preselected', {}) # reset last used exhibit
            self.exhibit_menu()

    def loop_input_filter(self, keys, raw):
        """Intercept all user input, so we can stop `preselected_timer` if there is any."""
        if self.preselected_timer_handle != None:
            self.loop.remove_alarm(self.preselected_timer_handle)
            self.preselected_timer_handle = None
        return keys

    def preselected_timer(self, exhibit, level):
        """Wait for a while and then select the preselected (previously used) exhibit and level."""
        self.preselected_timer_handle = self.loop.set_alarm_in(5, self.preselected_timer_end, (exhibit, level))

    def preselected_timer_end(self, loop, (exhibit, level)):
        self.set_result(exhibit, level)

    def exhibit_menu(self):
        """Display exhibit menu"""
        body = [urwid.Text("Zvolit exponat"), urwid.Divider()]
        for exhibit in self.exhibits:
            button = urwid.Button(exhibit.name)
            urwid.connect_signal(button, 'click', self.exhibit_menu_click, exhibit)
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))
        menu = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        self.main.original_widget = menu

    def exhibit_menu_click(self, button, exhibit):
        self.level_menu(exhibit, None)

    def level_menu(self, exhibit, preselected_level):
        """Display level menu for a given exhibit"""
        body = [urwid.Text("%s: Zvolit level" % exhibit.name), urwid.Divider()]
        focus = None
        for level in exhibit.levels:
            if level == preselected_level:
                focus = len(body)
            button = urwid.Button(level.name)
            urwid.connect_signal(button, 'click', self.level_menu_click, (exhibit, level))
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))
        menu = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        if focus != None:
            menu.set_focus(focus)
        self.main.original_widget = menu

    def level_menu_click(self, button, (exhibit, level)):
        self.set_result(exhibit, level)

    def set_result(self, exhibit, level):
        """Save the selected exhibit and level and close the menu"""
        self.config.set('preselected', {'exhibit': exhibit.name, 'level': level.name})
        self.result = (exhibit, level)
        raise urwid.ExitMainLoop()


def start_menu(exhibits):
    """Convenience wrapper for Menu class"""
    menu = Menu(exhibits)
    menu.run()
    return menu.result


