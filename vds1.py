import idaapi

def main():
    if not idaapi.init_hexrays_plugin():
        return False

    print "Hex-rays version %s has been detected" % idaapi.get_hexrays_version()

    f = idaapi.get_func(idaapi.get_screen_ea());
    if f is None:
        print "Please position the cursor within a function"
        return True

    cfunc = idaapi.decompile(f);
    if cfunc is None:
        print "Failed to decompile!"
        return True

    sv = cfunc.get_pseudocode();
    for i in xrange(0, sv.size()):
        line = idaapi.tag_remove(str(sv[i]));
        print line

    return True

if main():
    idaapi.term_hexrays_plugin();
