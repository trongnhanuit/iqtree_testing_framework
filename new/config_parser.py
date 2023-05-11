import configparser
import logging
import yaml
import multiprocessing
import os
import subprocess
import sys
import time
from datetime import datetime

from ArgParser import ArgParser
from logger import gen_log

# config logger, useful when doing ui?
logger = logging.getLogger("test")


class YmlParser:
    '''
    This class parses the config file and generate test commands
    The cmds and special_tests are stored in a list of dict
    The dict contains the following keys:
    name: the name of the test
    command: the command to run
    tests: the tests to run
    tests is also a list of dict with the following keys:
    log: word to check in the log(output) file
    comparison: the comparison operator and the value to compare with
    The syntax is in readme.md or in the example config.yml
    '''
    def __init__(self, file, iqtree="iqtree2", bin="bin", default_tests=("log-likelihood:", "time used:")):
        self.data = None
        self.parse_data(file)
        self.cmds = []

        # this is the parameter used to compare the result
        self.keys = ["equal", "greater", "less", "greater_equal", "less_equal", "between"]
        # print(self.data)
        self.gen_test_cmds(iqtree=iqtree, bin=bin, default_tests=default_tests)
        if "specific_test" in self.data.keys():
            self.gen_specific_test(iqtree=iqtree, bin=bin, default_tests=default_tests)
        self.add_prefix()

    def parse_data(self, file):
        try:
            with open(file, 'r') as f:
                self.data = yaml.safe_load(f)
        # code that handles the exception and upload the error to log file.
        except FileNotFoundError as e:
            logger.error(f"Error: {e}. File not found.")
        except Exception as e:
            logger.error(f"Error: {e}. Yaml file is not valid.")

    def gen_test_cmds(self, test_files="test_data/", iqtree="iqtree2", bin="bin",
                      default_tests=("log-likelihood:", "time used:"), out_file="test_cmds") -> list:
        """
        This function reads config file and output test commands in a list accordingly.
        Returns: list of CMD() objects
        """
        # Generate test commands for single model
        ali_cmds = []
        for aln in self.data["single_alignments"]:
            cmd = f"-s {test_files}{aln} -redo"
            ali_cmds.append(cmd)

        # Generate test commands for partition model
        for part_aln in self.data["partition_alignments"]:
            for partOpt in self.data["partition_options"]:
                cmd = f"-s {test_files}{part_aln['aln']} -redo {partOpt} {test_files}{part_aln['prt']}"
                ali_cmds.append(cmd)

        gen_cmds = []
        # Generate test commands for generic options
        for cmd in ali_cmds:
            if "generic_options" in self.data.keys():
                for gen_opt in self.data["generic_options"]:
                    new_cmd = f"{cmd} {gen_opt}"
                    gen_cmds.append(new_cmd)
        # new options
        cmds = []
        for cmd in gen_cmds:
            if "options" in self.data.keys():
                for gen_opt in self.data["options"]:
                    new_cmd = f"{cmd} {gen_opt}"
                    cmds.append(new_cmd)

        # test commands that with more options
        # for opt in self.data["option"]:
        #     self.cmds = [f"{cmd} {opt}" for cmd in self.cmds]

        # adding iqtree directory to the start of cmd
        self.cmds = [{"command": f"{bin}/{iqtree} {cmd}", "tests": []} for cmd in cmds]

        # add default tests to tests
        for cmd in self.cmds:
            for default_test in default_tests:
                cmd["tests"].append({"log": default_test})

        # output the cmd for debug
        with open(out_file, "w") as f:
            for cmd in [f"{bin}/{iqtree} {cmd}" for cmd in cmds]:
                f.write(cmd + "\n")

        f.close()

        return self.cmds

    def gen_specific_test(self, iqtree="iqtree2", bin="bin", default_tests=("log-likelihood:", "time used:")):
        """
        This function reads config file and output specific test commands in the dict self.special_test
        In a format of {cmd: CMD()}
        Every test command should be unique
        Returns: list of CMD() objects
        """
        special_tests = []
        for test in self.data["specific_test"]:
            # add command with iqtree directory
            test["command"] = f"{bin}/{iqtree} {test['command']}"
            # add default tests to test and check duplication
            for default_test in default_tests:
                duplicated = False
                for t in test["tests"]:
                    if t["log"] == default_test:
                        duplicated = True
                        break
                # add test to the list
                if not duplicated:
                    test["tests"].append({"log": default_test})
            # the syntax is in config.yml file and readme.md
            special_tests.append(test)
        # remove duplicate tests in self.cmds
        for cmd in self.cmds:
            # self.cmds.remove(cmd)
            for test in special_tests:
                if cmd["command"] == test["command"]:
                    self.cmds.remove(cmd)
                    break
        self.cmds = self.cmds + special_tests

        return special_tests

    def add_prefix(self):
        prefix = 0
        for cmd in self.cmds:
            cmd["command"] = f"{cmd['command']} -pre test.{prefix}"
            prefix += 1

    def save_value(self, file):
        with open(file, "w") as f:
            if len(self.cmds) > 0:
                yaml.dump(self.cmds, f)
            else:
                logger.error("YAML ERROR: No commands to save when saving commands' values to YAML file.")
        f.close()

    def parse_value(self) -> str:
        # test if we find the result
        info = ""
        for key in self.value.keys():
            try:
                float(self.value[key])
                info += f"{key} {self.value[key]},"
            except ValueError:
                print(f"Keyword error: {key}, find a non-number value in the output file")
                logger.error(f"Keyword error: {key}, find a non-number value in the output file")
                info += f"{key} ERROR,"
            except TypeError:
                print(f"Keyword error: {key}, cannot find the value in the output file")
                logger.error(f"Keyword error: {key}, cannot find the value in the output file")
                info += f"{key} ERROR,"
        return info



    def set_config(filename='config.ini'):
        pass


# used for yaml class read
def cmd_constructor(loader, node):
    cmd, specific_test, value = loader.construct_scalar(node)
    return CMD(cmd, specific_test, value)


class CMD:
    yaml_tag = 'CMD'

    def __init__(self, cmd, specific_test={"log-likelihood:": [], "used:": []}, value={}, single_aln=None,
                 part_aln=None, part_option=None, option=None, test_dir=None, iqbin=None):
        """
        This class is used to generate test commands.
        Bin is the path to iqtree binary.
        """
        self.cmd = cmd

        # special test {keyword: [(comparison, value)]}
        self.specific_test = specific_test

        self.value = value

    # def gen_test_cmds(self):
    #     """
    #     This function reads config file and output test commands in a list accordingly.
    #     """
    #     # Generate test commands for single model
    #     cmd = ""
    #     if self.single_aln is not None:
    #         cmd = f"-s {self.test_dir}{self.single_aln} -redo"
    #
    #     # Generate test commands for partition model and
    #     elif self.part_option is not None:
    #         cmd = f"-s {self.test_dir}{self.part_aln['aln']} -redo {self.part_option} {self.test_dir}{self.part_aln['prt']}"
    #
    #     # test commands that with more options
    #     cmd = f"{cmd} {self.option}"
    #
    #     # adding iqtree directory to the start of cmd
    #     cmd = f"{self.bin} {cmd}"
    #
    #     self.cmd = cmd

    def equal(self, other):  # FIXME
        if self.cmd == other.cmd:
            return True
        else:
            return False

    def parse_value(self) -> str:
        # test if we find the result
        info = ""
        for key in self.value.keys():
            try:
                float(self.value[key])
                info += f"{key} {self.value[key]},"
            except ValueError:
                print(f"Keyword error: {key}, find a non-number value in the output file")
                logger.error(f"Keyword error: {key}, find a non-number value in the output file")
                info += f"{key} ERROR,"
            except TypeError:
                print(f"Keyword error: {key}, cannot find the value in the output file")
                logger.error(f"Keyword error: {key}, cannot find the value in the output file")
                info += f"{key} ERROR,"
        return info

# def get_config(filename='config.ini'):
#     config = configparser.ConfigParser()
#
#     config.read(filename)
#     config_dict = {}
#
#     # iterate through the config file
#     for section in config.sections():
#         config_list = []
#         # option is the index
#         for option in config.options(section):
#             value = config.get(section, option)
#             config_list.append(value)
#         config_dict[section] = config_list
#     return config_dict
#
#
# def gen_test_cmds(in_file='config.ini', out_file="test_cmds", test_files="test_data/", iqtree=None, bin="build", flag=None):
#     '''This function reads config file and output test commands accordingly.
#     It can output a txt file or return the test commands for further use.
#     '''
#
#     configs = get_config(in_file)
#     test_cmds = []
#     # Generate test commands for single model
#     for aln in configs["single_alignments"]:
#         for opt in configs["generic_options"]:
#             cmd = '-s ' + test_files + aln + ' -redo ' + opt
#             if flag:
#                 cmd = cmd + ' ' + flag
#             test_cmds.append(bin + "/" + iqtree + " " + cmd)
#
#     # Generate test commands for partition model
#     for aln in configs["partition_alignments"]:
#         aln, par = aln.split()
#         for opt in configs["generic_options"]:
#             for partOpt in configs["partition_options"]:
#                 cmd = '-s ' + test_files + aln + ' -redo ' + opt + ' ' + partOpt + ' ' + test_files + par
#                 if flag:
#                     cmd = cmd + ' ' + flag
#                 test_cmds.append(bin + "/" + iqtree + " " + cmd)
#
#     # execute it in the build directory
#     with open(out_file, "w") as f:
#         for cmd in test_cmds:
#             f.write(cmd + "\n")
#
#     f.close()
#     # print("test command generated")
#     # log file
#     if len(test_cmds) != 0:
#         logger.info("test command generated")
#     else:
#         logger.error("No test file generated, check config file (default config.ini).")
#
#     return test_cmds
