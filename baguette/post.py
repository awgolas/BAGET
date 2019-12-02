################################################################################
# Author: Alec Golas                                                           #
# Date: June 17, 2019                                                          #
# Description: Processes the output data from running baget.py                 #
################################################################################

import glob
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

################################################################################
class PostProcessing:

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.rxn_data = self.xs_collect()


    def xs_collect(self):

        path_format = os.path.join(self.data_dir,'*','*','*')

        rxns = ['g','n','nn','nnn','np','p','pn','pp']
        rxn_paths = []
        for rxn in rxns:
            if len(glob.glob(os.path.join(path_format,rxn))) != 0:
                rxn_paths.append(os.path.join(path_format,rxn))
        
        rxn_lists = {}
        mapped_rxn_data = {}
        for path in rxn_paths:
            data_paths = glob.glob(os.path.join(path,'*cs*.dat'))
            for data_path in data_paths:
                label = data_path.split('/')[-1][:-4]
                try:
                    rxn_lists[label].append(data_path)
                except:
                    rxn_lists[label] = [data_path,]

        for label, paths in rxn_lists.items():
            mapped_rxn_data[label] = self.xs_map(paths)

        return mapped_rxn_data


    def xs_map(self, dir_list):
        xs_array = []
        xs_matrix = []
        for path in dir_list:
            f = open(path, 'r')
            xvals = []
            yvals = []
            for line in f.readlines():
                if '#' in line: continue
                sline = line.split()
                xvals.append(float(sline[0]))
                yvals.append(float(sline[1]))

            xs_array.append([xvals,yvals])

        num_e_bins = len(xs_array[0][0])
        for i in range(num_e_bins):
            xs_vals = []
            for e_xs_pairs in xs_array:
                xs_vals.append(e_xs_pairs[1][i])

            xs_matrix.append(xs_vals)

        xs_matrix = np.asarray(xs_matrix)
        e_vals = xs_array[0][0]
        xs_mapped = (e_vals, xs_matrix)

        return xs_mapped

################################################################################
class Analysis(PostProcessing):

    def normality_test(self, rxn, alpha=5E-3):
        e_vals, rxn_data = self.rxn_data[rxn]

        p_sum = 0.
        num_pops = len(rxn_data)

        for xs_vals in rxn_data:
            k2, p = stats.normaltest(xs_vals)
            psum += p

        avg_p = psum/num_pops
        non_gauss = 'p={} < alpha={}: The {} distribution is not gaussian'
        gauss = 'p={} > alpha={}: The {} distribution is gaussian'

        if avg_p < alpha:
            out_str = non_gauss
        else:
            out_str = gauss

        print(out_str.format(avg_p,alpha,rxn))

    def covariance(self, rxn):

        e_vals, rxn_data = self.rxn_data[rxn]
        cov = np.cov(rxn_data)
        return cov


################################################################################
class Plotting(PostProcessing):

    def __init__(self, xs_rxn_map):
        self.xs_rxn_map = xs_rxn_map


    def hist(self):
        pass
