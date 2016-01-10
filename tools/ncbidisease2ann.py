#!/usr/bin/env python

import sys

from os import path

from ncbidisease import load_ncbi_disease

def main(argv):
    if len(argv) != 3:
        print >> sys.stderr, 'Usage: ncbidisease2ann INFILE OUTDIR'
        return 1
    infn, outdir = argv[1:]
    
    if not path.isdir(outdir):
        print >> sys.stderr, '%s is not a directory' % outdir
        return 1

    documents = load_ncbi_disease(infn)

    for d in documents:
        with open(path.join(outdir, d.PMID+'.txt'), 'wt') as out:
            print >> out, d.tiab
        with open(path.join(outdir, d.PMID+'.ann'), 'wt') as out:
            print >> out, '\n'.join(d.to_standoff())
            
    return 0
        
if __name__ == '__main__':
    sys.exit(main(sys.argv))
