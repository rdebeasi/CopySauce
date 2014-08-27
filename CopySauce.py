import shutil, json, time, os, sys, re, stat, shlex
from win32com.shell import shell
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from subprocess import call
from time import strftime

defaults = {
    "web_root":"",
    "folders_to_watch": ["css", "images", "img", "javascript", "js", "scripts", "layouts", "views", "xsl"],
    "file_exclude_patterns": ["^\.", ".*\\.cs$","(?i).*\\.tmp$"],
    "folder_exclude_patterns": ["^\."],
    "cmd_after_copy": ""
}

class ChangeHandler(FileSystemEventHandler):
    def __init__(self,project_path,web_root,file_exclude_patterns,folder_exclude_patterns,cmd_after_copy):
        self.project_path = project_path
        self.web_root = web_root
        self.file_exclude_patterns = file_exclude_patterns
        self.folder_exclude_patterns = folder_exclude_patterns
        self.cmd_after_copy = cmd_after_copy

    def _timestamp(self):
        return strftime("[%I:%M:%S %p] ")

    def _get_directories(self, path):
        directories = []
        while 1:
            path, directory = os.path.split(path)

            if directory != "":
                directories.append(directory)
            else:
                if path != "":
                    directories.append(path)
                break
        return directories

    def exclude_check(self, src, is_directory):
        for pattern in self.folder_exclude_patterns:
            for directory in self._get_directories(src):
                if re.match(pattern,directory):
                    # print "Excluding directory", os.path.basename(src)
                    return True
        if not is_directory:
            for pattern in self.file_exclude_patterns:
                if re.match(pattern,os.path.basename(src)):
                    # print "Excluding file", os.path.basename(src)
                    return True

    def cmd_after_copy_check(self,dst):
        if len(self.cmd_after_copy):
           call(shlex.split(self.cmd_after_copy) + [dst])

    def on_created(self, event):
        src = event.src_path
        dst = src.replace(self.project_path,self.web_root)
        if self.exclude_check(src,event.is_directory):
            return
        try:
            if (event.is_directory):
                shutil.copytree(src,dst)
            else:
                # check if directory exists
                dir = os.path.dirname(dst)
                if not os.path.exists(dir):
                    os.makedirs(dir)
                shutil.copy(src,dst)
            # include extra whitespace after "added" so that the paths line up
            print self._timestamp(), "Added   ", src.replace(self.project_path,"")
            self.cmd_after_copy_check(dst)
        except Exception, err:
            print err

    def on_modified(self, event):
        src = event.src_path
        dst = src.replace(self.project_path,self.web_root)
        if self.exclude_check(src,event.is_directory):
            return
        try:
            if not event.is_directory:
                # check if directory exists
                dir = os.path.dirname(dst)
                if not os.path.exists(dir):
                    os.makedirs(dir)
                shutil.copy(src,dst)
                print self._timestamp(), "Updated ", src.replace(self.project_path,"")
                self.cmd_after_copy_check(dst)
        except Exception, err:
            print err

    def _remove_readonly(self, fn, path, excinfo):
        excvalue = exc[1]
        if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            func(path)
        else:
            raise

    def on_deleted(self, event):
        src = event.src_path
        dst = src.replace(self.project_path,self.web_root)
        if self.exclude_check(src,event.is_directory):
            return
        try:
            if (event.is_directory):
                shutil.rmtree(dst, ignore_errors=False, onerror=self._remove_readonly)
            else:
                os.unlink(dst)
            print self._timestamp(), "Removed ", src.replace(self.project_path,"")
        except Exception, err:
            print err

class ShellError(Exception):
    def __init__(self, message):
        print "An error occurred!\n"
        raw_input("%s\n" % message)
        sys.exit()

class Settings():
    def __init__(self,project_path):
        self.settings = defaults
        self.settings_file = os.path.join(project_path,".CopySauce.json")
        if not os.path.exists(self.settings_file):
            open(self.settings_file,"ab+").write(json.dumps(self.settings, sort_keys=True, indent=4, separators=(',', ': ')))
        try:
            self.settings = json.loads(open(self.settings_file,"ab+").read())
        except ValueError, e:
            pass
        if not "web_root" in self.settings or not len(self.settings['web_root']):
            self.choose()

    def choose(self):
        print "Choose the web root directory...\n\n"
        web_root = _directory()
        if web_root == [] or not web_root:
            raise ShellError("Please choose a web root directory")
        self.settings["web_root"] = web_root
        open(self.settings_file,"w+").write(json.dumps(self.settings, sort_keys=True, indent=4, separators=(',', ': ')))

    def get(self,key = None):
        if not key:
            return self.settings
        if key not in self.settings:
            return []
        return self.settings[key]

class Project:
    def __init__(self, path = None):
        self.projects = []
        if path:
            self.path = path
        else:
            app_data = os.path.join(os.path.expanduser("~"),"AppData\\Local\\CopySauce")
            if not os.path.exists(app_data):
                os.makedirs(app_data)
            self.projects_file = os.path.join(app_data,"CopySauce Projects.json")
            try:
                self.projects = json.loads(open(self.projects_file,"ab+").read())['projects']
            except ValueError, e:
                pass
            if len(self.projects):
                self.list()
            else:
                self.choose()

    def choose(self):
        print "Choose the project directory...\n"
        self.path = _directory()
        if self.path == [] or not self.path:
            raise ShellError("Please choose a project directory")
        if self.path not in self.projects:
            self.projects.append(self.path)
            open(self.projects_file,"w+").write(json.dumps({"projects":self.projects}, sort_keys=True, indent=4, separators=(',', ': ')))

    def list(self):
        if len(self.projects):
            for i in range(len(self.projects)):
                print str((i + 1)) + ".", self.projects[i]
            print
            choice = raw_input("Choose a previous project or press enter to choose a new one. [" + "".join(str(n) for n in range(1,len(self.projects)+1)) + "]\n\n")
            print
        try:
            int(choice)
            if int(choice) in range(1,len(self.projects) + 1):
                self.path = self.projects[(int(choice) - 1)]
        except (ValueError, UnboundLocalError):
            self.choose()

def _directory():
    try:
        pidl, display_name, image_list = shell.SHBrowseForFolder()
        return shell.SHGetPathFromIDList(pidl)
    except TypeError, e:
        if e.message ==  "None is not a valid ITEMIDLIST in this context":
            return []
    except Exception, e:
        return False

if __name__ == "__main__":
    print "\nCopySauce running...\n"

    if len(sys.argv) == 3 and sys.argv[1] == "-p":
        project = Project(sys.argv[2])
    else:
        project = Project()

    settings = Settings(project.path)
    event_handler = ChangeHandler(project.path,settings.get("web_root"),settings.get("file_exclude_patterns"),settings.get("folder_exclude_patterns"),settings.get("cmd_after_copy"))

    print "Project: %s" % project.path
    print "Web root: %s\n" % settings.get("web_root")

    watching = False
    for path in settings.get('folders_to_watch'):
        if not os.path.exists("%s\\%s" % (project.path,path)):
            #print "Skipping ", path
            continue
        print "Watching", path + "..."
        p = "%s\\%s" % (project.path,path)
        observer = Observer()
        observer.schedule(event_handler, path=p, recursive=True)
        observer.start()
        watching = True
    print
    if not watching:
        raise ShellError("No folders found to watch")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
