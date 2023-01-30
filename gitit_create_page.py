def create_file(text):
    filename = text + ".page"
    print(filename)
    open(filename, "a").close()

try:
    import vim
    import re
    link = "\[(.+)\]\((.*)\)"
    match = re.search(link, vim.current.line)

    if match:
        linktext = match.group(1)
        filename = match.group(2) 
        if filename != "":
            create_file(filename)
        else:
            create_file(linktext)

except:
    print("")
