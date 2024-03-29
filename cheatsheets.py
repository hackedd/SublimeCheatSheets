import os
import sublime
import sublime_plugin

PACKAGE = "Cheat Sheets"
SETTINGS = PACKAGE + ".sublime-settings"

def get_default_directory():
    return os.path.join(sublime.packages_path(), PACKAGE, "Sheets")

def get_directory():
    settings = sublime.load_settings(SETTINGS)
    directory = settings.get("directory", None)
    if directory is None:
        return get_default_directory()
    return os.path.expanduser(directory)

class OpenCheatSheetCommand(sublime_plugin.WindowCommand):
    """A command that presents a list of cheat sheets, allowing the user to
    select one to open.
    """

    def list_sheets(self):
        """List all files in the configured cheat sheet directory. Populates
        the sheets property to be used with show_quick_panel.
        """

        directory = get_directory()
        if not os.path.exists(directory):
            sublime.error_message("The selected directory (%s) does not exist" % directory)
            return False

        self.sheets = []
        p = len(directory) + len(os.sep)

        for dirpath, dirnames, filenames in os.walk(directory):
            for entry in filenames:
                if not entry.startswith("."):
                    filename = os.path.join(dirpath, entry)
                    name = filename[p:].replace(os.sep, " - ")
                    self.sheets.append([name, filename])

            dirnames[:] = filter(lambda d: not d.startswith("."), dirnames)

        if not self.sheets:
            sublime.error_message("No cheat sheets found in selected directory (%s)" % directory)
            return False

        return True

    def run(self):
        if not self.list_sheets():
            return

        self.window.show_quick_panel(self.sheets, self.on_done)

    def on_done(self, picked):
        """Quick panel user selection handler - opens the selected cheat sheet.
        """

        if picked == -1:
            return

        name, filename = self.sheets[picked]

        flags = 0
        if sublime.load_settings(SETTINGS).get("transient"):
            flags |= sublime.TRANSIENT

        self.window.open_file(filename, flags)

class NewCheatSheetCommand(sublime_plugin.WindowCommand):
    """A command that allows the user to create a new cheat sheet.
    """

    def run(self):
        view = self.window.show_input_panel("New Cheat Sheet: ", "Name", self.on_done, None, None)
        view.run_command("select_all")

    def on_done(self, name):
        directory = get_directory()
        filename = os.path.join(directory, name)
        file_directory = os.path.dirname(filename)

        try:
            if not os.path.exists(file_directory):
                os.makedirs(file_directory)
            open(filename, "w").close()
        except IOError, ex:
            sublime.error_message("Unable to create cheat sheet '%s' (%s)" % (name, ex))
            return

        self.window.open_file(filename)
