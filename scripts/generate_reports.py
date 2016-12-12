#!/usr/bin/python3

import argparse
import sys
import os

from gentoopy.resolve import Resolver

class readable_dir(argparse.Action):
  def __call__(self,parser, namespace, values, option_string=None):
    prospective_dir=values
    if not os.path.isdir(prospective_dir):
      raise argparse.ArgumentTypeError("{0} is not a valid path".format(prospective_dir))
    if os.access(prospective_dir, os.R_OK):
      setattr(namespace,self.dest,prospective_dir)
    else:
      raise argparse.ArgumentTypeError("{0} is not a readable dir".format(prospective_dir))

def main(args=None):
  parser = argparse.ArgumentParser(description='Generate reports for Python 3.5 stability reporting')
  parser.add_argument('-o', '--output', help='output path for reports', action=readable_dir, default=os.path.expanduser("~"))
  parser.add_argument('-a', '--arch', help="the arch for resolving packages", default="amd64")
  arguments = parser.parse_args(args)

  resolver = Resolver(arguments.arch)
  (pycompat_35_test, pycompat_35_stabilize) = resolver.get_python34_packages()

  with open(os.path.join(arguments.output, "pycompat_35_test.txt"), 'w') as file_handler:
    for ebuild in pycompat_35_test:
        file_handler.write("{}\n".format(ebuild)) 
  
  with open(os.path.join(arguments.output, "pycompat_35_stabilize.txt"), 'w') as file_handler:
    for ebuild in pycompat_35_stabilize:
        file_handler.write("{}\n".format(ebuild)) 

if __name__ == "__main__":
  main(sys.argv[1:])
