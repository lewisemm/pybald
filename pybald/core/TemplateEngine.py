#!/usr/bin/env python
# encoding: utf-8
"""
TemplateEngine.py

Created by mikepk on 2009-06-29.
Copyright (c) 2009 Michael Kowalchik. All rights reserved.
"""

import sys
import os
import unittest

import project
from mako.template import Template
from mako.lookup import TemplateLookup

class TemplateEngine:
    '''The basic template engine, looks up templates and renders them. Uses the mako template system'''
    def __init__(self): #,project_path=project.path): #'/usr/share/enerd/template_project'):
        self.path = project.get_path()
        
    def __call__(self,data,format="html"):
        '''Callable method that executes the template.'''

        try:
            format = data["format"]
        except:
            pass

        mylookup = TemplateLookup(directories=[os.path.join(self.path,'app/views')], module_directory=os.path.join(self.path,'viewscache'),
        imports=['from routes import url_for',
        'from pybald.core.helpers import link',
        'from pybald.core.helpers import img',
        'from pybald.core.helpers import link_to',
        'from pybald.core.helpers import link_img_to',
        ],
        input_encoding='utf-8',output_encoding='utf-8')
        mytemplate = mylookup.get_template("/"+data['template_id'].lower()+"."+format.lower()+".template")
        return mytemplate.render(**data)

    
    def clear_viewscache(self):
        '''Clears out the viewscache. This isn't being used at the moment.'''
        folder = os.path.join(self.path,'viewscache')
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception, e:
                print e

class TemplateEngineTests(unittest.TestCase):
    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()