# mediasort
Move images and video files into subfolders grouped by year, month or day.
If EXIF data exists, exif datetime will be used.
If there is no EXIF datetime, the filename will be parsed for a datetime string.

This was made for usage on my Synology Diskstation.

* Install the DSM package Python Modules to run it

## Usage
```
Usage: mediasort.py [options]

Options:
  -h, --help            show this help message and exit
  -i SOURCE, --input=SOURCE, --source=SOURCE 
                       Read from folder SOURCE. Default = current dir
  -o TARGET, --output=TARGET, --target=TARGET
                        Write all files to a single location = TARGET. If not
                        specified = current working dir
  -r LEVEL, --recursive=LEVEL, --recursionlevel=LEVEL
                        Levels of subfolders to scan. 0 = unlimited
  -g GROUP, --groupby=GROUP
                        GROUP = YEARLY|MONTHLY|DAILY. Default = MONTHLY
  -s, --simulate        Simulation mode. No files will be moved
  -l LOGLEVEL, --loglevel=LOGLEVEL
                        LOGLEVEL = ERROR|WARNING|INFO|DEBUG
