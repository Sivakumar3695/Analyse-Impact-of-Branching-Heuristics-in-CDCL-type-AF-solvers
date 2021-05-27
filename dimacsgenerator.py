from tempfile import NamedTemporaryFile
import os

class Generator:
    def __init__(self):
        self._cla_list = []
        self.__cla_cnt = 0
        self.__var_cnt = 0
        self.__var_arr = []
        self.__temp_file = NamedTemporaryFile(mode='r+')

    def add_clause(self, clause_arr):
        clause_arr_str = map(str, clause_arr)
        test_str = ' '.join(clause_arr_str)
        test_str += ' 0'
        self._cla_list.append(test_str)
        if len(self._cla_list) >= 5000:
            # print("started")
            test = '\n'.join(self._cla_list)
            self.__temp_file.write(test)
            self._cla_list = []
            # print("ended")
        # clause_arr_str += '0'
        # clause_arr_str = clause_arr_str.replace('[', '')
        # clause_arr_str = clause_arr_str.replace(',', '')
        # clause_arr_str = clause_arr_str.replace(']', ' 0')
        # + self.__content_str + test_str + ' 0'
        self.__cla_cnt += 1
        # for lit in clause_arr:
        #     var = lit.replace('-', '')
        #     if var not in self.__var_arr:
        #         self.__var_cnt += 1
        #         self.__var_arr.append(var)
        #     self.__content_str += str(lit)
        #     self.__content_str += " "
        # self.__content_str += "0"

    def add_clause_cnf_format(self, clause_cnf):
        self._cla_list.append(clause_cnf.replace('&', ' ') + ' 0')
        self.__cla_cnt += 1
        if len(self._cla_list) >= 15000:
            # print("started")
            test = '\n'.join(self._cla_list)
            self.__temp_file.write(test)
            self._cla_list = []
            # print("ended")

    def get_dimacs_file(self, var_cnt=None):
        if var_cnt is None:
            var_cnt = self.__var_cnt
        dimac_file = NamedTemporaryFile('w')
        print("CLa cnt:" + str(self.__cla_cnt))
        dimac_file.write("p cnf VAR_CNT CLA_CNT\n"
                          .replace('VAR_CNT', str(var_cnt))
                          .replace('CLA_CNT', str(self.__cla_cnt)))
        self.__temp_file.seek(0)
        lines = self.__temp_file.readlines()
        dimac_file.writelines(lines)

        print('started transferring contents from Temp file to Dimacs file')
        test = '\n'.join(self._cla_list)
        self._cla_list = []
        # print('ended')
        # for clause in self._cla_list:
        #     self.__content_str += '\n'
        #     self.__content_str = self.__content_str + clause
        dimac_file.write(test)
        self.__temp_file.close()
        # os.system("cp {0} ~/Desktop/{1}".format(dimac_file.name, 'test_128_tt1_'+dimac_file.name.replace('/tmp/', '')))
        return dimac_file
