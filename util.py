# -*- coding: utf-8 -*-

import string


def whitelisted(s):
    WHITELIST = "-_." + string.ascii_letters + string.digits
    SUBSTITUTE = "_"
    return "".join(c if c in WHITELIST else SUBSTITUTE for c in s)


def open_file(fname, mode="r"):
    import gzip
    if "gz" in fname.split("."):
        return gzip.open(fname, mode)
    return open(fname, mode)


def read_file(fname):
    with open_file(fname, "r") as f:
        return f.read().decode("utf-8")


def write_file(fname, data):
    with open_file(fname, "w") as f:
        f.write(data.encode("utf-8"))


SESSION = None


def get_url(url, **kwargs):
    import requests
    from time import sleep
    throttle = kwargs.pop("throttle", 1)  # be kind to server
    sleep(throttle)
    try:
        global SESSION  # reuse  q
        SESSION = SESSION or requests.session()
        kwargs.setdefault("timeout", 10)
        doc = SESSION.get(url, **kwargs)
        return doc.text  # unicode
    except requests.Timeout:
        print("timed out connecting to %s" % url)
        return None


def make_cache_fname(url):
    import hashlib
    from os.path import join
    from tempfile import gettempdir
    h = hashlib.md5(url).hexdigest()
    return join(gettempdir(), ".cache.%s.gz" % h)


def load_url(url, **kwargs):
    """ load with local cache """
    fname = make_cache_fname(url)
    try:
        return read_file(fname)
    except (IOError, OSError):
        pass
    doc = get_url(url, **kwargs)
    if doc:
        write_file(fname, doc)
    return doc


def load_doc(url, **kwargs):
    doc = load_url(url, **kwargs)
    import bs4
    return bs4.BeautifulSoup(doc) if doc else None
