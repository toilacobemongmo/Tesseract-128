README - TESSERACT-128 SUBMISSION GUIDE
=======================================

Manuscript Title:
  Tesseract-128: A 128-Bit Symmetric Block Cipher Integrating 4D Hypercube
  Permutations and ARX Diffusion for Constrained Telemetry Networks

Author:
  Hao Gia Nguyen
  Faculty of Information Security, Posts and Telecommunications Institute
  of Technology (PTIT), Hanoi, Vietnam
  Corresponding email: haong.b24at088@stu.ptit.edu.vn

--------------------------------------------------------------------------------
1. PACKAGE CONTENTS
--------------------------------------------------------------------------------
  manuscript_submission.pdf          Full manuscript (elsarticle, review mode)
  manuscript_submission.tex          LaTeX source
  tesseract128_text_only.txt         Plain-text extract of the manuscript (for text-matching checks)
  trail_weight_experiment_log.txt    Raw output of the Section 8.5 trail-weight experiment
                                     (MILP vs brute-force cross-check; evidence for the reported
                                     negative/failed-method result)
  Cover_Letter.docx                  Cover letter (Word, for portal upload)
  Cover_Letter.txt                   Cover letter (plain text)
  Highlights.txt                     Four highlight bullets (<= 85 characters each)
  Declaration_of_Competing_Interests.txt
  CRediT_Author_Statement.txt
  README_SUBMISSION_GUIDE.txt        This file
  fig_tesseract_4d.png               Figure 1 - 4D hypercube state mapping
  fig_tesseract_architecture.png     Figure 2 - Architectural overview
  fig_key_schedule.png               Figure 3 - Key schedule
  fig_avalanche_diffusion.png        Figure 4 - SAC / MILP active S-box plot
  fig_benchmark_charts.png           Figure 5 - Benchmark charts
  fig_related_key_desync.png         Figure 6 - Related-key desynchronization
  Lena_cryptanalysis_result.png      Figure 7 - Encryption/decryption test image
  Baboon_cryptanalysis_result.png    Figure 8 - Encryption/decryption test image

--------------------------------------------------------------------------------
2. CONSISTENCY NOTE (IMPORTANT)
--------------------------------------------------------------------------------
All documents report a SINGLE, UNIFIED set of security figures. Do not
reintroduce the older word-level values anywhere in the package.

  Differential (8 rounds) : >= 78 active S-boxes, P_diff <= 2^-468
  Linear     (8 rounds)   : >= 108 active S-boxes
  Related-key (bidirect.) : P_RK <= 2^-576
  Impossible differential : zero trails at >= 5 rounds (4-round margin)
  Table footprint         : 192 bytes
  Byte diffusion (linear layer) : 16 (computed, see tools/compute_branch_number.py)
  AES wide-trail branch number  : 5  (re-derived by brute force in the same script)

  Deprecated values (must NOT appear): 22 active S-boxes / 2^-132 / 2^-240.
  These originated from an early word-level XOR-abstraction MILP model that
  underestimated active S-boxes; they were superseded by the exact bit-level
  ARX-carry model (pulp/rubik_differential.py).

  Model-relative wording (must be preserved): all MILP figures are described as
  "lower bounds within the stated model", never as proofs or guarantees, and the
  comparison table (tab:branch_number) separates the AES wide-trail branch
  number (5, F_2^8 metric) from the Tesseract byte-diffusion number (16, value
  metric) because the two live in different algebraic domains.

  SO(4) ablation (tab:layer_ablation, Section 8.3): a controlled experiment
  replacing the SO(4) permutation with the identity and with 5 random byte
  permutations. All 7 configurations reach full bit diffusion at round 3, so
  the ARX ripple - not the SO(4) geometry - carries the diffusion. This is
  reported as a deliberate negative result; do not reintroduce any claim that
  SO(4) improves mixing. Script: tools/measure_layer_value.py.

  SO(4) invariant trade-off (tab:group_invariants, Section 8.4): direct
  enumeration of the 12 SO(4) tables vs 240 random byte permutations. Two
  reportable facts, BOTH of which must be kept:
    * the SO(4) table set has ZERO fixed points (every table moves all 16
      bytes; 0 of 192 element-slots); every random 12-element set had 7-19.
      This is the one structural property SO(4) excludes by construction.
    * 4 of the 12 SO(4) tables (indices 0,1,10,11) preserve a 32-bit word
      plane; 0 of 240 random elements did. This is a WEAKNESS of the
      geometric layer, masked by the ARX ripple. Do not present SO(4) as
      uniformly safer than a random permutation - the honest framing is a
      trade, not a win. Script: tools/measure_so4_invariants.py.

  Trail-weight experiment - a reported FAILED METHOD (tab:trail_weight,
  Table 18, Section 8.5): the last attempt to separate SO(4) on the true
  attack metric (minimum differential trail weight). Two independent models
  were cross-checked and DISAGREE by a factor of 18x-60x:
    * a bit-level linear relaxation (reusing the published milp_differential
      carry constraints) reports 1 cumulative active bit for one round;
    * exhaustive enumeration on REAL byte values (the exact rubik4d.c round)
      reports 60 active bits. The relaxation therefore picks carry-absorption
      configurations no real byte value realises - the same failure mode the
      branch-number tool documents (returned 3 where the truth is 16).
  Ground truth: SO(4) 60/107/168 vs identity 60/110/168 vs random 60/118/175
  over 1/2/3 rounds - within 1.5%, i.e. below the noise floor. CONCLUSION:
  the bit-level MILP is UNUSABLE for ARX trail weight without carry-DDT /
  Matsui bit-masking, and the ground truth shows no SO(4) advantage. Report
  this as a failed method plus its honest substitute; do NOT quote the MILP
  numbers (37/52/61 etc.) as trail weights - they are under-counts.
  Script: tools/compare_arx_milp_trail_weight.py.

--------------------------------------------------------------------------------
3. CODE AND DATA AVAILABILITY
--------------------------------------------------------------------------------
  https://github.com/toilacobemongmo/Tesseract-128

  All scalar C, SSSE3/AVX2 intrinsics, MILP solvers (PuLP/CBC), integral and
  impossible-differential search scripts, and testbenches are provided.

--------------------------------------------------------------------------------
4. BUILDING THE MANUSCRIPT
--------------------------------------------------------------------------------
  From the repository root:

    powershell -ExecutionPolicy Bypass -File paper/build_paper.ps1

  Or manually, from paper/build/ (where the .tex is generated):

    pdflatex manuscript_submission.tex
    pdflatex manuscript_submission.tex     (run twice for cross-references)

--------------------------------------------------------------------------------
5. TARGET JOURNAL
--------------------------------------------------------------------------------
  JOURNAL-NEUTRAL BY DEFAULT. The source is prepared for a general-purpose
  information-security / applied-cryptography venue. \journal{} is intentionally
  left EMPTY so the same source can be submitted unchanged to any of:

    * Journal of Information Security and Applications (Elsevier)
    * IEEE Access
    * Computers & Security (Elsevier)
    * Cryptography (MDPI)
    * Applied Sciences (MDPI)

  To target a specific journal, edit the \journal{...} line near the top of
  paper/create_paper.py (currently \journal{} in the preamble string), fill in
  the venue name, rebuild with paper/build_paper.ps1, and the regenerated
  .tex/.pdf land in paper/submission/ automatically.
  The Cover_Letter.txt / Cover_Letter.docx carry a matching bracketed placeholder
  line ("[Target journal to be filled in at submission time...]") that must be
  edited to name the venue before sending; CRediT and Declaration files carry the
  same "Journal:" placeholder. No other file hard-codes a journal name.
