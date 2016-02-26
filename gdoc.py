#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util import read_file, load_url
from pandas import read_csv
from StringIO import StringIO
from filter import FILE_SELECTION

FILE_GDOC = "gdoc.conf"


def download():
    url = read_file(FILE_GDOC).strip()
    print("loading %s" % url)
    sheet = load_url(url)
    phenos = read_csv(StringIO(sheet))
    sel = phenos[phenos["malformation?"] == "y"]["phenotype"]
    sel.to_csv(FILE_SELECTION, index=False)
    print("got %d selected phenotypes out of %d, stored in %s" %
          len(sel), len(phenos), FILE_SELECTION)


if __name__ == '__main__':
    download()
