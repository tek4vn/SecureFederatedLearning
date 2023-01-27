from tek4fed.fed_learn import get_args, Server, FedAvg
from tek4fed.model_lib import get_model_function, set_model_weights
from tek4fed.data_lib import DataSetup
from tek4fed.compress_params_lib import CompressParams
from tek4fed.experiment_lib import Experiment, get_experiment_result
import copy
import numpy as np
import json


print("*** FIX VER 11")
"""
    ARGUMENT PARSER AND UNPACK JSON OBJECT
"""
args = get_args()

with open(args.config_path, 'r') as openfile:
    config = json.load(openfile)

global_config = config['global_config']
data_config = config['data_config']
fed_config = config['fed_config']
dp_config = config['dp_config']


"""
    SETTING EXPERIMENT
"""

print('Overwrite experiment mode: ', global_config['overwrite_experiment'])

experiment_config = {
    'name': global_config['name'],
    'dataset_name': data_config['dataset_name'],
    'overwrite_experiment': global_config['overwrite_experiment']
}

experiment = Experiment(experiment_config)
experiment.serialize_config(config)


"""
    CREATING SERVER AND CLIENT
"""

training_config = {
    'compress_digit': global_config['compress_digit'],
    'dataset_name': data_config['dataset_name'],
    'dp_mode': global_config['dp_mode'],
    'batch_size': fed_config['batch_size'], 
    'global_epochs': fed_config['global_epochs'], 
    'local_epochs': fed_config['local_epochs']
    }


weight_summarizer = FedAvg()
server = Server(get_model_function(data_config['dataset_name']), weight_summarizer, training_config, fed_config, dp_config)

server.update_training_config(training_config)
server.create_clients()

"""
    PREPROCESSING DATA AND DISTRIBUTING DATA
"""
DataSetup(data_config).setup(server)


"""
    SET UP CLIENTS
"""
server.setup()

"""
    TRAINING MODEL
"""
print('[INFO] TRAINING MODEL ...')
server.train_fed_encryption()

with open(str(experiment.train_hist_path), 'w') as f:
    test_dict = copy.deepcopy(server.global_test_metrics)
    json.dump(test_dict, f)

server.save_model_weights(experiment.global_weight_path)


'''
    EVALUATING MODEL
'''
print('[INFO] GET EXPERIMENT RESULTS ...')
get_experiment_result(server, experiment, data_config['dataset_name'])
