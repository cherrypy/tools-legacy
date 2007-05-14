# vim: set fileencoding=utf-8 :
# Copyright (c) 2007 CherryPy Team
# Licensed under the same terms as CherryPy.

# To use this tool
# cherrypy.tools.kidrender = KidRender()
# class foo(object):
#     @cherrypy.expose
#     @cherrypy.tools.kidrender(template = 'kidservtemplate',
#                         output='xhtml-strict', encoding='utf-8',
#                         assume_encoding='utf-8')
#     def index(self):
#         return dict(title=u'Tést yøur brôüuser', text=u'¡Qué tal mundo, Dígamelo!')

# Sample template
#  <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
#  <html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
#  
#  <head>
#      <title>${title}</title>
#  </head>
#  
#  <body>
#      ${text}
#  </body>
#  
#  </html>
#  

import cherrypy

import kid

class KidRender(cherrypy.Tool):
    def __init__(self):
        self._name = None
        self._point = 'before_finalize'
        self._priority = 99
        self._templatecache = {}

    def callable(self, template, output=None, encoding='utf-8',
                 assume_encoding='utf-8'):
        '''
            A simple template rendering mechanism using a trivial cache.  By
            default generates xhtml output using utf-8 encoding.  The
            dictionary returned by your exposed method is transformed by kid
            into the proper output.

            Most of the time the defaults are good enough

            @param template: The name of the template to be imported
            @param output: The type transform to perform.  See
                http://kid-templating.org/guide.html#common-output-methods for
                possible values.
            @param encoding: Character encoding to use in the output
            @param assume_encoding: Format to use when parsing the kid template
        '''
        templ = self._templatecache.get(template, None)
        if not templ:
            templ = kid.import_template(name=template)
            self._templatecache[template] = templ
        t = templ.Template(**cherrypy.response.body)
        t.assume_encoding=assume_encoding
        cherrypy.response.body = t.serialize(output=output, encoding=encoding)
        if output is None or 'xhtml' in output:
            if 'application/xhtml+xml' in cherrypy.request.headers['Accept']:
                cherrypy.response.headers['Content-Type'] = 'application/xhtml+xml'
            else:
                #This is nasty, but such is the state of XHTML today
                cherrypy.response.headers['Content-Type'] = 'text/html; charset=%s' % encoding

