from flask import Flask,render_template,url_for,request,redirect
import os,subprocess
from subprocess import PIPE
from utils import *
import logging
from execution import run_file

app=Flask(__name__)
   
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/runCode',methods=['GET', 'POST'])
def run():
    if request.method == 'POST':
        code=request.form['code']
        input_data=request.form['input']
        
        data = request.form
         
        logging.info("Input Data Received")
        
        if is_tool('g++'):
            # output=getOutput(code,input_data, time_limit)
            received_data = run_file(data)
            output = received_data["output"]
            verdict = received_data["verdict"]
            
    return render_template('index.html',code=code,output=output,input_data=input_data, verdict=verdict)



#function to create C file, compile it and run it using subprocess module and return the output
def getOutput(code,input, time_limit=1):
    
    if not os.path.exists('demo.cpp'):
        os.open('demo.cpp',os.O_CREAT)

    fd=os.open('demo.cpp',os.O_WRONLY)
    os.truncate(fd,0)
    
    contents=str.encode(code)
    os.write(fd,contents)
    os.close(fd)
    
    compile=subprocess.run(['g++','-o','demorun','demo.cpp'],stderr=PIPE)
    hasCompiled=compile.returncode
    #hasCompiled is 0 if compilation is successful
    if hasCompiled==0:
        runfile=subprocess.run(['./demorun'],input=input.encode(),stdout=PIPE)
        os.remove('./demorun')
        
        return runfile.stdout.decode('utf-8')
    else:
        return compile.stderr.decode('utf-8')
    
@app.before_first_request
def logger_configuration():
    configure_logger()
                    
if __name__=='__main__':
    app.run(debug=True)