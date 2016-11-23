#!/usr/bin/env python

import sys

from os import path
from collections import defaultdict
from logging import warn

from ncbidisease import load_ncbi_disease


def main(argv):
    if len(argv) == 4 and argv[1] == '-dedup':
        dedup = True
        argv = argv[:1] + argv[2:]
    else:
        dedup = False
    if len(argv) != 3:
        print >> sys.stderr, 'Usage: ncbidisease2ann [-dedup] INFILE OUTDIR'
        return 1
    infn, outdir = argv[1:]
    
    if not path.isdir(outdir):
        print >> sys.stderr, '%s is not a directory' % outdir
        return 1

    documents = load_ncbi_disease(infn)

    seen_count = defaultdict(int)
    def output_filename(id_):
        if id_ in seen_count and not dedup:
            outfn = path.join(outdir, '{}.{}'.format(id_, seen_count[id_]))
            warn('{} repeated in {}, saving dup as {}'.format(id_, infn, outfn))
        else:
            outfn = path.join(outdir, id_)
            if id_ in seen_count:
                warn('{} repeated in {}, overwriting earlier'.format(id_, infn))
        seen_count[id_] += 1
        return outfn

    for d in documents:
        outfn = output_filename(d.PMID)
        with open(outfn+'.txt', 'wt') as out:
            print >> out, d.tiab
        with open(outfn+'.ann', 'wt') as out:
            print >> out, '\n'.join(d.to_standoff())
            
    return 0
        
if __name__ == '__main__':
    sys.exit(main(sys.argv))
