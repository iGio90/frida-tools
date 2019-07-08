# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import socket


def main():
    from frida_tools.application import ConsoleApplication

    class ModulesApplication(ConsoleApplication):
        def _usage(self):
            return "usage: %prog"

        def _start(self):
            if is_connected():
                modules = ModulesList()
                print("type h (help) to print help or q to continue")
                while True:
                    cmd = input('> ')
                    if cmd == 'q':
                        break

                    cmd = cmd.split(' ')
                    args = cmd[1:]
                    cmd = cmd[0]
                    if cmd == 'h' or cmd == 'help':
                        print('a|add {module-name}')
                        print('i|info {module-name}')
                        print('l|list [filter]')
                    elif cmd == 'l' or cmd == 'list':
                        modules.print(args)
                    elif cmd == 'a' or cmd == 'add':
                        modules.install(args)
                    elif cmd == 'i' or cmd == 'info':
                        modules.print_info(args)

            print('')
            exit(0)

    app = ModulesApplication()
    app.run()


def is_connected():
    try:
        socket.setdefaulttimeout(2)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except:
        return False


class ModulesList:
    def __init__(self):
        import requests

        self.modules = {}

        updated_module_list = requests.get(
            'https://raw.githubusercontent.com/iGio90/frida-create-modules/master/modules.json').json()
        for module in updated_module_list:
            m = ModuleInfo(module)
            self.modules[m.name] = m

    def print(self, args):
        _filter = None
        if len(args) > 0:
            _filter = args[0].lower()
        for module_name in self.modules.keys():
            if _filter is not None:
                try:
                    if module_name.index(_filter) < 0:
                        continue
                except:
                    continue
            self.print_module(self.modules[module_name])

    def print_info(self, args):
        if len(args) == 0:
            print("you must specify a module name. use `list` to get the list of available modules")
        else:
            module = self.get_module(args[0])
            if module is not None:
                print(module.to_string())

    def print_module(self, module):
        print('%s\t%s' % (module.name, module.description))

    def install(self, args):
        if len(args) == 0:
            print("you must specify a module name. use `list` to get the list of available modules")
        else:
            module = self.get_module(args[0])
            if module is not None:
                self.npm_install(module.npm_setup)
            else:
                install = input("no module found with name %s. do you want to npm install anyway? " % args[0])
                if install.lower() == 'y':
                    self.npm_install(args[0])

    def npm_install(self, module):
        os.system("npm install %s" % module)

    def get_module(self, module_name):
        if module_name in self.modules:
            return self.modules[module_name]
        return None


class ModuleInfo:
    def __init__(self, data):
        self.name = data["name"].lower()
        self.description = data["description"]
        self.author = data["author"]
        self.link = data["link"]
        self.npm_setup = data["npm-setup"]

    def to_string(self):
        return 'Name: %s\nDescription: %s\nAuthor: %s\nLink: %s' % (
            self.name, self.description, self.author, self.link)


if __name__ == '__main__':
    main()
