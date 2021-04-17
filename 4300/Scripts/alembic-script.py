#!"c:\users\eric whitehead\desktop\junioryear\spring\cs4300\cs4300sp2020-nmm85-cal362-ajl346-ew424-djf252\4300\scripts\python.exe"
# EASY-INSTALL-ENTRY-SCRIPT: 'alembic==1.4.0','console_scripts','alembic'
__requires__ = 'alembic==1.4.0'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('alembic==1.4.0', 'console_scripts', 'alembic')()
    )
