import networkx as nx
import matplotlib.pyplot as plt
import random as random
import xlsxwriter
from time import time
import math
import satExtensionFinder
import customMiniSatExtensionFinder


def compute_graph_instance(row):
    g = nx.DiGraph()
    g.add_nodes_from(range(1, noOfNodes + 1))
    nodeMappingForGraph = {}
    for i in range(1, noOfNodes + 1):
        node_map_i = []  # if not nodeMappingForGraph.get(i) else nodeMappingForGraph.get(i)
        for j in range(1, noOfNodes + 1):
            if i == j:
                continue
            # print("Has edge from " + str(j) + " to " + str(i))
            # print(g.has_edge(u=j, v=i))
            random_n = random.random()
            # print("Random No. for " + str(i) + " to " + str(j) + ":" + str(random_n))

            if random_n <= probability and not g.has_edge(u=j, v=i):
                g.add_edge(i, j)
                node_map_i.append(j)
            else:
                continue
        nodeMappingForGraph[i] = node_map_i
    for i in range(1, noOfNodes + 1):
        for j in range(i + 1, noOfNodes + 1):
            hasEdgeAlreadyItoJ = g.has_edge(u=i, v=j)
            hasEdgeAlreadyJtoI = g.has_edge(u=j, v=i)
            nodeMapI = nodeMappingForGraph[i]
            nodeMapJ = nodeMappingForGraph[j]
            random_n = random.random()
            # print("Random No. :" + str(random_n))
            if random_n <= q_probability and (hasEdgeAlreadyItoJ or hasEdgeAlreadyJtoI):
                if hasEdgeAlreadyJtoI:
                    # print("Establishing symmetric attack... between " + str(i) + " and " + str(j))
                    g.add_edge(i, j)
                    nodeMapI.append(j)
                elif hasEdgeAlreadyItoJ:
                    # print("Establishing symmetric attack... between " + str(j) + " and " + str(i))
                    g.add_edge(j, i)
                    nodeMapJ.append(i)
                else:
                    continue
            else:
                continue
    # nx.draw(g, with_labels=True)
    labels = {}
    for i in range(1, noOfNodes + 1):
        labels[i] = str(i)

    # start
    # pos = nx.spring_layout(g)
    # nx.draw_networkx_nodes(g, pos=pos, node_size=10)
    # nx.draw_networkx_labels(g, pos=pos, labels=labels, font_size=10)
    # nx.draw_networkx_edges(g, pos)
    # file_name = "graph_instance_" + str(row) + ".png"
    # plt.savefig(file_name)
    # end

    # plt.close()

    # g2 = nx.erdos_renyi_graph(noOfNodes, p, directed=True)
    # pos = nx.circular_layout(g2)
    # nx.draw_networkx_nodes(g2, pos=pos, node_size=200)
    # # nx.draw_networkx_labels(g2, pos=pos, labels=labels, font_size=8)
    # nx.draw_networkx_edges(g2, pos)
    # fileName1 = "graph_instance_ER_" + str(row) + ".png"
    # plt.savefig(fileName1)
    # plt.close()

    # plt.show()
    # print("Attack Set:")
    # print(nodeMappingForGraph)
    friends_set = compute_friends(nodeMappingForGraph)
    # print("Friend Set:")
    # print(friends_set)
    vertex_set = [i for i in range(1, noOfNodes + 1)]
    # print("Vertex:")
    # print(vertex_set)

    extension = None
    extension_compute_start_time = int(time() * 1000)
    for x in vertex_set:
        # print("Computing extension for :" + str(x))
        extension = compute_arg_extension(nodeMappingForGraph, friends_set, [x], friends_set[x],
                                          remove_arr(get_nodes_attacks_given_v(nodeMappingForGraph, x),
                                                     get_nodes_attacked_by_given_v(nodeMappingForGraph, x)))
        if extension and len(extension) != 0:
            extension = None if not extension else merge_arr(extension, [x])
            print("Extension Found")
            break

    outputStr = extension_to_str(extension)
    # print(outputStr)
    extension_compute_end_time = int(time() * 1000)
    time_taken_our_solver = extension_compute_end_time - extension_compute_start_time
    time_taken_our_solver = round(time_taken_our_solver / 1000, 0)

    write_in_worksheet(row, 0, "Graph-Instance-" + str(row - 3))
    write_in_worksheet(row, 1, outputStr)

    extension_compute_start_time = int(time() * 1000)
    satExtension = satExtensionFinder.get_admissible_set(nodeMappingForGraph, vertex_set)
    extension_compute_end_time = int(time() * 1000)
    time_taken_sat_solver = extension_compute_end_time - extension_compute_start_time
    time_taken_sat_solver = round(time_taken_sat_solver / 1000, 0)

    outputSatExtensionStr = extension_to_str(satExtension)

    extension_compute_start_time = int(time() * 1000)
    csatExtension = customMiniSatExtensionFinder.get_admissible_set(nodeMappingForGraph, vertex_set, satExtension is None)
    extension_compute_end_time = int(time() * 1000)
    time_taken_csat_solver = extension_compute_end_time - extension_compute_start_time
    time_taken_csat_solver = round(time_taken_csat_solver / 1000, 0)

    outputCSatExtensionStr = extension_to_str(csatExtension)

    write_in_worksheet(row, 2, outputSatExtensionStr)
    write_in_worksheet(row, 3,
                       str(math.floor(time_taken_our_solver / 60)) + " mins " + str(
                           time_taken_our_solver % 60) + " sec")
    write_in_worksheet(row, 4,
                       str(math.floor(time_taken_sat_solver / 60)) + " mins " + str(
                           time_taken_sat_solver % 60) + " sec")
    write_in_worksheet(row, 5,
                       str(math.floor(time_taken_csat_solver / 60)) + " mins " + str(
                           time_taken_csat_solver % 60) + " sec")
    return {"success": False if not extension else True, "time_taken_cus_solver": time_taken_our_solver,
            "time_taken_sat_solver": time_taken_sat_solver, "time_taken_csat_solver": time_taken_csat_solver,
            "sat_cus_differ": False if (satExtension and extension) or (not satExtension and not extension) else True,
            "sat_csat_differ": False if (satExtension and csatExtension) or (
                        not satExtension and not csatExtension) else True
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


def compute_arg_extension(graph_set, friend_set, e, f, h):
    if len(h) == 0:
        return e
    p = select_pivot_set(graph_set, f, h)
    p = order_pivot_set_based_on_hostile_attack_weight(graph_set, p, f, h)
    while len(p) != 0:
        v = p[0]  # select_pivot
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


def order_pivot_set_based_on_hostile_attack_weight(attack_set, p, f, h):
    pivot_attack_weight = []
    for x in p:
        attack_weight_x = [x]
        hostile_attacked_by_x = get_nodes_attacked_by_given_v(attack_set, x, h)
        friends_attacks_x = get_nodes_attacks_given_v(attack_set, x, f)
        friends_attacked_by_x = get_nodes_attacked_by_given_v(attack_set, x, f)

        friends_set_considered = remove_arr(friends_attacks_x, friends_attacked_by_x)

        attack_weight_x.append(len(hostile_attacked_by_x) - len(friends_set_considered))
        pivot_attack_weight.append(attack_weight_x)

    pivot_attack_weight.sort(key=sort_by_weight, reverse=True)
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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # noOfNodes = int(input("Enter the No. of Nodes: "))
    # probability = float(input("Enter probability: "))
    # q_probability = float(input("Enter Symmetric attack probability: "))
    # noOfGraphInstances = int(input("No. of graph instances needed: "))

    noOfNodes = 128
    probability = 0.75
    q_probability = 0.30
    noOfGraphInstances = 25
    worksheetNeeded = True

    x_axis = []
    y_axis = []

    y_axis_time_taken_cus = []
    y_axis_time_taken_sat = []
    y_axis_time_taken_csat = []
    y_axis_solver_err = []
    y_axis_solver_err_csat = []

    firststartTime = int(time() * 1000)

    while q_probability <= 0.40:
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
        noOfSatCusSolverErr = 0
        noOfCSatCusSolverErr = 0

        startTime = int(time() * 1000)
        print("StartTime:" + str(startTime))
        for i in range(1, noOfGraphInstances + 1):
            instanceStartTime = int(time() * 1000)
            print("q_probability:", q_probability, "#graph_instance:", i)
            returnValueSet = compute_graph_instance(row)
            noOfSuccess = noOfSuccess + 1 if returnValueSet.get("success") else noOfSuccess
            timeTakenByCustomSolver += returnValueSet.get("time_taken_cus_solver")
            timeTakenBySatSolver += returnValueSet.get("time_taken_sat_solver")
            timeTakenByCSatSolver += returnValueSet.get("time_taken_csat_solver")
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

        timeTakenInSec = round(timeTaken / 1000, 0)
        write_in_worksheet(1, 5, str(math.floor(timeTakenInSec / 60)) + " mins " + str(timeTakenInSec % 60) + " sec")

        # for i in range(4, noOfGraphInstances + 4):
        #     row = row + 3
        #     write_in_worksheet(row, 0, "Graph Instance" + str(i - 3) + ":")
        #     row = row + 2
        #     worksheet.insert_image(row, 0, "graph_instance_" + str(i) + ".png")
        #     # worksheet.insert_image(row, 14, "graph_instance_ER_" + str(i) + ".png")
        #     row = row + 24

        q_probability += 0.02
        if worksheetNeeded:
            workbook.close()

    fig, axs = plt.subplots(2, 1)
    plt.subplots_adjust(left=0.14, bottom=0.12, hspace=0.70)
    fig.suptitle("New Random Model with n=" + str(noOfNodes) + ", p=" + str(probability), fontsize=16)

    fig.set_size_inches(8, 8)

    axs[0].plot(x_axis, y_axis, marker='o', markerfacecolor='black', markersize=5, color='black')
    axs[0].set_title("Success rate in Admissible set computation")
    axs[0].set_xlabel('q_probability')
    axs[0].set_ylabel('Average value of success instance')

    axs[1].set_title("Time taken comparison between Custom solver, SAT(MiniSAT) solver, "
                     "SAT(MiniSAT) Solver with custom branching heuristics")
    axs[1].set_xlabel('q_probability')
    axs[1].set_ylabel('Time taken(in Seconds)')
    axs[1].plot(x_axis, y_axis_time_taken_cus, marker='o', markerfacecolor='green', markersize=5,
                color='green', label='Custom solver')
    axs[1].plot(x_axis, y_axis_time_taken_sat, marker='o', markerfacecolor='red', markersize=5,
                color='red', label='SAT(MiniSAT) solver')
    axs[1].plot(x_axis, y_axis_time_taken_csat, marker='o', markerfacecolor='violet', markersize=5,
                color='violet', label='SAT(MiniSAT) solver with custom branching heuristics')
    axs[1].legend()
    plt.savefig("./output/comparison_graph.png")
    plt.close()

    plt.plot(x_axis, y_axis_solver_err, marker='o', markerfacecolor='black', markersize=5, color='black')
    plt.title("Solver Error Stats")
    plt.xlabel("q_probability")
    plt.ylabel("No. of solver error instance")
    plt.savefig("./output/solver_error.png")
    plt.close()

    plt.plot(x_axis, y_axis_solver_err_csat, marker='o', markerfacecolor='black', markersize=5, color='black')
    plt.title("Custom MiniSAT Solver Error Stats")
    plt.xlabel("q_probability")
    plt.ylabel("No. of solver error instance")
    plt.savefig("./output/csat_solver_error.png")
    plt.close()

    finalEndTime = int(time() * 1000)
    print("start:" + str(firststartTime))
    print("end:" + str(finalEndTime))
    print(finalEndTime - firststartTime)
