import os
import sublime
import sublime_plugin

PACKAGE = "Cheat Sheets"
SETTINGS = PACKAGE + ".sublime-settings"

def get_default_directory():
    return os.path.join(sublime.packages_path(), PACKAGE, "Sheets")

class OpenCheatSheetCommand(sublime_plugin.WindowCommand):
    """A command that presents a list of cheat sheets, allowing the user to
    select one to open.
    """

    def get_directory(self):
        settings = sublime.load_settings(SETTINGS)
        directory = settings.get("directory", None)
        if directory is None:
            return get_default_directory()
        return os.path.expanduser(directory)

    def list_sheets(self):
        """List all files in the configured cheat sheet directory. Populates
        the sheets property to be used with show_quick_panel.
        """

        directory = self.get_directory()
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
