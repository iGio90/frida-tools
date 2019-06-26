# -*- coding: utf-8 -*-
"""
roadmap:
inputs
* path (*)
* project name (*)
* optional modules to install (*)
* create py attacher or just agent
    for py attacher:
    * target package name
"""

from __future__ import print_function


def main():
    import json
    import os

    from io import open

    agent_template = """
    """

    babel_template = """
        {
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
        }    
    """

    package_template = {
        "name": "",
        "version": "1.0.0",
        "description": "",
        "private": True,
        "main": "agent.ts",
        "scripts": {
            "prepare": "npm run build",
            "build": "frida-compile agent.ts -o _agent.js",
            "watch": "frida-compile agent.ts -o _agent.js -w"
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
    with open(os.path.join(path, "agent.ts"), 'w', encoding='utf-8') as f:
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


if __name__ == '__main__':
    main()
