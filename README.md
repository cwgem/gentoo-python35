# Python 3.5 Overlay

This is an overlay for attempting to make Python 3.5 stable for Gentoo. Most will be simply adding python3_5 to the targets, but some may included python 3.5 specific fixes such as patches. Any patches that make it to upstream Gentoo will still remain here however.

Testing is mainly done by setting a `/etc/portage/repos.conf/` file like so:

```
[DEFAULT]
main-repo = gentoo

[gentoo-python]
location = /[path-to-checked-out-git-repo]/gentoo-python
```

`/etc/portage/make.conf` will need to be updated with the proper python targets:

```
PYTHON_TARGETS="python2_7 python3_4 python3_5"
PYTHON_SINGLE_TARGET="python3_5"
```

For work on stable, the python 3.5 flag will need to be unmasked

```
# mkdir /etc/portage/profile
# echo '-python_targets_python3_5' >> /etc/portage/profile/use.mask
```
