# Windows
# Add the LASTools bin folder in system Path environment variable
# CSV file will be generated containing the list of tiles checked
# Set HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\Windows Error
# Reporting\DontShowUI registry value to 1.

__version__ = "0.6"

from datetime import datetime
import csv
import json
import os
import subprocess
import time

# Add lasinfo location to path
lasinfo_default_paths = ['C:\\Applications\\LAStools\\bin']
os.environ['PATH'] = os.pathsep.join(
    lasinfo_default_paths) + os.pathsep + os.environ['PATH']
# print 'PATH:', os.environ['PATH']

# Get current working directory
inDir = os.getcwd()
outCSV = "output.csv"
las_laz = 'corrupted_las_laz.txt'

# Start timing
startTime = time.time()

# Output CSV file
csvfile = open(outCSV, 'wb')
spamwriter = csv.writer(csvfile, delimiter=',',
                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
spamwriter.writerow(['File', 'IsCorrupted', 'FileFormat'])

# Loop through the current directory
corrupt_set = {'.las': set(), '.laz': set()}
for path, dirs, files in os.walk(inDir, topdown=False):

    files = [f for f in files if not f[0] == '.']
    dirs[:] = [d for d in dirs if not d[0] == '.']

    for las in sorted(files):

        # Check if las or laz
        if las.endswith(".las") or las.endswith(".laz"):

            # Open temporary text file
            # tempText = open(os.path.join(inDir, randomFN + ".txt"), "w")
            # tempPath = os.path.join(inDir, randomFN + ".txt")
            lasPath = os.path.join(path, las)
            lasFormat = lasPath[-3:].upper()
            filename, fileext = os.path.splitext(las)
            file_num = int(filename.replace('pt', ''))

            # Lasinfo
            file_path = lasPath
            outfile = file_path + '.lasinfo'
            # Check if json output file exists
            if not os.path.isfile(outfile):
                # Process file and redirect output to json file
                proc = subprocess.Popen(
                    ['lasinfo', file_path], stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)
                out, err = proc.communicate()
                returncode = proc.returncode
                output = {'out': str(out).lower(),
                          'returncode': returncode}
                json.dump(output, open(outfile, 'w'), indent=4,
                          sort_keys=True)

            # Load output from json file
            output = json.load(open(outfile, 'r'))
            corrupted = False
            # Determine if file is corrupted from output
            if output['returncode'] != 0:
                corrupted = True

            if 'error' in output['out']:
                corrupted = True

            # Ignore these warning messages
            ignored = ['points outside of header bounding box',
                       'range violates gps week time specified by global encoding bit 0']
            egm = False
            # Parse output for warning messages
            for l in output['out'].split('\n'):
                line = l.strip()
                # Ignore some lines
                ignore_line = False
                for i in ignored:
                    if i in line:
                        ignore_line = True
                        break
                if ignore_line:
                    continue

                if 'warning' in line:
                    corrupted = True
                if 'never classified' in line:
                    corrupted = True

                if 'generating software' in line and 'lasheight' in line:
                    egm = True

            if corrupted:
                print "[" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "]", lasPath, "--- Error!"
                spamwriter.writerow([lasPath, 'Corrupted', lasFormat])
                corrupt_set[fileext].add(file_num)
            else:
                print "[" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "]", lasPath, "--- No errors found!"
                if egm:
                    spamwriter.writerow([lasPath, 'EGM Adjusted', lasFormat])
                else:
                    spamwriter.writerow([lasPath, 'Unadjusted', lasFormat])


# Close CSV file
csvfile.close()

endTime = time.time()  # End timing
print '\nElapsed Time:', str("{0:.2f}".format(round(endTime - startTime, 2))), 'seconds'

# Get las and laz files that are both corrupted

# 96	DPC\TERRA\LAS_Tiles\Bohol\Bohol_1H_add_20151106\LAS_FILES

with open(las_laz, 'w') as open_file:

    print >>open_file, 'LAS only:'
    print >>open_file, ','.join(
        [str(x) for x in sorted(corrupt_set['.las'])])

    print >>open_file, '\nLAZ only:'
    print >>open_file, ','.join(
        [str(x) for x in sorted(corrupt_set['.laz'])])

    print >>open_file, '\nLAS/LAZ:'
    print >>open_file, ','.join(
        [str(x) for x in sorted(corrupt_set['.las'] & corrupt_set['.laz'])])

raw_input('\nPress ENTER to exit...')
