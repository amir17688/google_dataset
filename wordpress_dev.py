import sublime
import sublime_plugin
import os.path
import platform
import re
import webbrowser

class WordpressdocCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print('doing stuff')
        for region in self.view.sel():
            if not region.empty():
                s = self.view.substr(region)
                webbrowser.open_new_tab('https://developer.wordpress.org/?s=' + s + '&post_type%5B%5D=wp-parser-function&post_type%5B%5D=wp-parser-hook&post_type%5B%5D=wp-parser-class&post_type%5B%5D=wp-parser-method')

class PhpdocCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print('doing stuff')
        for region in self.view.sel():
            if not region.empty():
                s = self.view.substr(region)
                webbrowser.open_new_tab('http://www.php.net/' + s)

class WordpressOpenConfigCommand(sublime_plugin.WindowCommand):
    def run(self):
        # Get config file location
        s = sublime.load_settings("WordPressDev.sublime-settings")
        config_file_location = s.get("wp_config_file")

        try:  # Open up config file
            with open(config_file_location, 'r') as wp_config:
                pass

            window = sublime.active_window()
            window.open_file(config_file_location)
        except IOError:  # Couldn't open config file, alert user
            # Open the settings file
            db_names.append("wp-config file doesn't exist, " +
                            'check your settings')
            sublime.status_message("wp-config file doesn't exist, " +
                                   'check your settings')

class WordpressOpenParentConfigCommand(sublime_plugin.TextCommand):
  
  # Set by is_enabled()
  base_name = ''
  path_parts = []

  def run(self, edit):
    self.base_name = self.view.file_name()
    self.path_parts = self.base_name.split('/')
    
    self.path_base = self.path_parts
    self.path_base.pop()
    self.path_base = '/'.join( self.path_base )

    if len(self.base_name) > 0:

      string_loc = self.base_name.find('wp-content')

      # sublime.error_message( 'path base : ' + self.path_base ) 
      if ( string_loc > 0 ):

        wp_install_base = self.base_name[0:string_loc]
        self.view.window().open_file( wp_install_base + 'wp-config.php')
      # elif ( True ):
        # Check if the wp-config file is in the current folder
        # in_curr_folder = self.view.window().open_file( self.path_base + '/wp-config.php') 
      else:
        sublime.error_message( 'You must run this command while viewing a file inside a WordPress install in the /wp-content folder or deeper.' ) 

    return False


class WordpressDbSwitcherCommand(sublime_plugin.WindowCommand):
    def run(self, extensions=[]):
        self.dblist = []

        # Pull the config file from the settings
        s = sublime.load_settings("WordPressDev.sublime-settings")
        self.config_file_location = s.get("wp_config_file")

        # Show the quick menu with the databases in it
        self.populate_db_list()
        self.show_db_list()

    def populate_db_list(self):
        if len(self.dblist) is 0:
            self.dblist = self.extract_wp_db_defs()

    def extract_wp_db_defs(self):
        db_names = []

        try:
            with open(self.config_file_location, 'r') as wp_config:
                file_contents = wp_config.read()
            wp_config.close()

            # DB's are defined as define('DB_NAME', 'wp_default');
            repatt = '(?:\/\/)?(define\(\'DB_NAME\'.*)'
            dbs = re.findall(repatt, file_contents)

            # For each database def we've found, pull out the name
            # and optional comment to show a nice list to the user
            for db in dbs:
                dbrepat = "define\('DB_NAME\',\s+'([^']*)'\);\s*(\/\/(.*))?"
                match = re.search(dbrepat, db)

                if match.group(3) is not None:
                    db_names.append("%s - %s" %
                                   (match.group(1), match.group(3)))
                else:
                    db_names.append(match.group(1))
        except IOError:  # Couldn't open config file, alert user
            #Open the settings file
            db_names.append("wp-config file doesn't exist, " +
                            'check your settings')
            sublime.status_message("wp-config file doesn't exist, " +
                                   'check your settings')

        return db_names

    def show_db_list(self):
        # Show the quick find popup
        window = sublime.active_window()
        window.show_quick_panel(self.dblist,
                                self.database_selected,
                                sublime.MONOSPACE_FONT)

    def database_selected(self, selectedListIndex):
        if 0 > selectedListIndex < len(self.dblist):
            return

        # If the user chose wp_def - my site split out the "wp_def"
        dbname = self.dblist[selectedListIndex].split(' ')[0]
        del self.dblist[:]  # clear the list

        self.switch_active_database(dbname)

    def switch_active_database(self, dbname):
        try:  # open the wordpress config file
            with open(self.config_file_location, 'r') as wp_config:
                file_contents = wp_config.read()
            wp_config.close()

            # Comment out all uncommented db
            uncommentedDB = r'([^\/\/])define\(\'DB_NAME\''
            commentedDB = r"\1//define('DB_NAME'"
            file_contents = re.sub(uncommentedDB,
                                   commentedDB,
                                   file_contents)

            # Un-comment our our chosen database
            commentedDB = r'\/\/define\(\'DB_NAME\',\s+\'%s\'' % dbname
            uncommentedDB = "define('DB_NAME', '%s'" % dbname
            file_contents = re.sub(commentedDB,
                                   uncommentedDB,
                                   file_contents)

            # Overwrite the config file with our new config
            with open(self.config_file_location, 'w') as wp_config:
                wp_config.write(file_contents)
            wp_config.close()
            message = "Switched database to %s" % dbname
            sublime.status_message(message)
        except IOError:  # Couldn't open config file, alert user
            sublime.status_message("wp-config file doesn't exist, " +
                                   'check your settings')


class WordpressDebugToggleCommand(sublime_plugin.WindowCommand):
    def run(self):
        s = sublime.load_settings("WordPressDev.sublime-settings")
        config_file_location = s.get("wp_config_file")

        try:  # open the wordpress config file
            with open(config_file_location, 'r') as wp_config:
                file_contents = wp_config.read()
            wp_config.close()

            # Toggle the WP_DEBUG value
            debugpat = "define\('WP_DEBUG\',\s+(true|false)\);"
            match = re.search(debugpat, file_contents)
            debugStatus = match.group(1)

            if debugStatus == 'true':
                debugStatus = 'false'
            else:
                debugStatus = 'true'

            currentDebugValue = r'define\(\'WP_DEBUG\', (true|false)'
            newDebugValue = r"define('WP_DEBUG', %s" % debugStatus
            file_contents = re.sub(currentDebugValue,
                                   newDebugValue,
                                   file_contents)

            # Overwrite the config file with our new config
            with open(config_file_location, 'w') as wp_config:
                wp_config.write(file_contents)
            wp_config.close()
            message = "Toggled WP_DEBUG to %s" % debugStatus
            sublime.status_message(message)
        except IOError:  # Couldn't open config file, alert user
            sublime.status_message("wp-config file doesn't exist, " +
                                   'check your settings')
