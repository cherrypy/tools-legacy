# Copyright (c) 2007 CherryPy
# Released under the same license as CherryPy

# To use:
# cherrypy.tools.jsonrender = JsonRender()
# 
# class foo(object):
#     @cherrypy.expose
#     @cherrypy.tools.jsonrender()
#     def index(self):
#         return dict(foo=['complication', dict(a='b')])

import cherrypy

import simplejson

class JsonRender(cherrypy.Tool):
    def __init__(self, name=None, priority=0):
        self._point = 'before_handler'
        self._name=name
        self._priority = priority

    def callable(self):
        cherrypy.request._handler = cherrypy.request.handler
        def wrap(*args, **kwargs):
            ret = cherrypy.request._handler(*args, **kwargs)
            return simplejson.dumps(ret)
        cherrypy.request.handler = wrap
