#!/usr/bin/env python
# encoding: utf-8
# __init__.py
'''
Pybald
======

An MVC-like framework using many best-of-breed components (i.e. webob, sqlalchemy).

(c) 2015 Michael Kowalchik
MIT License, see LICENSE file
'''
import imp
import sys
import os
from pybald.util.context import AppContext
import logging
from default import default_config
log = logging.getLogger(__name__)

__version__ = '0.0.4-dev'


def build_config(root_path='.', filename='project.py'):
    filename = os.path.join(root_path, filename)
    config_module = imp.new_module("config")
    config_module.__dict__.update(default_config)
    try:
        with open(filename) as config_file:
            exec(compile(config_file.read(), filename, 'exec'), config_module.__dict__)
    except IOError:
        sys.stderr.write("Warning: Using default pybald configuration\n")
    return config_module


class MockEngine(object):
    def __getattr__(self, key):
        raise RuntimeError("Pybald is not configured")


class DefaultApp(dict):
    def __init__(self, *pargs, **kargs):
        self.register('config', {})
        self.register('engine', MockEngine())
        self.register('controller_registry', [])
        self.register('model_registry', [])
        self.default = True
        super(DefaultApp, self).__init__(*pargs, **kargs)

    def register(self, key, value):
        self[key] = value
        setattr(self, key, self[key])

# unconfigured application stack context
context = AppContext()
sys.modules['pybald.context'] = context
# push the default placeholder app onto the context stack
# the default allows for temporary storage of elements required
# for bootstrapping (and eliminates some sequencing requirements
# for configuration)
context._push(DefaultApp())

# the template engine and database session are built at config time
context_template = '''
from pybald.core.templates import TemplateEngine
from pybald.db.db_engine import create_session, create_engine, create_dump_engine
from pybald.util.command_line import start

render = TemplateEngine()
dump_engine = create_dump_engine()
engine = create_engine()
db = create_session(engine=engine)

def register(key, value):
    globals()[key] = value

'''


def configure(name, config_file=None, config_object=None):
    '''
    Generate a dynamic context module that's pushed / popped on
    the application context stack.
    '''
    mod = sys.modules.get(name)
    # if mod is not None and hasattr(mod, '__file__'):
    try:
        root_path = os.path.dirname(os.path.abspath(mod.__file__))
    except AttributeError:
        root_path = os.getcwd()

    if config_object:
        config = config_object
    elif config_file:
        config = build_config(root_path=root_path, filename=config_file)
    else:
        config = build_config(root_path=root_path, filename='project.py')

    new_context = imp.new_module("context")
    # new_app._MODULE_SOURCE_CODE = app_template
    # new_app.__file__ = "<string>"
    if hasattr(context._proxied(), 'default'):
        placeholder = context._pop()
        new_context.__dict__.update(placeholder)
    else:
        new_context.__dict__['controller_registry'] = []
        new_context.__dict__['model_registry'] = []
    # always set the runtime config
    new_context.__dict__['path'] = root_path
    new_context.__dict__['config'] = config
    new_context.__dict__['name'] = name
    # now execute the app context with this config
    context._push(new_context)
    exec(compile(context_template, '<string>', 'exec'), new_context.__dict__)
    return new_context

# aliases for convenience
# from pybald.core.controllers import Controller, action
# from pybald.core.router import Router
# from pybald.core.logs import default_debug_log as debug_log