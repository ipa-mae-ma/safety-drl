
"""
Created on December 14, 2018

@author: mae-ma
@attention: architectures for the safety DRL package
@contact: albus.marcel@gmail.com (Marcel Albus)
@version: 1.2.2

#############################################################################################

History:
- v1.2.2: update output
- v1.2.1: save experiment yaml
- v1.2.0: save results
- v1.1.0: add class
- v1.0.4: use global variables for yaml names
- v1.0.3: use dict for all configurations
- v1.0.2: catch if not all possibilities are calculated
- v1.0.1: output all configurations as yaml
- v1.0.0: first init
"""

import yaml
import os.path as path
import itertools
import datetime
import shutil
import time
###############################
# Necessary to import packages from different folders
###############################
import sys
import os
sys.path.extend([os.path.split(sys.path[0])[0]])
############################
from environment.fruit_collection_train import FruitCollectionTrain
from architectures.misc import Font

DOE_YAML = 'doe.yaml'
OUTPUT_YAML = 'experiments.yaml'

class DesignOfExperiments:
    def __init__(self):
        self.file_dir = path.dirname(os.path.realpath(__file__))
        self.output_dir = path.join(self.file_dir, 'output')
        if not path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.design_dict = yaml.load(
            open(path.join(self.file_dir, DOE_YAML), 'r'))

    def create_experiments(self) -> None:
        """
        creates combinations of all possible values
        """
        values = list(self.design_dict.values())
        experiments_tuple = list(itertools.product(*values))
        experiments = {}
        for num, tup in enumerate(experiments_tuple):
            experiments[num] = dict(zip(self.design_dict.keys(), tup))
        if self.how_many_possibilities() == len(experiments):
            yaml.dump(experiments, open(path.join(self.file_dir, OUTPUT_YAML), 'w'))
            print('Succesfully saved all possibilities!')
        else:
            self.experiments = None
            raise ValueError('Not all possibilites are covered... {} Possibilities but only {} are calculated'.format(
                self.how_many_possibilities(), len(experiments)))

    def how_many_possibilities(self) -> int:
        """
        calculates all possibilities
        """
        many = 1
        for value in self.design_dict.values():
            many *= len(value)
        return many



class RunDesignOfExperiments:
    def __init__(self):
        self.doe = DesignOfExperiments()
        self.experiments = yaml.load(open(path.join(self.doe.file_dir, OUTPUT_YAML), 'r'))
        self.src_filepath = os.getcwd()
        self.tgt_filepath = path.join(self.src_filepath, 'results')

        if not path.exists(self.tgt_filepath):
            os.makedirs(self.tgt_filepath)


    def info(self) -> None:
        """
        print info text in terminal
        """
        print('–' * 100)
        print('Run tests for {} possible configurations.'.format(self.doe.how_many_possibilities()))
        print('Variables:')
        print('NAME [NUM OF CHANGES]')
        for key in self.doe.design_dict.keys():
            print('- ', key, '[' + str(len(self.doe.design_dict[key])) + ']')
        print('–' * 100)

    def run(self) -> None:
        """
        run the experiments
        """
        global_time = time.time()
        for ex_number, experiment in self.experiments.items():
            start_time = time.time()
            architecture = experiment['architecture']
            fct = FruitCollectionTrain(warmstart=False, 
                                        simple=experiment['simple'], 
                                        render=False, 
                                        testing=False, 
                                        mode='mini', 
                                        architecture=architecture, 
                                        doe_params=experiment)
            print(Font.red + ('–' * 100 + '\n') * 2 + Font.end)
            print(Font.yellow + '>>> Experiment: {}/{}'.format(ex_number, self.doe.how_many_possibilities()) + Font.end)
            for key, value in experiment.items():
                print(Font.yellow + '-' + str(key) + ' : '  + str(value) + Font.end)
            print(Font.red + ('–' * 100 + '\n') * 2 + Font.end)
            if architecture.lower() == 'dqn':
                fct.main_dqn()
            elif architecture.lower() == 'a3c':
                fct.main_a3c()
            elif architecture.lower() == 'hra':
                fct.main_hra()
            else:
                raise ValueError('Incorrect architecture defined')
            print(Font.red + ('–' * 100 + '\n') * 2 + Font.end)
            self.save_results(architecture=architecture, 
                              experiment_number=ex_number, 
                              experiment_dict=experiment)
            time.sleep(1)
            print(Font.yellow + '>>> Time for experiment: {:.3f} min'.format((time.time() - start_time)/60) + Font.end)
            print(Font.red + ('–' * 100 + '\n') * 2 + Font.end)
        print(Font.red + ('–' * 100 + '\n') * 2 + Font.end)
        print('>>> Overall time for experiments: {:.3f} min'.format((time.time() - global_time)/60))
        print(Font.red + ('–' * 100 + '\n') * 2 + Font.end)

    def save_results(self, architecture: str=None, 
                     experiment_number: int=None, 
                     experiment_dict: dict=None,
                     game_mode: str='mini') -> None:
        """
        save the results of the experiment including experiment yaml file
        """
        if architecture is None or experiment_number is None:
            raise ValueError('Please provide a correct architecture name or experiment number')
        
        experiment_file_name = 'experiment_' + str(experiment_number) + '.yaml'
        yaml.dump(experiment_dict, open(path.join('output', experiment_file_name), 'w'))

        filelist = ['output/reward.yml', 
                    'output/training_log_' + architecture + '.csv',
                    'architectures/config_' + architecture + '.yml',
                    'output/model_' + architecture + '.yml',
                    path.join('output', experiment_file_name)]
        
        output_folder_name = datetime.datetime.today().strftime('%Y_%m_%d-%H_%M') + '___' + architecture + '_' + str(experiment_number)
        output_folder_path = os.path.join(self.tgt_filepath, output_folder_name)
        print('>>> Save all files to: ' + output_folder_path)
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)
        for file in filelist:
            shutil.copy2(os.path.join(self.src_filepath, file), output_folder_path)



if __name__ == '__main__':
    doe = DesignOfExperiments()
    doe.create_experiments()
    run_doe = RunDesignOfExperiments()
    run_doe.info()
    run_doe.run()