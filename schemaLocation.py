#!/usr/bin/python
import requests
import re
import sys
import os
from urllib.parse import urlparse

cache = {}


def localdir(url: str) -> str:
    uri = urlparse(url)
    return f"{os.getcwd()}/xsd/{uri.hostname}/{os.path.dirname(uri.path)}"


def grepLocation(haystack: str) -> [str]:
    matches = re.findall('schemaLocation="([^"]+)"', haystack)
    return matches


def fix(url: str, page: str) -> str:
    locations = grepLocation(page)
    for loc in locations:
        if loc.startswith("http"):
            link = localdir(loc)
            curdir = localdir(url)
            page = page.replace(loc, os.path.relpath(link, curdir))
    return page


def GET(url: str) -> str:
    if cache.get(url, None) is None:
        cache[url] = requests.get(url).content.decode("utf-8")
    return cache[url]


def DL(url: str) -> str:
    uri = urlparse(url)
    dir = f"xsd/{uri.hostname}/{os.path.dirname(uri.path)}"
    if not os.path.exists(dir):
        os.makedirs(dir)
    f = open(f"{dir}/{os.path.basename(uri.path)}", "w")
    page = fix(url, GET(url))
    f.write(page)
    return GET(url)


def get(url: str, depth: int):
    print(depth*' ' + url)
    page = DL(url)
    locations = grepLocation(page)
    for loc in locations:
        if not loc.startswith("http"):
            dir = os.path.dirname(url)
            loc = dir + "/" + loc
        get(loc, depth+1)


if __name__ == "__main__":
    get(sys.argv[1], 0)
