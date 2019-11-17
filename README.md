# PKG_utils
Some tools to parse and work with Apple PKG format files (old and new types)

## Use example

As simple as:
```python
from PKG_utils import pkg
extract_path = pkg.unpack_pkg(pkg_path, dst_path)
pkg.extract_payload_and_scripts(extract_path)
```


## Requirements

* python <3.7
* `pip install -r requirements.txt`
* 7z
