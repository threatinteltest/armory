#!/usr/bin/python
import argparse
import sys

if sys.version_info[0] < 3:
    from subprocess32 import Popen
else:
    from subprocess import Popen

from multiprocessing import Pool as ThreadPool
from included.utilities.color_display import display, display_error
from included.utilities import which
import shlex
import pdb

class ModuleTemplate(object):
    """
    Master template for a module. Actual modules should just override this

    """
    name = "Template"
    db = None

    def __init__(self, db=None):

        pass


    def set_options(self):

        self.options = argparse.ArgumentParser(prog=self.name)

        


    def run(self, args):
        '''
        Execute the module, receives argparse arguments.
        '''
        pass


class ToolTemplate(ModuleTemplate):
    """
    Generic template for running a tool, and ingesting the output.
    """

    timeout = 0
    binary_name = ''

    def set_options(self):
        super(ToolTemplate, self).set_options()
        
        self.options.add_argument('-b', '--binary', help="Path to the binary")
        self.options.add_argument('-o', '--output_path', help="Relative path (to the base directory) to store output", default=self.name)
        self.options.add_argument('--threads', help="Number of Armory threads to use", default="10")
        self.options.add_argument('--timeout', help="Thread timeout in seconds, default is 300.", default="300")
        self.options.add_argument('--extra_args', help="Additional arguments to be passed to the tool")
        self.options.add_argument('--no_binary', help="Runs through without actually running the binary. Useful for if you already ran the tool and just want to process the output.", action="store_true")
        # self.options.add_argument('--profile1', help="Use first profile options")

    def run(self, args):


        if not args.binary:
            self.binary = which.run(self.binary_name)

        else:
            self.binary = which.run(args.binary)

        if not self.binary:
            print("%s binary not found. Please explicitly provide path with --binary" % self.name)

        else:
            timeout = int(args.timeout)
            targets = self.get_targets(args)
            
            if not args.no_binary:
                cmd = self.build_cmd(args)
                cmds = [shlex.split(cmd.format(target=t[0], output=t[1])) + [timeout] for t in targets]
                pool = ThreadPool(int(args.threads))

                pool.map(run_cmd, cmds)
            self.process_output(targets)


    def process_output(self, cmds):
        '''
        Process the output generated by the earlier commands.
        '''

    def get_targets(self, args):
        '''
        This module is used to build out a target list and output file list, depending on the arguments. Should return a
        list in the format [(target, output), (target, output), etc, etc]
        '''

        return []

    def build_cmd(self, args):
        '''
        Create the actual command that will be executed. Use {target} and {output} as placeholders.
        '''
        
        return ''


def run_cmd(cmd):
    c = cmd[:-1]
    timeout = cmd[-1]
    display("Executing command: %s" % ' '.join(c))
    
    try:
        Popen(c).wait(timeout=timeout)
    except:
        display_error("Timeout of %s reached. Aborting thread for command: %s" % (timeout, ' '.join(c)))
