#!/usr/bin/env python3
import wilby
import time

grabber = wilby.Wilby(rootdir="/rootdir", config_file="orgstructure.xml")
grabber.organize()
input("Press any key to organize again")
grabber.organize()