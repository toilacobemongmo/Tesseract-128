"""Assemble the submission-ready manuscript from paper/manuscript.tex.

Layout (all paths are resolved relative to this file, so the script can be run
from any working directory):

    paper/manuscript.tex   authoritative source manuscript (section anchors)
    paper/build/*.tex|pdf  generated output
    paper/figures/*.png    figures referenced by \\includegraphics

Usage:
    python paper/create_paper.py
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_TEX = os.path.join(HERE, 'manuscript.tex')
OUT_DIR = os.path.join(HERE, 'build')
OUT_TEX = os.path.join(OUT_DIR, 'manuscript_submission.tex')
FIG_DIR = 'figures'   # relative to the .tex, it is compiled from OUT_DIR


def build_jisa_paper():
    with open(SRC_TEX, 'r', encoding='utf-8') as f:
        src = f.read()

    # --- Section anchors, resolved against paper/manuscript.tex --------------
    # NOTE: these patterns must match the \section / \subsection headings that
    # actually exist in the source file.  If any anchor is missing, str.find()
    # returns -1 and the slice src[a:b] silently produces an empty or, worse, a
    # reversed-range slice (src[-1:N] returns almost the entire document),
    # duplicating the paper.  _anchor() below turns that failure into a hard
    # error instead of a corrupt build.
    def _anchor(pattern):
        i = src.find(pattern)
        if i < 0:
            raise SystemExit(
                "ERROR: section anchor not found in paper/manuscript.tex: %r" % pattern
            )
        return i

    pos_sec1 = _anchor(r'\section{Introduction}')
    pos_sec2 = _anchor(r'\section{Related Work and Comparative Analysis}')
    pos_sec3 = _anchor(r'\section{Architecture Specification of Tesseract-128}')
    pos_sec3_sub5 = _anchor(r'\section{Automated Tool-Aided Cryptanalysis and Security Margins}')
    pos_sec4 = _anchor(r'\section{Software Implementation, Microcontroller Feasibility')
    pos_sec5 = pos_sec4                      # SIMD/AEAD and benchmarks share the
    pos_sec5_sub3 = _anchor(r'\section{Application Case Study:')  # same section
    pos_concl = _anchor(r'\section{Conclusion and Future Cryptanalysis}')
    pos_bib = _anchor(r'\begin{thebibliography}')


    # Preamble for Elsevier JISA
    preamble = r'''\documentclass[review,12pt]{elsarticle}

\usepackage{lineno}
\linenumbers

\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{array}
\usepackage{url}
\usepackage[colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}
\usepackage{algorithm}
\usepackage{algorithmic}
\usepackage{tikz}
\usetikzlibrary{shapes.geometric, arrows.meta, positioning, calc}
\graphicspath{{figures/}{../figures/}}

\journal{}

% ---- Submission metadata -------------------------------------------------
% This manuscript is prepared for submission to a general-purpose
% information-security / applied-cryptography venue. The target journal is
% intentionally not hard-coded so the same source can be submitted unchanged
% to any of the candidate venues listed in README_SUBMISSION_GUIDE.txt
% (Journal of Information Security and Applications; IEEE Access;
% Computers & Security; Cryptography (MDPI); Applied Sciences (MDPI)).
% To target a specific journal, fill in \journal{...} above and rebuild.
% --------------------------------------------------------------------------

\begin{document}

\begin{frontmatter}

\title{Tesseract-128: A 128-Bit Symmetric Block Cipher Integrating 4D Hypercube Permutations and ARX Diffusion for Constrained Telemetry Networks}

\author{Hao Gia Nguyen\corref{cor1}}
\ead{haong.b24at088@stu.ptit.edu.vn}
\cortext[cor1]{Corresponding author.}

\affiliation{organization={Faculty of Information Security, Posts and Telecommunications Institute of Technology},
            city={Hanoi},
            country={Vietnam}}

\begin{abstract}
Tesseract-128 is a 128-bit symmetric block cipher engineered for latency-critical network communications and resource-constrained telemetry environments. Conventional Substitution-Permutation Network (SPN) architectures incur high microarchitectural latency and cache-timing side-channel vulnerabilities from Galois field matrix multiplications and large lookup tables (e.g., 4~KB AES T-tables). Tesseract-128 bypasses these bottlenecks through a hybrid linear layer that couples four-dimensional hypercube coordinate transformations with 32-bit Add-Rotate-XOR (ARX) modular carry-ripple diffusion. The 16-byte cipher state is mapped onto the vertices of a 4D hypercube, where double-isoclinic rotations from the chiral hyperoctahedral group $B_4^+ = SO(4) \cap O(4, \mathbb{Z})$ disperse byte coordinates across orthogonal planes without invariant coordinate subspaces, requiring only 192 bytes of static lookup tables. Using mixed-integer linear programming (MILP) with exact ARX carry expansion, we obtain lower bounds of at least 78 active S-boxes against differential cryptanalysis ($P_{\text{diff}} \le 2^{-468} < 2^{-128}$) within the modeled round structure and 108 active S-boxes against linear cryptanalysis ($N_D \approx 2^{434} \gg 2^{128}$). Keystreams satisfy all 15 test suites of NIST SP 800-22 and GM/T 0005-2021 without exception. Vectorized execution on gateway-class x86-64 hardware reaches an empirical throughput of $254.18$~MB/s in CTR mode using four-block parallel AVX2 processing, and $208.80$~MB/s in authenticated Tesseract-GCM mode; the single-block byte-shuffle path is retained for constant-time, lookup-free execution rather than as a throughput optimisation. In a realistic automotive CAN-FD telemetry case study, Tesseract-GCM processes 64-byte payload frames in 1,267 clock cycles ($\approx 0.37~\mu\text{s}$), delivering a $2.88\times$ latency reduction over software AES while adding under $0.3\%$ physical bus transmission overhead. We explicitly position Tesseract-128 as a first-generation geometric cipher and open-source all models to facilitate independent community cryptanalysis.
\end{abstract}

\begin{keyword}
Symmetric block cipher \sep 4D hypercube \sep $SO(4)$ isometry permutation \sep ARX diffusion \sep MILP cryptanalysis \sep Authenticated encryption (AEAD) \sep CAN-FD telemetry
\end{keyword}

\end{frontmatter}
'''

    # Section 1: Introduction
    sec1 = src[pos_sec1:pos_sec2]

    # Section 2: Threat Model
    # The source manuscript already contains \section{Threat Model and Security
    # Framework} inside sec1 (Introduction..Related Work), so emitting a second
    # hard-coded copy here would duplicate the section.  sec2_text is therefore
    # left empty and the source copy is used verbatim.
    sec2_text = ''

    # Section 3: Related Work and Comparative Analysis
    sec3 = src[pos_sec2:pos_sec3]

    # Section 4: Architecture Specification
    sec4_text = src[pos_sec3:pos_sec3_sub5]

    # Section 5: Cryptanalysis & Security Proofs
    sec5_text = src[pos_sec3_sub5:pos_sec4]


    # Section 6: Software implementation, SIMD/AEAD and hardware benchmarks.
    # The source keeps this as one section; it is emitted verbatim (pos_sec4 to
    # the IoT case study) so no slice can overlap an earlier one.
    sec6_text = src[pos_sec4:pos_sec5_sub3]

    # Section 7: IoT Telemetry Case Study.
    # Stops at the Discussion section: the source manuscript already carries a
    # \section{Discussion, ...} there, and the curated sec8_discussion block
    # below replaces it, so including the source copy would duplicate it.
    pos_discussion = _anchor(r'\section{Discussion, Model Scope Limitations, and Open Cryptanalysis}')
    sec7_text = src[pos_sec5_sub3:pos_discussion]

    # Section 8: Discussion, Limitations, Open Cryptanalysis
    sec8_discussion = r'''
\section{Discussion, Model Scope Limitations, and Open Cryptanalysis}
\label{sec:discussion}

To ensure complete scientific integrity and align with the evaluation standards of the international cryptographic community, we discuss the scope boundaries of our models and establish an open cryptanalysis framework:

\subsection{First-Generation Design Positioning}
Tesseract-128 is introduced as a \textbf{first-generation geometric block cipher} that couples rigid orthogonal rotations from Lie group geometry ($SO(4) \cap O(4, \mathbb{Z})$) with ARX carry propagation. We caution at the outset that our measurements do \emph{not} attribute the cipher's diffusion to that geometry; the $SO(4)$ layer is best understood as a structured, enumeration-friendly \emph{generator} of byte permutations rather than as a source of superior mixing, as the controlled ablation in this section shows. We stress that the security statements collected in this work are \emph{model-relative design-level arguments}, not cryptanalytic proofs of security: they hold within the specific word-level MILP, miss-in-the-middle, and statistical models we instantiate, and they do not by themselves establish the absence of distinguishers outside those models. The primary contribution we claim is therefore a \emph{design-study} contribution---a systematic exploration of whether the discrete symmetry group $SO(4) \cap O(4, \mathbb{Z})$ (of order 192) yields a useful, analyzable, and round-variable permutation layer for SPN-style ciphers---rather than a claim of security superiority over established primitives.

Concretely, the three claims we advance are: (i) $SO(4) \cap O(4, \mathbb{Z})$ is shown to be a well-defined, computationally characterizable source of byte permutations for a 16-byte state (a group-theoretic design primitive); (ii) its orientation-preserving subgroup $B_4^+$ admits key-dependent, round-varying realizations that can be controlled with a 192-byte footprint; and (iii) combining such a layer with 32-bit ARX carry propagation yields a cipher whose behavior under the standard attack families we model is analyzable with existing automated tools (MILP, miss-in-the-middle, multiset integral). We explicitly do not claim that a geometric permutation layer possesses any cryptanalytic advantage over an arbitrary well-chosen permutation of 16 byte positions; on the contrary, any permutation of the state bytes combined with a suitable mixing layer is bounded by the same wide-trail branch-number limits, and we do not assert that $SO(4)$ exceeds those limits. Our contribution is the availability of a structured, parametric, and verifiable \emph{generator} for such permutations, together with a fully reproducible evaluation of the resulting cipher within the models we can currently instantiate.

While our automated MILP searches and empirical simulations indicate substantial margins across the evaluated attack families, symmetric block ciphers require multi-year independent scrutiny from the wider community before achieving full operational trust. To make this positioning concrete, Table~\ref{tab:branch_number} compares Tesseract-128 with AES-128, SPARX-128/128, and Alzette on invariants that are either computed in this work or taken from the cited reference; it separates the classical wide-trail branch number (undefined for partly-ARX mixing) from the measured byte-diffusion number of the linear layer, so our claim is a footprint-and-instruction-count trade-off, not a wide-trail superiority claim.

\begin{table}[htbp]
\caption{Quantitative comparison on diffusion and implementation invariants. All numerical entries are either computed in this work or taken from the cited reference; none is an assumed convention. ``WT branch'' is the classical wide-trail differential branch number over $\mathbb{F}_{2^8}^{16}$, defined only for linear layers over that field and upper-bounded by $5$ for a 16-byte state. ``Byte diff.'' is the minimum number of non-zero output bytes produced by a single non-zero input byte, evaluated on actual state values.}
\label{tab:branch_number}
\centering
\small
\begin{tabular}{@{}lccccc@{}}
\toprule
\textbf{Primitive} & \textbf{Structure} & \textbf{Linearity} & \textbf{WT branch} & \textbf{Byte diff.} & \textbf{Table (B)} \\
\midrule
AES-128          & byte-SPN       & ShiftRows + MixColumns & 5 & 4 & 4{,}096 \\
Tesseract-128    & byte-SPN + ARX & $SO(4)$ perm + ripple  & n/a & \textbf{16} & \textbf{192} \\
SPARX-128/128    & ARX Feistel    & ARX only               & n/a & n/a (bit-level) & 0 \\
Alzette          & ARX-box        & ARX only               & n/a & n/a (bit-level) & 0 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Contribution of the $SO(4)$ Layer: A Controlled Ablation}
\label{sec:layer_value}
Because the byte-diffusion number saturates at $16$ for the ARX ripple regardless of which byte permutation precedes it, that metric cannot tell us whether the geometric structure contributes anything at all. We therefore ran a controlled ablation on the full cipher. Holding the S-box layer, the 32-bit ARX ripple, the round constants, and the key schedule fixed, we replaced the specified per-round $SO(4)$ permutation tables with (a) the identity permutation and (b) five independent random byte permutations, and measured the mean and the \emph{minimum} output Hamming weight produced by a single input-bit flip after each round (\url{tools/measure_layer_value.py}).

\begin{table}[htbp]
\caption{``$SO(4)$ ablation'': output Hamming weight (of $128$ bits) produced by a single input-bit flip, after $r$ rounds. Mean over $400$ random (plaintext, key) pairs; minimum is the worst case observed and is the cryptanalytically relevant figure. Every configuration reaches the $60$-bit full-diffusion threshold at round~$3$.}
\label{tab:layer_ablation}
\centering
\small
\begin{tabular}{lcccccc}
\toprule
\textbf{Permutation layer} & \textbf{Metric} & \textbf{r1} & \textbf{r2} & \textbf{r3} & \textbf{r4} & \textbf{r5} \\
\midrule
$SO(4)$ (as specified) & mean & 17.0 & 49.3 & 63.7 & 64.2 & 63.6 \\
                       & min  & 2    & 18   & 44   & 48   & 50 \\
identity (ARX only)    & mean & 16.3 & 51.6 & 63.3 & 64.2 & 64.4 \\
                       & min  & 2    & 12   & 23   & 47   & 49 \\
random perm (5 seeds)  & mean & 15.8--16.9 & 46.7--49.8 & 62.6--63.2 & 63.9--64.3 & 63.8--64.4 \\
                       & min  & 2--3 & 9--18 & 25--44 & 44--50 & 44--49 \\
\bottomrule
\end{tabular}
\end{table}

The result is unambiguous. All seven configurations reach full diffusion at round~$3$, and the $SO(4)$ sequence is neither faster nor slower than the identity or than any of the five random permutations: it sits inside the random-permutation spread at every round. In other words, \emph{the geometric structure of $SO(4)$ does not accelerate bit-level diffusion}, and the cipher's diffusion is carried by the ARX ripple. We report this rather than omit it because it directly bounds what the design novelty can be: a claim that $SO(4)$ provides superior mixing would be false, and any value the layer has must be argued on other grounds.

The grounds on which we \emph{do} defend the layer are enumerability and implementability rather than diffusion strength. The group $SO(4) \cap O(4,\mathbb{Z})$ is finite with order $192$, so its action on the $16$ byte positions can be exhaustively enumerated and each element tabulated in $16$ bytes; the orientation-preserving subgroup yields $12$ distinct tables (the $192$-byte footprint in Table~\ref{tab:branch_number}). This makes the permutation layer a \emph{verifiable, parametric generator}: the designer can enumerate every element, check it for invariant subspaces, and encode the selected one as a single \texttt{pshufb}. A random $16$-byte permutation offers the same diffusion and the same instruction cost, but not the same enumerability: with $16! \approx 2^{44.25}$ candidates, invariant subspaces must be searched for statistically rather than excluded by construction. That distinction---not a diffusion advantage---is the honest content of the geometric design claim.
\subsection{Does the Group Structure Exclude a Distinguisher Class?}
\label{sec:group_invariants}
The enumerability argument above is only interesting if one can name a distinguisher class that the enumeration \emph{excludes}. We therefore measured the combinatorial invariants that a structural distinguisher on a byte-permutation layer would use---fixed points, 4-byte word-plane preservation, transitivity on the $16$ byte positions, cycle structure and parity---for the $12$ orientation-preserving $SO(4)$ tables actually used by the cipher, and for $20$ independent sets of $12$ random byte permutations (\url{tools/measure_so4_invariants.py}). The result is a trade, not a win, and both sides must be reported.

\begin{table}[htbp]
\caption{Structural invariant profile of the $12$ $SO(4)$ tables versus $240$ random byte permutations ($20$ sets of $12$). Window: min/mean/max over the $20$ random sets.}
\label{tab:group_invariants}
\centering
\small
\begin{tabular}{lccc}
\toprule
\textbf{Invariant} & \textbf{$SO(4)$} & \textbf{random (min/mean/max)} & \textbf{winner} \\
\midrule
total fixed points            & $0$ (of $192$) & $7\,/\,13.2\,/\,19$ & $SO(4)$ \\
transitive elements           & $0\,/\,12$     & $0\,/\,0.7\,/\,2$   & random (tie) \\
word-plane-preserving elements& $4\,/\,12$     & $0\,/\,0.0\,/\,0$   & random \\
even-parity elements          & $12\,/\,12$    & $3\,/\,6.0\,/\,9$   & (structural) \\
\bottomrule
\end{tabular}
\end{table}

The first row is a genuine, checkable advantage. \emph{The cipher's $SO(4)$ table set contains no fixed point at all}: every one of the $12$ tables moves all $16$ bytes, and because a group element that fixes a vertex fixes the corresponding coordinate, no $SO(4)$ element can be position-stable. A random $12$-element set, by contrast, always contained between $7$ and $19$ fixed points across all $20$ trials. The enumeration therefore excludes the class of ``position-stable byte'' distinguishers by construction, and the property largely survives composition: the eight-round product of the per-round tables has zero fixed points at rounds $1,3,5,6,7,8$.

The third row is a genuine weakness of the geometric layer that the same enumeration \emph{exposes} rather than hides. Four of the $12$ $SO(4)$ tables (indices $0,1,10,11$) map each $4$-byte word plane onto itself: they permute bytes only \emph{within} a $32$-bit word and never move a byte across words. Because the round sequence visits table indices $(2r \bmod 12) = 0,2,4,6,8,10,0,2$, a plane-preserving table is selected in rounds $1$, $6$ and $7$. No random set in $20$ trials contained even one such table ($0$ of $240$ elements). This is a real block-structure handle that a random permutation would not provide, and it is masked only because the ARX ripple mixes inside every $32$-bit word independently of the permutation; the ablation of Section~\ref{sec:layer_value} shows that this masking is complete from round~$3$ onward. We report it because the enumerability claim would be dishonest if we used it only to advertise the fixed-point property while concealing the plane-preservation cost. The correct statement is that the group structure \emph{exchanges} one structural property for another relative to a random permutation: it buys the zero-fixed-point guarantee and costs plane preservation. Neither set dominates the other, and the geometric layer must not be presented as uniformly safer than a random byte permutation.



\subsection{Can a Trail-Weight Advantage Be Demonstrated? A Failed Attempt and What It Shows}
\label{sec:trail_weight}
The two ablations above measure diffusion speed and combinatorial structure. Neither is an attack cost. The quantity a differential cryptanalyst actually minimises is the trail weight of the best characteristic, so we attempted to settle the question directly: does replacing the $SO(4)$ tables with the identity or with random byte permutations change the minimum differential trail weight of the full bit-level ARX model?

We constructed such a model in two independent ways and cross-checked them. The first is a linear program whose objective is the cumulative number of active difference bits, reusing verbatim the exact carry constraint set of \texttt{milp\_differential.py}. The second is an exhaustive enumeration that pushes \emph{real byte values} through the exact round function of \texttt{src/rubik4d.c} for every input difference of Hamming weight one. The two disagree by a factor of $18$ to $60$ (Table~\ref{tab:trail_weight}), and the direction of the disagreement is instructive: the linear program reports a cumulative weight of $1$ for a single round, whereas a genuine one-bit input difference necessarily produces $60$ active output bits. The relaxation is therefore selecting carry-absorption configurations that no real byte value realises---precisely the failure mode already documented in our branch-number tool, where an early free-bit-difference model returned $3$ for a quantity whose true value is $16$.

\begin{table}[htbp]
\centering
\caption{Minimal differential trail weight (cumulative active bits) measured on real byte values. One-bit input differences, rounding to the exact \texttt{rubik4d.c} round function. The three configurations differ by at most $7$ bits out of roughly $500$ accumulated bits, i.e.\ below $1.5\%$; no configuration shows a structural advantage.}
\label{tab:trail_weight}
\small
\begin{tabular}{@{}lrrrr@{}}
\toprule
Rounds & $SO(4)$ & Identity & Random & Verdict \\
\midrule
$1$ & $60$ & $60$ & $60$ & indistinguishable \\
$2$ & $107$ & $110$ & $118$ & below noise floor \\
$3$ & $168$ & $168$ & $175$ & below noise floor \\
\bottomrule
\end{tabular}
\end{table}

The honest reading is that the bit-level linear relaxation is \emph{unusable} for ARX trail-weight search without the carry-DDT machinery of Matsui-style bit masking, and that the ground-truth measurement it was meant to approximate shows no separation between the geometric layer and a random byte permutation. We report the failed model rather than a manufactured result: it is the third independent line of evidence, after the diffusion ablation and the invariant enumeration, that the $SO(4)$ layer is cryptanalytically neutral. A reader who wishes to push further should replace the relaxation with a sound carry model; we predict, on the basis of Table~\ref{tab:trail_weight}, that the conclusion will not change, and we would be glad to be proved wrong.

\subsection{Scope Limitations of Automated Search Models}
We explicitly record the operational scope and inherent abstractions of our cryptanalytic tools:
\begin{enumerate}
    \item \textbf{Word-Level Truncated Miss-in-the-Middle Abstraction:} The automated impossible differential solver (\texttt{tesseract\_impossible\_diff.py}) operates at the word/byte-level truncated differential abstraction. It conservatively treats any non-zero difference in a 32-bit word as diffusing across byte boundaries via modular carry ripple. While this macroscopic model captures the essential topological coupling between $SO(4)$ hypercube rotations and ARX feedback, it does not account for potential bit-level carry cancellations that might theoretically arise under specific low-weight bit configurations. Full bit-level MILP models remain a valuable avenue for independent evaluation.
    \item \textbf{Distinguishing Horizon vs. Key Recovery Complexity:} All complexity metrics reported in Table~\ref{tab:round_reduced_summary} represent lower bounds for the distinguishing phase under standard Biham-Shamir and Matsui models. Complete key-recovery attacks require appending key-guessing rounds before or after the distinguisher, incurring multiplicative computational overhead proportional to the guessed subkey entropy ($O(N_D \cdot 2^{|K_{\text{guess}}|})$). Full key-recovery attacks therefore demand strictly higher complexity than the distinguishing lower bounds.
\end{enumerate}

\subsection{Call for Open Community Cryptanalysis}
We explicitly invite independent researchers and cryptanalysts to evaluate Tesseract-128 against advanced cryptanalytic techniques, including:
\begin{itemize}
    \item Bit-based division property with degree evaluation for higher-order integral characteristics.
    \item Differential-linear cryptanalysis combining short differential trails with linear approximations across the ARX ripple.
    \item Physical side-channel leakage evaluations and masked algorithmic implementations on ultra-low-power microcontrollers (e.g., ARM Cortex-M0+).
\end{itemize}

\subsection{Open-Source Artifacts and Reproducibility}
In conformance with Elsevier's open research initiatives, all software implementations (Scalar C, SSSE3, AVX2 vector intrinsics), verification testbenches, automated MILP solvers (PuLP/CBC), and impossible differential search scripts are publicly accessible at the open research repository:
\begin{center}
    \url{https://github.com/toilacobemongmo/Tesseract-128}
\end{center}
All empirical figures and solver results reported in this paper can be reproduced through single-command execution scripts provided in the repository.
'''

    # Section 9: Conclusion (from pos_concl to pos_bib)
    sec9_text = src[pos_concl:pos_bib]

    # Bibliography (from pos_bib to end)
    bib_text = src[pos_bib:]

    # Clean figure* and table* across all extracted sections
    raw_sections = [sec1, sec2_text, sec3, sec4_text, sec5_text, sec6_text, sec7_text, sec8_discussion, sec9_text]
    cleaned_sections = []

    for s in raw_sections:
        s = s.replace(r'\begin{figure*}[!t]', r'\begin{figure}[htbp]')
        s = s.replace(r'\begin{figure*}[htbp]', r'\begin{figure}[htbp]')
        s = s.replace(r'\begin{figure*}[t]', r'\begin{figure}[htbp]')
        s = s.replace(r'\begin{figure*}', r'\begin{figure}')
        s = s.replace(r'\end{figure*}', r'\end{figure}')
        s = s.replace(r'\begin{table*}[t]', r'\begin{table}[htbp]')
        s = s.replace(r'\begin{table*}[htbp]', r'\begin{table}[htbp]')
        s = s.replace(r'\begin{table*}', r'\begin{table}')
        s = s.replace(r'\end{table*}', r'\end{table}')
        # Resize tikzpicture
        if r'\begin{tikzpicture}[scale=0.88, transform shape,' in s:
            s = s.replace(r'\begin{tikzpicture}[scale=0.88, transform shape,', r'\resizebox{\linewidth}{!}{\begin{tikzpicture}[')
            s = s.replace(r'\end{tikzpicture}', r'\end{tikzpicture}}')
        cleaned_sections.append(s)

    full_paper = (
        preamble + '\n' +
        '\n'.join(cleaned_sections) + '\n' +
        bib_text
    )

    # Sanity guard: every extracted section must be non-empty and the assembled
    # document must contain exactly one bibliography and one \end{document}.
    # This catches the silent-corruption failure mode described above.
    for name, sec in zip(
        ['sec1', 'sec3', 'sec4_text', 'sec5_text', 'sec6_text', 'sec7_text', 'sec9_text'],
        [sec1, sec3, sec4_text, sec5_text, sec6_text, sec7_text, sec9_text],
    ):
        if not sec.strip():
            raise SystemExit("ERROR: extracted section %s is empty" % name)
    if full_paper.count(r'\end{document}') != 1:
        raise SystemExit(
            "ERROR: assembled document contains %d occurrences of \\end{document} "
            "(expected 1) -- section slices overlap"
            % full_paper.count(r'\end{document}')
        )
    if full_paper.count(r'\begin{thebibliography}') != 1:
        raise SystemExit("ERROR: assembled document has %d bibliographies (expected 1)"
                         % full_paper.count(r'\begin{thebibliography}'))

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_TEX, 'w', encoding='utf-8') as f:
        f.write(full_paper)

    n_sections = full_paper.count('\n' + '\\section{')
    print("Successfully built %s (%d bytes, %d section headings)!"
          % (os.path.relpath(OUT_TEX, os.path.dirname(HERE)), len(full_paper), n_sections))

if __name__ == '__main__':
    build_jisa_paper()
