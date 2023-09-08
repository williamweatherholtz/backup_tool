import os

'''
1) Recursively search source dir for all files
2) For each file, save into dict:
    - source file path
    - file size, unique checksum (method TBD)    
    - checksum is initially None
    - checksum calculated later if a file is found in dest that has the same filesize, i.e. checksum is calculated AS NEEDED since it is costly
3) Recursively search dest dir for all files
4) For each file, save into a different dict:
    - dest file path
    - same as above...
5) For each source file, see if there exists in the dest a file of the same length
    - if a file of the same length exists, it might be the same file
    - proceed to calcualte a checksum to see if it is the same file
    - if it is the same file, ignore
    - if it is *not* the same file, i.e. backup is required, add to backup list
6) Create a COPYME folder in source to copy into dest
    - check that folder doesn't already exist, append to dirname as necessary
7) Clone the directory structure from ./source to ./COPYME for each file to copy, & copy each file
8) Report on results
'''

