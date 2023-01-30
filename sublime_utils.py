# coding: utf-8
import os, sys
from sublime import *

def get_selection(view=None):
    if not view:
        view = active_window().active_view()
    return view.sel()

def set_selection(view, region):
    sel = view.sel()
    sel.clear()
    sel.add(region)

def redraw_view(view=None):
    if not view:
        view = active_window().active_view()
    pos = view.viewport_position()
    pos = (pos[0], pos[1]+1)
    view.set_viewport_position(pos)
    pos = (pos[0], pos[1]-1)
    view.set_viewport_position(pos)

def select_line(view, line):
    pt = view.text_point(line-1, 0)
    ln = view.line(pt)
    sel = view.sel()
    sel.clear()
    sel.add(ln)
    view.show_at_center(ln)

def select_all(view):
    size = view.size()
    sel = view.sel()
    sel.clear()
    sel.add( Region(0,size) )

def get_view_text(view):
    region = Region(0, view.size())
    return view.substr(region)

def set_view_text(view, text):
    if not isinstance(text, unicode):
        text = unicode(text)
    view.settings().set("syntax", "Packages/Python/Python.tmLanguage")
    r = Region(0, view.size())
    e = view.begin_edit()
    view.erase(e, r)
    view.insert(e, 0, text)
    # view.show(0)

def flash_select(view, region, callback=None):
    sel = view.sel()
    old_sel = list(sel)
    sel.clear()
    sel.add(region)

    def restore():
        sel.clear()
        b = old_sel[0].b
        sel.add(Region(b,b))
        redraw_view(view)
        if callback:
            set_timeout(callback, 10)

    set_timeout(restore, 50)


def show_panel(name):
    window = active_window()
    window.run_command(
        "show_panel", {"panel": "output." + name}
    )

def hide_panel():
    window = active_window()
    window.run_command(
        "hide_panel", { "cancel": True }
    )

def show_msg(msg):
    window = active_window()
    panel = window.get_output_panel('flash_message')
    set_view_text(panel, msg)
    show_panel('flash_message')
    # hide after a while
    set_timeout(hide_panel, 1200)


#==============================
if __name__ == "__main__":
    main(sys.argv)
    pass
#==============================
