import os

def get_pf_files(pf_data_folder_path):
    '''
    get_pf_files

    DESCRIPTION:
    this function gets a list of all the power flow files generated by `gridcal2rec`,
    `pp2rec` or `raw2rec` (functions provided with pf2rec) and returns them in a list`

    INPUTS:
    - data_path: absolute path to the folder where the records (`PF_data` subfolder)
    are stored.

    OUTPUTS:
    - pf_list: a list containing all the power flow results inside the `PF_data`
    folder

    LAST MODIFICATION DATE:
    10/09/2020 by Sergio A. Dorado-Rojas
    '''

    pf_list = []

    # Constructing the power flow record list
    # Ref: https://stackabuse.com/python-list-files-in-a-directory/
    with os.scandir(pf_data_folder_path) as entry_list:
        for entry in entry_list:
            # Check if the entry is a file
            if entry.is_file():
                if entry.name not in ['Power_Flow.mo', 'Power_Flow_Template.mo', 'package.mo', 'package.order', '.DS_Store']:
                    pf_list.append(entry.name)

    if len(pf_list) == 0:
        raise ValueError("No power flow records are available. Check the path of the OpenIPSL model.")

    return pf_list
