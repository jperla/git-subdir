#!/usr/bin/env python

import os
import shutil
import subprocess
import contextlib

repo_name = 'pebbles'
repo_url = 'https://github.com/jperla/pebbles'
test_dirname = './sampledir'

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
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return (p.wait(), stdout, stderr)

def cleanup():
    if os.path.exists(test_dirname):
        shutil.rmtree(test_dirname)
    if os.path.exists('.subdirs'):
        os.remove('.subdirs')

def setupcleanup(f):
    @contextlib.contextmanager
    def decorated(*args, **kwargs):
        cleanup()
        make_test_dir_if_not_exists()
        try:
            f(*args, **kwargs)
        finally:
            cleanup()
    decorated.__name__ = f.__name__
    return decorated

def test_help():
    r, o, e = call_git_subdir([])
    assert r == 0
    assert 'clone' in o
    assert 'pull' in o
    assert 'push' in o
    assert 'rm' in o

def check_files_exist(new=False):
    """Checks that the files from the old commit are around, and that new files are are not there."""
    exists = lambda f: os.path.exists(os.path.join(test_dirname, repo_name, f))

    for f in ['pebbles.js', 'README', 'test/index.html']:
        assert exists(f)
    for f in ['test/test2.js', 'test/index2.html']:
        if new:
            assert exists(f)
        else:
            assert not exists(f)

@setupcleanup
def test_clone_master_explicit():
    path = os.path.join(test_dirname, repo_name)
    r, o, e = call_git_subdir(['clone', path, repo_url, 'master'])
    assert r == 0
    check_files_exist(new=True)

    # calling twice fails
    r, o, e = call_git_subdir(['clone', path, repo_url, 'master'])
    assert r == 1
    assert 'already cloned' in o
    check_files_exist(new=True)

@setupcleanup
def test_clone_master_implicit_and_rm():
    path = os.path.join(test_dirname, repo_name)
    r, o, e = call_git_subdir(['clone', path, repo_url, 'master'])
    assert r == 0
    check_files_exist(new=True)

    r, o, e = call_git_subdir(['rm', path])
    assert not os.path.exists(path)

@setupcleanup
def test_clone_hash():
    path = os.path.join(test_dirname, repo_name)
    r, o, e = call_git_subdir(['clone', path, repo_url, 'ae374469'])
    assert r == 0
    check_files_exist(new=False)

    # calling twice fails
    r, o, e = call_git_subdir(['clone', path, repo_url, 'master'])
    assert r == 1
    assert 'already cloned' in o
    check_files_exist(new=False)

@setupcleanup
def test_pull_explicit():
    path = os.path.join(test_dirname, repo_name)

    r, o, e = call_git_subdir(['clone', path, repo_url, 'ae374469'])
    assert r == 0
    check_files_exist(new=False)

    r, o, e = call_git_subdir(['pull', path, 'master'])
    assert r == 0
    check_files_exist(new=True)

@setupcleanup
def test_pull_implicit():
    path = os.path.join(test_dirname, repo_name)

    r, o, e = call_git_subdir(['clone', path, repo_url, 'ae374469'])
    assert r == 0
    check_files_exist(new=False)

    r, o, e = call_git_subdir(['pull', path])
    assert r == 0
    check_files_exist(new=True)
