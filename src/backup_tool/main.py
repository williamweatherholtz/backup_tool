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


from dataclasses import dataclass

@dataclass
class FileData:
    filename: str
    checksum: int = None
    copyme: bool = False

import glob

@dataclass
class FileList:
    """
    pass in a directory, get a list of all files, optionally ONLY of a certain extension
    """
    dir: str
    ext_filter: str = '.*'
    
    def search(self) -> dict:
        sizes = dict()
        files = glob.glob(self.dir + f'/**/*{self.ext_filter}', recursive=True)
        for file in files:
            size = os.path.getsize(file)
            
            if size in sizes:
                sizes[size].append(FileData(file))
            else:
                sizes[size] = [FileData(file)]
        
        return sizes
    
    def __len__(self):
        sizes = self.search()
        
        return sum(len(files) for size, files in sizes.items())


import hashlib

@dataclass
class ListComparator:
    source_list: FileList
    dest_list: FileList
    
    @staticmethod
    def save_files(copylist, source_dir, dest_dir):
        import shutil
        
        #find empty directory
        DEST_BASE_DIR = './BACKUP/'
        
        num_files = len(copylist)
        len_digits = len(str(num_files))
        
        for i, file in enumerate(copylist):
            if not file.copyme:
                continue
            
            relpath = os.path.relpath(file.filename, SOURCE_DIR)
            #print (relpath)
            dest_fn = os.path.join(DEST_DIR, relpath)
            print (f'copying file {str(i+1).zfill(len_digits)}/{num_files}: {file.filename[:-30]}')
            
            os.makedirs(os.path.dirname(dest_fn), exist_ok=True)
            shutil.copy2(file.filename, dest_fn)
    
    def compare(self):
        dest_sizes = self.dest_list.search()
        source_sizes = self.source_list.search()
        
        for size, filedatas in source_sizes.items():
            if size not in dest_sizes:
                # mutate source_list
                for file in source_sizes[size]:
                    file.copyme = True
                continue
            
            # if size IS already in list, we need to compute checksums
            dest_files = dest_sizes[size]
            source_files = source_sizes[size]
            
            for fileset in [dest_files, source_files]:                
                for file in fileset:
                    file.copyme = True
                    with open(file.filename, 'rb') as f:
                        digest = hashlib.file_digest(f, 'blake2b')
                    file.checksum = digest.hexdigest()
            
            copyme = []
            for file in source_files:
                dest_checksums = [f.checksum for f in dest_files]
                #skip if already exists
                
                if file.checksum in dest_checksums:
                    continue
                
                copyme.append(file)
            return copyme
        


if __name__ == '__main__':
    
    import time

    SOURCE_DIR = './src/backup_tool'
    DEST_DIR = './test_dest'
    
        
    fl = FileList(SOURCE_DIR, ext_filter='.bmp')
    fl2 = FileList(DEST_DIR, ext_filter='.bmp')
    
    t_fl = time.process_time()
    files = fl.search()
    print(f'source dir search took {time.process_time() - t_fl} seconds')
    t_fl2 = time.process_time()
    files2 = fl2.search()
    print(f'dest dir search took {time.process_time() - t_fl2} seconds')
    print()
    
    c = ListComparator(fl, fl2)
    copylist = c.compare()
    ListComparator.save_files(copylist, SOURCE_DIR, DEST_DIR)
    #print (f'copy list: {copylist}')

    print()
    #print (files)
    print (f'{len(fl)} files found in {SOURCE_DIR} with extension {fl.ext_filter}')
    #print (files)
    print (f'{len(fl2)} files found in {DEST_DIR} with extension {fl2.ext_filter}')
    #print (files2)
    #'''