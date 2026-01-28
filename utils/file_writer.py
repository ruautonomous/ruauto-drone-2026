import os
from logger import log_system, bcolors
def write_file(overwrite: bool, path: str):
    with open(f'info_files/{path}.txt', 'w' if overwrite else 'a') as f:
        pass
    pass



def recreate_file(file: str):
    with open(f'info_files/{file}.txt', 'w') as f:
        f.write('')
    

def delete_file(file: str): # not sure how useful ts is
    if(os.path.exists(f'info_files/{file}.txt')):
        os.remove(f'info_files/{file}.txt')
        if(not os.path.exists(f'info_files/{file}.txt')):
            log_system(msg=f"FILE {file}.txt deleted successfully", msgname="FILE DELETED", color=bcolors.SUCCESS)
        else:
            log_system(msg=f"FILE {file}.txt failed to delete", msgname="FILE NOT DELETED", color=bcolors.FAIL)

    

recreate_file('coordinates')
delete_file('coordinates')