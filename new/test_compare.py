import matplotlib.pyplot as plt
import numpy as np
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
# plot_keywords = ['log-likelihood:', 'time used:']

plot_keywords = ['time used:']
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
    plt.figure(figsize=(20, 12))
    for i in range(len(plot_keywords)):
        plt.subplot(len(plot_keywords), 1, i + 1)
        # plt.plot(name, [float(data1[i][j]) - float(data2[i][j]) for j in range(len(data1[i]))], label="difference")
        plt.bar(name, [float(data1[i][j]) / float(data2[i][j]) for j in range(len(data1[i]))], label="ratio")
        plt.legend()
        plt.title(plot_keywords[i])




    plt.savefig(args.image_output)
    plt.show()
# compare multiple results
def horizontal_compare_runtime():
    files = ["iqtree-1.6.12-Stable.yml",  "iqtree-2.1.3.yml", "iqtree-2.2.0.yml", "iqtree-2.2.0.3.mm.yml", "iqtree-2.2.0.3.yml", "iqtree-2.2.0.4.yml", "iqtree-2.2.0.5.yml", "iqtree-2.2.0.7.yml", "iqtree-2.2.2.yml", "iqtree-2.2.2.3.yml", "iqtree-2.2.2.5-Latest.yml"]
    names = [" " + files[i][0:-4].replace("iqtree", "v") for i in range(len(files))]
    plot_keywords = ['time used:']
    all_results = []
    # Read and process the output files
    for name in files:
        with open(f"{name}", "r") as f:
            result = []
            data = yaml.safe_load(f)
            for cmd in data:
                # boolean if the cmd has tests

                for test in cmd["tests"]:
                    if "value" in test.keys():
                        for i in range(len(plot_keywords)):
                            if plot_keywords[i] == test["log"] and "value" in test.keys():
                                result.append(test["value"])
            all_results.append(result)
    num_tests = len(all_results[0])
    # Plot the results in a bar chart
    # Create an array to store the results for each test across files
    results = np.zeros((num_tests, len(files)))

    # Set global font size
    # plt.rcParams.update({'font.size': 18})

    # Fill the results array with the test results
    for i, results_list in enumerate(all_results):
        results[:, i] = results_list

    # Plot the results in a bar chart
    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(num_tests)
    bar_width = 1.0 / (len(files) + 1)

    for i, name in enumerate(names):
        bars = ax.bar(x + i * bar_width, results[:, i], width=bar_width, label=name)
        if i == 0 or i == len(names) - 1:
            for bar in bars:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                        name, ha='center', va='bottom',
                        rotation='vertical')

    # Set labels and titles
    ax.set_xlabel('Test Index')
    # ax.set_xticks(x)
    # ax.set_xticklabels(files)
    ax.set_ylabel('Running time (seconds)')
    ax.set_title('Comparison of Running Time In Version Number Ascending Order')

    ax.set_xticks(x + (len(files) / 2) * bar_width)
    ax.set_xticklabels([f"Test {i + 1}" for i in range(num_tests)])

    # Add a legend
    ax.legend(bbox_to_anchor=(1, 1), loc='upper left')

    # Show the bar chart
    plt.tight_layout()
    plt.savefig('output.pdf')
    plt.show()

def horizontal_compare_loglikelihood():
    files = ["iqtree-1.6.12-Stable.yml",  "iqtree-2.1.3.yml", "iqtree-2.2.0.yml", "iqtree-2.2.0.3.mm.yml", "iqtree-2.2.0.3.yml", "iqtree-2.2.0.4.yml", "iqtree-2.2.0.5.yml", "iqtree-2.2.0.7.yml", "iqtree-2.2.2.yml", "iqtree-2.2.2.3.yml", "iqtree-2.2.2.5-Latest.yml"]
    names = [" " + files[i][0:-4].replace("iqtree", "v") for i in range(len(files))]
    plot_keywords = ['log-likelihood:']
    all_results = []
    benchmark = []
    # Read and process the output files
    for name in files:
        with open(f"{name}", "r") as f:
            result = []
            data = yaml.safe_load(f)
            for j, cmd in enumerate(data):
                # boolean if the cmd has tests
                for test in cmd["tests"]:
                    if "value" in test.keys():
                        for i in range(len(plot_keywords)):
                            if name == "iqtree-1.6.12-Stable.yml":
                                if plot_keywords[i] == test["log"]:
                                    benchmark.append(test["value"])
                            if plot_keywords[i] == test["log"] and "value" in test.keys():
                                result.append(float(test["value"]) - float(benchmark[j]))

            all_results.append(result)
    del all_results[0]
    del files[0]
    del names[0]
    num_tests = len(all_results[0])
    # Plot the results in a bar chart
    # Create an array to store the results for each test across files
    results = np.zeros((num_tests, len(files)))

    # Set global font size
    # plt.rcParams.update({'font.size': 18})

    # Fill the results array with the test results
    for i, results_list in enumerate(all_results):
        results[:, i] = results_list

    # Plot the results in a bar chart
    fig, ax = plt.subplots(figsize=(8, 3))
    x = np.arange(num_tests)
    bar_width = 1.0 / (len(files) + 1)

    for i, name in enumerate(names):
        bars = ax.bar(x + i * bar_width, results[:, i], width=bar_width, label=name)
        # if i == 0 or i == len(names) - 1:
        #     for bar in bars:
        #         ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
        #                 name, ha='center', va='bottom',
        #                 rotation='vertical')

    # Set labels and titles
    ax.set_xlabel('Test Index')
    # ax.set_xticks(x)
    # ax.set_xticklabels(files)
    ax.set_ylabel('Log-likelihood')
    ax.set_title('Log-likelihood Difference to Stable Version of Different Versions In Ascending Order')

    ax.set_xticks(x + (len(files) / 2) * bar_width)
    ax.set_xticklabels([f"Test {i + 1}" for i in range(num_tests)])

    # Add a legend
    ax.legend(bbox_to_anchor=(1, 1), loc='upper left')

    # Show the bar chart
    plt.tight_layout()
    plt.savefig('output1.pdf')
    plt.show()

# horizontal_compare_runtime()
# plt.legend()
# plt.show()
# plt.savefig(args.image_output)
    # plt.show()