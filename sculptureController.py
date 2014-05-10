""" theSculpture server.

Launch the server with 'python sculptureController.py' Currently the server defaults to port
8888. The server provides a secured interface to the theSculpture sculpture,
allowing the sculpture's mode to be changed.

Front end and back end code by Liav Koren 2013 - 2014. """

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.auth
import tornado.escape
import os
from tornado.options import define, options
import tornado.httputil
import time
import paramiko
import subprocess
import json

define("port", default=8888, help="run on the given port", type=int)


class ModeHandler(tornado.web.RequestHandler):
    ''' Handler for the main interface. This serves up the mode selector page. '''

    ssh = ""

    def get(self):
        self.render('modes.html', current_mode='TESTING')

    def post(self):
        """ Mode handler. The mode selector page presents 'slow', 'medium', 'fast',
        'return to landing page' and 'logout' options to user. This handler is also
        the endpoint for the main page options 'ON' and 'OFF'. Slow, medium, fast, on
        and off all initiate a series of remote operations on theSculpture that involve
        opening an SSH tunnel, triggering various shell scripts and transfering files
        between the Pi and theSculpture. """

        path = ""
        data = self.request.arguments

        if 'slow' in data or 'slow-swatch' in data:
            path = '/home/pi/theSculpture/dat/slower1.dat'
        if 'medium' in data or 'medium-swatch' in data:
            path = '/home/pi/theSculpture/dat/med.dat'
        if 'fast' in data  or 'fast-swatch' in data:
            path = '/home/pi/theSculpture/dat/AGH4.dat'
        if 'on' in data or 'on-swatch' in data:
            self.kill_theSculpture()
            self.reset_theSculpture()
            time.sleep(5)
            self.write(json.dumps({"file_transfer": "finished"}))
        if 'off' in data or 'off-swatch' in data:
            self.kill_theSculpture()
            time.sleep(5)
            self.write(json.dumps({"file_transfer": "finished"}))

        if path:
            self.file_transfer(path)
            #self.file_transfer_mock(path)

    def file_transfer_mock(self, path):
        """ A debugging utility method for accepting commands but not
        passing them on to theSculpture. """
        new_path = "new path is: %s" % path
        print new_path
        time.sleep(10)
        self.write(json.dumps({"file_transfer": "finished"}))

    def kill_theSculpture(self):
        """ Turns theSculpture off. """
        cmd = "cd /bin; ./kill_theSculpture.sh"
        self.talk_to_sign(cmd)

    def reset_theSculpture(self):
        """ Restarts theSculpture from an off or currently running state. """
        self.kill_theSculpture()
        self.talk_to_sign("/bin/reset_theSculpture.sh")

    def file_transfer(self, path):
        """ This function deals with resetting theSculpture and
        transferring the new dat files. """
        self.kill_theSculpture()
        print "waiting 30s"
        time.sleep(30)
        print "starting scp"
        proc = subprocess.Popen(['scp', path,
                                'root@***.**.57.230:/data/theSculpture.dat'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()
        print "stdOut: %s " % proc.stdout.readline()
        print "stdErr: %s" % proc.stderr.readline()
        self.talk_to_sign("/bin/reset_theSculpture.sh")
        self.write(json.dumps({"file_transfer": "finished"}))

    def talk_to_sign(self, cmd):
        ''' Talk_to_sign calls open_ssh to get an ssh client object, then emits
        commands to the target system.'''
        if not self.ssh:
            self.ssh = self.open_ssh_tunnel('***.**.57.230', 'root', 'foobar')
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        if stderr.readlines():
            print "Error: %s" % stderr.readlines()
        if stdout.readlines():
            print "Cmd returned: %s" % stdout.readlines()


    def get_current_sign_status(self): # ToDo: narrow the exception handling
        ''' Tries to get the current state of the sign and return it to the
        client. '''
        if not self.ssh:
            self.ssh = self.open_ssh_tunnel('***.***.1.105', 'pi', 'foobar')
        stdin, stdout, stderr = self.ssh.exec_command('cat test')
        if stderr.readlines():
            print "Error reading current sign state."
        output = stdout.readlines()
        if output:
            print "current sign state is: "
            print output[0][:-1]
            return output[0][:-1]


    def open_ssh_tunnel(self, ip, username, passwd):
        ''' Provides a ssh client to the talk_to_sign method '''
        try:
            s = paramiko.SSHClient()
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(ip, username = username, password = passwd)
            return s
        except paramiko.AuthenticationException:
            self.write(json.dumps(
                {"status": "Failed to login to sign server successfully."}))
            return
        except paramiko.ChannelException:
            self.write(json.dumps(
                {"status": "Error opening channel to sign server."}))
            return
        except paramiko.SSHException:
            self.write(json.dumps(
                {"status": "SSH error when trying to contact sign server."}))
            return


class MainHandler(ModeHandler):
    """ The landing page once the user has logged in. """

    def get(self):
        self.render('main_revised.html')


def main():
    tornado.options.parse_command_line()
    settings = dict(
        template_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True,
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        login_url="/login",
    )
    application = tornado.web.Application([
        (r"/mode", ModeHandler),
        (r"/", MainHandler),
        (r"/main", MainHandler),
    ], **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
