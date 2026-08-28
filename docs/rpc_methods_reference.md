### AmazingFastaExtract.process
  summary: Extract FASTA by ID list / pattern / region; index-based, large-file friendly.
    - inputPath: string (required) - path to input FASTA file
    - idListPath: string (required) - path to ID/region list file (lines: 1-2 cols ID or pattern, 3 cols id/start/end, 4 cols geneName/chrName/start/end)
    - outputPath: string (required) - path to output FASTA file
    - options: object (optional) - usePattern, caseInsensitive, dontTreatSpaceAsColSep, wholeWordMatch
  -> returns: ok (boolean), outputPath (string), stats (object - extractedCount, missedCount, missedIds), message (string)

### AmazingHeatMap.process
  summary: Render heatmap image from expression matrix with optional grouping and trees.
    - matrixPath: string (required) - path to matrix file
    - outputPath: string (required) - path to output image
    - options: object (optional) - rowGroupPath, colGroupPath, rowNwk, colNwk, rowColorPath, colColorPath, showWindow
  -> returns: ok (boolean), outputPath (string), message (string)

### AmazingHeatMap.validateInput
  summary: Validate heatmap matrix and output path without rendering.
    - matrixPath: string (required) - path to matrix file
    - outputPath: string (required) - path to output image file
  -> returns: ok (boolean), matrixPath (string), outputPath (string), message (string)

### BatchStringReplace.process
  summary: Batch replace strings in text/table file via tab-delimited mapping rules.
    - inputPath: string (required) - input text/table file path
    - patternMapPath: string (required) - tab-delimited mapping file path
    - outputPath: string (required) - output file path
    - fullWordMatch: boolean (optional, default true) - boolean (optional, default true)
  -> returns: ok (boolean), outputPath (string), ruleCount (integer), message (string)

### BatchStringReplace.validateParams
  summary: Validate BatchStringReplace params without replacement.
    - inputPath: string (required) - input text/table file path
    - patternMapPath: string (required) - tab-delimited mapping file path
    - outputPath: string (required) - output file path
    - fullWordMatch: boolean (optional, default true) - boolean (optional, default true)
  -> returns: ok (boolean), validated (boolean), inputPath (string), patternMapPath (string), outputPath (string), ruleCount (integer), message (string)

### BestIdConverter.process
  summary: Best-hit ID mapping between two protein sets (BestIDConverter).
    - queryPath: string (required) - query protein FASTA
    - subjectPath: string (required) - subject protein FASTA
    - outputPrefixPath: string (required) - output prefix
    - threadNum: int (optional) - integer (optional)
    - useDiamond: boolean (optional) - boolean (optional)
  -> returns: ok (boolean), outputPath (string), outputPrefixPath (string), message (string)

### BestIdConverter.validateParams
  summary: Validate BestIdConverter.process parameters.
    - queryPath: string (required) - string (required)
    - subjectPath: string (required) - string (required)
    - outputPrefixPath: string (required) - string (required)
  -> returns: ok (boolean), outputPath (string), message (string)

### BlastCompareTwoSeqBigFileSet.process
  summary: Same as BlastCompareTwoSeqSet for large FASTA file pairs; defaults blastType to blastn when Auto.
    - queryPath: string (required) - query FASTA
    - subjectPath: string (required) - subject FASTA
    - outputPath: string (required) - single BLAST result file
    - options: object (optional) - threadNum, evalue, numOfHits, numOfAlignments, blastType (blastn|blastx|blastp|tblastn|tblastx|Auto), outFmt (5|0|7), otherMakeDbOpts, otherBlastOpts, useShortQueryParams
  -> returns: ok (boolean), outputPath (string), message (string)

### BlastCompareTwoSeqBigFileSet.validateParams
  summary: Validate BlastCompareTwoSeqBigFileSet.process parameters.
    - queryPath: string (required) - string (required)
    - subjectPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
  -> returns: ok (boolean), outputPath (string), message (string)

### BlastCompareTwoSeqRegion.process
  summary: Extract paired regions from two genomes and BLAST; tabular output (regionBlast).
    - genomeAPath: string (required) - genome A FASTA
    - genomeBPath: string (required) - genome B FASTA
    - regionInfoPath: string (required) - tab file: chrA start end chrB start end
    - outputPath: string (required) - output table file
    - evalue: number (optional, default 1.0E-5) - number (optional, default 1e-5)
    - threadNum: int (optional, default 6) - integer (optional, default 6)
    - blastType: string (optional, default tblastx) - string (optional, default tblastx)
  -> returns: ok (boolean), outputPath (string), blastType (string), message (string)

### BlastCompareTwoSeqRegion.validateParams
  summary: Validate BlastCompareTwoSeqRegion.process parameters.
    - genomeAPath: string (required) - string (required)
    - genomeBPath: string (required) - string (required)
    - regionInfoPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
  -> returns: ok (boolean), outputPath (string), message (string)

### BlastCompareTwoSeqSet.process
  summary: BLAST+ query FASTA vs subject FASTA; single result file. Requires BLAST+ in PATH.
    - queryPath: string (required) - query FASTA file
    - subjectPath: string (required) - subject FASTA file
    - outputPath: string (required) - result file path (not a directory)
    - options: object (optional) - threadNum, evalue, numOfHits, numOfAlignments, blastType (blastn|blastx|blastp|tblastn|tblastx|Auto), outFmt (5|0|7), otherMakeDbOpts, otherBlastOpts, useShortQueryParams
  -> returns: ok (boolean), outputPath (string), resultType (SUCCESS), message (string)

### BlastCompareTwoSeqSet.validateParams
  summary: Validate BlastCompareTwoSeqSet.process parameters.
    - queryPath: string (required) - string (required)
    - subjectPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
  -> returns: ok (boolean), outputPath (string), message (string)

### BlastSeveralSeq2BigGenesets.process
  summary: Several query sequences (inline or FASTA) vs a large subject FASTA; one BLAST result file.
    - sequenceText: string (optional) - FASTA text; use queryPath instead for file input
    - queryPath: string (optional) - query FASTA file
    - subjectPath: string (required) - large subject FASTA
    - outputPath: string (required) - result file
    - options: object (optional) - threadNum, evalue, numOfHits, numOfAlignments, blastType (blastn|blastx|blastp|tblastn|tblastx|Auto), outFmt (5|0|7), otherMakeDbOpts, otherBlastOpts, useShortQueryParams
  -> returns: ok (boolean), outputPath (string), message (string)

### BlastSeveralSeq2BigGenesets.validateParams
  summary: Validate BlastSeveralSeq2BigGenesets.process parameters.
    - subjectPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
    - sequenceText: string (optional) - string (optional)
    - queryPath: string (optional) - string (optional)
  -> returns: ok (boolean), outputPath (string), message (string)

### BlastXmlToTable.process
  summary: Convert BLAST XML to Blast tab / TBtools tab / summary / pairwise table.
    - inputXmlPath: string (required) - input BLAST XML file
    - outputPath: string (required) - output table file
    - tableFormat: string (optional, BlastTab|TBtoolsTab|Summary|Pairwise) - BlastTab|TBtoolsTab|Summary|Pairwise (default Summary)
    - hitNum: int (optional, default 20) - max hits per query for Summary format
  -> returns: ok (boolean), outputPath (string), tableFormat (string), message (string)

### BlastXmlToTable.validateParams
  summary: Validate BlastXmlToTable.process parameters.
    - inputXmlPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
    - tableFormat: string (optional) - string (optional)
  -> returns: ok (boolean), outputPath (string), message (string)

### BlastZone.process
  summary: BLAST query vs an on-disk BLAST DB prefix (Blast Zone core BlastOnTheFly).
    - sequenceText: string (optional) - string (optional)
    - queryPath: string (optional) - string (optional)
    - subjectDbPrefixPath: string (required) - existing BLAST DB prefix file/path
    - outputPath: string (required) - string (required)
    - blastType: string (optional, default blastn) - string (optional, default blastn)
    - outFmt: string (optional, XML|Pairwise|Table) - XML|Pairwise|Table
    - threadNum: int (optional) - integer (optional)
    - evalue: number (optional) - number (optional)
    - numberOfHits: int (optional) - integer (optional, 0 = unlimited)
    - useShortQueryParams: boolean (optional) - boolean (optional)
  -> returns: ok (boolean), outputPath (string), subjectDbPrefixPath (string), message (string)

### BlastZone.validateParams
  summary: Validate BlastZone.process parameters.
    - subjectDbPrefixPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
  -> returns: ok (boolean), outputPath (string), message (string)

### BlatAlign.process
  summary: Run BLAT alignment via jBLAT wrapper.
    - databasePath: string (required) - BLAT database FASTA/2bit path
    - queryPath: string (required) - query FASTA path
    - outputPath: string (required) - output alignment file path
    - outFormat: string (optional, psl|pslx|blast8|blast9|axt|maf|sim4|wublast|blast|blast8ncbi) - string (optional, psl|pslx|blast8|blast9|axt|maf|sim4|wublast|blast|blast8ncbi)
    - minScore: int (optional) - int (optional, must be >= 0)
    - minIdentity: number (optional) - number (optional, must be within [0,100])
    - noHead: boolean (optional, default false) - boolean (optional, default false)
    - autoDetectMode: boolean (optional, default true) - boolean (optional, default true)
    - extraOptions: string (optional) - raw extra BLAT options
  -> returns: ok (boolean), outputPath (string), elapsedMs (integer), message (string)

### BlatAlign.validateParams
  summary: Validate BLAT params and runtime dependency.
    - databasePath: string (required) - BLAT database FASTA/2bit path
    - queryPath: string (required) - query FASTA path
    - outputPath: string (required) - output alignment file path
    - outFormat: string (optional, psl|pslx|blast8|blast9|axt|maf|sim4|wublast|blast|blast8ncbi) - string (optional, psl|pslx|blast8|blast9|axt|maf|sim4|wublast|blast|blast8ncbi)
    - minScore: int (optional) - int (optional, must be >= 0)
    - minIdentity: number (optional) - number (optional, must be within [0,100])
    - extraOptions: string (optional) - raw extra BLAT options
  -> returns: ok (boolean), validated (boolean), databasePath (string), queryPath (string), outputPath (string), message (string)

### CdsToProtein.process
  summary: Translate nucleotide CDS FASTA to protein FASTA (standard codon table via Translater).
    - inputPath: string (required) - input nucleotide FASTA (CDS)
    - outputPath: string (required) - output protein FASTA path
  -> returns: ok (boolean), outputPath (string), message (string), recordCount (integer)

### CdsToProtein.validateParams
  summary: Validate CdsToProtein.process parameters and count input records.
    - inputPath: string (required) - input nucleotide FASTA
    - outputPath: string (required) - output protein FASTA path
  -> returns: ok (boolean), validated (boolean), message (string), inputPath (string), outputPath (string), recordCount (integer)

### CheckPrimer.process
  summary: Check primers against target FASTA (tab pairs: primerID\tsequence per line, see CheckPrimer CLI help).
    - primerInfoPath: string (required) - primer table file path
    - subjectPath: string (required) - target genome/contig FASTA path
    - outputPath: string (required) - report text output path
    - maxMismatch: int (optional, default 0) - max mismatches per primer
  -> returns: ok (boolean), outputPath (string), message (string), maxMismatch (integer)

### CheckPrimer.validateParams
  summary: Validate CheckPrimer.process.
    - primerInfoPath: string (required) - string (required)
    - subjectPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
    - maxMismatch: int (optional, default 0) - integer (optional, default 0)
  -> returns: ok (boolean), validated (boolean), message (string), outputPath (string)

### EmblToFasta.process
  summary: Convert EMBL records to FASTA.
    - inputPath: string (required) - input EMBL file path
    - outputPath: string (required) - output FASTA file path
  -> returns: ok (boolean), outputPath (string), recordCount (integer), message (string)

### EmblToFasta.validateParams
  summary: Validate EmblToFasta params without conversion.
    - inputPath: string (required) - input EMBL file path
    - outputPath: string (required) - output FASTA file path
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPath (string), message (string)

### ExpressionCorrMatrix.process
  summary: Calculate sample correlation matrix from expression table.
    - inputPath: string (required) - input expression matrix
    - outputPath: string (required) - output correlation matrix
  -> returns: ok (boolean), outputPath (string), message (string)

### ExpressionCorrMatrix.validateParams
  summary: Validate ExpressionCorrMatrix params without calculating.
    - inputPath: string (required) - input expression matrix
    - outputPath: string (required) - output correlation matrix
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPath (string), message (string)

### ExpressionFpkmToTpm.process
  summary: Normalize FPKM matrix to TPM-like scaled matrix.
    - fpkmTablePath: string (required) - input FPKM matrix path
    - outputPath: string (required) - output TPM matrix path
  -> returns: ok (boolean), outputPath (string), geneCount (integer), sampleCount (integer), message (string)

### ExpressionFpkmToTpm.validateParams
  summary: Validate FPKM->TPM params and table shape.
    - fpkmTablePath: string (required) - input FPKM matrix path
    - outputPath: string (required) - output TPM matrix path
  -> returns: ok (boolean), validated (boolean), outputPath (string), geneCount (integer), sampleCount (integer), message (string)

### ExpressionRpkm.process
  summary: Calculate RPKM from count matrix and length table.
    - countTablePath: string (required) - input count matrix path
    - lengthTablePath: string (required) - gene length table path
    - outputPath: string (required) - output RPKM matrix path
  -> returns: ok (boolean), outputPath (string), geneCount (integer), sampleCount (integer), message (string)

### ExpressionRpkm.validateParams
  summary: Validate RPKM params and count/length compatibility.
    - countTablePath: string (required) - input count matrix path
    - lengthTablePath: string (required) - gene length table path
    - outputPath: string (required) - output RPKM matrix path
  -> returns: ok (boolean), validated (boolean), outputPath (string), geneCount (integer), sampleCount (integer), message (string)

### ExpressionTau.process
  summary: Calculate TAU index and preferred sample from expression table.
    - inputPath: string (required) - input expression matrix
    - outputPath: string (required) - output TAU table
  -> returns: ok (boolean), outputPath (string), message (string)

### ExpressionTau.validateParams
  summary: Validate ExpressionTau params without calculating.
    - inputPath: string (required) - input expression matrix
    - outputPath: string (required) - output TAU table
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPath (string), message (string)

### ExpressionTpm.process
  summary: Calculate TPM from count matrix and length table.
    - countTablePath: string (required) - input count matrix path
    - lengthTablePath: string (required) - gene length table path
    - outputPath: string (required) - output TPM matrix path
  -> returns: ok (boolean), outputPath (string), geneCount (integer), sampleCount (integer), tmpFileUsed (boolean), message (string)

### ExpressionTpm.validateParams
  summary: Validate TPM params and count/length compatibility.
    - countTablePath: string (required) - input count matrix path
    - lengthTablePath: string (required) - gene length table path
    - outputPath: string (required) - output TPM matrix path
  -> returns: ok (boolean), validated (boolean), outputPath (string), geneCount (integer), sampleCount (integer), tmpFileUsed (boolean), message (string)

### FastaExtract.process
  summary: Extract/filter FASTA records by ID list file.
    - inputPath: string (required) - input FASTA path
    - idListPath: string (required) - ID list path
    - outputPath: string (required) - output FASTA path
    - processMode: string (optional, default Extract, Extract|Filter) - string (optional, Extract|Filter, default Extract)
    - matchMode: string (optional, default Match, Match|Contain) - string (optional, Match|Contain, default Match)
    - caseInSensitive: boolean (optional, default false) - boolean (optional, default false)
    - fullWordMatch: boolean (optional, default true) - boolean (optional, default true)
    - unusedIdOutputPath: string (optional) - string (optional)
  -> returns: ok (boolean), outputPath (string), processMode (string), matchMode (string), message (string)

### FastaExtract.validateParams
  summary: Validate FastaExtract parameters and IO paths without extraction.
    - inputPath: string (required) - input FASTA path
    - idListPath: string (required) - ID list path
    - outputPath: string (required) - output FASTA path
    - processMode: string (optional, default Extract, Extract|Filter) - string (optional, Extract|Filter, default Extract)
    - matchMode: string (optional, default Match, Match|Contain) - string (optional, Match|Contain, default Match)
  -> returns: ok (boolean), validated (boolean), processMode (string), matchMode (string), inputPath (string), idListPath (string), outputPath (string), message (string)

### FastaIDTools.appendPrefix
  summary: Append prefix to every FASTA ID and output a new FASTA file.
    - inputPath: string (required) - path to input FASTA file
    - outputPath: string (required) - path to output FASTA file
    - prefix: string (required) - prefix for FASTA IDs
  -> returns: ok (boolean), outputPath (string), message (string)

### FastaIDTools.extractLongestRepresentative
  summary: Extract longest representative sequence per ID group from FASTA.
    - inputPath: string (required) - path to input FASTA file
    - outputPath: string (required) - path to output FASTA file
    - groupPattern: string (required) - regex containing group(1) for transcript grouping
  -> returns: ok (boolean), outputPath (string), message (string)

### FastaIDTools.renameByMap
  summary: Rename FASTA IDs using mapping file (original and new ID columns).
    - inputPath: string (required) - path to input FASTA file
    - renameMapPath: string (required) - mapping file path
    - outputPath: string (required) - path to output FASTA file
  -> returns: ok (boolean), outputPath (string), message (string)

### FastaIDTools.simplifyIds
  summary: Simplify FASTA IDs with optional version removal and custom separator pattern.
    - inputPath: string (required) - path to input FASTA file
    - outputPath: string (required) - path to output FASTA file
    - rmVersion: boolean (optional, default false) - remove trailing version like .1
    - specifySepPattern: string (optional) - regex split pattern to keep left part
  -> returns: ok (boolean), outputPath (string), message (string)

### FastaMerge.process
  summary: Merge multiple FASTA files into one (order preserved; uses FastaMergerAndSpliter.Merge).
    - inputPaths: array (required) - input FASTA paths (>=1)
    - outputPath: string (required) - merged output FASTA path
  -> returns: ok (boolean), outputPath (string), message (string), inputFileCount (integer)

### FastaMerge.validateParams
  summary: Validate FastaMerge.process paths without writing output.
    - inputPaths: array (required) - input FASTA paths
    - outputPath: string (required) - merged output FASTA path
  -> returns: ok (boolean), validated (boolean), message (string), outputPath (string), inputFileCount (integer)

### FastaPatternLocate.process
  summary: Locate regex pattern hits in FASTA (QuickLocateSeqPattern; GUI Sequence Pattern Locate).
    - inputPath: string (required) - input FASTA path
    - outputPath: string (required) - output tab path
    - pattern: string (required) - Java regex for sequence match
    - maxSeqLenKb: int (optional, default 2) - chunk reader buffer size in KB
    - overlap: boolean (optional, default false) - overlapping scan mode
    - ignoreCase: boolean (optional, default false) - boolean (optional, default false)
  -> returns: ok (boolean), outputPath (string), message (string), maxSeqLenKb (integer), overlap (boolean), ignoreCase (boolean)

### FastaPatternLocate.validateParams
  summary: Validate FastaPatternLocate.process (regex compiles; paths).
    - inputPath: string (required) - input FASTA path
    - outputPath: string (required) - output tab path
    - pattern: string (required) - Java regex
    - maxSeqLenKb: int (optional, default 2) - integer (optional, default 2)
    - overlap: boolean (optional, default false) - boolean (optional, default false)
    - ignoreCase: boolean (optional, default false) - boolean (optional, default false)
  -> returns: ok (boolean), validated (boolean), message (string), outputPath (string), inputPath (string), maxSeqLenKb (integer)

### FastaSeqManipulator.process
  summary: Process FASTA file: reverse, complement, RNA, case, format.
    - inputPath: string (required) - path to input FASTA file
    - outputPath: string (required) - path to output FASTA file
    - options: object (optional) - reverse, complement, rna, upperCase, lowerCase, basesPerLine, onlyIds, onlySeqs
  -> returns: ok (boolean), outputPath (string), message (string)

### FastaSplitAsOneSeq.process
  summary: Split a multi-sequence FASTA into one .fa file per sequence (sanitized id as filename; uses SplitAsOneSeq).
    - inputPath: string (required) - input FASTA
    - outputPrefix: string (required) - output directory path, or file path whose parent folder receives id.fa files
  -> returns: ok (boolean), message (string), outputPrefix (string), outputFileCount (integer)

### FastaSplitAsOneSeq.validateParams
  summary: Validate FastaSplitAsOneSeq.process and count sequences.
    - inputPath: string (required) - input FASTA
    - outputPrefix: string (required) - output directory or prefix path
  -> returns: ok (boolean), validated (boolean), message (string), inputPath (string), outputPrefix (string), outputFileCount (integer)

### FastaSplitByCount.process
  summary: Split a multi-sequence FASTA into multiple .fa files with at most N sequences each (uses FastaMergerAndSpliter.Split).
    - inputPath: string (required) - input FASTA
    - outputPrefix: string (required) - output path prefix; writes prefix.1.fa, prefix.2.fa, ...
    - maxNumInOneFasta: int (required) - max sequences per output file, must be >= 1
  -> returns: ok (boolean), message (string), outputPrefix (string), inputSequenceCount (integer), maxNumInOneFasta (integer), outputFileCount (integer)

### FastaSplitByCount.validateParams
  summary: Validate FastaSplitByCount.process and estimate output file count.
    - inputPath: string (required) - input FASTA
    - outputPrefix: string (required) - output path prefix
    - maxNumInOneFasta: int (required) - max sequences per output file, must be >= 1
  -> returns: ok (boolean), validated (boolean), message (string), inputPath (string), outputPrefix (string), inputSequenceCount (integer), maxNumInOneFasta (integer), outputFileCount (integer)

### FastaSsrMiner.process
  summary: Mine SSR motifs in FASTA (SSRminer; GUI SSRminer).
    - inputPath: string (required) - input FASTA path
    - outputPath: string (required) - output tab path
    - maxLenKbases: int (required) - scan chunk size in kbases, must be >= 1
    - ssrPattern: string (optional) - motifs as len-count pairs separated by ; default like CLI
  -> returns: ok (boolean), outputPath (string), message (string), maxLenKbases (integer), ssrPattern (string)

### FastaSsrMiner.validateParams
  summary: Validate FastaSsrMiner.process parameters.
    - inputPath: string (required) - input FASTA path
    - outputPath: string (required) - output tab path
    - maxLenKbases: int (required) - must be >= 1
    - ssrPattern: string (optional) - string (optional)
  -> returns: ok (boolean), validated (boolean), message (string), outputPath (string), inputPath (string), maxLenKbases (integer)

### FastaStat.process
  summary: FASTA sequence statistics: total length, seq count, N50, GC, etc.; output table to file.
    - inputPath: string (required) - path to input FASTA file
    - outputPath: string (required) - path to output stat table file (e.g. .xls)
    - options: object (optional) - getLengthOnly (boolean, default false) for ID+length only
  -> returns: ok (boolean), outputPath (string), summary (string), message (string)

### FastaSubseqFromList.process
  summary: Extract subsequences by region list (ExtractFastaSubseq; GUI Fasta Subseq Basic).
    - regionsListPath: string (required) - tab/space file: geneId targetSeqId start end per line
    - inputPath: string (required) - input FASTA path
    - outputPath: string (required) - output FASTA path
  -> returns: ok (boolean), outputPath (string), message (string), regionsListPath (string)

### FastaSubseqFromList.validateParams
  summary: Validate FastaSubseqFromList.process paths.
    - regionsListPath: string (required) - region list file path
    - inputPath: string (required) - input FASTA path
    - outputPath: string (required) - output FASTA path
  -> returns: ok (boolean), validated (boolean), message (string), outputPath (string), regionsListPath (string), inputPath (string)

### FastaToTable.process
  summary: Convert FASTA to a two-column TSV: sequence id, then tab, then sequence (no wrapping).
    - inputPath: string (required) - input FASTA file
    - outputPath: string (required) - output table file path
  -> returns: ok (boolean), outputPath (string), message (string), recordCount (integer)

### FastaToTable.validateParams
  summary: Validate parameters for FastaToTable.process (paths, readable FASTA, record count preview).
    - inputPath: string (required) - input FASTA file
    - outputPath: string (required) - output table file path
  -> returns: ok (boolean), validated (boolean), message (string), inputPath (string), outputPath (string), recordCount (integer)

### FastaWindowStat.process
  summary: Per-window GC skew/ratio and N ratio (FastaWindowCalc). Writes three files: outputPath.GCskew, .GCratio, .Nratio.
    - inputPath: string (required) - input FASTA path
    - outputPath: string (required) - output base path (three stats files use this prefix)
    - windowSize: int (required) - window length in bp, >= 1
    - windowOverlap: int (required) - overlap in bp, >= 0
  -> returns: ok (boolean), outputPath (string), message (string), gcSkewPath (string), gcRatioPath (string), nRatioPath (string), windowSize (integer), windowOverlap (integer)

### FastaWindowStat.validateParams
  summary: Validate FastaWindowStat.process.
    - inputPath: string (required) - input FASTA path
    - outputPath: string (required) - output base path
    - windowSize: int (required) - >= 1
    - windowOverlap: int (required) - >= 0
  -> returns: ok (boolean), validated (boolean), message (string), outputPath (string), inputPath (string), gcSkewPath (string), gcRatioPath (string), nRatioPath (string)

### FastqBlast.listDbPrefixes
  summary: List BLAST DB prefixes under a FastqBlast database directory.
    - dbDirPath: string (required) - directory containing .nhr files
  -> returns: ok (boolean), dbDirPath (string), dbPrefixes (array), message (string)

### FastqBlast.process
  summary: BLASTn several sequences against a pre-built nucleotide DB prefix (FastQ Blast GUI).
    - sequenceText: string (optional) - inline FASTA
    - queryPath: string (optional) - string (optional)
    - dbPrefixPath: string (required) - BLAST DB prefix (path without .nhr)
    - outputPath: string (required) - result file
    - threadNum: int (optional) - integer (optional)
    - evalue: string (optional) - string (optional)
    - outFmt: string (optional) - 5|0|7
    - useShortQueryParams: boolean (optional) - boolean (optional)
    - otherBlastOpts: string (optional) - string (optional)
  -> returns: ok (boolean), outputPath (string), dbPrefixPath (string), message (string)

### FastqBlast.validateParams
  summary: Validate FastqBlast.process parameters.
    - dbPrefixPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
  -> returns: ok (boolean), message (string)

### FastxExtract.process
  summary: Extract one FASTA sequence by ID or by region using index-backed random access.
    - inputPath: string (required) - path to input FASTA file
    - outputPath: string (required) - path to output FASTA file
    - mode: string (optional, default byId, byId|byRegion) - byId|byRegion
    - id: string (required) - sequence ID
    - start: long (optional) - region start; mandatory only when mode=byRegion
    - end: long (optional) - region end; mandatory only when mode=byRegion
    - zeroStart: boolean (optional, default false) - boolean (optional, default false)
    - cleanTmp: boolean (optional, default false) - boolean (optional, default false)
  -> returns: ok (boolean), outputPath (string), mode (string), id (string), message (string)

### FastxExtract.validateParams
  summary: Validate FastxExtract parameters and paths without extraction.
    - inputPath: string (required) - path to input FASTA file
    - outputPath: string (required) - path to output FASTA file
    - mode: string (optional, default byId, byId|byRegion) - byId|byRegion
    - id: string (required) - string (required)
    - start: long (optional) - mandatory only when mode=byRegion
    - end: long (optional) - mandatory only when mode=byRegion
  -> returns: ok (boolean), validated (boolean), mode (string), inputPath (string), outputPath (string), message (string)

### FastxIndex.process
  summary: Format FASTA and build .fai index.
    - inputPath: string (required) - input FASTA path
    - outputPath: string (required) - output formatted FASTA path
    - lineWidth: int (optional, default 60) - int (optional, default 60)
  -> returns: ok (boolean), outputPath (string), indexPath (string), message (string)

### FetchATimeTree.process
  summary: Fetch an official TimeTree global-timetree subset as Newick for a list of binomial species names.
    - speciesNames: array (optional) - binomial names, e.g. Homo sapiens
    - speciesListPath: string (optional) - text file, one binomial per line
    - outputPath: string (optional) - write Newick to this file path
  -> returns: ok (boolean), newick (string), inputNames (array), warnings (array), source (string), citation (string), outputPath (string when set), message (string)

### FetchATimeTree.validateParams
  summary: Validate FetchATimeTree parameters and binomial name format.
    - speciesNames: array (optional) - array of string (optional)
    - speciesListPath: string (optional) - string (optional)
    - outputPath: string (optional) - string (optional)
  -> returns: ok (boolean), validated (boolean), message (string), speciesCount (number)

### GXFFix.process
  summary: Fix GXF/GFF3: sort, fix structure (gene/mRNA/exon/CDS/UTR), CDS phase, deduplicate IDs.
    - inputPath: string (required) - path to input GXF/GFF3 file
    - outputPath: string (required) - path to output fixed GXF/GFF3 file
  -> returns: ok (boolean), outputPath (string), message (string)

### GXFRenameByMap.process
  summary: Rename annotation IDs in GXF/GFF/GTF by mapping file.
    - inputPath: string (required) - input GXF/GFF/GTF path
    - renameMapPath: string (required) - tab-delimited old/new ID map path
    - outputPath: string (required) - output renamed file path
    - targetAttrs: array (optional) - reserved attr whitelist
  -> returns: ok (boolean), outputPath (string), renameMapPath (string), message (string)

### GXFRenameByMap.validateParams
  summary: Validate GXFRenameByMap params without renaming.
    - inputPath: string (required) - input GXF/GFF/GTF path
    - renameMapPath: string (required) - tab-delimited old/new ID map path
    - outputPath: string (required) - output renamed file path
    - targetAttrs: array (optional) - reserved attr whitelist
  -> returns: ok (boolean), validated (boolean), inputPath (string), renameMapPath (string), outputPath (string), message (string)

### GenBankToFasta.process
  summary: Convert GenBank/GBFF records to FASTA.
    - inputPath: string (required) - input GenBank/GBFF file path
    - outputPath: string (required) - output FASTA file path
  -> returns: ok (boolean), outputPath (string), recordCount (integer), message (string)

### GenBankToFasta.validateParams
  summary: Validate GenBankToFasta params without conversion.
    - inputPath: string (required) - input GenBank/GBFF file path
    - outputPath: string (required) - output FASTA file path
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPath (string), message (string)

### GeneExpFilter.process
  summary: Filter gene expression matrix by minimum expression and CV.
    - inputPath: string (required) - input expression table
    - outputPath: string (required) - output filtered table
    - minExpValue: number (optional, default 1.0) - number (optional, default 1.0)
    - minExpFilterRatio: number (optional, default 5/7) - number (optional, default 5/7)
    - minCV: number (optional, default 0.25) - number (optional, default 0.25)
  -> returns: ok (boolean), outputPath (string), message (string)

### GeneExpFilter.validateParams
  summary: Validate GeneExpFilter params without running filtering.
    - inputPath: string (required) - input expression table
    - outputPath: string (required) - output filtered table
    - minExpValue: number (optional, default 1.0) - number (optional, default 1.0)
    - minExpFilterRatio: number (optional) - number (optional, should be within [0,1])
    - minCV: number (optional, default 0.25) - number (optional, default 0.25)
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPath (string), minExpValue (number), message (string)

### GenePairCorr.process
  summary: Calculate Pearson correlation for gene pairs from expression matrix.
    - inputExpPath: string (required) - input expression matrix
    - outputPath: string (required) - output table
    - genePairPath: string (optional) - pair file; if absent, run global high-correlation scan
  -> returns: ok (boolean), outputPath (string), message (string)

### GenePairCorr.validateParams
  summary: Validate GenePairCorr params without running correlation.
    - inputExpPath: string (required) - input expression matrix
    - outputPath: string (required) - output table
    - genePairPath: string (optional) - pair file
  -> returns: ok (boolean), validated (boolean), inputExpPath (string), outputPath (string), message (string)

### GfaToFasta.process
  summary: Convert GFA segment records to FASTA.
    - inputPath: string (required) - input GFA path
    - outputPath: string (required) - output FASTA path
  -> returns: ok (boolean), outputPath (string), segmentCount (integer), message (string)

### GfaToFasta.validateParams
  summary: Validate GFA conversion params without writing output.
    - inputPath: string (required) - input GFA path
    - outputPath: string (required) - output FASTA path
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPath (string), segmentCount (integer), message (string)

### GffCdsPhase.process
  summary: GFF3/GTF CDS phase check: split correct vs problematic records.
    - inputPath: string (required) - path to input GFF3/GTF file
    - outputCorrectPath: string (required) - path for correct records
    - outputProblematicPath: string (required) - path for problematic records
    - reportPath: string (required) - path for report file
  -> returns: ok (boolean), outputCorrectPath (string), outputProblematicPath (string), reportPath (string), stats (object - totalTranscriptCount, validTranscriptCount, problematicTranscriptCount, correctRecordCount, problematicRecordCount)

### GffExtractRegion.process
  summary: Intersect GXF with region list chr\tstart\tend tab lines (GxFOverlapIndexer); writes outputPath plus .clean.tab.xls.
    - gxfPath: string (required) - string (required)
    - regionListPath: string (required) - tab-separated regions
    - outputPath: string (required) - string (required)
    - binSize: int (optional, default 10000) - indexer bin size
    - usePreBuildIndex: boolean (optional, default true) - boolean (optional, default true)
  -> returns: ok (boolean), outputPath (string), cleanTablePath (string), message (string)

### GffExtractRegion.validateParams
  summary: Validate GffExtractRegion paths.
    - gxfPath: string (required) - string (required)
    - regionListPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
  -> returns: ok (boolean), validated (boolean), outputPath (string), cleanTablePath (string)

### GffFeatureExtract.process
  summary: Extract feature sequences from GFF and genome FASTA.
    - gffPath: string (required) - input GFF path
    - genomePath: string (required) - genome FASTA path
    - outputPath: string (required) - output FASTA path
    - feature: string (required) - feature type
    - uniqId: string (required) - attribute key for unique ID
    - retainAttr: boolean (optional, default true) - boolean (optional, default true)
    - upStreamBases: int (optional, default 0) - int (optional, default 0)
    - downStreamBases: int (optional, default 0) - int (optional, default 0)
    - onlyRetainFlank: boolean (optional, default false) - boolean (optional, default false)
    - addN: boolean (optional, default false) - boolean (optional, default false)
    - maxFeatureCounts: int (optional) - int (optional)
    - minFeatureCounts: int (optional) - int (optional)
  -> returns: ok (boolean), outputPath (string), feature (string), uniqId (string), message (string)

### GffFeatureExtract.validateParams
  summary: Validate GFF feature extraction params without running extraction.
    - gffPath: string (required) - input GFF path
    - genomePath: string (required) - genome FASTA path
    - outputPath: string (required) - output FASTA path
    - feature: string (required) - feature type
    - uniqId: string (required) - attribute key for unique ID
    - upStreamBases: int (optional, default 0) - int (optional, default 0)
    - downStreamBases: int (optional, default 0) - int (optional, default 0)
  -> returns: ok (boolean), validated (boolean), gffPath (string), genomePath (string), outputPath (string), message (string)

### GffFeatureScan.process
  summary: Scan GFF file and list available feature + unique-id tag pairs.
    - gffPath: string (required) - input GFF path
    - maxScanLines: int (optional, default 100000) - int (optional, default 100000)
  -> returns: ok (boolean), validated (boolean), inputPath (string), featureIdPairs (array), count (integer), message (string)

### GffFeatureScan.validateParams
  summary: Validate GFF feature scan params without scanning.
    - gffPath: string (required) - input GFF path
    - maxScanLines: int (optional, default 100000) - int (optional, default 100000, must be > 0)
  -> returns: ok (boolean), validated (boolean), inputPath (string), maxScanLines (integer), message (string)

### GffReconstructorBatch.process
  summary: Batch reconstruct gene structure GFF from mRNA and genome DNA (BatchGffReconstructor). Needs BLAST+ like GUI.
    - mrnaFastaPath: string (required) - string (required)
    - dnaFastaPath: string (required) - string (required)
    - outputGffPath: string (required) - string (required)
    - notGoodIdsPath: string (required) - string (required)
  -> returns: ok (boolean), outputPath (string), notGoodIdsPath (string), message (string)

### GffReconstructorBatch.validateParams
  summary: Validate GffReconstructorBatch paths.
    - mrnaFastaPath: string (required) - string (required)
    - dnaFastaPath: string (required) - string (required)
    - outputGffPath: string (required) - string (required)
    - notGoodIdsPath: string (required) - string (required)
  -> returns: ok (boolean), validated (boolean), outputPath (string), notGoodIdsPath (string)

### GtfFeatureExtract.process
  summary: Extract feature sequences from GTF and genome FASTA.
    - gtfPath: string (required) - input GTF path
    - genomePath: string (required) - genome FASTA path
    - outputPath: string (required) - output FASTA path
    - feature: string (required) - feature type
    - uniqId: string (required) - attribute key for unique ID
    - retainAttr: boolean (optional, default true) - boolean (optional, default true)
    - upStreamBases: int (optional, default 0) - int (optional, default 0)
    - downStreamBases: int (optional, default 0) - int (optional, default 0)
    - onlyRetainFlank: boolean (optional, default false) - boolean (optional, default false)
    - addN: boolean (optional, default false) - boolean (optional, default false)
    - maxFeatureCounts: int (optional) - int (optional)
    - minFeatureCounts: int (optional) - int (optional)
  -> returns: ok (boolean), outputPath (string), feature (string), uniqId (string), message (string)

### GtfFeatureExtract.validateParams
  summary: Validate GTF feature extraction params without running extraction.
    - gtfPath: string (required) - input GTF path
    - genomePath: string (required) - genome FASTA path
    - outputPath: string (required) - output FASTA path
    - feature: string (required) - feature type
    - uniqId: string (required) - attribute key for unique ID
    - upStreamBases: int (optional, default 0) - int (optional, default 0)
    - downStreamBases: int (optional, default 0) - int (optional, default 0)
  -> returns: ok (boolean), validated (boolean), gtfPath (string), genomePath (string), outputPath (string), message (string)

### GtfFeatureScan.process
  summary: Scan GTF file and list available feature + unique-id tag pairs.
    - gtfPath: string (required) - input GTF path
    - maxScanLines: int (optional, default 100000) - int (optional, default 100000)
  -> returns: ok (boolean), validated (boolean), inputPath (string), featureIdPairs (array), count (integer), message (string)

### GtfFeatureScan.validateParams
  summary: Validate GTF feature scan params without scanning.
    - gtfPath: string (required) - input GTF path
    - maxScanLines: int (optional, default 100000) - int (optional, default 100000, must be > 0)
  -> returns: ok (boolean), validated (boolean), inputPath (string), maxScanLines (integer), message (string)

### GxfCat.process
  summary: Merge multiple GXF files (GXFcat).
    - inputPaths: array (required) - ordered list of GXF files
    - outputPath: string (required) - merged output GXF
    - conflictPrefixPath: string (required) - conflict report path prefix/file like GUI output panel
  -> returns: ok (boolean), outputPath (string), conflictPrefixPath (string), message (string)

### GxfCat.validateParams
  summary: Validate GxfCat.process.
    - inputPaths: array (required) - array of strings (required)
    - outputPath: string (required) - string (required)
    - conflictPrefixPath: string (required) - string (required)
  -> returns: ok (boolean), validated (boolean), outputPath (string), conflictPrefixPath (string)

### GxfFilter.process
  summary: Filter GXF/GFF/GTF records by ID list.
    - inputPath: string (required) - input GXF/GFF/GTF path
    - outputPath: string (required) - output filtered path
    - idList: array (optional) - array of string (optional)
    - idListPath: string (optional) - file of IDs, one per line
  -> returns: ok (boolean), outputPath (string), idCount (integer), message (string)

### GxfFilter.validateParams
  summary: Validate GxfFilter params without filtering.
    - inputPath: string (required) - input GXF/GFF/GTF path
    - outputPath: string (required) - output filtered path
    - idList: array (optional) - array of string (optional)
    - idListPath: string (optional) - file of IDs, one per line
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPath (string), idCount (integer), message (string)

### GxfGeneDensityProfiler.process
  summary: Gene density profiling (GeneDensityProfiler).
    - inputPath: string (required) - GXF
    - outputPath: string (required) - output table
    - binSize: int (required) - integer (required) >= 1
    - definedFeatureTag: string (optional) - overrides default gene feature tag when non-empty
    - chrLengthPath: string (optional) - optional chromosome length table
  -> returns: ok (boolean), outputPath (string), message (string)

### GxfGeneDensityProfiler.validateParams
  summary: Validate density profiler.
    - inputPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
    - binSize: int (required) - integer (required)
    - chrLengthPath: string (optional) - string (optional)
  -> returns: ok (boolean), validated (boolean), outputPath (string), binSize (integer)

### GxfGeneFamilyStructErrorDetect.process
  summary: Gene family structure error scan (StructureAlnQualityUtils).
    - gxfPath: string (required) - string (required)
    - genomePath: string (required) - string (required)
    - cdsIdListPath: string (required) - CDS / gene ID list file
    - outputPath: string (required) - output QA table path
  -> returns: ok (boolean), outputPath (string), message (string)

### GxfGeneFamilyStructErrorDetect.validateParams
  summary: Validate family error-detect paths.
    - gxfPath: string (required) - string (required)
    - genomePath: string (required) - string (required)
    - cdsIdListPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
  -> returns: ok (boolean), validated (boolean), outputPath (string)

### GxfGenomeMatch.process
  summary: Test whether GXF seqids overlap genome FASTA headers (GxfGenomeMatch).
    - gxfPath: string (required) - string (required)
    - genomePath: string (required) - genome FASTA
  -> returns: ok (boolean), matched (boolean), message (string)

### GxfGenomeMatch.validateParams
  summary: Validate GxfGenomeMatch paths.
    - gxfPath: string (required) - string (required)
    - genomePath: string (required) - string (required)
  -> returns: ok (boolean), validated (boolean), message (string)

### GxfIdAppender.process
  summary: Prefix chr and ID attributes on GFF3/GTF (GxfIDAppender).
    - inputPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
    - prefix: string (required) - prefix string appended to chromosome and ID-like attributes
  -> returns: ok (boolean), outputPath (string), message (string)

### GxfIdAppender.validateParams
  summary: Validate GxfIdAppender.process.
    - inputPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
    - prefix: string (required) - string (required)
  -> returns: ok (boolean), validated (boolean), outputPath (string)

### GxfPatch.process
  summary: Patch reference GXF with features from patch GXF (GXFPatch).
    - refGxfPath: string (required) - string (required)
    - patchGxfPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
  -> returns: ok (boolean), outputPath (string), message (string)

### GxfPatch.validateParams
  summary: Validate GxfPatch.process.
    - refGxfPath: string (required) - string (required)
    - patchGxfPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
  -> returns: ok (boolean), validated (boolean), outputPath (string)

### GxfQuickDiagnosis.process
  summary: Structural annotation QA (GsaQuickDiagnosis).
    - inputPath: string (required) - GXF path
    - outputPath: string (required) - stats table output
    - checkUTR: boolean (optional, default false) - boolean (optional, default false)
    - utrRelax: number (optional, default 0.5) - number (optional, default 0.5)
    - genomePath: string (optional) - genome FASTA for strand/length checks when provided
  -> returns: ok (boolean), outputPath (string), message (string)

### GxfQuickDiagnosis.validateParams
  summary: Validate diagnosis paths.
    - inputPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
    - genomePath: string (optional) - string (optional)
  -> returns: ok (boolean), validated (boolean), outputPath (string)

### GxfRecallMrna.process
  summary: Recall missing mRNA features from exon/cds/utr records.
    - inputPath: string (required) - input GXF/GFF/GTF path
    - outputPath: string (required) - output recalled GFF3 path
  -> returns: ok (boolean), outputPath (string), recordCount (integer), message (string)

### GxfRecallMrna.validateParams
  summary: Validate GxfRecallMrna params without recall.
    - inputPath: string (required) - input GXF/GFF/GTF path
    - outputPath: string (required) - output recalled GFF3 path
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPath (string), message (string)

### GxfRepresentativeGxf.process
  summary: Filter representative transcript records from GXF.
    - inputPath: string (required) - input GXF/GFF/GTF path
    - outputPath: string (required) - output representative GXF path
    - featurePattern: string (optional, default CDS) - target feature regex
    - attachPattern: string (optional) - extra feature regex to keep
  -> returns: ok (boolean), outputPath (string), keptRecordCount (integer), message (string)

### GxfRepresentativeGxf.validateParams
  summary: Validate representative GXF filtering params.
    - inputPath: string (required) - input GXF/GFF/GTF path
    - outputPath: string (required) - output representative GXF path
    - featurePattern: string (optional, default CDS) - target feature regex
    - attachPattern: string (optional) - extra feature regex to keep
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPath (string), message (string)

### GxfRepresentativeIds.process
  summary: Extract representative transcript IDs from GXF.
    - inputPath: string (required) - input GXF/GFF/GTF path
    - outputPath: string (required) - output representative id table path
    - featurePattern: string (optional, default CDS) - target feature regex
  -> returns: ok (boolean), outputPath (string), representativeCount (integer), message (string)

### GxfRepresentativeIds.validateParams
  summary: Validate representative ID extraction params.
    - inputPath: string (required) - input GXF/GFF/GTF path
    - outputPath: string (required) - output representative id table path
    - featurePattern: string (optional, default CDS) - target feature regex
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPath (string), message (string)

### GxfSeqExtract.process
  summary: Extract sequences from GFF3/GTF and genome FASTA by feature type and ID attribute.
    - gxfPath: string (required) - path to input GFF3 or GTF file
    - genomePath: string (required) - path to genome FASTA file
    - outputPath: string (required) - path to output FASTA file
    - featureTag: string (required) - feature type e.g. CDS, mRNA, exon
    - idTag: string (required) - attribute name for sequence ID e.g. ID, Name
    - options: object (optional) - retainAttr, onlyUpOrDownStreamBases, upStreamBases, downStreamBases, maxFeatureSize, minFeatureSize
  -> returns: ok (boolean), outputPath (string), warnings (string), message (string)

### GxfSplit.process
  summary: Split large GXF/GFF/GTF into multiple balanced chunks.
    - inputPath: string (required) - input GXF/GFF/GTF path
    - outputPrefix: string (required) - output prefix for split files
    - numOfFile: int (optional, default 8) - int (optional, default 8, must be > 0)
  -> returns: ok (boolean), outputPrefix (string), splitFileCount (integer), message (string)

### GxfSplit.validateParams
  summary: Validate GxfSplit params without splitting.
    - inputPath: string (required) - input GXF/GFF/GTF path
    - outputPrefix: string (required) - output prefix for split files
    - numOfFile: int (optional, default 8) - int (optional, default 8, must be > 0)
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPrefix (string), numOfFile (integer), message (string)

### GxfStat.process
  summary: Generate statistics table for GXF/GFF/GTF annotation.
    - inputPath: string (required) - input GXF/GFF/GTF path
    - outputPath: string (required) - output stat table path
  -> returns: ok (boolean), outputPath (string), geneCount (integer), mrnaCount (integer), chrCount (integer), message (string)

### GxfStat.validateParams
  summary: Validate GxfStat params without running statistics.
    - inputPath: string (required) - input GXF/GFF/GTF path
    - outputPath: string (required) - output stat table path
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPath (string), message (string)

### GxfToGenePos.process
  summary: Generate gene position table and chromosome length table from GXF.
    - inputPath: string (required) - input GXF/GFF/GTF path
    - outputPath: string (required) - output gene position table path
    - chrLenPath: string (required) - output chromosome length table path
    - featurePattern: string (optional, default cds) - feature regex
  -> returns: ok (boolean), outputPath (string), outputGenePosPath (string), outputChrLenPath (string), geneCount (integer), chrCount (integer), message (string)

### GxfToGenePos.validateParams
  summary: Validate GxfToGenePos params without generation.
    - inputPath: string (required) - input GXF/GFF/GTF path
    - outputPath: string (required) - output gene position table path
    - chrLenPath: string (required) - output chromosome length table path
    - featurePattern: string (optional, default cds) - feature regex
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPath (string), outputChrLenPath (string), message (string)

### McScanXFileMerge.process
  summary: Merge files for MCScanX: PlainText (concat non-meta lines), GtfGff2SimGxf (via gene pos temp), or Collinear (filter by block size).
    - inputPaths: array (required) - input file paths in merge order
    - outputPath: string (required) - merged output file path
    - mode: string (optional, default PlainText, PlainText|GtfGff2SimGxf|Collinear) - PlainText|GtfGff2SimGxf|Collinear
    - minBlockSize: int (optional, default 5) - used when mode is Collinear
  -> returns: ok (boolean), outputPath (string), message (string), inputFileCount (integer), mode (string)

### McScanXFileMerge.validateParams
  summary: Validate McScanXFileMerge.process without writing merged content.
    - inputPaths: array (required) - input file paths
    - outputPath: string (required) - merged output file path
    - mode: string (optional, default PlainText, PlainText|GtfGff2SimGxf|Collinear) - PlainText|GtfGff2SimGxf|Collinear
    - minBlockSize: int (optional, default 5) - used when mode is Collinear
  -> returns: ok (boolean), validated (boolean), message (string), outputPath (string), inputFileCount (integer), mode (string), minBlockSize (integer)

### MemeSuiteXmlToTab.process
  summary: Convert MEME/MAST XML to motif-domain tabular file.
    - inputPath: string (required) - input MEME/MAST XML path
    - outputPath: string (required) - output table path
  -> returns: ok (boolean), outputPath (string), seqCount (integer), motifHitCount (integer), message (string)

### MemeSuiteXmlToTab.validateParams
  summary: Validate MEME/MAST XML conversion params without conversion.
    - inputPath: string (required) - input MEME/MAST XML path
    - outputPath: string (required) - output table path
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPath (string), xmlRoot (string), message (string)

### MiRBaseDatToFasta.process
  summary: Convert miRBase DAT records to FASTA.
    - inputPath: string (required) - input miRBase DAT file path
    - outputPath: string (required) - output FASTA file path
  -> returns: ok (boolean), outputPath (string), recordCount (integer), message (string)

### MiRBaseDatToFasta.validateParams
  summary: Validate MiRBaseDatToFasta params without conversion.
    - inputPath: string (required) - input miRBase DAT file path
    - outputPath: string (required) - output FASTA file path
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPath (string), message (string)

### NcbiDownloadBulk.process
  summary: Bulk Entrez epost/efetch (DownloadSeqEntrezUtils). Larger lists; obey NCBI usage guidelines and RPC timeout.
    - accessionListPath: string (required) - newline-separated IDs
    - outputPath: string (required) - output file path (not directory)
    - database: string (optional, default nuccore, nuccore|protein) - string (optional, nuccore|protein, default nuccore)
    - format: string (optional, default Fasta, Fasta|GenBank) - string (optional, Fasta|GenBank, default Fasta)
    - greedyMode: boolean (optional, default false) - retry subsets like GUI greedy mode
  -> returns: ok (boolean), outputPath (string), message (string), database (string), format (string), greedyMode (boolean), failedIds (array when greedy)

### NcbiDownloadBulk.validateParams
  summary: Validate NcbiDownloadBulk parameters.
    - accessionListPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
    - database: string (optional) - string (optional)
    - format: string (optional) - string (optional)
  -> returns: ok (boolean), validated (boolean), message (string), outputPath (string)

### NcbiDownloadSimple.process
  summary: Download <=100-ish accessions via NCBI HTTPS viewer CGI (DownLoadNCBIFasta). One request per ID with sleeps; GUI recommends Bulk for larger lists.
    - accessionListPath: string (required) - one ID per line; optional chr range: accession start end
    - outputPath: string (required) - merged output file path (.fa or .gb)
    - format: string (optional, default Fasta, Fasta|GenBank) - string (optional, Fasta|GenBank, default Fasta)
  -> returns: ok (boolean), outputPath (string), message (string), format (string), failedIds (array)

### NcbiDownloadSimple.validateParams
  summary: Validate NcbiDownloadSimple paths and format.
    - accessionListPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
    - format: string (optional) - string (optional)
  -> returns: ok (boolean), validated (boolean), message (string), outputPath (string)

### OneStepBuildATree.process
  summary: One-step ML tree: MUSCLE alignment, trimAl, IQ-Tree. Input FASTA, output directory; tree at {outputPath}/TBtools.IQtree.treefile. Requires MUSCLE (or muscle5), trimAl, IQ-Tree in PATH.
    - inputPath: string (required) - path to input FASTA file (sequences for alignment)
    - outputPath: string (required) - output directory (created if missing); tree file written as {outputPath}/TBtools.IQtree.treefile
    - options: object (optional) - ultraFastBS (boolean, default true), bbTime (int, default 5000 for ultrafast / 1000 for standard), freeRate (boolean, default false), ascertainmentBias (boolean, default false), model (string, default Auto), threads (int, default 2; use 0 for AUTO), redo (boolean, default true)
  -> returns: ok (boolean), outputPath (string), treeFilePath (string), message (string)

### OneStepBuildATree.validateParams
  summary: Validate OneStepBuildATree input/output paths without running external tools.
    - inputPath: string (required) - path to input FASTA file
    - outputPath: string (required) - path to output directory
  -> returns: ok (boolean), inputPath (string), outputDir (string), message (string)

### OrfBatchLongestComplete.process
  summary: Batch longest complete ORF per sequence (GetLongestORF; GUI Batch Predict). Writes outputPath nucleotide FAA, plus .Pep.fa and .NoORF.
    - inputPath: string (required) - input FASTA
    - outputPath: string (required) - output ORF FASTA prefix (same as CLI --outORFs)
  -> returns: ok (boolean), outputPath (string), pepPath (string), noOrfReportPath (string), message (string)

### OrfBatchLongestComplete.validateParams
  summary: Validate OrfBatchLongestComplete.process paths.
    - inputPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
  -> returns: ok (boolean), validated (boolean), message (string), outputPath (string), inputPath (string)

### OrfPredictMax.process
  summary: Predict ORFs all six-frame style (MaxORFPredict; GUI Get ORF). Writes TSV: frame/start/end/length/peptide/info.
    - outputPath: string (required) - output tab file path
    - sequenceText: string (optional) - raw nucleotide paste; FASTA header line stripped like GUI
    - inputFastaPath: string (optional) - if sequenceText omitted, first FASTA record is used
    - minOrfLength: int (optional, default 30) - minimum peptide length passed to predictor
    - startCodon: boolean (optional, default true) - require/start ATG-derived M semantics in MaxORFPredict
    - stopCodon: boolean (optional, default true) - boolean (optional, default true)
  -> returns: ok (boolean), outputPath (string), message (string), orfCount (integer)

### OrfPredictMax.validateParams
  summary: Validate OrfPredictMax.process (either sequenceText or readable inputFastaPath; output writable).
    - outputPath: string (required) - string (required)
    - sequenceText: string (optional) - raw nucleotide; if blank, inputFastaPath is required
    - inputFastaPath: string (optional) - first FASTA record if sequenceText blank
    - minOrfLength: int (optional, default 30) - integer (optional, default 30, must be >= 1)
  -> returns: ok (boolean), validated (boolean), message (string), outputPath (string)

### OrfSixFrameTranslate.process
  summary: Six-frame nucleotide translation (SixFrameTranlater). Writes outputPath and outputPath.LongestORF.
    - inputPath: string (required) - input FASTA
    - outputPath: string (required) - output protein FASTA base path
  -> returns: ok (boolean), outputPath (string), longestOrfPath (string), message (string)

### OrfSixFrameTranslate.validateParams
  summary: Validate OrfSixFrameTranslate.process paths.
    - inputPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
  -> returns: ok (boolean), validated (boolean), message (string), outputPath (string), inputPath (string), longestOrfPath (string)

### PlantCareClassify.process
  summary: Classify PlantCARE result records using bundled mapping resource.
    - inputPath: string (required) - input PlantCARE result table path
    - outputPath: string (required) - output classified table path
  -> returns: ok (boolean), outputPath (string), classifiedCount (integer), naCount (integer), message (string)

### PlantCareClassify.validateParams
  summary: Validate PlantCARE classify params without classification.
    - inputPath: string (required) - input PlantCARE result table path
    - outputPath: string (required) - output classified table path
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPath (string), message (string)

### QuickGeneFamilyIdentification.process
  summary: Quick gene family identification vs reference pep + gene set list.
    - queryPepPath: string (required) - string (required)
    - referencePepPath: string (required) - string (required)
    - referenceGeneSetPath: string (required) - reference family ID list file
    - outputPath: string (required) - string (required)
    - threadNum: int (optional, default 4) - integer (optional, default 4)
    - useDiamond: boolean (optional, default true) - boolean (optional, default true)
    - autoFillIterations: int (optional, default 2) - integer (optional, default 2)
  -> returns: ok (boolean), outputPath (string), message (string)

### QuickGeneFamilyIdentification.validateParams
  summary: Validate QuickGeneFamilyIdentification.process parameters.
    - queryPepPath: string (required) - string (required)
    - referencePepPath: string (required) - string (required)
    - referenceGeneSetPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
  -> returns: ok (boolean), outputPath (string), message (string)

### QuickProteinAnno.process
  summary: Diamond/BLAST Swiss-Prot quick protein annotation table (QuickProteinAnno).
    - proteinPath: string (required) - query protein FASTA
    - swissProtDbPath: string (required) - Swiss-Prot DB FASTA for Diamond
    - outputPath: string (required) - summary table output
    - threadNum: int (optional, default 2) - integer (optional, default 2)
    - numberOfHits: int (optional, default 20) - integer (optional, default 20)
  -> returns: ok (boolean), outputPath (string), numberOfHits (integer), message (string)

### QuickProteinAnno.validateParams
  summary: Validate QuickProteinAnno.process parameters.
    - proteinPath: string (required) - string (required)
    - swissProtDbPath: string (required) - string (required)
    - outputPath: string (required) - string (required)
  -> returns: ok (boolean), outputPath (string), message (string)

### ReciprocalBlast.process
  summary: Reciprocal BLAST between two sequence sets; writes files under outputPrefixPath.
    - queryPath: string (required) - string (required)
    - subjectPath: string (required) - string (required)
    - outputPrefixPath: string (required) - output file prefix (not directory alone)
    - threadNum: int (optional) - integer (optional)
    - retainBestHitNum: int (optional, default 5) - integer (optional, default 5)
    - evalue: string (optional) - string (optional)
    - minIdentity: string (optional) - string (optional)
    - minWeightedCov: string (optional) - string (optional)
    - queryBlastType: string (optional, blastn|blastp|blastx|tblastn|tblastx|Guess) - blastn|blastp|blastx|tblastn|tblastx|Guess
    - subjectBlastType: string (optional) - string (optional)
    - useDiamond: boolean (optional) - boolean (optional)
    - limitedQueryIds: array (optional) - array (optional)
    - limitedQueryIdListPath: string (optional) - string (optional)
  -> returns: ok (boolean), outputPrefixPath (string), message (string)

### ReciprocalBlast.validateParams
  summary: Validate ReciprocalBlast.process parameters.
    - queryPath: string (required) - string (required)
    - subjectPath: string (required) - string (required)
    - outputPrefixPath: string (required) - string (required)
  -> returns: ok (boolean), outputPath (string), message (string)

### SendEmail.process
  summary: Send email via SMTP with optional attachments. Uses TBtools Config: mailUser, mailPassword, mailSmtpHost, mailSmtpPort.
    - to: string (required) - recipient email address
    - subject: string (optional) - subject line, default empty
    - body: string (optional) - plain text body, default empty
    - attachmentPaths: array (optional) - file paths to attach
  -> returns: ok (boolean), message (string), sentTo (string), subject (string)

### SraXmlToTable.process
  summary: Parse NCBI SRA experiment XML into run-level table and study summary.
    - inputPath: string (required) - input SRA XML path
    - outputPath: string (required) - output run table path
  -> returns: ok (boolean), outputPath (string), studyInfoPath (string), runCount (integer), studyCount (integer), message (string)

### SraXmlToTable.validateParams
  summary: Validate SraXmlToTable params without parsing.
    - inputPath: string (required) - input SRA XML path
    - outputPath: string (required) - output run table path
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPath (string), studyInfoPath (string), message (string)

### TableRowManipulator.process
  summary: Extract or filter rows by column using TableRowManipulator (GUI Table Row Manipulator); provide idList (JSON array) and/or idListPath like TableTools.selectRows.
    - inputPath: string (required) - input table path
    - outputPath: string (required) - output table path
    - selectedColumn: string (required) - header name, or zero-based column index when containHeader=false
    - idList: array (optional) - IDs/patterns in request order; used when non-empty, otherwise idListPath is required
    - idListPath: string (optional) - ID list file when idList is empty
    - conditionMode: string (optional, default match, match|contain|equal|bigger|smaller) - match|contain|equal|bigger|smaller
    - selectedMode: string (optional, default extract, extract|filter) - extract|filter
    - separator: string (optional, default tab) - string (optional, default tab)
    - containHeader: boolean (optional, default true) - boolean (optional, default true)
    - caseSensitive: boolean (optional, default true) - boolean (optional, default true)
    - sortByIdList: boolean (optional, default true) - boolean (optional, default true)
    - regex: boolean (optional, default false) - boolean (optional, default false)
    - commentString: string (optional, default #) - string (optional, default #)
  -> returns: ok (boolean), outputPath (string), message (string)

### TableRowManipulator.validateParams
  summary: Validate TableRowManipulator.process without writing the output table.
    - inputPath: string (required) - input table path
    - outputPath: string (required) - output table path
    - selectedColumn: string (required) - header name or column index when containHeader=false
    - idList: array (optional) - array of string (optional)
    - idListPath: string (optional) - string (optional)
    - conditionMode: string (optional, default match) - string (optional, default match)
    - selectedMode: string (optional, default extract) - string (optional, default extract)
    - separator: string (optional, default tab) - string (optional, default tab)
    - containHeader: boolean (optional, default true) - boolean (optional, default true)
    - caseSensitive: boolean (optional, default true) - boolean (optional, default true)
    - sortByIdList: boolean (optional, default true) - boolean (optional, default true)
    - regex: boolean (optional, default false) - boolean (optional, default false)
    - commentString: string (optional, default #) - string (optional, default #)
  -> returns: ok (boolean), validated (boolean), message (string), outputPath (string), idCount (integer)

### TableToFasta.process
  summary: Convert two-or-more-column table to FASTA: last column is sequence; id columns joined with underscore.
    - inputPath: string (required) - input table (tab or space separated)
    - outputPath: string (required) - output FASTA file path
  -> returns: ok (boolean), outputPath (string), message (string), lineCount (integer)

### TableToFasta.validateParams
  summary: Validate parameters for TableToFasta.process (paths, readable table, line count preview).
    - inputPath: string (required) - input table file
    - outputPath: string (required) - output FASTA file path
  -> returns: ok (boolean), validated (boolean), message (string), inputPath (string), outputPath (string), lineCount (integer)

### TableTools.appendByKey
  summary: Append columns from right table into left table by key columns.
    - leftTablePath: string (required) - left table path
    - rightTablePath: string (required) - right table path
    - leftKeyColIndex: int (required) - key column in left table, must be >= 0
    - rightKeyColIndex: int (required) - key column in right table, must be >= 0
    - outputPath: string (required) - output table path
  -> returns: ok (boolean), outputPath (string), message (string)

### TableTools.castLongToWide
  summary: Cast 3-column long table to wide matrix table.
    - inputPath: string (required) - input long table path
    - outputPath: string (required) - output wide table path
  -> returns: ok (boolean), outputPath (string), message (string)

### TableTools.collapseColumnsByGroup
  summary: Collapse sample columns by group with aggregate method.
    - inputPath: string (required) - input table with header
    - groupPath: string (required) - sample/group map file
    - outputPath: string (required) - output collapsed table path
    - method: string (optional, default Sum, Sum|Mean|Max|Min|Var|Std) - Sum|Mean|Max|Min|Var|Std
  -> returns: ok (boolean), outputPath (string), message (string)

### TableTools.collapseDuplicateKeys
  summary: Collapse duplicate key rows by joining same-key column values.
    - inputPath: string (required) - input table path
    - outputPath: string (required) - output table path
    - keyColumnIndex: int (required) - key column index, must be >= 0
    - separator: string (optional, default tab) - string (optional, default tab)
    - containHeader: boolean (optional, default true) - boolean (optional, default true)
    - commentString: string (optional, default #) - string (optional, default #)
    - naString: string (optional, default NA) - string (optional, default NA)
    - rmEmpty: boolean (optional, default true) - boolean (optional, default true)
    - rmDup: boolean (optional, default true) - boolean (optional, default true)
    - onlyRetainFirst: boolean (optional, default false) - boolean (optional, default false)
  -> returns: ok (boolean), outputPath (string), message (string)

### TableTools.fillMissingValues
  summary: Fill missing values in selected columns.
    - inputPath: string (required) - input table path
    - outputPath: string (required) - output table path
    - strategy: string (optional, default constant, constant|mean|median) - constant|mean|median
    - targetColumns: string (optional) - comma-separated zero-based column indexes
    - fillValue: string (optional) - constant fill value; mandatory only when strategy=constant
    - containHeader: boolean (optional, default true) - boolean (optional, default true)
    - separator: string (optional, default tab) - string (optional, default tab)
  -> returns: ok (boolean), outputPath (string), message (string)

### TableTools.groupAggregate
  summary: Alias of collapseColumnsByGroup for group-based column aggregation.
    - inputPath: string (required) - input table with header
    - groupPath: string (required) - sample/group map file
    - outputPath: string (required) - output collapsed table path
    - method: string (optional, default Sum, Sum|Mean|Max|Min|Var|Std) - Sum|Mean|Max|Min|Var|Std
  -> returns: ok (boolean), outputPath (string), message (string)

### TableTools.melt
  summary: Melt wide table into 3-column long format.
    - inputPath: string (required) - wide table path
    - outputPath: string (required) - long table path
    - separator: string (optional, default tab) - string (optional, default tab)
  -> returns: ok (boolean), outputPath (string), message (string)

### TableTools.mergeByKeyInnerLeft
  summary: Merge two tables by key with explicit join type.
    - leftTablePath: string (required) - left table path
    - rightTablePath: string (required) - right table path
    - leftKeyColIndex: int (required) - key column in left table, must be >= 0
    - rightKeyColIndex: int (required) - key column in right table, must be >= 0
    - outputPath: string (required) - output table path
    - joinType: string (optional, default left, left|inner) - left|inner
    - separator: string (optional, default tab) - string (optional, default tab)
    - naValue: string (optional, default empty) - string (optional, default empty)
  -> returns: ok (boolean), outputPath (string), message (string)

### TableTools.mergeByKeyMulti
  summary: Merge multiple tables by key columns.
    - inputPaths: array (required) - input table paths
    - keyColumnIndexes: array (required) - key column index per input table, each must be >= 0
    - outputPath: string (required) - merged output path
    - separator: string (optional, default tab) - string (optional, default tab)
    - defaultNAvalue: string (optional, default empty) - string (optional, default empty)
    - appendMergedKey: boolean (optional, default true) - boolean (optional, default true)
    - rmKeyColumns: boolean (optional, default true) - boolean (optional, default true)
    - appendOnly: boolean (optional, default false) - boolean (optional, default false)
    - containHeader: boolean (optional, default false) - boolean (optional, default false)
  -> returns: ok (boolean), outputPath (string), message (string)

### TableTools.selectColumnsByList
  summary: Select table columns by ID/pattern list matched on header.
    - inputPath: string (required) - input table path
    - idListPath: string (required) - ID/pattern list file path
    - outputPath: string (required) - output table path
    - selectionMode: string (optional, default Match, Match|Contain) - Match|Contain
    - caseSensitive: boolean (optional, default false) - boolean (optional, default false)
    - sortByIdList: boolean (optional, default true) - boolean (optional, default true)
    - separator: string (optional, default tab) - string (optional, default tab)
  -> returns: ok (boolean), outputPath (string), message (string)

### TableTools.selectColumnsByRegexList
  summary: Select table columns by regex list matched on header.
    - inputPath: string (required) - input table path
    - regexListPath: string (required) - regex list file path, one regex per line
    - outputPath: string (required) - output table path
    - selectionMode: string (optional, default Match, Match|Contain) - Match|Contain
    - caseSensitive: boolean (optional, default false) - boolean (optional, default false)
    - sortByInputList: boolean (optional, default true) - boolean (optional, default true)
    - separator: string (optional, default tab) - string (optional, default tab)
  -> returns: ok (boolean), outputPath (string), message (string)

### TableTools.selectRows
  summary: Extract or filter rows by target column and ID list.
    - inputPath: string (required) - input table path
    - idListPath: string (required) - ID/pattern list file path
    - outputPath: string (required) - output table path
    - selectedColumn: string (required) - header name; if containHeader=false then must be zero-based integer >= 0
    - conditionMode: string (optional, default match, match|contain|equal|bigger|smaller) - match|contain|equal|bigger|smaller
    - selectedMode: string (optional, default extract, extract|filter) - extract|filter
    - separator: string (optional, default tab) - string (optional, default tab)
    - containHeader: boolean (optional, default true) - boolean (optional, default true)
    - caseSensitive: boolean (optional, default true) - boolean (optional, default true)
    - sortByIdList: boolean (optional, default true) - boolean (optional, default true)
    - regex: boolean (optional, default false) - boolean (optional, default false)
    - commentString: string (optional, default #) - string (optional, default #)
  -> returns: ok (boolean), outputPath (string), message (string)

### TableTools.selectRowsByNumericRange
  summary: Select rows where numeric value is within [minValue, maxValue].
    - inputPath: string (required) - input table path
    - outputPath: string (required) - output table path
    - selectedColumn: string (required) - header name or index when containHeader=false
    - minValue: number (required) - minimum numeric threshold
    - maxValue: number (required) - maximum numeric threshold
    - containHeader: boolean (optional, default true) - boolean (optional, default true)
    - separator: string (optional, default tab) - string (optional, default tab)
    - commentString: string (optional, default #) - string (optional, default #)
  -> returns: ok (boolean), outputPath (string), message (string)

### TableTools.sortByColumns
  summary: Sort table rows by multiple columns.
    - inputPath: string (required) - input table path
    - outputPath: string (required) - output table path
    - sortColumns: array (required) - zero-based sort column indexes
    - sortOrders: array (optional) - asc|desc for each sort column
    - numeric: boolean (optional, default false) - boolean (optional, default false)
    - containHeader: boolean (optional, default true) - boolean (optional, default true)
    - separator: string (optional, default tab) - string (optional, default tab)
  -> returns: ok (boolean), outputPath (string), message (string)

### TableTools.splitByColumn
  summary: Split one table into multiple files by one column value.
    - inputPath: string (required) - input table path
    - outputDir: string (required) - output directory path
    - columnIndex: int (required) - split column index, must be >= 0
    - suffix: string (optional, default .split) - string (optional, default .split)
  -> returns: ok (boolean), outputPath (string), outputDir (string), message (string)

### TableTools.transpose
  summary: Transpose a table file.
    - inputPath: string (required) - input table path
    - outputPath: string (required) - output table path
    - inputSeparator: string (optional, default tab) - string (optional, default tab)
    - outputSeparator: string (optional, default tab) - string (optional, default tab)
  -> returns: ok (boolean), outputPath (string), message (string)

### TableTools.uniq
  summary: Count unique values in one table column.
    - inputPath: string (required) - input table path
    - outputPath: string (required) - output path
    - columnIndex: int (required) - zero-based column index, must be >= 0
    - sortByFreq: boolean (optional, default true) - boolean (optional, default true)
    - showCounts: boolean (optional, default true) - boolean (optional, default true)
    - containHeader: boolean (optional, default false) - boolean (optional, default false)
    - separator: string (optional, default tab) - string (optional, default tab)
    - commentString: string (optional, default #) - string (optional, default #)
  -> returns: ok (boolean), outputPath (string), message (string)

### TodoList.addTask
  summary: Create a todo task.
    - title: string (required) - task title
    - memo: string (optional) - task memo
    - priority: int (optional, default 0) - int (optional, default 0)
    - dueDateEpochMillis: long (optional) - long (optional)
    - tags: array (optional) - array of string (optional)
    - columnId: string (optional, default TODO) - string (optional, default TODO)
  -> returns: id (string), title (string), columnId (string), priority (integer), createdAtEpochMillis (long), updatedAtEpochMillis (long)

### TodoList.deleteTask
  summary: Delete one Todo task by id.
    - id: string (required) - task id
  -> returns: ok (boolean), id (string), deleted (boolean)

### TodoList.listTasks
  summary: List all todo tasks.
    (no params)
  -> returns: tasks (array - list of task objects)

### TodoList.moveTask
  summary: Move task to another status/column.
    - id: string (required) - task id
    - columnId: string (required) - target column/status
  -> returns: ok (boolean), id (string), columnId (string)

### TodoList.updateTask
  summary: Update an existing task fields by id.
    - id: string (required) - task id
    - title: string (optional) - string (optional)
    - memo: string (optional) - string (optional)
    - priority: int (optional) - int (optional)
    - dueDateEpochMillis: long (optional) - long (optional)
    - tags: array (optional) - array of string (optional)
    - columnId: string (optional) - string (optional)
  -> returns: id (string), title (string), columnId (string), updatedAtEpochMillis (long)

### TrimMsaGblocks.process
  summary: Trim MSA using Gblocks-style algorithm.
    - inputPath: string (required) - input MSA FASTA path
    - outputPath: string (required) - output MSA FASTA path
    - infoOutputPath: string (optional) - trim info output
    - IS: number (optional, default 0.5) - number (optional, default 0.5)
    - FS: number (optional, default 0.85) - number (optional, default 0.85)
    - CP: int (optional, default 8) - int (optional, default 8)
    - BL1: int (optional, default 10) - int (optional, default 10)
    - BL2: int (optional, default 10) - int (optional, default 10)
    - nonGapRatio: number (optional, default 1.0) - number (optional, default 1.0)
    - gapTreatment: string (optional, default NONE, NONE|HALF|ALL) - string (optional, NONE|HALF|ALL, default NONE)
  -> returns: ok (boolean), outputPath (string), gapTreatment (string), message (string)

### TrimMsaGblocks.validateParams
  summary: Validate TrimMsaGblocks params without trimming.
    - inputPath: string (required) - input MSA FASTA path
    - outputPath: string (required) - output MSA FASTA path
    - IS: number (optional, default 0.5) - number (optional, default 0.5)
    - FS: number (optional, default 0.85) - number (optional, default 0.85)
    - CP: int (optional, default 8) - int (optional, default 8)
    - BL1: int (optional, default 10) - int (optional, default 10)
    - BL2: int (optional, default 10) - int (optional, default 10)
    - nonGapRatio: number (optional, default 1.0) - number (optional, default 1.0)
    - gapTreatment: string (optional, default NONE, NONE|HALF|ALL) - string (optional, NONE|HALF|ALL, default NONE)
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPath (string), gapTreatment (string), message (string)

### TrimMsaSimple.process
  summary: Trim MSA columns by non-gap ratio threshold.
    - inputPath: string (required) - input MSA FASTA path
    - outputPath: string (required) - output MSA FASTA path
    - ratio: number (optional, default 0.95) - keep site threshold
  -> returns: ok (boolean), outputPath (string), ratio (number), message (string)

### TrimMsaSimple.validateParams
  summary: Validate TrimMsaSimple params without trimming.
    - inputPath: string (required) - input MSA FASTA path
    - outputPath: string (required) - output MSA FASTA path
    - ratio: number (optional, default 0.95) - number (optional, default 0.95, must be in (0,1])
  -> returns: ok (boolean), validated (boolean), inputPath (string), outputPath (string), ratio (number), message (string)

### VcfAddId.process
  summary: Fill VCF column 3 (ID) with CHROM_POS for each variant line; supports .gz in/out.
    - inputPath: string (required) - input VCF or .vcf.gz
    - outputPath: string (required) - output VCF or .vcf.gz
  -> returns: ok (boolean), outputPath (string), message (string), variantLineCount (integer)

### VcfAddId.validateParams
  summary: Validate VcfAddId.process paths and count variant lines in input (non-# lines).
    - inputPath: string (required) - input VCF path
    - outputPath: string (required) - output VCF path
  -> returns: ok (boolean), validated (boolean), message (string), inputPath (string), outputPath (string), variantLineCount (integer)

## 08/29 实测状态（子任务 D，真实基因家族数据）

| 方法 | 状态 | 说明 |
|:-----|:-----|:-----|
| FastaStat.process | ✅ | 序列统计；getLengthOnly 模式可用 |
| FastaExtract.process | ✅ | 按 ID 提取 + Filter 反向模式 |
| CdsToProtein.process | ✅ | CDS→蛋白翻译（6 条验证）|
| FastaSsrMiner.process | ✅ | SSR 搜索；⚠️ ssrPattern 参数关键，默认(1-10;2-6;3-5;4-5;5-5;6-5)对短 CDS 常 0 命中，敏感模式(2-4;3-3;4-3;5-3;6-3)可找到 |
| BatchStringReplace.process | ✅ | 批量替换（tab 分隔映射文件）|
| TableTools.melt | ✅ | 宽表转长表 |
| TableTools.transpose | ✅ | 转置 |
| TableTools.selectRows | ✅ | 按值筛选 |
| TableTools.sortByColumns | ⚠️ RPC bug | 数组参数被 JSON 强转 float([1]→[1.0]) 报错——RPC 层类型转换 bug |
| TableTools.mergeByKey* | ⚠️ 待测 | 标量 int 可能可用 |
| FastaRepeatStater / Sequence2Feature / GCContentStater / RemoveRedundantSeq / Enrichment | ❌ 未暴露 | RPC 无此方法（非 RPC 覆盖）|
