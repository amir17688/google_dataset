#   __        __   _       ____  _     _
#   \ \      / /__| |__   / ___|| |__ (_)_ __ ___
#    \ \ /\ / / _ \ '_ \  \___ \| '_ \| | '_ ` _ \
#     \ V  V /  __/ |_) |  ___) | | | | | | | | | |
#      \_/\_/ \___|_.__/  |____/|_| |_|_|_| |_| |_|
#
#    The 80/20 friggn' rule --
#    Gotta' use it. It's a tool
#    Reducing clutter that we pack
#    Into our lives to hold us back.
#    
#    When goals elude and time flies past
#    And with each step, you're still in last
#    Consider how you lost your aim
#    You'll find recursive tasks to blame.
#    
#    With each thing you set to do,
#    A hundred more come fly at you.
#    Until at last, you quite forget
#    The goal for which you had first set.
#    
#    The 80/20 Rule just asks
#    That you should start to plan your tasks
#    So when you're only one-fifth done
#    You could have stopped and still have won.
#
#    --December 7, 2002, Mike Levin

from pipulate import *
import os
import globs, common
print(r'''********************* Welcome to Pipulate, running on **************************
        ____        _   _                    _______ _           _
       |  _ \ _   _| |_| |__   ___  _ __    / /  ___| | __ _ ___| | __
       | |_) | | | | __| '_ \ / _ \| '_ \  / /| |_  | |/ _` / __| |/ /
       |  __/| |_| | |_| | | | (_) | | | |/ / |  _| | | (_| \__ \   <
       |_|    \__, |\__|_| |_|\___/|_| |_/_/  |_|   |_|\__,_|___/_|\_\
              |___/

 Hello World! This is a native Python webserver: no Apache, nginx or node.js.
 Pipulate is designed for exclusive access to the webserver, letting you watch
 this console like a web logfile. Feel free to crack it open and customize.

 THIS IS     THIS IS YOUR BROWSER                 THIS IS PIPULATE     THIS IS
   YOU            ____ ____                     (disposable servers)    THIS!
              ,__/site\____\___. ...which       ,------------------.  ,-------.
    O         |                ||    SENDS      |   ...to the      |  | Debug |
   /|\---1.-----> bookmarklet ----------2.-------> Pipulate Server--->|Console|
   ( ) CLICK  | with a website ||     URL and   |   | which checks |  '-------'
  =====       |   displaying.  ||      context  '---|----|--|--|---'
    |         |                ||                   |    |  |  '------------> ?
    5.        '----------------'|     then sends    |    |  '--------3.-----> ?
  SEE THE--->  | to Google Sheet|<-------4.---------'    '------------------> ?
  RESULTS      '----------------'   a response                ...stuff on net''')

if __name__ == "__main__":
  globs.WEB = True
  if 'pipulate' in socket.gethostname():
    globs.PCOM = True
    app.run(host='0.0.0.0', port=80, debug=True)
  else:
    app.run(host='0.0.0.0', port=8888, debug=False)

