import portage
from portage import portagetree
from portage import config
from portage.dep import extract_affecting_use
import os
import re

class Resolver:
  def __init__(self,arch):
    # portage API doesn't seem to have an easy way to switch
    # keywords between looks so this simply creates both
    # a stable and unstable tree that can be referenced back
    # and forth as needed. The forcing of keywords is done
    # by passing in a custom environment to the portage tree
    # constructor. config() while still allowing for other
    # environment variables
    myenv = os.environ
    myenv['ACCEPT_KEYWORDS'] = "{}".format(arch)
    self.portdb_stable = portagetree(settings=config(env=myenv)).dbapi
    
    myenv['ACCEPT_KEYWORDS'] = "~{}".format(arch)
    self.portdb_unstable = portagetree(settings=config(env=myenv)).dbapi

    self.matching_packages = {}

    # This will cache the current visible ebuilds for the
    # package in question to prevent doing the same loop
    # over and over
    self.__cur__visibles = []

    # To give some performance the regex here is compiled that is used to
    # get python depend strings later
    self.__pydep_regex = re.compile(r"\s*([^\s]*dev-lang/python[[:]*[^\s]*)")
  
  def get_python34_packages(self):
    # The unstable tree packages are traveresed since
    # it is the least restrictive
    packages = self.portdb_unstable.cp_all()
    
    pycompat_35_test = []
    pycompat_35_stabilize = []
    for package in packages:
      # This is done to avoid dealing with any packages
      # that are masked
      self.__cur_visibles = \
        set(self.__visible_ebuilds(self.portdb_unstable, package)) | \
        set(self.__visible_ebuilds(self.portdb_stable, package))

      if not self.__has_python_compat34(package):
        continue

      # There's a chance that due to different slots a package
      # may have multiple stable/unstable versions that need
      # to be dealt with
      package_slots = self.__get_package_slots(package)

      for slot,ebuilds in package_slots.items():
         # This are unstable packages that have py34 compat
         # and need py35 compat support added
         if not self.__check_python_compat34(ebuilds["unstable"],True):
           pycompat_35_test.append(self.__get_ebuild_notation(ebuilds["unstable"],slot))
         # These are packages that already have py35 compat support
         # but do not have a stable version
         elif ebuilds["stable"]:
           if self.__check_python_compat34(ebuilds["unstable"],True) and \
           not self.__check_python_compat34(ebuilds["stable"],True):
             pycompat_35_stabilize.append(self.__get_ebuild_notation(ebuilds["unstable"],slot))
         else:
           continue
      
    return (pycompat_35_test, pycompat_35_stabilize)
  
  # This is a private function that is used to append slot info
  # for ebuilds that are not slot 0, and any USE flags that may
  # be required to enable python support and test pycompat
  def __get_ebuild_notation(self, ebuild, slot):
     if slot is "0":
       ebuild_notation = ebuild
     else:
       ebuild_notation = ebuild + " Slot = {}".format(slot)
     
     python_use_dep = self.__get_python_use_dep(ebuild)
     if python_use_dep:
       ebuild_notation += " Python USE: " + ",".join(python_use_dep)

     return ebuild_notation

  # This is a private function that takes an ebuilds *DEPEND and
  # checks if there are any use conditionals which may hit python.
  # Otherwise "builds fine with python 3.5" may be a false positive.
  def __get_python_use_dep(self, ebuild):
     dep_useflags = set()

     for depstring in self.portdb_unstable.aux_get(ebuild, ["DEPEND", "RDEPEND", "PDEPEND"]):
       # This is a regex to pull out specific dev-lang/python atoms since
       # that's what extract_affecting_use wants
       python_atoms = self.__pydep_regex.findall(depstring)

       # Now that we have the specific deps, give a listing of the possible USE flags that
       # will be related to dev-lang/python, with the exception of the use expand python_targets_*
       # and python_single_target_* USE
       [ [ dep_useflags.add(useflag) for useflag in extract_affecting_use(depstring,dep) \
       if not useflag.startswith("python_target") and not useflag.startswith("python_single") ] for dep in python_atoms ]
     
     return dep_useflags

  def __has_python_compat34(self,package):
    python_compat = False

    for ebuild in self.__cur_visibles:
      if self.__check_python_compat34(ebuild):
        python_compat = True
        break
    
    return python_compat

  # This is a private function with two purposes. The first
  # ( missing_35_check=False ) is an initial loop filter to
  # make sure we only do work on ebuilds that actually have
  # py34 compat support. The next check ( missing_35_check=True)
  # will see if py35 compat support is also available or not
  def __check_python_compat34(self,ebuild,missing_35_check=False):
    iuse = self.portdb_unstable.aux_get(ebuild, ["IUSE"])[0].split()
    if "python_targets_python3_4" in iuse:
      if missing_35_check and not "python_targets_python3_5" in iuse:
        return False
      else:
        return True
    else:
      return False

  # This is a private function to map all slots of ebuilds
  # to the latest stable and unstable for that slot
  def __get_package_slots(self,package):
    package_slots = {}

    for ebuild in self.__cur_visibles:
      # This is to avoid subslots which really don't matter for these
      # reports
      slot = self.portdb_unstable.aux_get(ebuild, ["SLOT"])
      slot = slot[0].split("/")[0]
      if not slot in package_slots:
        # we only care about the latest stable and unstable for the slot
        # this will be looped through later for pycompat checks
        package_slots[slot] = {}
        slot_formatted_package_name = package + ":" + slot
        package_slots[slot]["unstable"] = self.portdb_unstable.xmatch("bestmatch-visible", slot_formatted_package_name)
        package_slots[slot]["stable"] = self.portdb_stable.xmatch("bestmatch-visible", slot_formatted_package_name)
      else:
        continue

    return package_slots

  def __visible_ebuilds(self, tree, package):
    return tree.xmatch("match-visible", package)
