import argparse


class ArgParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__()

    def standard_arg(self):
        self.bin_arg()
        self.config_arg()
        self.iqtree_ver_arg()
        self.output_arg()

    def compare_arg(self):
        self.add_argument('-1', '--first', dest="iqtree1", help='Path to your IQ-TREE1 result file')
        self.add_argument('-2', '--second', dest="iqtree2", help='Path to your IQ-TREE2 result file')
        self.add_argument('-o', '--output', dest="output_file", help='Output result for test cases')
        self.add_argument('-i', '--image', dest="image_output", help='Output result for test cases')

    def iqtree_ver_arg(self):
        self.add_argument('-v', '--version', dest="version", help='IQ-TREE testing version')

    def bin_arg(self):
        self.add_argument('-b', '--binary', dest="bin", help='Path to your IQ-TREE binary directory')

    def config_arg(self):
        self.add_argument('-c', '--config', dest="config_file", help='Path to test configuration file')

    def output_arg(self):
        self.add_argument('-o', '--output', dest="output_file", help='Output file for test cases')



