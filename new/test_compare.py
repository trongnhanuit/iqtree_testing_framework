import matplotlib.pyplot as plt
import yaml

from config_parser import cmd_constructor
from ArgParser import ArgParser
from logger import gen_log

parser = ArgParser()
parser.compare_arg()
args = parser.parse_args()

# set up logger
logger = gen_log(f"compare {args.iqtree1} {args.iqtree2}")

keys = ["equal", "greater", "less", "greater_equal", "less_equal", "between"]


def compare(test_value, expected_value, test):
    # compare founded value with other
    # check if the value is a number or exists
    if test_value is None:
        return False
    else:
        try:
            test_value = float(test_value)
        except ValueError:
            logger.error(f"Value ERROR: {test_value} is not a number")
            return False
    if test == "equal":
        return test_value == expected_value
    elif test == "greater":
        return test_value > expected_value
    elif test == "less":
        return test_value < expected_value
    elif test == "greater_equal":
        return test_value >= expected_value
    elif test == "less_equal":
        return test_value <= expected_value
    elif test == "between":
        if expected_value[0] < expected_value[1]:
            return expected_value[0] <= test_value <= expected_value[1]
        else:
            return expected_value[1] <= test_value <= expected_value[0]


# iqtree1 args.iqtree1 args.iqtree2
with open(args.iqtree1, "r") as result:
    data1 = yaml.safe_load(result)
    # count the failed and passed tests
    failed_tests = 0
    passed_tests = 0
    # iqtree2
    with open(args.iqtree2, "r") as result2:
        data2 = yaml.safe_load(result2)
        # check if the special tests results are true
        for i in range(len(data1)):
            # for test_case in data1[i]["tests"]:
            #     if "value" in test_case.keys():
            #         cmd1.append(test_case["command"])
            #         log1.append(test_case["value"])
            #         time1.append(test_case["time"])
            # for test_case in data2[i]["tests"]:
            #     if "value" in test_case.keys():
            #         cmd2.append(test_case["command"])
            #         log2.append(test_case["value"])
            #         time2.append(test_case["time"])
            # check passed all the tests
            overall_passed = True
            for j in range(len(data1[i]["tests"])):
                test_dict1 = data1[i]["tests"][j]
                test_dict2 = data2[i]["tests"][j]
                # add benchmark value to data2
                if "value" in data1[i]["tests"][j]:
                    benchmark_value = test_dict1["value"]
                    test_dict2["benchmark"] = benchmark_value
                else:
                    test_dict2["benchmark"] = "No Result"
                # check if value exists
                if "value" in test_dict2.keys():
                    test_value = test_dict2["value"]
                    passed = True
                    # if there are tests
                    is_test = False
                    for key in test_dict2.keys():
                        if key in keys:
                            is_test = True
                            if not compare(test_value, test_dict2[key], key):
                                passed = False
                                overall_passed = False
                    if passed and is_test:
                        test_dict2["result"] = "Passed"
                    elif not is_test:
                        test_dict2["result"] = "NoTest"
                    else:
                        test_dict2["result"] = "Failed"
                # if there is no value
                else:
                    test_dict2["result"] = "Failed"
            if overall_passed:
                data2[i]["result"] = "Passed"
                passed_tests += 1
            else:
                data2[i]["result"] = "Failed"
                failed_tests += 1
        # args.output_file "result.yml"
        with open(args.output_file, "w") as f:
            yaml.dump(data2, f)
        f.close()

# plot the result
plot_keywords = ['log-likelihood:', 'time used:']
name = []
data1 = [[] for _ in range(len(plot_keywords))]
data2 = [[] for _ in range(len(plot_keywords))]

with open("result.yml", "r") as f:
    data = yaml.safe_load(f)
    for cmd in data:
        # boolean if the cmd has tests
        has_test = False
        for test in cmd["tests"]:
            if "value" in test.keys():
                for i in range(len(plot_keywords)):
                    if plot_keywords[i] == test["log"] and "benchmark" in test.keys() and "value" in test.keys():
                        has_test = True
                        data1[i].append(test["value"])
                        data2[i].append(test["benchmark"])
        # for cmd with no name, default name is the prefix of the test
        if has_test:
            if "name" in cmd.keys():
                name.append(cmd["name"])
            else:
                name.append(cmd["command"].split(" ")[-1])

    # plot
    for i in range(len(plot_keywords)):
        plt.subplot(len(plot_keywords), 1, i + 1)
        # plt.plot(name, [float(data1[i][j]) - float(data2[i][j]) for j in range(len(data1[i]))], label="difference")
        plt.plot(name, [float(data1[i][j]) / float(data2[i][j]) for j in range(len(data1[i]))], label="ratio")
        plt.legend()
        plt.title(plot_keywords[i])

    plt.savefig(args.image_output)
    # plt.show()
