import re

TEXT_LINE_RE = re.compile(r'^(\d+)\|([ta])\|(.*)$')

class FormatError(Exception):
    pass

class Annotation(object):
    def __init__(self, PMID, start, end, text, type_, norms):
        self.PMID = PMID
        self.start = start
        self.end = end
        self.text = text
        self.type = type_
        self.norms = norms

    def verify(self, tiab):
        if tiab[self.start:self.end] != self.text:
            raise FormatError(
                'text mismatch: annotation "%s", document "%s"' %
                (self.text, tiab[self.start:self.end]))

    def to_standoff(self, tidx, nidx):
        """Return list of annotation strings in the .ann standoff format."""
        anns = []
        anns.append('T%d\t%s %d %d\t%s' %
                    (tidx, self.type, self.start, self.end, self.text))
        for norm in self.norms:
            if ':' not in norm:
                # Normalizations without an explicit namespace are to MeSH
                norm = 'MeSH:' + norm
            anns.append('N%d\tReference T%d %s' % (nidx, tidx, norm))
            nidx += 1
        return anns
        
class Document(object):
    def __init__(self, PMID, title, abstract, annotations):
        self.PMID = PMID
        self.title = title
        self.abstract = abstract
        self.annotations = annotations

    @property
    def tiab(self):
        return self.title + '\n' + self.abstract

    def verify_annotations(self):
        tiab = self.tiab
        for a in self.annotations:
            a.verify(tiab)

    def to_standoff(self):
        """Return list of annotation strings in the .ann standoff format."""
        tidx, nidx = 1, 1
        all_anns = []
        for a in self.annotations:
            anns = a.to_standoff(tidx, nidx)
            all_anns.extend(anns)
            nidx += len(anns)-1    # all but one are norms
            tidx += 1
        return all_anns
        
def parse_annotation_line(line, ln):
    """Parse annotation line, return Annotation."""
    fields = [f.strip() for f in line.split('\t')]
    if len(fields) != 6:
        raise FormatError('Failed to parse line %d: %s' % (ln, line))
    PMID = fields[0]
    try:
        start = int(fields[1])
        end = int(fields[2])
    except:
        raise FormatError('Failed to parse line %d: %s' % (ln, line))
    text = fields[3]
    type_ = fields[4]
    if len(text) != end-start:
        raise FormatError('Text "%s" has length %d, end-start (%d-%d) is %s' %
                          (text, len(text), end, start, end-start))
    norms = fields[5].split('|')
    return Annotation(PMID, start, end, text, type_, norms)
        
def check_PMID(current, seen):
    if current is None or current == seen:
        return seen
    else:
        raise FormatError('Expected PMID %s, got %s' % (current, seen))

def read_ncbi_disease(flo):
    """Read NCBI corpus data from file-like object, return list of
    (title, abstract, annotations) tuples.
    
    The data has two different categories of lines: text and annotation.

    Text lines have the format

        PMID|TIAB|TEXT

    where PMID is the PubMed ID of the document, TIAB is either "t" or "a"
    for title or abstract, and TEXT is the corresponding text.

    Annotation lines have the tab-separated format

        PMID START END TEXT TYPE NORM

    where PMID is the PubMed ID, START and END are offsets into the
    text, TEXT is the annotated text spanned by START-END, TYPE is the
    type of the annotation, one of "SpecificDisease", "Modifier",
    "DiseaseClass", or "CompositeMention", and NORM is a '|' -
    separated list of ontology IDs that the mention is normalized to.
    """
    documents = []
    current_PMID, title, abstract, annotations = None, None, None, []
    for ln, line in enumerate(flo, start=1):
        line = line.rstrip('\n')
        if not line:
            if current_PMID is not None:
                documents.append(Document(current_PMID, title, abstract,
                                          annotations))
            current_PMID, title, abstract = None, None, None
            annotations = []
            continue
        m = TEXT_LINE_RE.match(line)
        if m:
            PMID, tiab, text = m.groups()
            current_PMID = check_PMID(current_PMID, PMID)
            if tiab == 't':
                if title is not None:
                    raise FormatError('Multiple titles for %s' % PMID)
                title = text
            elif tiab == 'a':
                if abstract is not None:
                    raise FormatError('Multiple abstracts for %s' % PMID)
                abstract = text
            else:
                raise FormatError('Failed to parse line %s' % line)
        else:
            # Annotation line
            annotation = parse_annotation_line(line, ln)
            current_PMID = check_PMID(current_PMID, annotation.PMID)
            annotations.append(annotation)
    if current_PMID is not None:
        documents.append(Document(current_PMID, title, abstract, annotations))
    for d in documents:
        d.verify_annotations()
    return documents
            
def load_ncbi_disease(fn):
    with open(fn) as f:
        return read_ncbi_disease(f)
