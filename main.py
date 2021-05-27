import networkx as nx
import matplotlib.pyplot as plt
import random as random
import xlsxwriter
from time import perf_counter, time
import math
import satExtensionFinder
import itertools
import matplotlib.gridspec as gridspec


def compute_graph_instance(row):
    g = nx.DiGraph()
    g.add_nodes_from(range(1, noOfNodes + 1))
    node_pairs = itertools.combinations(range(1, noOfNodes + 1), 2)
    attack_set = {}
    for node in range(1, noOfNodes + 1):
        attack_set[node] = []
    for node_pair in node_pairs:
        if random.random() < probability:
            if random.random() < q_probability:
                g.add_edge(node_pair[0], node_pair[1])
                attack_set[node_pair[0]].append(node_pair[1])

                g.add_edge(node_pair[1], node_pair[0])
                attack_set[node_pair[1]].append(node_pair[0])
            else:
                if random.random() < 0.5:
                    g.add_edge(node_pair[0], node_pair[1])
                    attack_set[node_pair[0]].append(node_pair[1])
                else:
                    g.add_edge(node_pair[1], node_pair[0])
                    attack_set[node_pair[1]].append(node_pair[0])

    labels = {}
    for node in range(1, noOfNodes + 1):
        labels[node] = str(node)

    friends_set = compute_friends(attack_set)
    vertex_set = [node for node in range(1, noOfNodes + 1)]

    extension = None
    extension_compute_start_time = perf_counter()
    # for x in vertex_set:
    #     # print("Computing Extension for: " + str(x))
    #     extension = compute_arg_extension(attack_set, friends_set, [x], friends_set[x],
    #                                       remove_arr(get_nodes_attacks_given_v(attack_set, x),
    #                                                  get_nodes_attacked_by_given_v(attack_set, x)))
    #     if extension and len(extension) != 0:
    #         extension = None if not extension else merge_arr(extension, [x])
    #         break
    # print(extension);
    # if extension and len(extension) != 0:
    #     print("BT Solver:Extension Found")
    # else:
    #     print("BT Solver: Extension not found.")
    outputStr = extension_to_str(extension)
    # print(outputStr)
    extension_compute_end_time = perf_counter()
    time_taken_our_solver = extension_compute_end_time - extension_compute_start_time
    # time_taken_our_solver = round(time_taken_our_solver / 1000, 0)

    write_in_worksheet(row, 0, "Graph-Instance-" + str(row - 3))
    write_in_worksheet(row, 1, outputStr)

    attacked_by_dict = {}
    for vertex in vertex_set:
        attacked_by_dict[vertex] = get_nodes_attacks_given_v(attack_set, vertex)

    solver_output = satExtensionFinder.get_admissible_set(attack_set, vertex_set, attacked_by_dict)

    is_sat_extension_found = solver_output.get('minisat_satisfiable')
    is_custom_sat_extension_found = solver_output.get('custom_minisat_satisfiable')

    time_taken_sat_solver = solver_output.get('minisat_total_time_taken')
    time_taken_sat_solver_wo_init = solver_output.get('minisat_time_taken_wo_formula_generation')

    time_taken_csat_solver = solver_output.get('custom_minisat_total_time_taken')
    time_taken_csat_solver_wo_init = solver_output.get('custom_minisat_time_taken_wo_formula_generation')

    time_taken_bh3_sat_solver = solver_output.get('bh3_minisat_total_time_taken')
    time_taken_bh3_sat_solver_wo_init = solver_output.get('bh3_minisat_time_taken_wo_formula_generation')

    write_in_worksheet(row,
                       3,
                       str(math.floor(time_taken_our_solver / 60)) + " mins " + str(
                           time_taken_our_solver % 60) + " sec")
    write_in_worksheet(row,
                       4,
                       str(math.floor(time_taken_sat_solver / 60)) + " mins " + str(
                           time_taken_sat_solver % 60) + " sec")
    write_in_worksheet(row,
                       5,
                       str(math.floor(time_taken_csat_solver / 60)) + " mins " + str(
                           time_taken_csat_solver % 60) + " sec")
    return {
        "success": False if not is_sat_extension_found else True,
        "time_taken_cus_solver": time_taken_our_solver,
        "time_taken_sat_solver": time_taken_sat_solver,
        "time_taken_csat_solver": time_taken_csat_solver,
        "time_taken_bh3_solver": time_taken_bh3_sat_solver,
        "sat_cus_differ": False if (is_sat_extension_found and solver_output.get("bh3_minisat_satisfiable"))
                                   or (not is_sat_extension_found and not solver_output.get(
            "bh3_minisat_satisfiable")) else True,
        "sat_csat_differ": False if (is_sat_extension_found and is_custom_sat_extension_found)
                                    or (not is_sat_extension_found and not is_custom_sat_extension_found) else True,
        "time_taken_sat_solver_wo_init": time_taken_sat_solver_wo_init,
        "time_taken_csat_solver_wo_init": time_taken_csat_solver_wo_init,
        "time_taken_bh3_solver_wo_init": time_taken_bh3_sat_solver_wo_init

    }


def extension_to_str(extension):
    if not extension:
        return "{}"
    output_str = "{"
    for x in extension:
        output_str = output_str + str(x) + ","
    output_str = output_str + "}"
    output_str = output_str.replace(",}", "}")
    return output_str


def compute_friends(attack_set):
    friends_set = {}
    for i in range(1, len(attack_set) + 1):
        if not friends_set.get(i):
            friends_set[i] = []
        for j in range(i + 1, len(attack_set) + 1):
            if i not in attack_set[j] and j not in attack_set[i]:
                friends_set[i].append(j)
                if friends_set.get(j):
                    friends_set[j].append(i)
                else:
                    friends_set[j] = []
                    friends_set[j].append(i)
    return friends_set


def compute_pure_attacked_by(attack_set):
    pure_attack_by_set = {}
    for i in range(1, len(attack_set) + 1):
        if not pure_attack_by_set.get(i):
            pure_attack_by_set[i] = []
        for j in range(i + 1, len(attack_set) + 1):
            if not pure_attack_by_set.get(j):
                pure_attack_by_set[j] = []
            if i not in attack_set[j] and j in attack_set[i]:
                pure_attack_by_set[j].append(i)
            elif j not in attack_set[i] and i in attack_set[j]:
                pure_attack_by_set[i].append(j)
            else:
                continue
    return pure_attack_by_set


def compute_arg_extension(graph_set, friend_set, e, f, h):
    if len(h) == 0:
        return e
    p = select_pivot_set(graph_set, f, h)
    # print(p)
    p = order_pivot_set_based_on_hostile_attack_weight(graph_set, p, f, h)
    while len(p) != 0:
        v = p[0]  # select_pivot
        print(v)
        e_new = merge_arr(e, [v])
        f_new = remove_arr(f, merge_arr(
            merge_arr(get_nodes_attacked_by_given_v(graph_set, v, f), get_nodes_attacks_given_v(graph_set, v, f)), [v]))
        h_new = remove_arr(
            merge_arr(h, remove_arr(get_nodes_attacks_given_v(graph_set, v, f),
                                    get_nodes_attacked_by_given_v(graph_set, v, f))),
            get_nodes_attacked_by_given_v(graph_set, v, h))

        result = compute_arg_extension(graph_set, friend_set, e_new, f_new, h_new)
        if result:
            return result
        p.remove(v)
    return None


def select_pivot_set(attak_set, f, h):
    pivot_set = []
    for x in f:
        hasAttackOnH = len([i for i in attak_set[x] if i in h]) != 0
        if hasAttackOnH:
            pivot_set.append(x)
    return pivot_set


def remove_arr(arr1, arr2):
    return [i for i in arr1 if i not in arr2]


def merge_arr(arr1, arr2):
    resutArr = arr1
    for x in arr2:
        if x not in resutArr:
            resutArr.append(x)
    return resutArr


# implemented BH3 branching heuristics
def order_pivot_set_based_on_hostile_attack_weight(attack_set, p, f, h):
    pivot_attack_weight = []
    # print("F_SET:"+ str(f))
    # print("H_SET:" + str(h))
    for x in p:
        attack_weight_x = [x]
        hostile_attacked_by_x = get_nodes_attacked_by_given_v(attack_set, x, h)
        friends_attacks_x = get_nodes_attacks_given_v(attack_set, x, f)
        friends_attacked_by_x = get_nodes_attacked_by_given_v(attack_set, x, f)
        # print("Hostile:"+ str(hostile_attacked_by_x))
        friends_set_considered = remove_arr(friends_attacks_x, friends_attacked_by_x)
        # print("F:" + str(friends_set_considered))
        attack_weight_x.append(len(hostile_attacked_by_x) - len(friends_set_considered))
        pivot_attack_weight.append(attack_weight_x)

    pivot_attack_weight.sort(key=sort_by_weight, reverse=True)
    print(pivot_attack_weight)
    ordered_pivot = []
    for x in pivot_attack_weight:
        ordered_pivot.append(x[0])
    return ordered_pivot


def sort_by_weight(value):
    return value[1]


def get_nodes_attacked_by_given_v(graph_set, v, givenset=None):
    attcks_by_v = graph_set[v]
    if not givenset:
        return attcks_by_v
    else:
        return [i for i in attcks_by_v if i in givenset]


def get_nodes_attacks_given_v(attack_set, v, givenset=None):
    resutl_arr = []
    for i in range(1, len(attack_set) + 1):
        if v in attack_set[i]:
            resutl_arr.append(i)
    if not givenset:
        return resutl_arr
    else:
        return [i for i in resutl_arr if i in givenset]


def friends_v(friends_set, v):
    return friends_set[v]


def write_in_worksheet(r, c, val):
    if worksheetNeeded:
        worksheet.write(r, c, val)
    else:
        return


def init_worksheet():
    if not worksheetNeeded:
        return
    else:
        write_in_worksheet(0, 0, "n")
        write_in_worksheet(0, 1, "p")
        write_in_worksheet(0, 2, "q")
        write_in_worksheet(0, 3, "Total Graph instances computed")
        write_in_worksheet(0, 4, "Result : Fraction of success instance")
        write_in_worksheet(0, 5, "Time taken for N graph instances generation & Extension computation")
        write_in_worksheet(1, 0, noOfNodes)
        write_in_worksheet(1, 1, probability)
        write_in_worksheet(1, 2, q_probability)
        write_in_worksheet(1, 3, noOfGraphInstances)

        write_in_worksheet(2, 0, "Extension Details:")
        write_in_worksheet(3, 0, "Graph-Instance")
        write_in_worksheet(3, 1, "Admissible Set by Our solver")
        write_in_worksheet(3, 2, "Admissible Set by Sat solver")
        write_in_worksheet(3, 3, "Time taken to compute extension by Our solver")
        write_in_worksheet(3, 4, "Time taken to compute extension by MiniSAT solver")
        write_in_worksheet(3, 5, "Time taken to compute extension by Custom MiniSAT solver")


if __name__ == '__main__':
    noOfNodes = 128
    probability = 0.75
    q_probability = 0.06
    noOfGraphInstances = 25
    worksheetNeeded = False

    noOfNodes = int(input("Enter the No. of Nodes: "))
    # probability = float(input("Enter probability: "))
    # q_probability = float(input("Enter Symmetric attack probability: "))
    # noOfGraphInstances = int(input("No. of graph instances needed: "))

    x_axis = []
    y_axis = []

    y_axis_time_taken_cus = []

    y_axis_time_taken_sat = []

    y_axis_time_taken_csat = []

    y_axis_time_taken_sat_wo_init = []

    y_axis_time_taken_csat_wo_init = []
    y_axis_time_taken_bh3_sat_wo_init = []
    y_axis_solver_err = []
    y_axis_solver_err_csat = []

    firststartTime = int(time() * 1000)

    while q_probability <= 0.50:
        x_axis.append(q_probability)

        if worksheetNeeded:
            workbook = xlsxwriter.Workbook('./output/Sample_D_d_p_q_output_' + str(q_probability) + '.xlsx')
            worksheet = workbook.add_worksheet()
            init_worksheet()

        row = 4
        noOfSuccess = 0

        timeTakenByCustomSolver = 0
        timeTakenBySatSolver = 0
        timeTakenByCSatSolver = 0
        timeTakenBySatSolverWoInit = 0
        timeTakenByCSatSolverWOInit = 0
        timeTakenByBh3SatSolverWOInit = 0
        noOfSatCusSolverErr = 0
        noOfCSatCusSolverErr = 0

        startTime = int(time() * 1000)
        print("StartTime:" + str(startTime))
        for i in range(1, noOfGraphInstances + 1):
            instanceStartTime = int(time() * 1000)
            print("\nq_probability:", q_probability, "#graph_instance:", i)
            returnValueSet = compute_graph_instance(row)
            noOfSuccess = noOfSuccess + 1 if returnValueSet.get("success") else noOfSuccess
            timeTakenByCustomSolver += returnValueSet.get("time_taken_bh3_solver")
            timeTakenBySatSolver += returnValueSet.get("time_taken_sat_solver")
            timeTakenByCSatSolver += returnValueSet.get("time_taken_csat_solver")
            timeTakenBySatSolverWoInit += returnValueSet.get("time_taken_sat_solver_wo_init")
            timeTakenByCSatSolverWOInit += returnValueSet.get("time_taken_csat_solver_wo_init")
            timeTakenByBh3SatSolverWOInit += returnValueSet.get("time_taken_bh3_solver_wo_init")
            noOfSatCusSolverErr += 1 if returnValueSet.get("sat_cus_differ") else 0
            noOfCSatCusSolverErr += 1 if returnValueSet.get("sat_csat_differ") else 0
            row = row + 1
            instanceEndTime = int(time() * 1000)
            print("Time taken for this instance:", round((instanceEndTime - instanceStartTime) / 60000, 0))

        endTime = int(time() * 1000)
        print("EndTime:" + str(endTime))
        timeTaken = endTime - startTime
        write_in_worksheet(1, 4, noOfSuccess / noOfGraphInstances)

        y_axis.append(noOfSuccess / noOfGraphInstances)
        y_axis_time_taken_cus.append(timeTakenByCustomSolver / noOfGraphInstances)
        y_axis_time_taken_sat.append(timeTakenBySatSolver / noOfGraphInstances)
        y_axis_time_taken_csat.append(timeTakenByCSatSolver / noOfGraphInstances)
        y_axis_solver_err.append(noOfSatCusSolverErr)
        y_axis_solver_err_csat.append(noOfCSatCusSolverErr)
        y_axis_time_taken_sat_wo_init.append(timeTakenBySatSolverWoInit / noOfGraphInstances)
        y_axis_time_taken_csat_wo_init.append(timeTakenByCSatSolverWOInit / noOfGraphInstances)
        y_axis_time_taken_bh3_sat_wo_init.append(timeTakenByBh3SatSolverWOInit / noOfGraphInstances)

        timeTakenInSec = round(timeTaken / 1000, 0)
        write_in_worksheet(1, 5, str(math.floor(timeTakenInSec / 60)) + " mins " + str(timeTakenInSec % 60) + " sec")

        q_probability += 0.02
        if worksheetNeeded:
            workbook.close()

    print("Y axis:")
    print(y_axis)
    print("Time take custom solver:")
    print(y_axis_time_taken_cus)
    print("Total Time taken minisat:")
    print(y_axis_time_taken_sat)
    print("Total time taken custom minisat:")
    print(y_axis_time_taken_csat)
    print("Time taken wo init minisat:")
    print(y_axis_time_taken_sat_wo_init)
    print("Time taken wo init custom minisat:")
    print(y_axis_time_taken_csat_wo_init)
    print("Time taken wo init bh3 minisat:")
    print(y_axis_time_taken_bh3_sat_wo_init)

    fig = plt.figure(figsize=[4, 2], facecolor='white', constrained_layout=True)
    plt.rc('font', size=3)
    plt.rcParams['font.size'] = 5
    plt.rcParams['text.color'] = '#8d8c8c'
    # plt.grid(True, linewidth=0.60, color='#eeeded', linestyle='-')
    axs = fig.add_subplot(1, 1, 1)
    axs.spines['top'].set_color('#c4c4c4')
    axs.spines['left'].set_color('#c4c4c4')
    axs.spines['bottom'].set_color('#c4c4c4')
    axs.spines['right'].set_color('#c4c4c4')
    for label in (axs.get_xticklabels() + axs.get_yticklabels()):
        label.set_fontsize(2)
    axs.set_xlim([0.06, 0.5])
    axs.set_xticks(x_axis, minor=True)
    axs.set_xticks([0.06, 0.16, 0.26, 0.36, 0.46], minor=False)
    axs.xaxis.grid(True, which='major', linewidth=0.3, color='#eeeded', linestyle='-')
    axs.xaxis.grid(True, which='minor', linewidth=0.3, color='#eeeded', linestyle='-')
    axs.yaxis.grid(True, linewidth=0.60, color='#eeeded', linestyle='-')
    axs.tick_params(
        axis='x', labelsize=5, length=0, width=0,
        labelcolor='#8d8c8c'
    )
    axs.tick_params(
        axis='x', labelsize=5, length=0, width=0,
        labelcolor='#8d8c8c', which='minor'
    )
    axs.tick_params(
        axis='y', labelsize=5, length=0, width=0,
        labelcolor='#8d8c8c'
    )

    axs.plot(x_axis, y_axis, marker='o', markerfacecolor='black', markersize=0.5, color='black', linewidth=0.25,
             label="Avg. rate of success")
    # axs.set_title("Success rate in Admissible set computation")
    axs.set_xlabel('Probability of Symmetric Attack: q')
    axs.set_ylabel('Average rate of success instance')

    axs.legend(loc='center left', frameon=False, facecolor='white')

    axs2 = axs.twinx()
    axs2.spines['top'].set_color('#c4c4c4')
    axs2.spines['left'].set_color('#c4c4c4')
    axs2.spines['bottom'].set_color('#c4c4c4')
    axs2.spines['right'].set_color('#c4c4c4')
    for label in (axs2.get_xticklabels() + axs2.get_yticklabels()):
        label.set_fontsize(5)
    axs2.set_xlim([0.06, 0.5])
    axs2.set_xticks(x_axis, minor=True)
    axs2.set_xticks([0.06, 0.16, 0.26, 0.36, 0.46], minor=False)
    # plt.grid(True, linewidth=0.60, color='#eeeded', linestyle='-')
    axs2.xaxis.grid(True, which='major', linewidth=0.3, color='#eeeded', linestyle='-')
    axs2.xaxis.grid(True, which='minor', linewidth=0.3, color='#eeeded', linestyle='-')
    axs2.tick_params(
        axis='x', labelsize=5, length=0, width=0,
        labelcolor='#8d8c8c'
    )
    axs2.tick_params(
        axis='x', labelsize=5, length=0, width=0,
        labelcolor='#8d8c8c', which='minor'
    )
    axs2.tick_params(
        axis='y', labelsize=5, length=0, width=0,
        labelcolor='#8d8c8c'
    )
    axs2.set_ylabel('Time taken (in Seconds)')
    axs2.plot(x_axis, y_axis_time_taken_sat_wo_init, marker='o', markerfacecolor='red', markersize=0.5,
              color='red', label='VSIDS branching', linewidth=0.25)
    axs2.plot(x_axis, y_axis_time_taken_csat_wo_init, marker='o', markerfacecolor='#4b0082', markersize=0.5,
              color='#4b0082', label='AROFS branching', linewidth=0.25)
    axs2.plot(x_axis, y_axis_time_taken_bh3_sat_wo_init, marker='o', markerfacecolor='green', markersize=0.5,
              color='green', label='BRmcha-BH3 branching', linewidth=0.25)
    axs2.legend(loc='center right', frameon=False, facecolor='white')

    plt.savefig("./output/comparison_graph.png", dpi=300)
    plt.close()

    fig = plt.figure(figsize=[8, 4], facecolor='white', constrained_layout=True)
    gs = fig.add_gridspec(2, 4)

    ax = fig.add_subplot(gs[0, :2])
    plt.rc('font', size=5)
    plt.rcParams['font.size'] = 5
    plt.rcParams['text.color'] = '#8d8c8c'
    ax.spines['top'].set_color('#c4c4c4')
    ax.spines['left'].set_color('#c4c4c4')
    ax.spines['bottom'].set_color('#c4c4c4')
    ax.spines['right'].set_color('#c4c4c4')
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontsize(5)
    ax.plot(x_axis, y_axis_time_taken_sat_wo_init, marker='o', markerfacecolor='red', markersize=0.5,
            color='red', label='VSIDS branching', linewidth=0.25)
    ax.plot(x_axis, y_axis_time_taken_csat_wo_init, marker='o', markerfacecolor='#4b0082', markersize=0.5,
            color='#4b0082', label='AROFS branching', linewidth=0.25)
    ax.plot(x_axis, y_axis_time_taken_bh3_sat_wo_init, marker='o', markerfacecolor='green', markersize=0.5,
            color='green', label='BRmcha-BH3 branching', linewidth=0.25)
    ax.set_xlim([0.06, 0.5])
    ax.set_xticks(x_axis, minor=True)
    ax.set_xticks([0.06, 0.16, 0.26, 0.36, 0.46], minor=False)
    plt.grid(True, linewidth=0.60, color='#eeeded', linestyle='-')
    ax.xaxis.grid(True, which='major', linewidth=0.3, color='#eeeded', linestyle='-')
    ax.xaxis.grid(True, which='minor', linewidth=0.3, color='#eeeded', linestyle='-')
    ax.tick_params(
        axis='x', labelsize=5, length=0, width=0,
        labelcolor='#8d8c8c'
    )
    ax.tick_params(
        axis='x', labelsize=5, length=0, width=0,
        labelcolor='#8d8c8c', which='minor'
    )
    ax.tick_params(
        axis='y', labelsize=5, length=0, width=0,
        labelcolor='#8d8c8c'
    )
    ax.set_title("(A): n = 512")

    leg = ax.legend(loc='best', frameon=False, facecolor='white')

    ax2 = fig.add_subplot(gs[0, 2:])
    plt.rc('font', size=5)
    plt.rcParams['font.size'] = 5
    plt.rcParams['text.color'] = '#8d8c8c'

    ax2.spines['top'].set_color('#c4c4c4')
    ax2.spines['left'].set_color('#c4c4c4')
    ax2.spines['bottom'].set_color('#c4c4c4')
    ax2.spines['right'].set_color('#c4c4c4')
    for label in (ax2.get_xticklabels() + ax2.get_yticklabels()):
        label.set_fontsize(5)
    ax2.plot(x_axis, y_axis_time_taken_sat_wo_init, marker='o', markerfacecolor='red', markersize=0.5,
             color='red', linewidth=0.25)
    ax2.plot(x_axis, y_axis_time_taken_csat_wo_init, marker='o', markerfacecolor='#4b0082', markersize=0.5,
             color='#4b0082', linewidth=0.25)
    ax2.plot(x_axis, y_axis_time_taken_bh3_sat_wo_init, marker='o', markerfacecolor='green', markersize=0.5,
             color='green', linewidth=0.25)
    ax2.set_xlim([0.06, 0.5])
    ax2.set_xticks(x_axis, minor=True)
    ax2.set_xticks([0.06, 0.16, 0.26, 0.36, 0.46], minor=False)
    plt.grid(True, linewidth=0.60, color='#eeeded', linestyle='-')
    ax2.xaxis.grid(True, which='major', linewidth=0.3, color='#eeeded', linestyle='-')
    ax2.xaxis.grid(True, which='minor', linewidth=0.3, color='#eeeded', linestyle='-')
    ax2.tick_params(
        axis='x', labelsize=5, length=0, width=0,
        labelcolor='#8d8c8c'
    )
    ax2.tick_params(
        axis='x', labelsize=5, length=0, width=0,
        labelcolor='#8d8c8c', which='minor'
    )
    ax2.tick_params(
        axis='y', labelsize=5, length=0, width=0,
        labelcolor='#8d8c8c'
    )
    ax2.set_title("(B): n = 256")

    ax3 = fig.add_subplot(gs[1, 1:3])
    plt.rc('font', size=5)
    plt.rcParams['font.size'] = 5
    plt.rcParams['text.color'] = '#8d8c8c'

    ax3.spines['top'].set_color('#c4c4c4')
    ax3.spines['left'].set_color('#c4c4c4')
    ax3.spines['bottom'].set_color('#c4c4c4')
    ax3.spines['right'].set_color('#c4c4c4')
    ax3.plot(x_axis, y_axis_time_taken_sat_wo_init, marker='o', markerfacecolor='red', markersize=0.5,
             color='red', linewidth=0.25)
    ax3.plot(x_axis, y_axis_time_taken_csat_wo_init, marker='o', markerfacecolor='#4b0082', markersize=0.5,
             color='#4b0082', linewidth=0.25)
    ax3.plot(x_axis, y_axis_time_taken_bh3_sat_wo_init, marker='o', markerfacecolor='green', markersize=0.5,
             color='green', linewidth=0.25)
    ax3.set_xlim([0.06, 0.5])
    ax3.set_xticks(x_axis, minor=True)
    ax3.set_xticks([0.06, 0.16, 0.26, 0.36, 0.46], minor=False)
    plt.grid(True, linewidth=0.60, color='#eeeded', linestyle='-')
    ax3.xaxis.grid(True, which='major', linewidth=0.3, color='#eeeded', linestyle='-')
    ax3.xaxis.grid(True, which='minor', linewidth=0.3, color='#eeeded', linestyle='-')
    ax3.tick_params(
        axis='x', labelsize=5, length=0, width=0,
        labelcolor='#8d8c8c'
    )
    ax3.tick_params(
        axis='x', labelsize=5, length=0, width=0,
        labelcolor='#8d8c8c', which='minor'
    )
    ax3.tick_params(
        axis='y', labelsize=5, length=0, width=0,
        labelcolor='#8d8c8c'
    )
    ax3.set_title("(C): n = 128")
    plt.savefig("./output/sat_comparison_graph.png", dpi=300)
    plt.close()

    # plt.plot(x_axis, y_axis_solver_err, marker='o', markerfacecolor='black', markersize=5, color='black')
    # plt.title("Solver Error Stats")
    # plt.xlabel("q_probability")
    # plt.ylabel("No. of solver error instance")
    # plt.savefig("./output/solver_error.png")
    # plt.close()
    #
    # plt.plot(x_axis, y_axis_solver_err_csat, marker='o', markerfacecolor='black', markersize=5, color='black')
    # plt.title("Custom MiniSAT Solver Error Stats")
    # plt.xlabel("q_probability")
    # plt.ylabel("No. of solver error instance")
    # plt.savefig("./output/csat_solver_error.png")
    # plt.close()

    finalEndTime = int(time() * 1000)
    print("start:" + str(firststartTime))
    print("end:" + str(finalEndTime))
    print(finalEndTime - firststartTime)
