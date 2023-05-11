import logging
import concurrent.futures
import subprocess
from concurrent.futures import ThreadPoolExecutor
import time

import yaml

from logger import gen_log
from config_parser import CMD, YmlParser

# set logger
logger = logging.getLogger("test")


def run_command(command: dict):
    """
    This function runs a command and returns the output
    This function also parse the error and output the error to log file if the return code is not 0
    """
    # task_output = open("output", "a")

    process = subprocess.run(command["command"], stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    output = process.stdout.decode().strip()
    # print(output)
    if process.returncode != 0:
        print(f"RUNTIME ERROR:Command {command['command']}: failed with Error code {process.returncode}")
        outputs = output.split()
        error = find_error(outputs)
        if len(error) == 0:
            logger.error(output)
        raise RuntimeError(f"failed with return code {process.returncode}")
    return command, output


def find_keyword_match(outputs, keywords):
    """
    This function finds keywords in outputs and return the string (should be a float) after the keyword
    """
    # outputs is output.split()
    # parse critical information from output file or (log file)
    # the keyword is a string with space
    keywords_result = {}
    keywords_split = []
    for i in range(len(keywords)):
        keywords_split.append(keywords[i].split())

    for i in range(len(outputs)):
        for j in range(len(keywords_split)):
            for k in range(len(keywords_split[j])):
                if outputs[i + k] == keywords_split[j][k]:
                    if k == len(keywords_split[j]) - 1:
                        keywords_result[keywords[j]] = outputs[i + k + 1]
                    continue
                else:
                    break

    return keywords_result


def find_error(outputs):
    """
    This function finds keyword ERROR: in outputs and output error to log file
    """
    # outputs is output.split()
    # parse error information from output file or (log file)
    rtn = []
    for i in range(len(outputs)):
        if outputs[i] == "ERROR:":
            sentence = []
            while i < len(outputs) and outputs[i] != "\n":
                sentence.append(outputs[i])
                i += 1
            rtn.append(" ".join(sentence))
            # output to log file
            logger.error(" ".join(sentence))
            print(f"ERROR DETAIL: {' '.join(sentence)}")
            print(time.time())
    return rtn


def concurrent_commands(cmds: list, processors=None, timeout=None, output_result="result"):
    ''' Default processors are maximum cores. Default timeout is no timeout. User can specify a timeout value.
        Run every task in parallel.
    '''
    # # set logger
    # logger = logging.getLogger("test")

    # set start time
    start_time = time.time()

    # create the list of test commands which is the concatenation of lists of cmds and special_test
    with ThreadPoolExecutor(max_workers=processors) as executor:
        futures = {executor.submit(run_command, cmd): cmd for cmd in cmds}
        # Wait for the results
        for future in concurrent.futures.as_completed(futures, timeout=timeout):
            command = futures[future]
            try:
                # FIXME timeout
                # here the returned cmd is CMD type
                cmd, output = future.result()
                outputs = output.split()
            except Exception as exc:
                logger.error(f"ERROR: {exc} for command: {command['command']}")
                continue
            else:
                # parse critical information from output file
                keywords = []
                for test in cmd["tests"]:
                    keywords.append(test["log"])
                result = find_keyword_match(outputs, keywords)

                # update value for each test
                # there might be situation where we failed to find the value or the value is not a number
                for test in cmd["tests"]:
                    if test["log"] not in result.keys():
                        logger.error(f"Value ERROR: Failed to find value for {test['log']} in {command['command']}")
                        print(f"Value ERROR: Failed to find value for {test['log']} in {command['command']}")
                    else:
                        test["value"] = result[test["log"]]

                # info = cmd.parse_value()
                print(f"Successfully run command {command['command']}")
                logger.info(f"Successfully run command {command['command']}")

    # set end time
    end_time = time.time()
    logger.info(f"All tests finished in --- {start_time - end_time} ---")

    # output the result to compare in later workflow
    # print(cmds)
    if len(cmds) > 0:
        with open(output_result, "w") as f:
            yaml.dump(cmds, f)
        f.close()


def compare(value, other):
    # compare founded value with other
    if value is None:
        raise ValueError("KEY ERROR: Comparison key is invalid")
    elif value == "equal":
        return value == other
    elif value == "greater":
        return value > other
    elif value == "less":
        return value < other
    elif value == "greater_equal":
        return value >= other
    elif value == "less_equal":
        return value <= other
    elif value == "between":
        return value[0] <= other <= value[1]

