import os, sys, re
from os.path import expanduser
from path import path
import json
from pprint import pprint, pformat
import time, socket

sys.path.insert(0, os.path.dirname(__file__))

from IPython.zmq.blockingkernelmanager import BlockingKernelManager

class Dict(dict):
    def __getattr__(self, key):
        return self[key]
    def __setattr__(self, key, value):
        self[key] = value


class RemoteError(Exception): pass

def print_msg(msg, banner=''):
    if banner: banner = '[%s]' % banner
    print ('=' * (78 - len(banner))) + banner
    remove_attrs = ['msg_id', 'parent_header', 'header']
    msg = dict([(k,v) for (k,v) in msg.items() if k not in remove_attrs])
    pprint(msg)

class IPythonProxy(object):
    def __init__(self):
        self.out = self.error = None
        self.disabled = False
        self._kernel =self.get_kernel()
    
    @property
    def kernel(self):
        if self.disabled: return None
        kernel = self._kernel
        #assert kernel.hb_channel.is_alive
        if kernel is None or not kernel.is_alive:
            print "IPython kernel seems not active."
            print "Re-establishing connection...",
            self._kernel = kernel = self.get_kernel()
            if kernel is not None:
                print "OK."
            else:
                print "Failed.\n" \
                      "disasbling IPython support."
            self.disabled = True
        return self._kernel

    @property
    def shell(self):
        if self.disabled: return None
        return self.kernel.shell_channel

    @property
    def listener(self):
        if self.disabled: return None
        return self.kernel.sub_channel

    def get_kernel(self):
        security_dir = expanduser('~/.ipython/profile_default/security')
        files = path(security_dir).files()
        files.sort(key=lambda f: f.mtime, reverse=True) # find last opened ipython session
        def check_port(ip, port):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect( (ip, int(port)) )
                s.shutdown(2)
                return True
            except:
                print 'failed to connect to %s:%s' % (ip, port)
                return False

        for file in files:
            cfg = json.loads(open(file).read())
            ip, port = cfg['ip'], cfg['shell_port']
            if not check_port(ip, port): continue
            kernel = BlockingKernelManager(**cfg)
            kernel.start_channels()
            kernel.shell_channel.session.key = kernel.key
            kernel.hb_channel.unpause()
            return kernel
        print "Did not find a running IPython console."
        print "Disabling IPython support..."
        self.disabled = True
        #raise Exception('Did not find a running IPython console.')
        return None

    def flush(self):
        if self.disabled: return
        shell, listener = self.shell, self.listener
        shell.get_msgs()
        listener.get_msgs()

    def execute(self, code, dump=None):
        if self.disabled: return None
        self.flush()
        shell = self.shell
        shell.execute(code)
        msg = shell.get_msg()
        #print_msg(msg, 'shell_channel')
        if dump:
            open(dump,'w').write(pformat(msg))

        self.process_result()
        if self.error:
            raise RemoteError(self.error)

        out = self.out
        return filter_unicode(out)

    def info(self, object_name):
        if self.disabled: return None
        shell = self.shell
        #shell.execute(object_name+u'?\n')
        id = shell.object_info(object_name) # id of the msg sent
        while True:
            msg = shell.get_msg(1)
            assert msg is not None
            if msg['parent_header']['msg_id'] == id: break
        return Dict(msg['content'])

    def process_result(self):
        """dump messages"""
        self.out = self.error = None
        listener = self.listener
        while True:
            msg = listener.get_msg()
            #print_msg(msg, 'sub_channel')
            if msg['msg_type'] == 'status':
                if msg['content']['execution_state'] == 'idle':
                    break
            elif msg['msg_type'] == 'stream':
                content = msg['content']
                output = "{0}: {1}".format(content['name'], content['data'])
                print output
            elif msg['msg_type'] == 'pyout':
                assert not self.out
                self.out = msg['content']['data']['text/plain']
            elif msg['msg_type'] == 'pyerr':
                assert not self.error
                c = msg['content']
                ename, evalue = c['ename'],c['evalue']
                traceback = '\n'.join(c['traceback'])
                self.traceback = self._extract_traceback(c['traceback'])
                self.error = '{1}: {2}'.format(traceback, ename, evalue)
            # we're done
        # end of "while True"
    # we're done processing result

    def _extract_traceback(self, traceback):
        # strip ANSI color controls
        strip = re.compile('\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]')
        tb = [strip.sub('',t) for t in traceback]
        if len(tb) == 1:
            m = re.search(', line (\d+)', tb[0])
            line = int(m.group(1))
            return [('<ipython-input>', line, tb[0])]
        else:
            result = []
            for t in tb[1:-1]:
                m = re.search(r'^(\S+) in (\S+)', t)
                filename = m.group(1)
                m = re.search(r'\--+> (\d+)', t)
                line_num = int(m.group(1))
                result.append( (filename, line_num, t))
            return result
        # done extracting traceback

    def chdir(self, path):
        if self.disabled: return None
        self.flush()
        path = unicode(path)
        code = u'%cd ' + path
        shell = self.shell
        shell.execute(code)
        msg = shell.get_msg(1)
        assert msg['content']['status'] == 'ok'
        self.process_result()

    def getcwd(self):
        if self.disabled: return None
        self.flush()
        shell = self.shell
        shell.execute(u'%pwd')
        self.process_result()
        return self.out

    def complete(self, text, line, cursor_pos):
        self.flush()
        shell = self.shell
        if shell is None: return []
        # print repr(line), repr(text), cursor_pos
        shell.complete(text, line, cursor_pos)
        msg = shell.get_msg(timeout=1)
        if msg:
            matches = msg['content']['matches']
            return matches

    def question(self, symbol):
        if not (symbol.startswith(u'?') or symbol.endswith(u'?')):
            symbol = symbol + u'?'
        shell = self.shell
        shell.execute(symbol)
        m = shell.get_msg(1)
        self.process_result()
        if self.error:
            raise RemoteError(self.error)
        try:
            result = m['content']['payload'][0]['text']
            strip = re.compile('\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]')
            result = strip.sub('', result)
            return result
        except:
            return "object `{0}` not found.".format(symbol)

    def test(self, code):
        self.flush()
        shell, listener = self.shell, self.listener
        shell.execute(code)
        time.sleep(1)
        for m in shell.get_msgs():
            print_msg(m, 'shell_channel')
        for m in listener.get_msgs():
            print_msg(m, 'sub_channel')


def filter_unicode(s_repr):
    if not isinstance(s_repr, basestring):
        return s_repr
    def filter(m):
        code_point = int(m.group(1), 16)
        u = unichr(code_point)
        return u
    return re.sub(r'\\u(\w\w\w\w)', filter, s_repr)

def main(args):
    # this routine is used to test, not called by sublime text 2.

    global proxy
    proxy = IPythonProxy()
    try:
        from path import path
        dir = path(__file__).parent
        # proxy.execute(r'10+20', dir.joinpath('dump/expression.json'))
        # proxy.execute(ur'cd d:\src', dir.joinpath('dump/test.json'))
        # proxy.chdir(r'd:\src\zzj')
        # src = path(r'z:\src\demo\darkside.py')
        # src = open(src).read()
        # src = src.replace('# coding', '# ________')
        # proxy.test('envoy.run?')
        # info = proxy.info('a')
        #print proxy.getcwd()
        import time; time.sleep(10)
    except RemoteError:
        for name,line,_ in proxy.traceback:
            print 'Line {0} of {1}'.format(line, name)

    #proxy.execute('import envoy; envoy.run("notepad")')
    #print proxy.execute('1+4')
    #from pprint import pprint
    #ia = proxy.info(u'a')
    #from IPython import embed; embed() #zzj
    #print ia.base_class
    return 0

#==============================
if __name__ == "__main__":
    main(sys.argv)
    pass
#==============================
