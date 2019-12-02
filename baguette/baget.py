################################################################################
#Author: Alec Golas                                                            #
#Date: June 10, 2019                                                           #
#Description: Performs UQ using yahfc_driver                                   #
################################################################################

import numpy as np
import os
import json
import argparse
import multiprocessing as mp
from collections import OrderedDict
import random
import time

from driver import YAHFC, GEF, Test

################################################################################
"""
jsonfile = {       'name' : name,
            'description' : description,
                    'out' : outputdirectory,
                   'code' : reaction_code,
              'num_procs' : np,
               'reaction' : {
                                   'target' : Zt At,
                               'projectile' : Zp Ap,
                             'proj_eminmax' : emin emax estep,
                                  'Delta_e' : delta_e,
                               'lev_option' : lev_option
                             },

                     'uq' : {'mode' : mc,
                             'num_samples' : num_samples,
                             'parameters'  : {       
                                              {'beta Zi Ai' : {
                                                               'sampling_type' : uniform/gauss/lognorm,
                                                               'parameters' : [min, max]/[mu, sigma]
                                                               },
                                               'beta Zj Aj' : {
                                                               'sampling_type' : uniform,
                                                               'parameters' : min max
                                                               }
                                                }
                }


inputdeck = {'target': Zt At,
             'projectile': Zp Ap,
             'beta Zi Bi': betai,
             'beta Zj Bj': betaj,
             ...}

"""


class Generator:

    def __init__(self, filename):
        f = open(filename,'r')
        self.params = json.load(f)
        self.input_list = self.input_gen()

    def input_gen(self):
        uq_modes = {'mc': self.mc_gen,
                    'gls' : self.gls_gen}
        mode = self.params['uq']['mode']
        generated_inputs = uq_modes[mode]()
        return generated_inputs

    def gls_gen(self):
        base_dir = self.params.get('out')
        if base_dir is None:
            base_dir = os.path.join(os.getcwd(), self.params['name'])

        uq_params = self.params['uq']['parameters']
        n_vals = self.params['uq'].get('samples_per_bin', 50)
        inp_vals = []
        names = list(uq_params.keys())
        for p, vals in uq_params.items():
            x, dx = vals['parameters']
            param_vals = [x-2.*dx, x-dx, x, x+dx, x+2.*dx]
            inp_vals.append(param_vals)

        param_mesh = np.meshgrid(*inp_vals)
        len_param_1d = len(param_mesh[0].flatten())
        param_mesh = np.array(param_mesh).reshape(len(param_mesh), len_param_1d)
        generated_inputs = []

        for i in range(len_param_1d):
            for n in range(n_vals):
                bin_dir = str(i).zfill(len(str(len_param_1d)))
                n_dir = str(n).zfill(len(str(n_vals)))
                deck = []
                for key, value in self.params['reaction'].items():
                    deck.append((key, value))
                for j, p in enumerate(names):
                    deck.append((p, param_mesh[j,i]))

                run_path = os.path.join(base_dir, bin_dir, n_dir)
                generated_inputs.append([run_path, deck])
        return generated_inputs

    def mc_gen(self):

        base_dir = self.params.get('out')
        if base_dir is None:
            base_dir = os.path.join(os.getcwd(), self.params['name'])
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)

        distributions = {'uniform' : random.uniform,
                         'gauss'   : random.gauss,
                         'lognorm' : random.lognormvariate}

        uq_params = self.params['uq']['parameters']
        n_vals = int(self.params['uq'].get(['num_samples'], 50))
        generated_inputs = []
        for i in range(n_vals):
            deck = []
            run_path = os.path.join(base_dir, str(i).zfill(len(str(n_vals))))
            for key, value in self.params['reaction'].items():
                deck.append((key,value))
            for p in uq_params.keys():
                rand = random.Random(time.clock())
                mc_dist = uq_params[p]['type']
                a_val, b_val = uq_params[p]['parameters']
                r = distributions[mc_dist](a_val,b_val)
                deck.append((p,r))
            generated_inputs.append([run_path, deck])
        return generated_inputs


################################################################################
class Driver(Generator):

    def run(self, input_deck):

        codes = {'yahfc'   : YAHFC,
                # 'gef'     : GEF,
                # 'frescox' : Frescox,
                 'test'    : Test
                }

        name = self.params['name']
        path, deck = input_deck

        if not os.path.exists(path):
            os.makedirs(path)
        os.chdir(path)

        code = codes[self.params['code']](deck,name)
        code.input_generator()
        code.run()


    def drive(self):

        num_procs = self.params.get('num_procs',mp.cpu_count())
        pool = mp.Pool(num_procs)

        name = self.params['name']
        if not os.path.exists(name):
            os.mkdir(name)

        os.chdir(name)

        input_list = self.input_list

        pool.map(self.run, input_list)

################################################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    filename = parser.parse_args().filename
    driver = Driver(filename)
    driver.drive()


