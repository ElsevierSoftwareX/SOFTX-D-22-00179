from dymola.dymola_interface import DymolaInterface

import numpy as np
import matplotlib.pyplot as plt
import sdf
import os
import time
import re
import shutil

import platform

def dymola_validation(pf_list, data_path, val_params, n_proc):
    '''

    '''
    # Instantiating dymola object (according to operating system)
    if platform.system() == 'Windows':
        # Extracting and formatting paths
        _openipsl_path = os.path.abspath(val_params['openipsl_path_windows'])
        _working_directory = os.path.join(os.path.abspath(val_params['working_directory_windows']), str(n_proc))

        # Instantiating dymola object
        dymolaInstance = DymolaInterface()
    elif platform.system() == 'Linux':

        # Extracting and formatting paths
        _openipsl_path = os.path.abspath(val_params['openipsl_path_linux'])
        # Making sure each process has an independent working directory
        _working_directory = os.path.join(os.path.abspath(val_params['working_directory_linux']), str(n_proc))
        _dymola_path = os.path.abspath(val_params['dymola_path_linux'])

        # Instantiating dymola object
        dymolaInstance = DymolaInterface(_dymola_path)

    if dymolaInstance is not None:
        print(f"{n_proc}: dymola using port: {dymolaInstance._portnumber}\n")
    else:
        print(f"{n_proc}: Failed to instantiate dymola instance")

    _model_path = os.path.abspath(val_params['model_path'])
    _model_package = val_params['model_package']
    _model_name = val_params['model_name']

    print(f"{n_proc}: Working directory:\n{_working_directory}")
    print(f"{n_proc}: OpenIPSL path:\n{_openipsl_path}")
    print(f"{n_proc}: Model path:\n{_model_path}\n")

    # Extracting simulation parameters
    _n_cores = val_params['n_cores']
    _startTime = val_params['startTime']
    _stopTime = val_params['stopTime']
    _numberOfIntervals = val_params['numberOfIntervals']
    _method = val_params['method']
    _tolerance = val_params['tolerance']
    _fixedstepsize = val_params['fixedstepsize']
    _resultFile = val_params['resultFile']

    # Opening library
    result = dymolaInstance.openModel(_openipsl_path)
    if result: print(f"{n_proc}: Library opened")

    # Opening model
    result = dymolaInstance.openModel(_model_path)
    if result: print(f"{n_proc}: Model opened successfully")

    # Changing working directory
    if not os.path.exists(_working_directory):
        os.makedirs(_working_directory)
    result = dymolaInstance.cd(_working_directory)
    if result: print(f"{n_proc}: Working directory changed successfully\n")

    # Executing special commands to speed up execution time
    dymolaInstance.ExecuteCommand("Advanced.TranslationInCommandLog = true")
    if _method == 'dassl':
        dymolaInstance.ExecuteCommand("Advanced.Define.DAEsolver = true")

    dymolaInstance.ExecuteCommand(f"Advanced.NumberOfCores = {_n_cores}")

    total = len(pf_list)

    for n, pf in enumerate(pf_list):

        # Getting power flow name and identifier via regex
        pf_name_regex = re.compile(r'(\w+)*(?:.mo)')
        pf_name = pf_name_regex.findall(pf)[0]

        pf_identifier_regex = re.compile(r'(?:PF_)([\w+]*_\d{5})')
        pf_identifier = pf_identifier_regex.findall(pf)[0]

        # Constructing `pf_path` and `pf_modifier`
        pf_path = f"{_model_package}.PF_Data.{pf_name}"
        pf_modifier = f"pf(redeclare record PowerFlow = {pf_path})"

        # Simulating model with different
        result = dymolaInstance.simulateModel(f"{_model_package}.{_model_name}({pf_modifier})",
            stopTime = _stopTime,
            resultFile = f"IEEE14_{pf_name}",
            numberOfIntervals = _numberOfIntervals,
            method = _method,
            tolerance = _tolerance)

        if result:
            print(f"{n_proc}: Simulation successful for power flow {pf_name} ({n + 1}/{total})")
            result_path = os.path.join(_working_directory, f"IEEE14_{pf_name}.mat")
            sdfData = sdf.load(result_path)

            tData = sdfData["Time"]
            v_mag2 = sdfData["Bus_02"]["V"]
            v_mag4 = sdfData["Bus_04"]["V"]

            t = np.array(tData.data)
            v_mag2np = np.array(v_mag2.data)
            v_mag4np = np.array(v_mag4.data)

            deltaV2 = np.max(v_mag2np) - np.min(v_mag2np)
            deltaV4 = np.max(v_mag4np) - np.min(v_mag4np)

            if deltaV2 > 0.005 or deltaV4 > 0.005:
                print(f"{n_proc}: Power flow {pf_name} did not initialize the model flat")
                print(f"{n_proc}: Removing {pf_name} result...")

                pf_path = {'main': os.path.join(data_path, f'{pf_name}.mo'),
                    'bus': os.path.join(data_path, 'Bus_Data', f'PF_Bus_{pf_identifier}.mo'),
                    'loads': os.path.join(data_path, 'Loads_Data', f'PF_Loads_{pf_identifier}.mo'),
                    'machines': os.path.join(data_path, 'Machines_Data', f'PF_Machines_{pf_identifier}.mo'),
                    'trafos': os.path.join(data_path, 'Trafos_Data', f'PF_Machines_{pf_identifier}.mo')}

                for file in pf_path:
                    if os.path.isfile(pf_path[file]):
                        os.unlink(pf_path[file])
            else:
                print(f"{n_proc}: Power flow {pf_name} converged")
        else:
            print(f"{n_proc}: Simulation fails for {pf_name}")

    # Remove all `.mat` files from working directory: they are useless
    print("Removing all '.mat' files from current working directory")
    for file_object in os.listdir(_working_directory):
        file_object_path = os.path.join(_working_directory, file_object)
        if os.path.isfile(file_object_path) or os.path.islink(file_object_path):
            os.unlink(file_object_path)
        else:
            shutil.rmtree(file_object_path)
