#!/usr/bin/env python3
import icegrabber
import time

grabber = icegrabber.IceGrabber(rootdir="/rootdir", config_file="orgstructure.xml")
grabber.organize()
input("Press any key to organize again")
grabber.organize()