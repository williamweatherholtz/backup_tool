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
    ext_filters: str = '.*'
    
    def search(self) -> dict:        
        sizes = dict()
        
        for ext in self.ext_filters:
            print (f'searching for {ext} files in {self.dir}...', end='')
            files_found = 0
            # not really handling upper & lower case, but we're currently using a windows system rn so...
                
            files = glob.iglob(self.dir + f'/**/*{ext}', recursive=True)
            for file in files:
                files_found += 1
                size = os.path.getsize(file)
                
                if size in sizes:                
                    sizes[size].append(FileData(file))
                else:
                    sizes[size] = [FileData(file)]
            print (f'found {files_found}')
        
        total_files = len([len(files) for files in sizes.values()])
        print (f'total files: {total_files}')
        print (f'total sizes: {len(sizes.keys())}')
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
        DEST_SUBDIR = 'BACKUP'
        new_dest_dir = os.path.join(dest_dir, DEST_SUBDIR)
        suffix = 0
        while os.path.exists(new_dest_dir):
            new_dest_dir = os.path.join(dest_dir, f'{DEST_SUBDIR}_{suffix}')
            suffix += 1            
        
        num_files = len(copylist)
        len_digits = len(str(num_files))
        
        for i, file in enumerate(copylist):
            if not file.copyme:
                continue
            
            relpath = os.path.relpath(file.filename, source_dir)
            #print (relpath)
            dest_fn = os.path.join(new_dest_dir, relpath)
            #print (f'dest_dir:{dest_dir}\tdest_subdir:{DEST_SUBDIR}\tdest_fn{dest_fn}\tnew_dest_dir:{new_dest_dir}')
            #stop
            print (f'copying file {str(i+1).zfill(len_digits)}/{num_files}: {file.filename[:-30]}')
            
            os.makedirs(os.path.dirname(dest_fn), exist_ok=True)
            shutil.copy2(file.filename, dest_fn)
    
    def compare(self):
        dest_sizes = self.dest_list.search()
        source_sizes = self.source_list.search()
        
        backups_found = 0
        no_backups_found = 0
        copyme = []
        
        for size, files in source_sizes.items():
            #print (f'processing {len(files)} files')
            if size not in dest_sizes.keys():
                # mutate source_list
                for file in files:
                    no_backups_found += 1
                    file.copyme = True
                continue
            
            # if size IS already in list, we need to compute checksums to know if they're the same or not
            dest_files = dest_sizes[size]
            
            # calculate checksums for all files of this size, both in src and dest dirs
            for fileset in [dest_files, files]:
                for _files in fileset:
                    for file in _files:
                        with open(file.filename, 'rb') as f:
                            digest = hashlib.file_digest(f, 'blake2b') #blake2b is robust and fast, apparently
                        file.checksum = digest.hexdigest()
            
            # now we can check to see if the source files are really unique
            for file in files:
                dest_checksums = [f.checksum for f in dest_files]
                #skip if already exists
                
                if file.checksum in dest_checksums:
                    backups_found += 1
                    continue
                
                no_backups_found += 1
                file.copyme = True
            
            print (len(files))
            stop
            copyme.extend([f for f in files if f.copyme])
        print (f'found backups for {backups_found} files')
        print (f'found {no_backups_found} files that need to be backed up')
        return copyme
        


if __name__ == '__main__':
    
    import time

    SOURCE_DIR = './src/backup_tool'
    DEST_DIR = './test_dest'
    
    SOURCE_DIR = 'Y:\\Pictures to backup\\unsorted_photos'
    DEST_DIR = 'Y:\\Pictures'
    #DEST_DIR = 'Y:\Pictures\kelly_single'
    
    extensions = ['.bmp',
                  '.jpg', '.jpeg', '.jpe', '.jig', '.jfif', '.jfi',
                  '.png',
                  '.gif',
                  '.webp',
                  '.tiff', '.tif',
                  '.raw', '.arw', '.cr2', '.nrw', '.k25',
                  '.heif', '.heic', 
                  '.ind', '.indd', '.indt',
                  '.svg', '.svgz',
                  '.ai',
                  '.eps',]
                  #'.pdf',
                  
    extensions = ['.bmp','.jpg', '.jpeg', 
                  '.png',
                  '.gif',
                  '.svg',]
    
    #extensions.extend([e.upper() for e in extensions])
    
        
    fl = FileList(SOURCE_DIR, ext_filters=extensions)
    fl2 = FileList(DEST_DIR, ext_filters=extensions)
    
    '''
    t_fl = time.process_time()
    files = fl.search()
    print(f'source dir search took {time.process_time() - t_fl} minutes')
    t_fl2 = time.process_time()
    files2 = fl2.search()
    print(f'dest dir search took {time.process_time() - t_fl2} minutes')
    print()
    '''
    
    c = ListComparator(fl, fl2)
    copylist = c.compare()
    print (f'copy list is {len(copylist)} items long')
    ListComparator.save_files(copylist, SOURCE_DIR, DEST_DIR)

    '''
    print()
    #print (files)
    print (f'{len(fl)} files found in {SOURCE_DIR} with extension {fl.ext_filters}')
    #print (files)
    print (f'{len(fl2)} files found in {DEST_DIR} with extension {fl2.ext_filters}')
    #print (files2)
    #'''