"""
Work in progress. Still many places to iron out...
"""

import sys, re
# hack against IPython
sys.argv = ['']

from IPython.zmq.blockingkernelmanager import BlockingKernelManager
from os.path import expanduser, join
from time import sleep
from path import path

import sublime
import sublime_plugin

from sublime_utils import redraw_view, select_line, select_all, \
                          set_view_text, get_view_text, flash_select, set_selection

from ipconsole import IPythonProxy, RemoteError
proxy = IPythonProxy()

# text processing
def strip_line_comment(line):
    if type(line) is not unicode:
        line = unicode(line)
    i, n = 0, len(line)
    count = 0  # num of '/"
    while i < n:
        c = line[i]
        if c == u'\\':
            i += 2
            continue
        if c in [u'"', u"'"]: count += 1
        elif c == u'#' and count % 2 == 0:
            return line[:i].rstrip()
        i += 1
    return line

def strip_color_escapes(s):
    strip = re.compile('\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]')
    return strip.sub('', s)

# not used. new version makes use of python ast module
def get_assigned_var(src):
    src = src.split('\n')[-1]
    #print "src is:", src
    m = re.match(r'(\w+)\s*=.*', src)
    if not m: return None
    return m.group(1)

def clear_code(python_src):
    python_src = python_src.splitlines(True) # keeps line ends

    # find out indent
    lines = [l for l in python_src if l.strip()]
    if not lines: return ''
    for i, c in enumerate(lines[0]):
        if not c.isspace():
            start = i
            break

    lines = [l[start:] for l in python_src] # python_src has '\n's
    lines = [strip_line_comment(l) for l in lines]
    if len(lines) == 1:
        vars = get_assigned_vars(lines[0])
        if vars:
            append = u'; {0}'.format(u','.join(vars))
            lines[0] = lines[0] + append
            print lines[0]
    return ''.join(lines)

import ast
def get_assigned_vars(line_code):
    try:
        node = ast.parse(line_code)
    except SyntaxError:
        return None
    if type(node.body[0]) is ast.Assign:
        target = node.body[0].targets[0]
        if type(target) is ast.Name:
            return [target.id]
        elif type(target) is ast.Tuple:
            return [e.id for e in target.elts]
    return None

class IpythonExecCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        sel = view.sel()

        sel0 = sel[0]
        if view.substr(sel0).strip().startswith(u'#'):
            sel0 = sublime.Region(sel0.begin(), sel0.begin())
        if sel0.empty():
            block = view.line(sel[0])
            the_line = view.substr(block)
            # stripping preceding spaces
            strip_count = len(the_line) - len(the_line.lstrip())
            block = sublime.Region(block.begin()+strip_count, block.end())
        elif '\n' in view.substr(sel0):
            # multiline selection
            block = view.line(sel[0])
        else:
            block = sel0
        code = view.substr(block)
        code = clear_code(code)

        # result should be a unicode string
        def update_result(result, varnames=None):
            if not sel0.empty(): return
            if result is None: result = 'None'
            sel_line = view.line(sel0)
            line = view.substr(sel_line)
            if sel0.empty():
                varnames = get_assigned_vars(line)
            else:
                varnames = None

            # to_underscore = lambda m: u'"{0}"'.format(u'_'*len(m.group(1)))
            # line_x = re.sub(ur'"(.*)"', to_underscore, line)
            # line_x = re.sub(ur"'(.*)'", to_underscore, line_x)
            # if u'#' in line_x:
            #     i = line_x.rfind(u'#')
            #     line = line[:i].rstrip()
            line = strip_line_comment(line)
            if not varnames:
                append = u'  # -> ' + result
            else:
                varnames = u', '.join(varnames)
                append = u'  # {0} -> {1}'.format(varnames, result)
            
            # selection points
            line += append
            a = sel_line.begin() + len(line)
            b = a - len(append)

            e = view.begin_edit()
            view.replace(e, view.line(sel0), line)
            set_selection(view, sublime.Region(a,b))
            view.end_edit(e)

        def eval_code():
            try:
                result = proxy.execute(code)
            except RemoteError:
                row_offset = view.rowcol(block.begin())[0]
                handle_remote_error(proxy, view, row_offset)
                return
            if sel0.empty():
                if not code.startswith((
                    'from ','import ',
                    '%'    # ipython magic commands
                )):
                    update_result(result)
            elif '\n' not in code:
                # selection on single line, we replace it evaled
                edit = view.begin_edit()
                view.replace(edit, sel0, result)
                view.end_edit(edit)
                a = sel0.begin()
                b = a + len(result)
                sel.clear()
                sel.add(sublime.Region(a,b))
            else:
                pass # do nothing on multiline selection

        def question_code():
            try:
                result = proxy.question(code)
            except RemoteError:
                handle_remote_error(proxy)
                return
            window = view.window()
            panel = window.get_output_panel('ipython_object_info')
            window.run_command(
                "show_panel", {"panel": "output.ipython_object_info"}
            )
            window.focus_view(panel)
            set_view_text(panel, result)
            panel.settings().set("syntax", "Packages/IPython/ipython_output.tmLanguage")
            panel.show(panel.size(), False) # scroll to bottom

            def foo():
                view.show_at_center(view.sel()[0].begin())
            sublime.set_timeout(foo, 10)


        if code.endswith(u'?') or code.startswith(u'?'):
            set_selection(view, block)
            sublime.set_timeout(question_code, 10)
        else:
            flash_select(view, block, callback=eval_code)

        return []



class PythonCompletions(sublime_plugin.EventListener):
    ''''Provides rope completions for the ST2 completion system.'''
    def on_query_completions(self, view, prefix, locations):
        l = locations[0]
        line = view.line(l)
        begin,end = line.begin(), line.end()
        line = view.substr(line).strip()
        text = view.substr(sublime.Region(begin, l)).strip()
        cursor_pos = len(text)
        # print repr(line), repr(text), cursor_pos
        matches = proxy.complete(text, line, cursor_pos)

        i = cursor_pos - len(prefix)
        matches = [a[i:] for a in matches]
        return [('{0} (IPython)'.format(a), a) for a in matches]

class IpythonExecFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        text = get_view_text(view)
        sel0 =view.sel()[0]
        select_all(view)
        
        def todo():
            sel = sublime.active_window().active_view().sel()
            sel.clear()
            sel.add(sel0)
            redraw_view()
            sublime.set_timeout(execute, 1)

        def execute():
            try:
                if view.file_name():
                    filename = path(view.file_name())
                    filedir = filename.parent
                    proxy.chdir(filedir)
                code2 = re.sub('# coding', '# ', text)
                proxy.execute(code2)
            except RemoteError:
                handle_remote_error(proxy, view)

        sublime.set_timeout(todo, 50)

        return []

def handle_remote_error(proxy, view, row_offset=0):
    print proxy.error
    window = view.window()
    panel = window.get_output_panel('ipython_traceback')
    set_view_text(panel, proxy.error)
    window.run_command(
        'show_panel', {'panel': 'output.ipython_traceback'})
    window.focus_view(panel)

    tb = proxy.traceback
    if '<ipython-input' in tb[0][0]:
        line = tb[0][1] + row_offset
        select_line(view, line)
        redraw_view(view)
    if len(tb) > 1:
        detailed_tb = []
        for filename, line, t in tb:
            if '<ipython-input' in filename:
                line += row_offset
            x = 'Line {0} of {1}'.format(line, filename)
            lines = t.splitlines()
            lines.insert(0, x)
            detailed_tb.append(lines)
        sublime.active_window().show_quick_panel(detailed_tb, sys)

class MyListener(sublime_plugin.EventListener):
    def on_activated(self, view):
        proxy.disabled = False
        #print "on_activated"

