#!/usr/bin/env python

# Minimal feature extractor for CRFsuite. Based on example/ner.py in the
# CRFsuite distribution (https://github.com/chokkan/crfsuite).

import sys

import crfutils

# Attribute templates.
templates = (
    (('w', -2), ),
    (('w', -1), ),
    (('w',  0), ),
    (('w',  1), ),
    (('w',  2), ),
    (('w', -1), ('w',  0)),
    (('w',  0), ('w',  1)),
)

def feature_extractor(sentence):
    crfutils.apply_templates(sentence, templates)

def main(argv):
    crfutils.main(feature_extractor, fields='w y', sep='\t')

if __name__ == '__main__':
    sys.exit(main(sys.argv))
