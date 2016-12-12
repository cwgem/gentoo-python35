# Python 34/35 Compat Report Generator

This script generates the following reports for all packages in the current system's tree:

* All ebuilds are unstable and have python 3.4 compat but not python 3.5 compat
* Stable and unstable ebuilds exist, and there are stable python 3.4/3.5 compat ebuilds but no stable python 3.4/3.5 compat ebuilds

## Example Run

```
 ./generate_reports.py -a amd64 -o ~/gentoo-python35/
```

This generates the reports in the `~/gentoo-python35/` folder for amd64

## Environment Considerations

* This script for the most part uses your system's `/etc/portage/repos.conf` and profile settings
* `ACCEPT_KEYWORDS` are forced however so that stable and unstable trees are constant no matter the architecture
* With this in mind be aware that `package.unmask` and any other local/profile masking will have significant impact on script output
* The integration with `/etc/portage/repos.conf` means that you can have this repo added so the resulting reports will show the progress of ebuilds here (or other repos for that matter)
* The `-a`/`--arch` setting lets you build reports for a certain arch which may not have as large a package set as say amd64

## Tech Details

* This script is written for Python 3
* That said make sure that eselect python is set to a python 3 interpreter, and that portage is built
  with that python version's support
* All other code uses the standard library
* Explanations of algorithms involved are commented in detail in the code
