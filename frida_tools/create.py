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

    agent_template = """
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

    package_lock_template = {
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

    current_path = os.getcwd()
    path = input('project path (%s): ' % current_path)
    if len(path) == 0:
        path = current_path
    if not os.path.exists(path):
        print('the specified path does not exists')
        exit(1)

    separator = '/'
    if os.name == 'nt':
        separator = '\\'
    current_project_name = current_path.split(separator)[-1]
    project_name = input('project name (%s): ' % current_project_name)
    if len(project_name) == 0:
        project_name = current_project_name
    package_template['name'] = project_name
    package_lock_template['name'] = project_name

    if not path.endswith(separator):
        path += separator
    with open(path + 'package.json', 'w') as f:
        f.write(json.dumps(package_template, indent=4))
    with open(path + 'tsconfig.json', 'w') as f:
        f.write(json.dumps(package_lock_template, indent=4))
    with open(path + '.babelrc', 'w') as f:
        f.write(babel_template)
    with open(path + 'agent.ts', 'w') as f:
        f.write(agent_template)

    os.system('cd %s && npm install' % path)
    print('')
    print('project create at %s')
    print('run `npm run watch` in the project path to automatically build the agent while you code it')
    exit(0)


if __name__ == '__main__':
    main()
