################################################################################
#Author: Alec Golas                                                            #
#Date: June 10, 2019                                                           #
#Description: Driver for YAHFC uncertainty quantification                      #
################################################################################

import subprocess
import os
from shutil import which
import random
class Main:

    def __init__(self, inputdeck, name):

        self.name = name
        self.parameters = inputdeck

################################################################################
class YAHFC(Main):

    def input_generator(self):
        parameters = self.parameters

        f = open("{}.com".format(self.name), 'w')

        f.write('time YAHFC.x << input \n')
        f.write('file {}\n'.format(self.name))
        input_format = "{param} {value} \n"
        seed_bool = False
        for param, value in parameters:
            if param == 'seed':
                seed_bool = True
            f.write(input_format.format(param=param,value=value))
        if not seed_bool: 
            f.write('seed {}\n'.format(random.randint(10000,100000)))
        f.write("end\ninput\n")
        f.close()

    def run(self):
        init_process = "chmod +x {}.com".format(self.name)
        run_process = "{}.com".format(self.name)

        os.system(init_process)
        os.system(run_process)

        #subprocess.run(init_process)
        #subprocess.run(run_process)
################################################################################
class GEF(Main):

    def input_generator(self):

        file_name = "{}.input".format(self.name)
        run_path = os.path.join(os.getcwd(), file_name)
        gef_path = which('GEF')[:-4]
        input_path = os.path.join(gef_path, 'file.in')
        with open(input_path, 'w') as f:
            f.write(run_path)
            f.close()
        
        enhancement = "{}\n".format(self.parameters['enhancement factor'])
        options = "Options({})\n".format(self.parameters['options'])
        fissioning_system = "{}\n"

        with open(run_path, 'w') as f:
            enhancement = "{}\n".format(self.parameters['enhancement factor'])

            f.write(enhancement)

################################################################################
class Test(Main):

    def input_generator(self):
        input_format = "{param} {value}\n"
        with open('test','w') as f:
            for param, value in self.parameters:
                f.write(input_format.format(param=param, value=value))
            
            f.close()

    def run(self):
        pass


################################################################################
#                                End of File                                   #
################################################################################
