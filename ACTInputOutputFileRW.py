# this script will generate the input files 
import os
import math
#
# Description: 
#   This file will create the folder system
#
#

# =====================================================
#    DEFINE FUNCTIONS
# =====================================================
def linspace(x0, x1, n):
    ''' linspace function'''
    # calculate the factor between elements
    lin_factor = float(x1-x0)/(n-1)
    # output
    linear_vector = [x*lin_factor+x0 for x in range(n)]
    return linear_vector

# =====================================================
#   CONTROLS
# =====================================================

# READ/WRITE FLAG
# 'w' : this will write mechanical APDL input files (.dat) to separate folders
# 'r' : this will read mechanical APDL results files (.rst) and get the phase results 
RW_FLAG = 'r'

# TEST OR RUN
# 0 : test - small number of parameters
# 1 : full - number of parameters
# 2 : mid - medium size test
RUN_FLAG = 1

# WRITE WINDOWS BATCH FILE
# 0 : do nothing
# 1 : write windows batch file
WRITE_WINDOWS = 1

# WRITE LINUX SERVER BASH SCRIPT
# 0 : do nothing
# 1 : write the file
WRITE_SERVER = 1

# =====================================================
#    DEFINE INPUT PARAMETERS
# =====================================================

# define frequency and angle vector
# frequency in MHz
frequency_vector = linspace(0.5,5,25) # just for a single frequency
# angle in degrees
angle_vector = linspace(0,45,25)
# phase export quantities
phase_vector = linspace(0,360,5)

# reduce the number of parameters for testing
if RUN_FLAG == 0:
    print('...testing option chosen...')
    frequency_vector = frequency_vector[0:3]
    angle_vector = angle_vector[0:2]

if RUN_FLAG == 2:
    print('...medium size testing chosen...')
    # define frequency and angle vector
    # frequency in MHz
    frequency_vector = linspace(0.5,5,5) # just for a single frequency
    # angle in degrees
    angle_vector = linspace(0,45,5)
    # phase export quantities
    phase_vector = linspace(0,360,5)

# print some helpful meassages
print('...frequency and angle vectors have been set...')

# =====================================================
#    DEFINE DIRECTORIES
# =====================================================

# output directory
work_dir = "C:/Users/Danny Ramasawmy/Synology Drive/My BUG Drive/Ansys Simulations/Server Example/"

# check if inp/oup directories exist and create
directories = os.listdir(work_dir)
if directories.Contains('InputFiles') == False:
    os.mkdir(work_dir + 'InputFiles')
if directories.Contains('AnsysResults') == False:
    os.mkdir(work_dir + 'AnsysResults')
# assign directory
results_dir = "AnsysResults/"
input_dir = "InputFiles/"

# print some helpful meassages
print('...working directory is set...')

# =====================================================
#    RUN ANALYSIS
# =====================================================
# print some helpful meassages
print('...starting for-loop...')

# input file counter
input_counter = 0

for frequency in frequency_vector:

    #=======================================================    
    # print some helpful meassages
    print('...updating frequency...')
    # update frequency
    AnalysisSettings = ExtAPI.DataModel.Project.Model.Analyses[0].AnalysisSettings
    AnalysisSettings.RangeMaximum = Quantity(str(frequency) +' [MHz]') 

    #=======================================================
    # print some helpful meassages
    print('...updating mesh...')
    # recalculate the mesh size using the frequency for 10 points per wavelength
    # mesh in micrometers
    lowest_sound_speed = 1500
    mesh_size = lowest_sound_speed / frequency / 12 

    # update mesh
    meshChildList = ExtAPI.DataModel.Project.Model.Mesh.GetChildren(DataModelObjectCategory.Sizing, True)
    sizing = meshChildList[0]
    sizing.ElementSize = Quantity(str(mesh_size) + ' [um]')

    for angle in angle_vector:

        #=======================================================
        # # frequency in MHz
        # frequency = 1.0
        # # angle in degrees
        # angle = 25.0
        display_string = "Frequency:{} MHz, Angle:{} Deg".format(frequency, angle)
        print(display_string)

        #=======================================================
        # print some helpful meassages
        print('...updating angle...')
        # update angle
        portInDuctList = ExtAPI.DataModel.Project.Model.Analyses[0].GetChildren(DataModelObjectCategory.AcousticPortInDuct, True)
        PortInDuct = portInDuctList[0]
        PortInDuct.AngleTheta = Quantity(str(angle) + ' [deg]')

        #=======================================================
        # print some helpful meassages
        print('...wrtiting or reading model...')
        
        # solve
        # ExtAPI.DataModel.Project.Model.Analyses[0].Solve(1)

        # increment the counter
        input_counter = input_counter + 1

        # input file directory
        input_file_directory = work_dir + input_dir +  str(input_counter)

        # for output names
        angle_str = "{:05.2f}".format(float(angle)).Replace('.','p')
        freq_str = "{:05.2f}".format(float(frequency)).Replace('.','p')
        mesh_str = "{:06.2f}".format(float(mesh_size)).Replace('.','p')
        name_str = 'f_'+freq_str+'_a_'+angle_str+'_m_'+mesh_str

        #=======================================================       
        # writing the input files
        if RW_FLAG == 'w':

            tmp_direct = os.listdir(work_dir + input_dir)
            if tmp_direct.Contains(str(input_counter)) ==  False:
                os.mkdir(input_file_directory)

            # input file name
            input_filename = "input_file.dat"
            # write input file
            ExtAPI.DataModel.Project.Model.Analyses[0].WriteInputFile(input_file_directory + '/' + input_filename)

            # write an output file with the key values       
            with open(work_dir + input_dir + "file_dict.txt", "a") as f:
                append_string = '\n' + str(input_counter) + ' : ' +  name_str  
                f.write(append_string)

            
            # write windows batch file
            if WRITE_WINDOWS == 1:

                # write .bat file    
                with open(work_dir + input_dir + "run.bat", "a") as f:

                    # string to ansys path
                    windows_ansys_path = "\"C:\\Program Files\\ANSYS Inc\\v190\\ansys\\bin\\winx64\\ANSYS190.exe\" -b -i "
                    # for the relative folder
                    prepath = "\"" +str(input_counter)
                    # for the input file
                    input_file_path = prepath +"\\input_file.dat\" -o " + prepath + "\\solve.out\""
                    # the final string to append    
                    append_string = "\n rem " + str(input_counter) + ' : ' +  name_str  
                    append_string_1 = '\n' + windows_ansys_path + input_file_path 
                    append_string_2 = '\n' + "copy /y \"file.rst\" "  + prepath+"\\file.rst\" "
                    # write to text file
                    f.write(append_string + append_string_1 + append_string_2)
            

            # write linux server bash script - these can be moved to the end.
            if WRITE_SERVER == 1:
                # write the bash files # need "b" flag to handle line endings
                # 1) send_to_server.sh, 
                with open(work_dir + input_dir + "send_to_server.sh", "w+b") as f:
                    f.write('#!/bin/bash')
                    f.write('\n# Send the files to the server from this folder.')
                    f.write('\n# Upload name')
                    f.write('\ntarName="input_files.tar"')
                    f.write('\n# Compress the input files.')
                    f.write('\necho "...Compressing input files..."')
                    f.write('\ntar -cvf $tarName */*.dat submission_script.sh tar_and_copy.sh') 
                    f.write('\necho "...Finished compressing input files..."')
                    f.write('\n# Send data to the server')
                    f.write('\nscp $tarName rmapdrr@myriad.rc.ucl.ac.uk:~/Scratch/ansys_test/$tarName ')
                    f.write('\necho "...input files have been sent..."')
                    f.write('\nrm *.tar')

                # 2) submission_script.sh - execute this script when on the server
                with open(work_dir + input_dir + "submission_script.sh", "w+b") as f:
                    f.write('#!/bin/bash')
                    f.write('\n# executing shell as bash')
                    f.write('\n#$ -S /bin/bash')
                    f.write('\n# time to run')
                    f.write('\n#$ -l h_rt=0:30:0')
                    f.write('\n# memory per node')
                    f.write('\n#$ -l mem=4G')
                    f.write('\n# set up job array SGE_TASK_ID')
                    f.write('\n#$ -t 1-'+str(input_counter))
                    f.write('\n# script name')
                    f.write('\n#$ -N test_example')
                    f.write('\n# select mpi')
                    f.write('\n#$ -pe mpi 8')
                    f.write('\n# choose ansys licenses, wait if none avail')
                    f.write('\n#$ -ac app=cfx')
                    f.write('\n# send an email when job has started and ended send each task!')
                    f.write('\n# -m be')
                    f.write('\n# set working directory')
                    f.write('\n#$ -wd /home/rmapdrr/Scratch/ansys_test')
                    f.write('\n# assign folder for SGE ID')
                    f.write('\nmyDir=$SGE_TASK_ID')
                    f.write('\n# load ansys')
                    f.write('\nmodule load ansys/19.1')
                    f.write('\n# run ansys')
                    f.write('\nansys191 -mpi ibmmpi -dis -np $NSLOTS -p aa_r -dir "/home/rmapdrr/Scratch/ansys_test/$myDir" < "$myDir/input_file.dat" > "$myDir/output.txt" 2>&1')

                # 3) tar_and_copy.sh - on the server put results in output folder
                with open(work_dir + input_dir + "tar_and_copy.sh",'w+b') as f:
                    f.write('#!/bin/bash')
                    f.write('\n# tar files for sending to desktop')
                    f.write('\ntar -cvf output_files.tar */file.rst')
                    f.write('\necho "Files have been compressed ready for retrieving"')                    

                # 4) retrieve_from_server.sh - get the results from the server to local folder 
                with open(work_dir + input_dir + "retrieve_from_server.sh", 'w+b') as f:
                    f.write('#!/bin/bash')
                    f.write('\n# Get the files from the server to this folder')
                    f.write('\ntarName="output_files.tar"')
                    f.write('\necho "...Retrieving data from server..."')
                    f.write('\n# get data from server copy to this directorys')
                    f.write('\nscp rmapdrr@myriad.rc.ucl.ac.uk:~/Scratch/ansys_test/$tarName .')
                    f.write('\necho "...Extracting Data..."')
                    f.write('\n# extract data')
                    f.write('\ntar -xvf $tarName')
                    f.write('\nrm *.tar')


        #=======================================================
        # reading and processing the results files after solving offline
        if RW_FLAG == 'r':
            
            # Check if output file has been previously written
            check_string = work_dir + results_dir +  "ang_"+angle_str+"_freq_"+freq_str+"_mesh_"+mesh_str+"_phase_360p00.txt"
            # only check if the last phase is written otherwise recalculate all of them (not too much overhead)
            if os.path.isfile(check_string):
                # skip to next angle or frequency.
                print('...Already calculated, skipping ...')
                continue

            # results file name
            filename = "file.rst"       
            # units must be specified - ANSYS is non dimensional
            units = Ansys.ACT.Automation.Mechanical.Enums.UnitSystemIDType.UnitsUMKS
            # TODO: clear previous results file?
            # read results file load as solution
            ExtAPI.DataModel.Project.Model.Analyses[0].Solution.ReadGivenAnsysResultFile(input_file_directory + '/' + filename, units)


            # evaluate at different phase and export to txt file
            result = ExtAPI.DataModel.Project.Model.Analyses[0].Solution.Children[2]

               
            # loop over phase to export
            for phase in phase_vector:

                # set sweeping phase term
                result.SweepingPhase = Quantity(str(phase) +" [degree]")

                # evaluate results
                result.EvaluateAllResults()

                # format parameters for writing to disk
                phase_str = "{:06.2f}".format(float(phase)).Replace('.','p')

                # create filename
                fileNameAcoustic = "ang_"+angle_str+"_freq_"+freq_str+"_mesh_"+mesh_str+"_phase_"+phase_str+".txt"
         
                # print some helpful meassages
                print('...exporting data...')

                # export the results
                result.ExportToTextFile(0, work_dir + results_dir + fileNameAcoustic)
            
# print some helpful meassages
print('...Finished reading/writing...')
