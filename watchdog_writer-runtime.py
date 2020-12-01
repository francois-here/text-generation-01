#Watchdog
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import linecache
import gc
import re
import fileinput
import datetime
import sys #enable import of mymodules
sys.path.insert(1, '/home/francois/gpt-2/') # insert at 1, 0 is the script path (or '' in REPL)
import mymodules #from /src folder
from playsound import playsound

DIR_TO_WATCH = "/home/francois/gpt-2/writer/input_auto1"

class Watcher:
    DIR_TO_WATCH = DIR_TO_WATCH
    print("Ready to receive input "+DIR_TO_WATCH)

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIR_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")
        self.observer.join()


class Handler(FileSystemEventHandler):
    DIR_TO_WATCH = DIR_TO_WATCH

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print("Received created event - %s." % event.src_path)
            filepath="/home/francois/gpt-2/writer/input_auto1/"
            filename = event.src_path.strip(filepath)
            
            def shorten_line_to_lastpoint(inputtext):
                questionmark_position = inputtext.rfind("?")
                finaldot_position = inputtext.rfind(".")
                if questionmark_position != -1:
                    outputtext = inputtext[0:questionmark_position+1]
                elif finaldot_position != -1:
                    outputtext = inputtext[0:finaldot_position+1]
                return outputtext

            def shorten_line_to_firstpoint(inputtext):
                questionmark_position = inputtext.rfind("?")
                dot_position = inputtext.rfind(".")
                exclam_position = inputtext.rfind("!")
                comma_position = inputtext.rfind(",")
                if questionmark_position != -1:
                    outputtext = inputtext.split("?")
                    outputtext = outputtext[0]+"?"
                elif dot_position != -1:
                    outputtext = inputtext.split(".")
                    outputtext = outputtext[0]+"."
                elif exclam_position != -1:
                    outputtext = inputtext.split("!")
                    outputtext = outputtext[0]+"!"
                elif comma_position != -1:
                    outputtext = inputtext.split(",")
                    outputtext = outputtext[0]+","
                else:
                    outputtext = inputtext[:150]+"..."
                if len(outputtext) > 160:
                    outputtext = inputtext[:157]+"..."
                return outputtext

            def shorten_lastline_to_lastsentence(inputtext):
                dot_position = inputtext.rfind(".")
                dot_position = inputtext.rfind(".",0,dot_position)
                #print(dot_position)
                questionmark_position = inputtext.rfind("?")
                questionmark_position = inputtext.rfind("?",0,questionmark_position)
                #print(questionmark_position)
                exclam_position = inputtext.rfind("!")
                exclam_position = inputtext.rfind("!",0,exclam_position)
                #print(exclam_position)
                if dot_position != -1:
                    outputtext = inputtext.split(".",dot_position)
                    outputtext = outputtext[-1]
                elif questionmark_position != -1:
                    outputtext = inputtext.split("?",questionmark_position)
                    outputtext = outputtext[-1]
                elif exclam_position != -1:
                    outputtext = inputtext.split("!",exclam_position)
                    outputtext = outputtext[-1]
                else:
                    outputtext = inputtext
                return outputtext
            
            def file_number_of_lines(fname):
                with open(fname) as f:
                    for i, l in enumerate(f):
                        pass
                return i + 1

            def number_of_gpt_run(number_of_lines):
                number_of_run = (number_of_lines-1)/(3)
                print("Number of runs = "+str(number_of_run))
                if str(number_of_run).isdigit() == False:
                    number_of_run = str(number_of_run).split(".",1)
                    number_of_run = number_of_run[0]
                return number_of_run

            def create_bookfile(bookcontent,bookfilename):
                #Create output book file
                BOOKFILE = "/home/francois/gpt-2/writer/output_auto/"+bookfilename
                f = open(BOOKFILE, "x") 
                f.write(bookcontent)
                f.close()
                return print("Created book file "+BOOKFILE)
                     
            def create_tmpgpt_input(tmp_linesummary,tmp_line1,tmp_line3,tmp_linefinal):
                #Create gpt-2 input (without file)
                gptinput = "<|chapter|>\n" + "<|summary|>" + tmp_linesummary + "<|line-03|>" + tmp_line3
                gptinput = gptinput + "<|line-last|>" + tmp_linefinal + "<|chapter-begin|>\n" + tmp_line1
                print("Created gpt input ")
                return gptinput
            
            def select_tmplines(startline):
                #select temporary lines from input file
                tmp_line1 = linecache.getline(event.src_path,startline-2)
                tmp_line2 = linecache.getline(event.src_path,startline-1)
                tmp_linefinal = linecache.getline(event.src_path,startline)
                return tmp_line1, tmp_line2, tmp_linefinal

            def gpt_processing01(seedinput):
                #gpt processing
                model_name='writerrun06'
                models_dir="/home/francois/gpt-2/models/"
                outputlength=500                      #max 1024 tbd, Number of tokens to generate (default 1023, the maximum)
                temperature=1
                top_k=2000                              #max 50257, limits the generated guesses to the top k guesses
                top_p=1.15                               #Nucleus sampling: limits the generated guesses to a cumulative probability. (gets good results on a dataset with top_p=0.9)
                gptoutput = mymodules.single_interact_model_4(models_dir,model_name,seedinput,outputlength,temperature,top_k,top_p)
                return gptoutput
            
            def postedit_gptoutput(input):
                #post edit gpt-2 output
                output = input.split("<|chapter-end|>",1)
                output = output[0]
                return output
                
            linetotal = file_number_of_lines(event.src_path)
            print("The file has " + str(linetotal) + " lines.")
            number_of_gpt_run = number_of_gpt_run(linetotal)
            print("Number of runs is "+number_of_gpt_run)
            number_of_run = (linetotal-1)/(3)
            summary = linecache.getline(event.src_path,1) #summary has to be provided as the single first line of the input file
            bookcontent = summary
            i = 1
            while i < number_of_run+1:
                print("Run #"+str(i))
                n=i*3+1
                tmplines = select_tmplines(n)
                seedinput = create_tmpgpt_input(summary,tmplines[0],tmplines[1],tmplines[2])
                print(seedinput)
                gptoutput = gpt_processing01(seedinput)
                print(gptoutput)
                gptoutput = postedit_gptoutput(gptoutput)
                bookcontent = bookcontent+tmplines[0]+gptoutput+tmplines[2]
                #Release memory
                unreachable_objects = gc.collect()
                #Number of collected and deallocated objects
                print("Unreachable objects: "+str(unreachable_objects))
                i += 1
  
            #tmplines = select_tmplines(1)
            timestampnow = datetime.datetime.now()
            tmpfileID = filename+"_"+timestampnow.strftime("%Y-%m-%d_%H%M_%S")
            
            #Book creation
            bookfilename = tmpfileID+".txt"
            create_bookfile(bookcontent,bookfilename)
            
            #Back up processed file
            shutil.move(event.src_path, "/home/francois/gpt-2/writer/"+filename)
            #Release memory
            unreachable_objects = gc.collect()
            #Number of collected and deallocated objects
            #print("Unreachable objects: "+str(unreachable_objects))
            print("Processed successfully "+filename)
            playsound("/home/francois/Music/python_bowlb.wav")

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print("Received modified event - %s." % event.src_path)

        elif event.event_type == 'deleted':
            # Taken any action here when a file is modified.
            print("Received deleted event - %s." % event.src_path)

        elif event.event_type == 'moved':
            # Taken any action here when a file is modified.
            print("Received moved event - %s." % event.src_path)

if __name__ == '__main__':
    w = Watcher()
    w.run()
