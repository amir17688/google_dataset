#   ____                   ____  _     _           
#  / ___|_ __ ___  _ __   / ___|| |__ (_)_ __ ___  
# | |   | '__/ _ \| '_ \  \___ \| '_ \| | '_ ` _ \ 
# | |___| | | (_) | | | |  ___) | | | | | | | | | |
#  \____|_|  \___/|_| |_| |____/|_| |_|_|_| |_| |_|
                                                  
#         To every man there comes in his lifetime that special
#         moment when he is figuratively tapped on the shoulder
#            and offered a chance to do a very special thing,
#            unique to him and fitted to his talents. What a
#             tragedy if that moment finds him unprepared or
#        unqualified for the work which would be his finest hour.

#                        -- Winston Churchill

from pipulate import *
import globs, common

def Scheduler():
  import os.path
  if os.path.isfile(globs.TOKEN) and os.path.getsize(globs.TOKEN) > 0:
    print('''
          _                      _             _       _                 
         | |    ___   ___  _ __ (_)_ __  _   _| | __ _| |_ ___           
         | |   / _ \ / _ \| '_ \| | '_ \| | | | |/ _` | __/ _ \          
         | |__| (_) | (_) | |_) | | |_) | |_| | | (_| | ||  __/_   _   _ 
         |_____\___/ \___/| .__/|_| .__/ \__,_|_|\__,_|\__\___(_) (_) (_)
                          |_|     |_|                                    
    ''')
    token = freshtoken(globs.TOKEN)
    creds = Credentials(access_token=token)
    import gspread
    gsp = gspread.authorize(creds)
    doclist = gsp.openall()
    #for x in range(2): #Accomodate for API failures
    for onedoc in doclist:
      if onedoc.title != 'Users':
        print(r'''
              _   _           _     ____  _               _   
             | \ | | _____  _| |_  / ___|| |__   ___  ___| |_ 
             |  \| |/ _ \ \/ / __| \___ \| '_ \ / _ \/ _ \ __|
             | |\  |  __/>  <| |_   ___) | | | |  __/  __/ |_ 
             |_| \_|\___/_/\_\\__| |____/|_| |_|\___|\___|\__|
        ''')
        dockey = onedoc.get_id_fields()['spreadsheet_id']
        print('PROCESSING SHEET: "%s" with key %s' % (onedoc.title, dockey))
        out("ENTERING PIPULATE FUNCTION", "0")
        STREAMIT = Pipulate(dockey=dockey, token=token)
        for thebits in STREAMIT:
          print(thebits)
        out("EXITING PIPULATE FUNCTION", "0", '-')
    print('''
              _____           _   _                      _ 
             | ____|_ __   __| | | |    ___   ___  _ __ | |
             |  _| | '_ \ / _` | | |   / _ \ / _ \| '_ \| |
             | |___| | | | (_| | | |__| (_) | (_) | |_) |_|
             |_____|_| |_|\__,_| |_____\___/ \___/| .__/(_)
                                                  |_|      
    ''')
  else:
    print("Please configure Pipulate by visiting from a browser.")

if __name__ == '__main__':
  socket.setdefaulttimeout(180)
  Scheduler()
