"""Tool to generate mod_status-like output.

Usage:

import status

cherrypy.tools.status = status.StatusMonitor()
cherrypy.config.update({"tools.status.on": True})
cherrypy.tree.mount(status.Root(), '/cpstatus')
"""

import threading
import time

import cherrypy


class ThreadStatus(object):
    
    start = None
    end = None
    url = None
    
    def last_req_time(self):
        if self.end is None:
            return 0
        return self.end - self.start
    
    def idle_time(self):
        if self.end is None:
            return 0
        return time.time() - self.end


class StatusMonitor(cherrypy.Tool):
    """Register the status of each thread."""
    
    def __init__(self):
        self._point = 'on_start_resource'
        self._name = 'status'
        self._priority = 50
        self.seen_threads = {}
    
    def callable(self):
        threadID = threading._get_ident()
        ts = self.seen_threads.setdefault(threadID, ThreadStatus())
        ts.start = cherrypy.response.time
        ts.url = cherrypy.url()
        ts.end = None
    
    def unregister(self):
        """Unregister the current thread."""
        threadID = threading._get_ident()
        if threadID in self.seen_threads:
            self.seen_threads[threadID].end = time.time()
    
    def _setup(self):
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('on_end_resource', self.unregister)


class Root(object):
    
    def index(self):
        threadstats = ["<tr><th>%s</th><td>%.4f</td><td>%.4f</td><td>%s</td></tr>"
                       % (id, ts.idle_time(), ts.last_req_time(), ts.url)
                       for id, ts in cherrypy.tools.status.seen_threads.items()]
        return """
<html>
<head>
    <title>CherryPy Status</title>
</head>
<body>
<h1>CherryPy Status</h1>
<table>
<tr><th>Thread ID</th><th>Idle Time</th><th>Last Request Time</th><th>URL</th></tr>
%s
</table>
</body>
</html>
""" % '\n'.join(threadstats)
    index.exposed = True
    
    def delay(self, secs):
        # Help demo last_req_time (since my box returns index in under 1 msec).
        time.sleep(float(secs))
        return "OK"
    delay.exposed = True

