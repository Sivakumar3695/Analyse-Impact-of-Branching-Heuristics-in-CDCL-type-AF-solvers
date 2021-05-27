from time import perf_counter
import main
import dimacsgenerator as dimacs
from tempfile import NamedTemporaryFile
import os
import tracemalloc

def get_admissible_set(attack_set, vertex_list, attacked_by_dict):
    print(attack_set)
    tracemalloc.start()
    start_time = perf_counter()
    dimac_g = dimacs.Generator()
    cla_cnt = 0
    clause_nf = ""
    for i in vertex_list:
        # print("Dimacs::Vertex:"+ str(i))
        clause_nf += ("&" + str(i))
        nodes_attacks_i = main.get_nodes_attacks_given_v(attack_set, i)

        if len(nodes_attacks_i) == 0:
            cla_cnt += 1
            dimac_g.add_clause_cnf_format(str(i))
        else:
            for j in nodes_attacks_i:
                cla_cnt += 1
                dimac_g.add_clause([i * -1, j * -1])
                nodes_attacks_j = attacked_by_dict[j].copy()
                nodes_attacks_j.insert(0, i * -1)
                dimac_g.add_clause(nodes_attacks_j)

    cla_cnt += 1
    dimac_g.add_clause_cnf_format(clause_nf)
    infile = dimac_g.get_dimacs_file(len(vertex_list))
    infile.flush()
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
    outfile = NamedTemporaryFile(mode='r')
    print("Dimacs file generated")
    time_taken_for_formula_construction = perf_counter() - start_time

    start_time = perf_counter()
    os.system("cd ./minisat/core && ./minisat {0} {1} >/dev/null"
              .format(infile.name, outfile.name))
    os.system("cd ../..")
    time_taken_for_solver = perf_counter() - start_time

    lines = outfile.readlines()
    return_obj = {}
    success = False if lines[0] == "UNSAT\n" else True
    if success:
        print("Minisat solver: Extension found.")
        return_obj['minisat_satisfiable'] = True
        return_obj['minisat_time_taken_wo_formula_generation'] = time_taken_for_solver
        return_obj['minisat_total_time_taken'] = time_taken_for_formula_construction + time_taken_for_solver
    else:
        print("Minisat solver: Extension not found.")
        return_obj['minisat_satisfiable'] = False
        return_obj['minisat_time_taken_wo_formula_generation'] = time_taken_for_solver
        return_obj['minisat_total_time_taken'] = time_taken_for_formula_construction + time_taken_for_solver
    outfile.close()

    outfile = NamedTemporaryFile(mode='r')
    start_time = perf_counter()
    os.system("cd ./minisat/core_arofs && ./minisat {0} {1} >/dev/null"
            .format(infile.name,outfile.name))
    os.system("cd ../..")
    time_taken_for_custom_solver = perf_counter() - start_time
    lines = outfile.readlines()
    success = False if lines[0] == "UNSAT\n" else True
    if success:
        print("Custom Minisat solver: Extension found.")
        return_obj['custom_minisat_satisfiable'] = True
        return_obj['custom_minisat_time_taken_wo_formula_generation'] = time_taken_for_custom_solver
        return_obj['custom_minisat_total_time_taken'] = time_taken_for_formula_construction + time_taken_for_custom_solver
    else:
        print("Custom minisat solver: Extension not found.")
        return_obj['custom_minisat_satisfiable'] = False
        return_obj['custom_minisat_time_taken_wo_formula_generation'] = time_taken_for_custom_solver
        return_obj['custom_minisat_total_time_taken'] = time_taken_for_formula_construction + time_taken_for_custom_solver
    outfile.close()

    outfile = NamedTemporaryFile(mode='r')
    start_time = perf_counter()
    os.system("cd ./minisat/core_bh3 && ./minisat {0} {1} >/dev/null"
              .format(infile.name, outfile.name))
    os.system("cd ../..")
    time_taken_for_bh3_solver = perf_counter() - start_time
    lines = outfile.readlines()
    success = False if lines[0] == "UNSAT\n" else True
    if success:
        print("BH3 Minisat solver: Extension found.")
        return_obj['bh3_minisat_satisfiable'] = True
        return_obj['bh3_minisat_time_taken_wo_formula_generation'] = time_taken_for_bh3_solver
        return_obj[
            'bh3_minisat_total_time_taken'] = time_taken_for_formula_construction + time_taken_for_bh3_solver
    else:
        print("BH3 minisat solver: Extension not found.")
        return_obj['bh3_minisat_satisfiable'] = False
        return_obj['bh3_minisat_time_taken_wo_formula_generation'] = time_taken_for_bh3_solver
        return_obj[
            'bh3_minisat_total_time_taken'] = time_taken_for_formula_construction + time_taken_for_bh3_solver
    outfile.close()
    infile.close()
    return return_obj
