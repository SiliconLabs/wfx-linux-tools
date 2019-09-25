#!/usr/bin/python
from cgi_commons import *

import sys
import json
import collections


def main():
    bash_res("wpa_cli disconnect")
    print( bash_res("wpa_cli status") )


if __name__=="__main__":
    main()
