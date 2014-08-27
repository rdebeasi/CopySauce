#CopySauce

CopySauce was developed for working on Sitecore .NET projects to circumvent the build process by copying static files to the web root. It should also work for .NET projects where the web root is separate to the source files.

[Download CopySauce.exe](https://github.com/rdebeasi/CopySauce/releases)

##Configuring

When first launched there will be a prompt to locate the project and web root directories. After this a `.CopySauce.json` will be created in the root of the project directory with these options:

    {
        "cmd_after_copy": "",
        "file_exclude_patterns": [
            "^\\.",
            ".*\\.cs$",
            "(?i).*\\.tmp$"
        ],
        "folder_exclude_patterns": [
            "^\\."
        ],
        "folders_to_watch": [
            "css",
            "images",
            "img",
            "javascript",
            "js",
            "scripts",
            "layouts",
            "views",
            "xsl"
        ],
        "web_root": ""
    }

##Requirements

To build CopySauce, you'll need the following:

- Windows
- Python 2.7
- [Python for Windows extensions](http://sourceforge.net/projects/pywin32/)
- [Watchdog](http://pypi.python.org/pypi/watchdog) module (install with [Setuptools](https://pypi.python.org/pypi/setuptools#windows))

##Optional

- [PyInstaller](http://www.pyinstaller.org/) (py2exe would probably work as well) can be used to make an executable:

        python pyinstaller.py -F CopySauce.py -i CopySauce.ico

- [UPX](http://upx.sourceforge.net/#download) for reducing binary size