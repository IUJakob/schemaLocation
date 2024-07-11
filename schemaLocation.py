#!/usr/bin/python
import requests
import re
import sys
import os
from urllib.parse import urlparse

cache = {}
errors = []


class error:
    def __init__(self, url: str, status: int):
        self.url = url
        self.status = status


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
            page = page.replace(loc, f"{os.path.relpath(link, curdir)}/{os.path.basename(loc)}")
    return page


def GET(url: str) -> str:
    if cache.get(url, None) is None:
        req = requests.get(url)
        if req.status_code > 220:
            errors.append(error(url, req.status_code))
        cache[url] = req.content.decode("utf-8")
    return cache[url]


def DL(url: str) -> str:
    uri = urlparse(url)
    dir = f"xsd/{uri.hostname}/{os.path.dirname(uri.path)}"
    if not os.path.exists(dir):
        os.makedirs(dir)
    page = fix(url, GET(url))
    f = open(f"{dir}/{os.path.basename(uri.path)}", "w")
    f.write(page)
    f.close()
    return GET(url)


def get(url: str, depth: int):
    print(depth*' ' + url)
    try:
        page = DL(url)
        locations = grepLocation(page)
        for loc in locations:
            if not loc.startswith("http"):
                dir = os.path.dirname(url)
                loc = dir + "/" + loc
            get(loc, depth+1)
    except KeyboardInterrupt:
        errors.append(error(url,0))
        raise
    except:
        errors.append(error(url, 0))


if __name__ == "__main__":
    try:
        get(sys.argv[1], 0)
    except KeyboardInterrupt:
        ...
    finally:
        if len(errors) > 0:
            print("Errors:")
            for e in errors:
                print(f"{e.status}: {e.url}")
