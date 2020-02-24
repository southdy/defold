#!/usr/bin/env python

import os, sys, shutil, zipfile, re, itertools, json, platform, math, mimetypes
import optparse, subprocess, urllib, urlparse, tempfile, time
import imp
from datetime import datetime
from tarfile import TarFile
from os.path import join, dirname, basename, relpath, expanduser, normpath, abspath
from glob import glob
from threading import Thread, Event
from Queue import Queue
from ConfigParser import ConfigParser

PACKAGES_NX64="protobuf-2.3.0".split()


def get_target_platforms():
    return ['arm64-nx64']

def get_install_host_packages(platform):
    """ Returns the packages that should be installed for the host
    """
    return []

def get_install_target_packages(platform):
    """ Returns the packages that should be installed for the host
    """
    if platform == 'arm64-nx64':    return PACKAGES_NX64
    return []

def install_sdk(platform):
    """ Installs the sdk for the private platform
    """
    pass

def is_library_supported(platform, library):
    if platform == 'arm64-nx64':    return library not in ['GLFW']
    return True
