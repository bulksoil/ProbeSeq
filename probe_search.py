#!/usr/bin/python

import sys
import re
from optparse import OptionParser
import math
from Bio.Seq import Seq

def opt_get():
	parser = OptionParser()
	parser.add_option("-r", help = "FASTA database file, no gaps",
						dest = "reference_file", type = "string")
	parser.add_option("-p", help = "Probe file. Tab seperated with the first column being the probe name and the second being the sequence",
						dest = "probe_file", type = "string")
	parser.add_option("-o", help = "Outfile to print to", dest = "out_file", type = "string")
	parser.add_option("-m", help = "Maximum mismatches allowed", dest = "max", type = "int", default = "0")
	parser.add_option("-t", help = "Taxonomy file corresponding to the OTU IDs", dest = "tax", type = "string")
	(options, args) = parser.parse_args()
	return(options)

def probe_file_parse(probe_file):
	probes = {}
	for line in probe_file:
		name, sequence = line.rstrip("\n").split("\t")
		seq = Seq(str(sequence))
		rev_comp = seq.reverse_complement()
		probes[name] = str(rev_comp)
	return(probes)



def hamming_dist(s, q, max):
	sq = zip(s, q)
	count = 0
	for s1, s2 in sq:
		if count > max:
			return(0)
		if s1 != s2:
			count += 1
	return(1)


def hamming_hit(probe, seq, max):
	for x in range(0, len(seq) - len(probe) + 1):
		q = seq[x:x+len(probe)]
		if hamming_dist(probe, q, max) == 1:
			return(1)
	return(0)


def probe_hits(seqs, probe_file, maximum_mismatches):
	probes = probe_file_parse(open(probe_file))
	hits = {}
	place = "header"
	header = ''
	seq = ''
	num_hits = 0
	done = 0

	for line in seqs:
		if place == 'header':
			header = line.rstrip("\n")
			header = re.sub(">", "", header)
			place = "seq"
			done += 1
		else:
			place = "header"
			seq = line.rstrip("\n")
			for probe in probes:
				if maximum_mismatches == 0:
					if re.search(probes[probe], seq):
						num_hits += 1
						if  probe in hits:
							hits[probe].append(header)
						else:
							hits[probe] = [header]
				else:
					if hamming_hit(probes[probe], seq, maximum_mismatches) == 1:
						num_hits += 1
						if probe in hits:
							hits[probe].append(header)
						else:
							hits[probe] = [header]

			sys.stdout.write('%s\r' % done)
			sys.stdout.flush()

	return(hits)


def tax_compile(tax_file):
	"""
	Take taxonomy file and make a dictionary where OTU ID is the key and the taxonomic information is the value
	"""
	tax = {}
	for line in tax_file:
		otu_id, tax_info = line.rstrip("\n").split("\t")
		tax[otu_id] = tax_info
	return(tax)

def tax_print(hits, tax, out_file):+
	"""
	Print out the taxonomic information for the hits
	"""
	fout = open(out_file, 'w')
	for probe in hits:
		for otu_id in hits[probe]:
			print>>fout, probe + "\t" + otu_id + "\t" + tax[otu_id]

"""
def out_print(hits, out_file):
	fout = open(out_file, 'w')
	for probe in hits:
		print>>fout, probe + "\t" + ", ".join(hits[probe])
"""

def main():
	opts = opt_get()
	ref_file = opts.reference_file
	probe_file = opts.probe_file
	out_file = opts.out_file
	maximum_mismatches = opts.max
	tax_file = opts.tax
	hits = probe_hits(open(ref_file), probe_file, maximum_mismatches)
	tax_print(hits, tax_compile(open(tax_file)), out_file)


main()