#!/usr/bin/env python3
import xml.dom.minidom
from xml.dom.minidom import Node
import os.path
import os
from sys import argv
import shutil

''' 
  Copyright 2017 VirtualIceShard
  
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
 
     http://www.apache.org/licenses/LICENSE-2.0
 
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
'''
 

class Wilby(object):
    folder_list = []
    fl_orient = []
    dirl = []
    oriens = []
    has_loaded_before = False
    defdir = "organize"
    defconf = "orgstructure.xml"
    def load_config(self,path):
        try:
            configf = xml.dom.minidom.parse(path)
            fstruct = configf.getElementsByTagName("folderstructure")[0]
            for fol in fstruct.childNodes:
                if not fol.nodeType == Node.TEXT_NODE:
                    self.folder_list.append(fol)
                    fl_orien = configf.getElementsByTagName("file-orientation")[0]
            for fl_or in fl_orien.getElementsByTagName("for"):
                self.fl_orient.append(fl_or)
        except Exception:
            print("Exception ocurred when loading config")
            
    def inner_forchilds(self, el, dirlist, setlist=None):
        atleast1 = False
        if not setlist:
            setlist = [el.getAttribute("name")]
            ret = []
        if(len(el.childNodes)):
            for c in el.childNodes:
                if not c.nodeType == Node.TEXT_NODE:
                    setlist.append(c.getAttribute("name"))
                    self.inner_forchilds(c, dirlist , setlist)
                    setlist.pop()
                    atleast1 = True
            if not atleast1:
                print("No tag childs found")
                dirlist.append("/".join(setlist))
        else:
            print("Has no childs")
            dirlist.append("/".join(setlist))

        
    def process_dirs(self):
        if len(self.folder_list):
            for f in self.folder_list:
                self.inner_forchilds(f, self.dirl)
        else:
             print("Dir list not loaded!")
             return

    def check_dirs(self,rootdir):
        if not rootdir.startswith("/"):
            rootdir = rootdir + "/"
        if len(self.dirl):
            for dir in self.dirl:
                foldtotal = []
                for fold in dir.split("/"):
                    foldtotal.append(fold)
                    ftotal = "/".join(foldtotal)
                    if ftotal.startswith("/"):
                        if not os.path.exists(os.getcwd() + rootdir + ftotal):
                            os.makedirs(os.getcwd() + rootdir + ftotal)
                    else:
                        if not rootdir.endswith("/"):
                            rootdir += "/"
                    if not os.path.exists(os.getcwd() + rootdir + ftotal):
                        os.makedirs(os.getcwd() + rootdir + ftotal)
        else:
            print("Dirs not processed!")
            
    class FileOrientation(object):
        def __init__(self, howknow, filetype, targetf, specification=None):
            if not targetf.startswith("/"):
                self.target_folder = "/" + targetf
            else:
                self.target_folder = targetf
            self.spec = specification
            self.how = howknow
            self.ftype = filetype
            
        def __repr__(self):
            return "Spec: " + self.spec + " how select: " + self.how +\
                " filetype: " + self.ftype + " target folder: " + self.target_folder
                
        def test_file(self, filen):
            if filen.endswith(self.ftype):
                if self.how == "FileTypeSpecification":
                    if filen.endswith(self.spec):
                        return True
                    else:
                        return False
                elif self.how == "FullNameSpecification":
                    if ".".join(filen.split(".")[:-1]) == self.spec:
                        return True
                    else:
                        return False
                elif self.how == "PrefixSpecification":
                    print("Checking prefix for", filen)
                    if filen.startswith(self.spec):
                        return True
                    else:
                        return False    
                elif self.how == "SufixSpecification":
                    print("Checking sufix for filename without type",".".join(filen.split(".")[:-1]))
                    if ".".join(filen.split(".")[:-1]).endswith(self.spec):
                        return True
                    else:
                        return False   
                elif self.how == "PrefixAndSufixSpecification":
                    if filen.startswith(self.spec.split(" ")[0]) and filen.endswith(self.spec.split(" %%")[1]):
                        return True
                    else:
                        return False
            else:
                return False
            
    def get_orientations(self):
        sub_ors = []
        f_ors = []
        for forien in self.fl_orient:
            for curr_sor in forien.childNodes:
                if not curr_sor.nodeType == Node.TEXT_NODE:
                        sub_ors.append(self.FileOrientation(curr_sor.getAttribute("how"), curr_sor.getAttribute("ftype"),\
                                forien.getAttribute("folder"), curr_sor.getAttribute("spec")))
            f_ors.append(sub_ors)
            sub_ors = []
        self.oriens = f_ors
                    
    def check_files(self,orgdir):
        fqueue = []
        allfiles = []
        for f in os.listdir(os.getcwd() + orgdir):
            if not orgdir.endswith("/"):
                orgdir += "/"
            if os.path.isfile(os.getcwd() + "".join([orgdir, f])):
                allfiles.append(f)
        return allfiles
    
    def org_files(self ,files, orgdir, rootdir):
        is_ok = True
        if not rootdir.startswith("/") and not rootdir == "":
            rootdir = "/" + rootdir
        if not orgdir.startswith("/"):
            orgdir = "/" + orgdir
        if not orgdir.endswith("/"):
            orgdir += "/"
        for orientations in self.oriens:
            for cfile in files:
                for orientation in orientations:
                    is_ok = orientation.test_file(cfile)
                    if not is_ok: break
                if is_ok:
                    print("File", cfile, " went ok in test for", orientation)
                    print("Moving", cfile)
                    print("From:", os.getcwd() + orgdir + cfile)
                    print("To:", os.getcwd() + rootdir + orientation.target_folder + "/" + cfile)
                    files.pop(files.index(cfile))
                    try:
                        shutil.copy(os.getcwd() + orgdir + cfile,os.getcwd() + rootdir + orientation.target_folder)
                        os.remove(os.getcwd() + orgdir + cfile)
                    except FileNotFoundError:
                        print("File not found!")
                        print("Path:", os.getcwd() + orgdir + cfile)
                        print("Target:", os.getcwd() + rootdir + orientation.target_folder + "/" + cfile)
                        return
                else: is_ok = True
                
    def organize(self):
        if not self.orgdir.startswith("/"):
            self.orgdir = "/" + self.orgdir
        if not self.rootdir.startswith("/"):
            self.rootdir = "/" + self.rootdir
        if not self.has_loaded_before:
            print("First time running")
            self.load_config(self.config_file)
            self.process_dirs()
            self.check_dirs(self.rootdir)
            self.get_orientations()
            print("Files to be checked")
            print("=======")
            for fl in self.check_files(self.orgdir):
                print(fl)
            print("=======")
            self.org_files(self.check_files(self.orgdir), self.orgdir , self.rootdir)
            self.has_loaded_before = True
        else:
            self.org_files(self.check_files(self.orgdir), self.orgdir , self.rootdir)
            
    def __init__(self, rootdir="/", config_file="orgstructure.xml", orgdir="/organize"):
        self.rootdir = rootdir
        self.config_file = config_file
        self.orgdir = orgdir
        self.oriens = {}
        






    