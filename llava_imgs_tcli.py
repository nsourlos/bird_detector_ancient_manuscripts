#'tcli' file created based on https://github.com/haotian-liu/LLaVA/issues/540
#It should be place inside 'LLaVA\llava\serve' folder
#If errors, change time.sleep(25) to 30

# #Dependencies
# git clone https://github.com/haotian-liu/LLaVA.git
# cd LLaVA
# conda create -n llava python=3.10 -y
# conda activate llava
# pip install --upgrade pip  # enable PEP 660 support
# pip install -e .

import subprocess
import os
import time
import select
import fcntl
import errno
import selectors

start_all=time.time()

img_path='/home/soyrl/pdf_saves_new/'    
all_imgs=sorted(os.listdir(img_path))
all_paths=[img_path+img for img in all_imgs]

# Define the list of commands to execute
commands = ['python -m llava.serve.tcli --model-path liuhaotian/llava-v1.5-7b --load-4bit']

flag=0
flag_inner=0

# Execute each command in the list
for cmd in commands:
    try:
        #subprocess.run doesn't allow interaction and so, we can't send multiple commands in the shell
        result = subprocess.Popen(cmd,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True, text=True)

        # Create a selector object and register the subprocess' stdout for event monitoring
        sel = selectors.DefaultSelector()
        sel.register(result.stdout, selectors.EVENT_READ)

        current_input_index = 0 # Index of the img

        # Set the O_NONBLOCK flag of the file descriptor for reading
        # This means os.read() will return even if there is no data
        fd = result.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        for i in range(len(all_paths)): #Loop through all imgs

            start_img=time.time() #start time for each img
            print(str(i)+'/'+str(len(all_paths)), '('+str(round(i/len(all_paths)*100,2))+'%)') #print progress in terminal

            while True:
                # Check if the subprocess is still running and if there is output
                reads = [result.stdout, result.stderr] 

                if i==0: #first img
                    ret = select.select(reads, [], [],None) 

                    for fd in ret[0]: 
                        if fd == result.stdout: #If there is output on the stdout
                            try: #Try to read
                                output=os.read(fd.fileno(), 4096).decode('utf-8') #Read the output
                            except OSError as e: #If os.read() would block or there is no more data
                                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK: #If there is an error
                                    raise  # Re-raise exception if a different error occurred

                            if output=='': #If there is no output
                                result.stdout.close() #Close the stdout
                            elif 'Image path' in output and current_input_index <= len(all_paths): #If there is output and we haven't reached the end of the list of imgs 
                                input_to_send = all_paths[current_input_index] + "\n" #Get the path of the img
                                current_input_index += 1 #Increment the index of the img

                                with open("output_llava.txt", "a") as file: #First time write the command we send to LlaVa to the output file
                                    file.write('\n')
                                    file.write("Are there any birds in the image? Respond with just a yes or no \n")
                                    file.write('\n')

                                with open("output_llava.txt", "a") as file: #Write the path of the img to the output file
                                    file.write(input_to_send)

                                result.stdin.write(input_to_send) #Send the path of the img to LlaVa
                                result.stdin.flush() #Flush the buffer

                                for key, events in sel.select(timeout=1): # adjust timeout as needed

                                    # Read output if available
                                    output = key.fileobj.readline()

                                    if output: #If there is output                              

                                        input_to_send = 'Are there any birds in the image? Respond with just a yes or no \n'
                                        result.stdin.write(input_to_send) #Send the command to LlaVa
                                        result.stdin.flush() #Flush the buffer
                                        time.sleep(25) #Wait for 25 seconds to give LlaVa time to process the img - Less time (e.g. 25sec) will not be enough

                                        for key2, events2 in sel.select(timeout=1): # adjust timeout as needed
                                            
                                            # Read output if available
                                            output2 = key2.fileobj.readline()

                                            if output2: #If there is output

                                                if 'yes' in output2.strip().lower(): #If the output contains 'yes'
                                                    with open("output_llava.txt", "a") as file: #Write 'Yes' to the output file
                                                        file.write("Yes")
                                                elif 'no' in output2.strip().lower(): #If the output contains 'no'
                                                    with open("output_llava.txt", "a") as file: #Write 'No' to the output file
                                                        file.write("No")
                                                else: #If the output contains neither 'yes' nor 'no'
                                                    with open("output_llava.txt", "a") as file: #Write 'No answer' to the output file
                                                        file.write("No answer")


                                                with open("output_llava.txt", "a") as file: #Write a new line to the output file
                                                    file.write('\n')

                                flag=1 #Set the flag to break the loop

                        elif fd == result.stderr: #If there is output on the stderr
                            error = result.stderr.readline() #Read the error
                            if error: #If there is an error
                                with open("output_llava.txt", "a") as file: #Write the error to the output file
                                    file.write(error.strip())
                                    file.write('\n')

                    if flag==1: #If the flag is set
                        flag=0 #Reset the flag
                        break #Break the loop

                else: #If it's not the first img

                    if output=='': #If there is no output
                        result.stdout.close() #Close the stdout
                    elif current_input_index <= len(all_paths): #If we haven't reached the end of the list of imgs 
                        input_to_send = all_paths[current_input_index] + "\n" #Get the path of the img
                        current_input_index += 1 #Increment the index of the img

                        with open("output_llava.txt", "a") as file: #First time write the command we send to LlaVa to the output file
                            file.write(input_to_send)

                        result.stdin.write(input_to_send) #Send the path of the img to LlaVa
                        result.stdin.flush() #Flush the buffer

                        for key, events in sel.select(timeout=1): # adjust timeout as needed

                            # Read output if available
                            output = key.fileobj.readline()

                            if output: #If there is output

                                for key2, events2 in sel.select(timeout=1): # adjust timeout as needed

                                    output2 = key2.fileobj.readline()
                                    time.sleep(1) #Wait for 1 second to give LlaVa terminal time to move to next command

                                    for key4, events4 in sel.select(timeout=1):  # adjust timeout as needed

                                        output4 = key4.fileobj.readline()

                                        for key5, events5 in sel.select(timeout=1):  # adjust timeout as needed

                                            output5 = key5.fileobj.readline()

                                            input_to_send = 'Are there any birds in the image? Respond with just a yes or no \n'
                                            result.stdin.write(input_to_send) # Send the command to LlaVa
                                            result.stdin.flush() # Flush the buffer
                                            time.sleep(25) # Wait for 30 seconds to give LlaVa time to process the img - Less time might not be enough

                                            for key6, events6 in sel.select(timeout=1):  # adjust timeout as needed

                                                output6 = key6.fileobj.readline()

                                                if output6: #If there is output
                                                    if 'yes' in output6.strip().lower(): #If the output contains 'yes'
                                                        with open("output_llava.txt", "a") as file: #Write 'Yes' to the output file
                                                            file.write("Yes")
                                                    elif 'no' in output6.strip().lower(): #If the output contains 'no'
                                                        with open("output_llava.txt", "a") as file: #Write 'No' to the output file
                                                            file.write("No")
                                                    else: #If the output contains neither 'yes' nor 'no'
                                                        with open("output_llava.txt", "a") as file: #Write 'No answer' to the output file
                                                            file.write("No answer")

                                                    with open("output_llava.txt", "a") as file: #Write a new line to the output file
                                                        file.write('\n')

                        flag_inner=1 #Set the flag to break the loop

                    else: #If we have reached the end of the list of imgs
                        with open("output_llava.txt", "a") as file: #Write a new line to the output file
                            file.write('\n')

                if flag_inner==1: #If the flag is set
                    flag_inner=0 #Reset the flag
                    break #Break the loop


        end_img=time.time() #end time for last img
        with open("output_llava.txt", "a") as file: #Write the time to run the last img to the output file
            file.write('\n')
            file.write("Time to run last img is "+str(end_img-start_img))
            file.write('\n')

    except subprocess.CalledProcessError as e: #If the command failed
        with open("output_llava.txt", "a") as file: #Write the error to the output file
            file.write(f"Command '{cmd}' failed with exit code {e.returncode}")
        break #Break the loop

    except Exception as e: #If there is an error
        with open("output_llava.txt", "a") as file: #Write the error to the output file
            file.write(f"An error occurred while executing '{cmd}': {str(e)}")
        break #Break the loop


end_all=time.time() #end time for all imgs
print("Time to run program is", end_all-start_all) #print time to run program in terminal
with open("output_llava.txt", "a") as file: #Write the time to run all imgs to the output file
    file.write("Time to run program is "+str(end_all-start_all))
    file.write('\n')