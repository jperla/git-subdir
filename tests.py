#!/usr/bin/env python

import os
import shutil
import subprocess
import contextlib

repo_name = 'pebbles'
repo_url = 'https://github.com/jperla/pebbles'
test_dirname = './test_dir'

@contextlib.contextmanager
def chdir(directory):
    """Accepts directory string.
        Changes to the directory for an operation within with 
            and then goes back to original one.
    """
    original_directory = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(original_directory)

def mkdir_if_not_exists(d):
    subprocess.call(['mkdir', '-p', d])

def make_test_dir_if_not_exists():
    mkdir_if_not_exists(test_dirname)

def call_git_subdir(args):
    command = ['./git-subdir',] + args
    print command
    return subprocess.call(command)

def cleanup():
    if os.path.exists(test_dirname):
        shutil.rmtree(test_dirname)
        shutil.rm('.subdirs')

def vendortest(f):
    @contextlib.contextmanager
    def decorated(*args, **kwargs):
        cleanup()
        make_test_dir_if_not_exists()
        f(*args, **kwargs)
        cleanup()
    decorated.__name__ = f.__name__
    return decorated

def test_help():
    assert call_git_subdir([]) == 0
    #TODO: jperla: test output

@vendortest
def test_clone_master():
    path = os.path.join(test_dirname, repo_name)
    assert call_git_subdir(['clone', path, repo_url, 'master']) == 0
    #TODO: jperla: test individual files

    # calling twice fails
    assert call_git_subdir(['clone', path, repo_url, 'master']) == 1
    #TODO: jperla: test error message

@vendortest
def test_clone_hash():
    path = os.path.join(test_dirname, repo_name)
    assert call_git_subdir(['clone', path, repo_url, 'ae374469']) == 0
    #TODO: jperla: test individual files

    # calling twice fails
    assert call_git_subdir(['clone', path, repo_url, 'master']) == 1

@vendortest
def test_pull():
    path = os.path.join(test_dirname, repo_name)

    #TODO: jperla: test individual files
    assert call_git_subdir(['clone', path, repo_url, 'ae374469']) == 0

    #TODO: jperla: test individual files
    assert call_git_subdir(['pull', path, repo_url, 'master']) == 0
