# https://pythonhosted.org/setuptools/setuptools.html#namespace-packages
__import__('pkg_resources').declare_namespace(__name__)

import json
import os.path
import sqlite3
import logging

import mapzen.whosonfirst.utils

def valid_modes():
    
    return (
        "directory",
        "filelist",
        "files",
        "meta",
        "repo",
        "sqlite"
    )

class indexer:

    def __init__ (self, mode, callback):
        
        self.mode = mode
        self.callback = callback

    def process(self, feature):
        yield self.callback(feature)

    def index_paths(self, paths):

        for _ in self.iter_paths(paths):
            pass

    def index_path(self, path):

        for _ in self.iter_path(path):
            pass
        
    def iter_paths(self, paths):    

        for path in paths:
            
            iter = self.iter_path(path)

            for i in iter:
                yield i
                
    def iter_path(self, path):

        iter = None
        
        if self.mode == "directory":
            iter = self.index_directory(path)

        elif self.mode == "filelist":
            iter = self.index_filelist(path)

        elif self.mode == "files":
            iter = self.index_file(path)

        elif self.mode == "meta":
            # Python 3 migration-ify
            # (20200910/vicchi)
           
            raise Exception("Please implement me")
        
        elif self.mode == "repo":
            iter = self.index_repo(path)
                
        elif self.mode == "sqlite":
            iter = self.index_sqlite(path)
                
        else:
            # Python 3 migration-ify
            # (20200910/vicchi)
            raise Exception("Invalid or unsupported mode")

        for i in iter:
            for j in i:
                yield j

    def index_file(self, path):

        f = mapzen.whosonfirst.utils.load_file(path)
        yield self.process(f)

    def index_files(self, paths):
        
        for path in paths:
            yield self.index_file(path)

    def index_filelist(self, path):

        fh = open(path, "r")

        for ln in fh:
            for f in self.index_file(ln.strip()):
                yield f
            
    def index_directory(self, path):

        iter = mapzen.whosonfirst.utils.crawl(path, inflate=True)

        for f in iter:
            yield self.process(f)

    def index_repo(self, path):

        data = os.path.join(path, "data")
        
        for i in self.index_directory(data):
            yield i

    def index_sqlite(self, path):
        
        conn = sqlite3.connect(path)

        rsp = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        has_table = False
        
        for row in rsp:
            if row[0] == "geojson":
                has_table = True
                break

        if not has_table:
            # Python 3 migration-ify
            # (20200910/vicchi)
            raise Exception("database is missing 'geojson' table")
        
        rsp = conn.execute("SELECT body FROM geojson")

        for row in rsp:
            f = json.loads(row[0])
            yield self.process(f)
        
