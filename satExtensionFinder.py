import main
from satispy import Variable, Cnf
from satispy.solver import Minisat


class CnfFormula:
    def __init__(self):
        self.clause_list = []

    def add_clause(self, clause):
        self.clause_list.append(clause)
        # cnf_formula = clause_list[0]
        # for i in range(1, len(clause_list)):
        #     clause = clause_list[i]
        #     cnf_formula = cnf_formula and clause
        # self.cnf = cnf_formula

    def print(self):
        exp = Cnf()
        cnf_formula = ""
        for i in range(0, len(self.clause_list)):
            clause = self.clause_list[i]
            if isinstance(clause, BaseClause):
                cnf_formula = cnf_formula + clause.get_clause_str()
            else:
                cnf_formula = cnf_formula + str(clause)
            if i < len(self.clause_list) - 1:
                cnf_formula = cnf_formula + " AND "
            else:
                continue
        print(cnf_formula)


class BaseClause:
    def __init__(self, node_list, operator, negate_nodes=False):
        self.node_list = node_list
        self.operator = str(operator)
        self.negate = negate_nodes
        # for i in range(1, len(nodeList)):
        #     node = nodeList[i]
        #     if operator == "&":
        #         clause = clause and node
        #     else:
        #         clause = clause or node
        # self.clause = clause

    def get_clause_str(self):
        clause_str = "("
        for i in range(0, len(self.node_list)):
            node = self.node_list[i]
            if isinstance(node, BaseClause):
                clause_str = clause_str + node.get_clause_str()
            else:
                clause_str = clause_str + ("" if not self.negate else "NOT ") + str(node)

            if i < len(self.node_list) - 1:
                clause_str = clause_str + " " + self.operator + " "
            else:
                continue

        clause_str = clause_str + ")"
        return clause_str


# class NodeClause:
#     def __init__(self, node, baseClause, operator):
#         self.clause = node and baseClause if operator == "&" else node or baseClause


def get_stable_extension(attack_set, vertex_list):
    # cnf_formula = CnfFormula()
    # attack_set = {1: [], 2: [1], 3: [1, 2], 4: [2]}
    # # print(attack_set)
    # vertex_list = [1, 2, 3, 4]
    var_list = {}
    for i in vertex_list:
        var_list[i] = Variable(str(i))
    exp = Cnf()
    for i in vertex_list:
        var_i = var_list[i]
        nodes_attacks_i = main.get_nodes_attacks_given_v(attack_set, i)

        if len(nodes_attacks_i) == 0:
            exp &= var_i
        else:
            sub_exp = Cnf()
            for node in nodes_attacks_i:
                sub_exp |= var_list[node]

            sub_exp |= var_i
            exp &= sub_exp

            sec_sub_exp = Cnf()
            for j in nodes_attacks_i:
                var_j = var_list[j]
                sec_sub_exp &= (-(var_i) | -(var_j))
            exp &= sec_sub_exp

    solver = Minisat()
    solution = solver.solve(exp)

    if solution.error != False:
        print("Error:")
        print(solution.error)
    elif solution.success:
        print("Found a solution:")
        for i in vertex_list:
            var_i = var_list[i]
            print(var_i, solution[var_i])
            if (solution[var_i]):
                print("Attacks:", attack_set[i])
                print("Attacked By:", main.get_nodes_attacks_given_v(attack_set, i))
    else:
        print("The expression cannot be satisfied")


def get_admissible_set(attack_set, vertex_list):
    # cnf_formula = CnfFormula()
    # attack_set = {1: [], 2: [1], 3: [1, 2], 4: [2]}
    # # print(attack_set)
    # vertex_list = [1, 2, 3, 4]
    var_list = {}
    for i in vertex_list:
        var_list[i] = Variable(str(i))
    exp = Cnf()
    for i in vertex_list:
        var_i = var_list[i]
        nodes_attacks_i = main.get_nodes_attacks_given_v(attack_set, i)

        if len(nodes_attacks_i) == 0:
            exp &= var_i
        else:
            sub_exp = Cnf()
            for j in nodes_attacks_i:
                var_j = var_list[j]
                sub_exp &= (-(var_i) | -(var_j))
            exp &= sub_exp

            sec_sub_exp = Cnf()
            for j in nodes_attacks_i:
                nodes_attacks_j = main.get_nodes_attacks_given_v(attack_set, j)
                paj = Cnf()
                for k in nodes_attacks_j:
                    # if k == i:
                    #     continue
                    paj |= var_list[k]
                if paj.dis.__len__() != 0:
                    sec_sub_exp &= -(var_i) | paj
                else:
                    sec_sub_exp &= -(var_i)
            exp &= sec_sub_exp

    non_false_condition = Cnf()
    for vertex_id in vertex_list:
        non_false_condition |= var_list[vertex_id]
    exp &= non_false_condition

    # print(exp)
    solver = Minisat()
    solution = solver.solve(exp)

    if solution.error:
        print("Error:")
        print(solution.error)
    elif solution.success:
        print("SAT found a solution.")
        extension = []
        for i in vertex_list:
            var_i = var_list[i]
            if solution[var_i]:
                # print(var_i, solution[var_i])
                extension.append(i)
                # print("Attacks:", attack_set[i])
                # print("Attacked By:", main.get_nodes_attacks_given_v(attack_set, i))
        return extension
    else:
        print("The expression cannot be satisfied")
    return None
