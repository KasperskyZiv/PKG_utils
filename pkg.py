#!/usr/bin/env python3
# Created by Ziv Kaspersky at 4/3/19

# Standard packages
import logging
import tempfile
from os import path, listdir, chdir, makedirs, remove
from shutil import rmtree, copyfile
from subprocess import PIPE, Popen

# External packages
import magic

# Proprietary models
from lib.utils.file_utils import is_installed

logger = logging.getLogger(__name__)

if not is_installed("7z"):
    print("7z command line tool is needed!")
elif not is_installed("cpio"):
    print("cpio command line tool is needed!")
elif not is_installed("gzip"):
    print("gzip command line tool is needed!")


def extract_payload_and_scripts(pkg_folder_path):
    payload_path = path.join(pkg_folder_path, "Payload")
    if path.isfile(payload_path):
        _extract_gz_cpio(payload_path)
    else:
        content = ", ".join(listdir(pkg_folder_path))
        raise Exception(f"pkg folder has no payload? content: '{content}'")
    script_path = path.join(pkg_folder_path, "Scripts")
    if path.isfile(script_path):
        _extract_gz_cpio(script_path)
    else:
        logger.info("No Scripts found in pkg")


def unpack_pkg(pkg_path, dst_path=None):
    """Extract pkg in a tmp folder, returns path"""
    logger.info(f"Extracting '{pkg_path}'")
    if not path.isfile(pkg_path):
        logger.error(f"Not A File: '{pkg_path}'")
        exit(1)
    elif"application/x-xar" != magic.from_file(pkg_path, mime=True):
        logger.error(f"Not A XAR File: '{pkg_path}'")
        exit(1)
    else:
        tmp_path = _extract_xar(pkg_path, dst_path)
        pkg_folder_path = None
        for f_name in listdir(tmp_path):
            if f_name.endswith(".pkg"):
                pkg_folder_path = path.join(tmp_path, f_name)
                extract_payload_and_scripts(pkg_folder_path)
        if not pkg_folder_path:
            content = ", ".join(listdir(tmp_path))
            logger.warning(f"pkg folder not found inside pkg archive '{pkg_path}', content: '{content}'")
            logger.debug("Trying to look for scripts and payload in root level of pkg")
            extract_payload_and_scripts(tmp_path)

        logger.info(f"Extracted successful to path {tmp_path}")
        return tmp_path


def _extract_xar(file_path, tmp_path=None):
    if not tmp_path:
        tmp_path = path.join(tempfile.gettempdir(), path.basename(file_path))
    makedirs(tmp_path, exist_ok=True)
    chdir(tmp_path)
    cmd = ["7z", "x", file_path, "-txar", "-o"+tmp_path]
    logger.debug(f"Running {' '.join(cmd)}")
    process = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE, encoding="utf-8")
    out, err = process.communicate()
    if not err and "Everything is Ok" in out:
        logger.debug("7z finished extracting pkg")
    else:
        logger.debug(f"Possible errors in pkg extraction, err={err}, out={out}")
    return tmp_path


def _extract_gz_cpio(file_path):
    file_name = path.basename(file_path)
    tmp_extract_path = file_path + "_"
    if path.isdir(tmp_extract_path):
        rmtree(tmp_extract_path)
    makedirs(tmp_extract_path, exist_ok=True)
    tmp_file = path.join(tmp_extract_path, file_name+".cpio.gz")
    copyfile(file_path, tmp_file)
    cmd = (f'cd "{tmp_extract_path}" && gzip -dc "{tmp_file}" | cpio -idm')
    logger.info(f"Running {cmd}")
    process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, encoding="utf-8")
    out, err = process.communicate()
    logger.debug(f"_extract_gz_cpio out: {out}")
    if err:
        logger.warning(f"_extract_gz_cpio err: {err}")
    remove(tmp_file)
    # TODO: what if fails
    # TODO: not gz but other compression?
