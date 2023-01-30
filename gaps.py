#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Calculates gap statistics and manipulate gaps in assembly.
"""

import os.path as op
import sys
import logging

from itertools import groupby

from jcvi.formats.sizes import Sizes
from jcvi.formats.bed import Bed, fastaFromBed
from jcvi.formats.blast import BlastSlow
from jcvi.apps.base import OptionParser, ActionDispatcher, need_update


def main():

    actions = (
        ('flanks', 'create sequences flanking the gaps'),
        ('sizes', 'compile gap sizes'),
        ('estimate', 'estimate gap sizes based on mates'),
        ('annotate', 'annotate AGP v2 file with linkage info'),
            )
    p = ActionDispatcher(actions)
    p.dispatch(globals())


def annotate(args):
    """
    %prog annotate agpfile gaps.linkage.bed assembly.fasta

    Annotate AGP file with linkage info of `paired-end` or `map`.
    File `gaps.linkage.bed` is generated by assembly.gaps.estimate().
    """
    from jcvi.formats.agp import AGP, bed, tidy

    p = OptionParser(annotate.__doc__)
    p.add_option("--minsize", default=200,
                 help="Smallest component size [default: %default]")
    opts, args = p.parse_args(args)

    if len(args) != 3:
        sys.exit(not p.print_help())

    agpfile, linkagebed, assemblyfasta = args
    linkagebed = Bed(linkagebed)
    spannedgaps = set()
    for b in linkagebed:
        score = int(b.score)
        if score == 0:
            spannedgaps.add((b.accn, b.start, b.end))

    agp = AGP(agpfile)
    newagpfile = agpfile.rsplit(".", 1)[0] + ".linkage.agp"
    newagp = open(newagpfile, "w")
    contig_id = 0
    minsize = opts.minsize
    for a in agp:
        if not a.is_gap:
            cs = a.component_span
            if cs < minsize:
                a.is_gap = True
                a.component_type = "N"
                a.gap_length = cs
                a.gap_type = "scaffold"
                a.linkage = "yes"
                a.linkage_evidence = []
            else:
                contig_id += 1
                a.component_id = "contig{0:04d}".format(contig_id)
                a.component_beg = 1
                a.component_end = cs
                a.component_type = "W"

            print >> newagp, a
            continue

        gapinfo = (a.object, a.object_beg, a.object_end)
        gaplen = a.gap_length

        if gaplen == 100 and gapinfo not in spannedgaps:
            a.component_type = "U"
            tag = "map"
        else:
            tag = "paired-ends"

        a.linkage_evidence.append(tag)
        print >> newagp, a

    newagp.close()
    logging.debug("Annotated AGP written to `{0}`.".format(newagpfile))

    contigbed = assemblyfasta.rsplit(".", 1)[0] + ".contigs.bed"
    bedfile = bed([newagpfile, "--nogaps", "--outfile=" + contigbed])

    contigfasta = fastaFromBed(bedfile, assemblyfasta, name=True, stranded=True)

    tidy([newagpfile, contigfasta])


def estimate(args):
    """
    %prog estimate gaps.bed all.spans.bed all.mates

    Estimate gap sizes based on mate positions and library insert sizes.
    """
    from collections import defaultdict
    from jcvi.formats.bed import intersectBed_wao
    from jcvi.formats.posmap import MatesFile

    p = OptionParser(estimate.__doc__)
    p.add_option("--minlinks", default=3, type="int",
                 help="Minimum number of links to place [default: %default]")
    opts, args = p.parse_args(args)

    if len(args) != 3:
        sys.exit(not p.print_help())

    gapsbed, spansbed, matesfile = args
    mf = MatesFile(matesfile)
    bed = Bed(gapsbed)
    order = bed.order

    gap2mate = defaultdict(set)
    mate2gap = defaultdict(set)

    for a, b in intersectBed_wao(gapsbed, spansbed):
        gapsize = a.span
        if gapsize != 100:
            continue

        gapname = a.accn

        if b is None:
            gap2mate[gapname] = set()
            continue

        matename = b.accn
        gap2mate[gapname].add(matename)
        mate2gap[matename].add(gapname)

    omgapsbed = "gaps.linkage.bed"
    fw = open(omgapsbed, "w")
    for gapname, mates in sorted(gap2mate.items()):
        i, b = order[gapname]
        nmates = len(mates)
        if nmates < opts.minlinks:
            print >> fw, "{0}\t{1}".format(b, nmates)
            continue

        print gapname, mates

    fw.close()


def blast_to_twobeds(blastfile, log=False,
                     rclip=1, maxsize=300000, flipbeds=False):

    key1 = lambda x: x.query
    key2 = lambda x: x.query[:-rclip] if rclip else key1
    data = BlastSlow(blastfile)
    OK = "OK"

    fw = open("after.bed", "w")
    fwlabels = open("after.labels", "w")
    for pe, lines in groupby(data, key=key2):
        label = OK
        lines = list(lines)
        assert len(lines) in (1, 2)

        if len(lines) != 2:
            label = "Singleton"

        else:
            a, b = lines

            aquery, bquery = a.query, b.query
            asubject, bsubject = a.subject, b.subject
            if asubject != bsubject:
                label = "Different chr {0}|{1}".format(asubject, bsubject)

            else:
                astrand, bstrand = a.orientation, b.orientation
                assert aquery[-1] == 'L' and bquery[-1] == 'R', str((aquery, bquery))

                if astrand == '+' and bstrand == '+':
                    sstart, sstop = a.sstop + 1, b.sstart - 1

                elif astrand == '-' and bstrand == '-':
                    sstart, sstop = b.sstop + 1, a.sstart - 1

                else:
                    label = "Strand {0}|{1}".format(astrand, bstrand)

        if label == OK:
            strand = '+'
            label = sstop - sstart + 1

            if sstart > sstop:
                sstart, sstop = sstop, sstart
                strand = '-'
                label = - (sstop - sstart + 1)

            print >> fw, "\t".join(str(x) for x in \
                      (asubject, sstart - 1, sstop, pe, strand))

        print >> fwlabels, "\t".join(str(x) for x in (pe, label))

    fw.close()
    fwlabels.close()

    return fwlabels.name


def sizes(args):
    """
    %prog sizes gaps.bed a.fasta b.fasta

    Take the flanks of gaps within a.fasta, map them onto b.fasta. Compile the
    results to the gap size estimates in b. The output is detailed below:

    Columns are:
    1.  A scaffold
    2.  Start position
    3.  End position
    4.  Gap identifier
    5.  Gap size in A (= End - Start)
    6.  Gap size in B (based on BLAST, see below)

    For each gap, I extracted the left and right sequence (mostly 2Kb, but can be shorter
    if it runs into another gap) flanking the gap. The flanker names look like gap.00003L
    and gap.00003R means the left and right flanker of this particular gap, respectively.

    The BLAST output is used to calculate the gap size. For each flanker sequence, I took
    the best hit, and calculate the inner distance between the L match range and R range.
    The two flankers must map with at least 98% identity, and in the same orientation.

    NOTE the sixth column in the list file is not always a valid number. Other values are:
    -   na: both flankers are missing in B
    -   Singleton: one flanker is missing
    -   Different chr: flankers map to different scaffolds
    -   Strand +|-: flankers map in different orientations
    -   Negative value: the R flanker map before L flanker
    """
    from jcvi.formats.base import DictFile
    from jcvi.apps.align import blast

    p = OptionParser(sizes.__doc__)
    opts, args = p.parse_args(args)

    if len(args) != 3:
        sys.exit(not p.print_help())

    gapsbed, afasta, bfasta = args
    pf = gapsbed.rsplit(".", 1)[0]
    extbed = pf + ".ext.bed"
    extfasta = pf + ".ext.fasta"

    if need_update(gapsbed, extfasta):
        extbed, extfasta = flanks([gapsbed, afasta])

    q = op.basename(extfasta).split(".")[0]
    r = op.basename(bfasta).split(".")[0]
    blastfile = "{0}.{1}.blast".format(q, r)

    if need_update([extfasta, bfasta], blastfile):
        blastfile = blast([bfasta, extfasta, "--wordsize=50", "--pctid=98"])

    labelsfile = blast_to_twobeds(blastfile)
    labels = DictFile(labelsfile, delimiter='\t')
    bed = Bed(gapsbed)
    for b in bed:
        b.score = b.span
        accn = b.accn
        print "\t".join((str(x) for x in (b.seqid, b.start - 1, b.end, accn,
                        b.score, labels.get(accn, "na"))))


def flanks(args):
    """
    %prog flanks gaps.bed fastafile

    Create sequences flanking the gaps.
    """
    p = OptionParser(flanks.__doc__)
    p.add_option("--extend", default=2000, type="int",
                 help="Extend seq flanking the gaps [default: %default]")
    opts, args = p.parse_args(args)

    if len(args) != 2:
        sys.exit(not p.print_help())

    gapsbed, fastafile = args
    Ext = opts.extend
    sizes = Sizes(fastafile).mapping

    bed = Bed(gapsbed)
    pf = gapsbed.rsplit(".", 1)[0]
    extbed = pf + ".ext.bed"
    fw = open(extbed, "w")
    for i, b in enumerate(bed):
        seqid = b.seqid
        gapname = b.accn
        size = sizes[seqid]

        prev_b = bed[i - 1] if i > 0 else None
        next_b = bed[i + 1] if i + 1 < len(bed) else None
        if prev_b and prev_b.seqid != seqid:
            prev_b = None
        if next_b and next_b.seqid != seqid:
            next_b = None

        start = prev_b.end + 1 if prev_b else 1
        start, end = max(start, b.start - Ext), b.start - 1
        print >> fw, "\t".join(str(x) for x in \
                             (b.seqid, start - 1, end, gapname + "L"))

        end = next_b.start - 1 if next_b else size
        start, end = b.end + 1, min(end, b.end + Ext)
        print >> fw, "\t".join(str(x) for x in \
                             (b.seqid, start - 1, end, gapname + "R"))
    fw.close()

    extfasta = fastaFromBed(extbed, fastafile, name=True)
    return extbed, extfasta


if __name__ == '__main__':
    main()