# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import socket


def main():
    from io import open

    import json

    agent_template = """"""

    babel_template = """{
  "presets": [
    [
      "@babel/preset-env",
      {
        "loose": true
      }
    ]
  ],
  "plugins": [
    [
      "@babel/plugin-transform-runtime",
      {
        "corejs": 2
      }
    ]
  ]
}"""

    package_template = {
        "name": "",
        "version": "1.0.0",
        "description": "",
        "private": True,
        "main": "agent.ts",
        "scripts": {
            "prepare": "npm run build",
            "build": "frida-compile agent/agent.ts -o _agent.js",
            "watch": "frida-compile agent/agent.ts -o _agent.js -w"
        },
        "devDependencies": {
            "@babel/core": "^7.4.5",
            "@babel/plugin-transform-runtime": "^7.4.4",
            "@babel/preset-env": "^7.4.5",
            "@babel/runtime-corejs2": "^7.4.5",
            "@types/frida-gum": "^13.0.0",
            "@types/node": "^12.0.4",
            "frida-compile": "^8.0.4",
            "typescript": "^3.5.1"
        }
    }

    tsconfig_template = {
        "compilerOptions": {
            "target": "esnext",
            "lib": ["esnext"],
            "strict": True,
            "module": "commonjs",
            "esModuleInterop": True,
            "declaration": True,
            "outDir": "./dist"
        },
        "include": [
            "src/**/*"
        ]
    }

    current_path = os.getcwd()
    path = input("project path (%s): " % current_path)
    if len(path) == 0:
        path = current_path
    if not os.path.exists(path):
        print("the specified path does not exists")
        exit(1)

    current_project_name = current_path.split(os.sep)[-1]
    project_name = input("project name (%s): " % current_project_name)
    if len(project_name) == 0:
        project_name = current_project_name
    package_template["name"] = project_name

    with open(os.path.join(path, "package.json"), 'w', encoding='utf-8') as f:
        f.write(json.dumps(package_template, indent=4))
    with open(os.path.join(path, "tsconfig.json"), 'w', encoding='utf-8') as f:
        f.write(json.dumps(tsconfig_template, indent=4))
    with open(os.path.join(path, ".babelrc"), 'w', encoding='utf-8') as f:
        f.write(babel_template)

    os.mkdir(os.path.join(path, 'agent'))
    with open(os.path.join(path, "agent/agent.ts"), 'w', encoding='utf-8') as f:
        f.write(agent_template)

    create_injector = input("do you want to create a base py injector? (Y): ")
    if len(create_injector) == 0 or create_injector.lower() == 'y':
        device_type = input("what's your target device? U:usb L:local R:remote (U): ").lower()
        if device_type == 'l':
            # todo
            pass
        elif device_type == 'r':
            # todo
            pass
        else:
            # fallback to usb in any case
            device_type = 'u'
        package = input("what's your target package name? ")
        with open(os.path.join(path, "injector.py"), 'w', encoding='utf-8') as f:
            f.write(get_injector_template(device_type, package))

    os.system("cd %s && npm install" % path)

    if is_connected():
        modules = ModulesList()
        print("now you can pick your weapons. type h to print help or q to continue")
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
    print("project create at %s" % path)
    print("run `npm run watch` in the project path to automatically build the agent while you code it")
    exit(0)


def get_injector_template(device_type, package):
    if device_type == 'l':
        device_token = "get_local_device"
    elif device_type == 'r':
        # todo here add properties
        device_token = "get_remote_device"
    else:
        # fallback to usb
        device_token = "get_usb_device"
    return """import frida
import os
import sys


def on_message(message, payload):
    if 'payload' in message:
        message = message['payload']
        print(message)
    else:
        print(message)


if not os.path.exists('_agent.js'):
    print('use `npm install` to build the agent')
    exit(0)

d = frida.%s()
pid = d.spawn('%s')
session = d.attach(pid)
script = session.create_script(open('_agent.js', 'r').read())
script.on('message', on_message)
script.load()
d.resume(pid)
sys.stdin.read()
""" % (device_token, package)


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
