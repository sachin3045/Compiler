import os
from utils import get_unique_identifier
import logging
import multiprocessing
import subprocess
from subprocess import PIPE



def create_local_files(data, exec_id, file_path = "codes/"):
    code_file_name = file_path + exec_id+"."+data["lang"]
    if not os.path.exists(code_file_name):
        os.open(code_file_name, os.O_CREAT)
    
    code = data["code"]
    
    fd=os.open(code_file_name,os.O_WRONLY)
    os.truncate(fd,0)
    
    contents=str.encode(code)
    os.write(fd,contents)
    os.close(fd)
    logging.info("Created file "+exec_id+data["lang"]+" at "+code_file_name)
    return code_file_name



def get_cmd_args(lang, code_file_path, exec_id):
    args = {'c': ['gcc', '-o', exec_id, code_file_path], 'cpp': ['g++', '-o', exec_id, code_file_path],
            'py': ['python3', code_file_path]}
    return args[lang]

    
def execute_file(exec_id, compiled_file_path, input_data, output_dict):
    
    run_code = subprocess.run([compiled_file_path], input = input_data.encode(), stdout=PIPE)
    logging.info("Executing the file")
    
    if run_code.returncode != 0:
        output_dict[exec_id] = run_code.stderr.decode('utf-8')
        output_dict[exec_id+"v"] = "Runtime Error"
    else:
        output_dict[exec_id] = run_code.stdout.decode('utf-8')
        output_dict[exec_id+"v"] = "Code ok"
    
    

        
    
def run_file(data):
    
    
    exec_id = get_unique_identifier(data['user_id'])
    logging.info(exec_id+" Starting Execution")
    
    code_file_path = create_local_files(data, exec_id)
    
    
    manager = multiprocessing.Manager()
    output_dict = manager.dict()
    
    lang = data["lang"]
    time_limit = float(data["time_limit"])
    input_data = data["input"]
    
    logging.info("Getting CMD Arguments for the submission")
    cmd = get_cmd_args(lang, code_file_path, exec_id)
    logging.info("CMD Arguments: "+' '.join(cmd))
    
    
    logging.info("Compiling "+code_file_path)
    
    compile_code=subprocess.run(cmd,stderr=PIPE)
    has_compiled = compile_code.returncode
    compiled_file_path = './'+exec_id
    logging.info("File Compiled with return code "+str(has_compiled))
    
    v="unknown"
    if has_compiled != 0:
        err = compile_code.stderr.decode('utf-8')
        logging.info("Error in Compilation : "+err)
        
        return {"output" : err, "verdict": "Compilation Error"}

    
    logging.info("Executing the compiled file with a time limit of "+str(time_limit));
    p = multiprocessing.Process(target=execute_file, name="Execute", args=(exec_id,compiled_file_path, input_data,output_dict))
    p.start()
    p.join(time_limit)
    if p.is_alive():
        v= "Time Limit Exceeded"
        output=""
        p.terminate()
        p.join()
    else:
        v = output_dict[exec_id+"v"]
        output = output_dict[exec_id]
    os.popen("rm "+exec_id)
    logging.info(output_dict)
    return {"output" : output, "verdict": v}
