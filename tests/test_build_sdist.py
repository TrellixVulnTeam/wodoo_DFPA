from pathlib import Path
from tarfile import TarFile

from whool.buildapi import _build_sdist


def test_build_sdist(addon1: Path, tmp_path: Path) -> None:
    sdist_name = _build_sdist(addon1, tmp_path)
    assert sdist_name == "odoo-addon-addon1-15.0.1.0.0.tar.gz"
    assert (tmp_path / sdist_name).exists()


def test_build_sdist_from_sdist(addon1_with_pyproject: Path, tmp_path: Path) -> None:
    sdist_name = _build_sdist(addon1_with_pyproject, tmp_path)
    assert sdist_name == "odoo-addon-addon1-15.0.1.1.0.tar.gz"
    # extract sdist and test that the root directory has the correct name
    tmp_path2 = tmp_path / "2"
    tmp_path2.mkdir()
    with TarFile.open(tmp_path / sdist_name, mode="r:gz") as tf1:
        tf1_names = sorted(tf1.getnames())
        
        import os
        
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tf1, tmp_path2)
    assert "odoo-addon-addon1-15.0.1.1.0/PKG-INFO" in tf1_names
    assert "odoo-addon-addon1-15.0.1.1.0/pyproject.toml" in tf1_names
    # build sdist from sdist
    tmp_path3 = tmp_path / "3"
    tmp_path3.mkdir()
    sdist_name = _build_sdist(tmp_path2 / "odoo-addon-addon1-15.0.1.1.0", tmp_path3)
    assert sdist_name == "odoo-addon-addon1-15.0.1.1.0.tar.gz"
    # extract 2nd sdist and test that the root directory has the correct name
    with TarFile.open(tmp_path3 / sdist_name, mode="r:gz") as tf2:
        tf2_names = sorted(tf2.getnames())
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tf2, tmp_path3)
    # content of both sdists must be identical
    assert tf1_names == tf2_names
    # PKG-INFO in both sdists must be identical
    assert (tmp_path2 / "odoo-addon-addon1-15.0.1.1.0" / "PKG-INFO").read_bytes() == (
        tmp_path3 / "odoo-addon-addon1-15.0.1.1.0" / "PKG-INFO"
    ).read_bytes()
