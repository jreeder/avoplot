import subprocess
import os

sizes = [16,22,24,32,48,64,96]
icon_files = [os.path.join('scalable',f) for f in os.listdir('scalable') if not f.startswith('.')]

#make sure all the output dirs exist
for s in sizes:
    try:
        os.makedirs('%dx%d'%(s,s))
    except OSError:
        pass

for fname in icon_files:    
    print "Creating sized icons for %s"%os.path.basename(fname)
    for s in sizes:        
        output = os.path.join('%dx%d'%(s,s),os.path.splitext(os.path.basename(fname))[0]+'.png')        
        if os.path.exists(output):
            continue
        subprocess.call(['inkscape','-z', '-f', fname, '-w', str(s), '-j', '-e', output])
print "Finished creating sized icons"
