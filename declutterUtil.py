import os
import shutil
import datetime
from pathlib import Path
from tqdm import tqdm

class DeclutterUtil:
    def __init__(self):
        self.starting_folder = input("Please enter a file path you wish to remove all excess video and loop folders from:")
        self.files_removed = 0
        self.num_of_directories = 0 
        self.skipped_directories = 0
        self.space_saved = 0
        self.current_step = 0
        self.total_steps = 0
        self.space_tag = ""
        self.now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        try:
            self.searchHomeDirectory(self.starting_folder)
            self.byteTotal(self.space_saved)
            end_string = f"Cleaning Process Complete!\nTotal Directories Skipped: {self.skipped_directories}\nTotal Files Removed: {self.files_removed}\nNumber of Directories Cleaned:{self.num_of_directories}\nTotal Space Saved: {self.space_tag}\n"
            print(end_string)
            self.writeLog(end_string)
            
        except Exception as e:
            self.writeLog(str(e))
            print("Error occured in cleaning process, please check the most recent log for more details.")
        
        
    def searchHomeDirectory(self, homeDir):
        dir_list = os.listdir(homeDir)
        self.total_steps = len(dir_list)
        with tqdm(total=self.total_steps, desc="Cleaning", unit="Directories") as pbar:
            while self.current_step < self.total_steps:
                step_increment = 1
                for folder in dir_list:
                    if "Generic" not in folder and folder != "Artist Cutouts":
                        self.clean_directory(folder)
                        self.current_step += step_increment
                        pbar.update(step_increment)
                    else:
                        self.writeLog("GENERIC FOLDER SKIP\n")
                        self.skipped_directories += 1
                        self.current_step += step_increment
                        pbar.update(step_increment)
                
    def clean_directory(self, selectedDir):
        current_dir = self.starting_folder + os.sep + selectedDir
        if self.isSkippableDir(current_dir):
            self.writeLog(f"Directory: {os.path.basename(current_dir)} is already clean. Moving to next file.\n")
            self.skipped_directories += 1
        else:
            file_structure = os.listdir(current_dir)
            for file in file_structure:
                if file == "Beat":
                    self.removeDir(os.path.abspath(current_dir + os.sep + file + os.sep + "Loops"))
                if file == "Video":
                    for content in os.listdir(os.path.abspath(current_dir + os.sep + file)):
                        if self.isClutter(content):
                            self.removeFiles(os.path.abspath(current_dir + os.sep + file + os.sep +content))
                        
    def removeFiles(self, filePath):
        if(os.path.exists(filePath)):
            file_size = os.path.getsize(filePath)
            os.remove(filePath)
            self.writeLog(f"File: {os.path.basename(filePath)} removed successfully.\n")
            self.update_totals(isDir=False,spaceRemoved=file_size)
        else:
            self.writeLog(f"File: {os.path.basename(filePath)} not found.\n")
            
    def removeDir(self, dirPath):
        if os.path.exists(dirPath):
            file_size = self.getFolderSize(dirPath)
            num_of_files = len([name for name in os.listdir(dirPath) if os.path.isfile(name)])
            try:
                os.rmdir(dirPath)
                self.writeLog(f"Directory: '{os.path.basename(dirPath)}' removed successfully.\n")
            except OSError:
                shutil.rmtree(dirPath)
                self.writeLog(f"Directory: '{os.path.basename(dirPath)}' and it's contents removed successfully.\n")
            
            self.update_totals(num_of_files, spaceRemoved=file_size)    
            
        else:
            self.writeLog(f"Directory: '{os.path.basename(dirPath)}' not found.\n")
                
    def isClutter(self, file):
        extensions = ['.mp4', '.wav']
        _, ext = os.path.splitext(file)
        return ext.lower() in extensions
    
    def getFolderSize(self, folder):
        return sum(file.stat().st_size for file in Path(folder).rglob('*'))
    
    def update_totals(self, numFiles=0, isDir=True, spaceRemoved=0):
        if(isDir):
            self.files_removed += numFiles
            self.num_of_directories += 1
        else:
            self.files_removed += 1
        self.space_saved += spaceRemoved
    
    def isSkippableDir(self, dirPath):
        loop_path = dirPath + os.sep + "Beat" + os.sep + "Loops"
        clutter_path = dirPath + os.sep + "Video"
        return not os.path.exists(loop_path) and not any([file for file in os.listdir(clutter_path) if self.isClutter(file)])
    
    def byteTotal(self, totalBytes):
        kb = 1024
        if 1 <= totalBytes / kb**3:
            self.space_tag = f"{round((totalBytes / kb**3),2)} Gb"
        elif 1 <= totalBytes / kb**2:
            self.space_tag = f"{round((totalBytes / kb**2),2)} Mb"
        elif 1 <= totalBytes / kb**1:
            self.space_tag = f"{round((totalBytes / kb**1),2)} Kb"
        else:
            self.space_tag = f"{totalBytes} bytes"
            
    def writeLog(self, line):
       with open(f"logs{os.sep}cleaning_log_{self.now}.txt", "a+") as f:
            f.write(line)
       
    

DeclutterUtil()