"use strict";
const { Document, Packer, Paragraph, TextRun, AlignmentType,
        HeadingLevel, BorderStyle, PageNumber, Header, Footer } = require("docx");
const fs = require("fs");

const sp = (before, after) => ({ spacing: { before, after } });

function authorBlock(num, name, email) {
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      ...sp(40, 0),
      children: [new TextRun({ text: `${num}  ${name}`, bold: true, font: "Times New Roman", size: 20 })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      ...sp(0, 0),
      children: [new TextRun({ text: "Department of CSE", font: "Times New Roman", size: 18, italics: true })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      ...sp(0, 0),
      children: [new TextRun({ text: "VNR VJIET, Hyderabad, India", font: "Times New Roman", size: 18, italics: true })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      ...sp(0, 40),
      children: [new TextRun({ text: email, font: "Courier New", size: 18 })],
    }),
  ];
}

function sectionRule() {
  return new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "1A1A6E", space: 1 } },
    children: [new TextRun("")],
    ...sp(120, 60),
  });
}

function hdr(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, font: "Times New Roman" })],
    ...sp(240, 120),
  });
}

function body(text) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    ...sp(0, 120),
    children: [new TextRun({ text, font: "Times New Roman", size: 20 })],
  });
}

function sub(text) {
  return new Paragraph({
    ...sp(120, 60),
    children: [new TextRun({ text, bold: true, font: "Times New Roman", size: 20 })],
  });
}

const children = [
  // TITLE
  new Paragraph({
    alignment: AlignmentType.CENTER,
    ...sp(0, 160),
    children: [new TextRun({
      text: "LP-Pruned Quantum Branch-and-Bound for the 0/1 Knapsack Problem: Query-Complexity Analysis and Spectral Validation",
      bold: true, font: "Times New Roman", size: 28,
    })],
  }),

  // AUTHORS
  ...authorBlock("1st", "Nagini S.",         "nagini_s@vnrvjiet.in"),
  ...authorBlock("2nd", "Madhavi A.",        "madhavi_a@vnrvjiet.in"),
  ...authorBlock("3rd", "Shiva Sai",         "venkatashivasai07@gmail.com"),
  ...authorBlock("4th", "Metta Kumudini",    "kumudini.metta@gmail.com"),
  ...authorBlock("5th", "Purusharth Mishra", "purusharthmishra10@gmail.com"),
  ...authorBlock("6th", "Rakshit Chaturvedi","rakshitchaturvedi09@gmail.com"),
  ...authorBlock("7th", "Veerabhadra Yerram","veerabhadrayerram@gmail.com"),

  new Paragraph({ children: [new TextRun("")], ...sp(0, 80) }),
  sectionRule(),

  // ABSTRACT
  new Paragraph({
    alignment: AlignmentType.CENTER,
    ...sp(80, 60),
    children: [new TextRun({ text: "Abstract", bold: true, font: "Times New Roman", size: 22 })],
  }),
  body("The 0/1 knapsack problem is a fundamental NP-hard combinatorial optimization problem with applications spanning resource allocation, cryptography, and logistics. The best provable quantum algorithms either match classical meet-in-the-middle at O(2^{n/2}) or rely on unproven heuristic assumptions (Heuristic 2) and infeasible QRAQM hardware. We present a hybrid algorithm that couples LP-guided reduced-cost variable fixing with Montanaro's quantum branch-and-bound framework. Our three-phase hybrid algorithm: (1) reduces the problem to m = αn core items via reduced-cost fixing; (2) applies a classical threshold-search outer loop with composed query complexity O(sqrt(T_max) * m*log(m)*log(V_max)); and (3) performs classical post-processing to reconstruct the global optimum. We prove instance-dependent complexity bounds, establish a core containment theorem and necessity-of-delta spacing result, validate spectral conditions on 889 completed simulated trees (T_LP <= 2000), synthesize the reversible LP bounding oracle at m=4, benchmark against Google OR-Tools (n up to 1000), and characterize the NISQ noise boundary on IBM's ibm_fez processor. We do not claim wall-clock quantum speedup or hardware advantage."),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    ...sp(0, 120),
    children: [
      new TextRun({ text: "Index Terms\u2014", bold: true, italics: true, font: "Times New Roman", size: 20 }),
      new TextRun({ text: "quantum computing, knapsack problem, branch-and-bound, quantum walk, LP relaxation, variable fixing, combinatorial optimization", italics: true, font: "Times New Roman", size: 20 }),
    ],
  }),
  sectionRule(),

  // I. INTRODUCTION
  hdr("I.  Introduction"),
  body("The 0/1 knapsack problem is NP-hard; the best classical exact algorithm (Horowitz-Sahni meet-in-the-middle) runs in O(2^{n/2}) time and space. Quantum approaches based on quantum walks (Bernstein et al.: O(2^{0.241n}); Helm-May: O(2^{0.226n})) require Heuristic 2 (unproven) and QRAQM (hardware-infeasible). Our work fills the gap: LP structure combined with provable, QRAQM-free quantum tree-search query bounds."),
  sub("A.  Contributions"),
  ...[
    "1. Exact LP/reduced-cost variable fixing with core containment theorem and necessity-of-delta spacing result.",
    "2. Threshold-optimization composition via classical binary-search outer loop and Montanaro-style quantum detection.",
    "3. Composed query bound O(sqrt(T_max)*m*log(m)*log(V_max)) with explicit T_max definition.",
    "4. Computational spectral validation on 889 completed simulated trees (T_LP <= 2000).",
    "5. Gate-level synthesis and verification of the reversible LP bounding oracle at m=4.",
    "6. Small-scale IBM hardware characterization (ibm_fez, 156-qubit Heron r2) for core sizes 3-6.",
    "7. Large-scale benchmarking vs Google OR-Tools (n up to 1000) with empirical T_LP regression.",
  ].map(t => new Paragraph({
    ...sp(0, 60),
    indent: { left: 360 },
    children: [new TextRun({ text: t, font: "Times New Roman", size: 20 })],
  })),
  sectionRule(),

  // II. LITERATURE REVIEW
  hdr("II.  Literature Review"),
  body("Classical exact methods: Dantzig LP relaxation (tight upper bound), Horowitz-Sahni MitM O(2^{n/2}), Kellerer-Pferschy-Pisinger DP/B&B, Pisinger core concept. Quantum search: Grover O(sqrt(N)), amplitude amplification. Quantum walks: MNRS framework; Bernstein et al. O(2^{0.241n}), Helm-May O(2^{0.226n}) — both heuristic and QRAQM-dependent. Implementable: Grover-based knapsack (no MitM speedup), QAOA/variational (no guarantees). Closest: Montanaro quantum B&B (generic, provable, QRAQM-free), QTG of Wilkening et al. (knapsack-specific, variational), Bonnetain et al. (provable walk, QRAQM-dependent)."),
  sectionRule(),

  // III. PRELIMINARIES
  hdr("III.  Mathematical Preliminaries"),
  body("Standard knapsack: n items, weights w_i, values v_i, capacity W. LP relaxation: fractional solution gives upper bound. Reduced-cost variable fixing: dual values determine items provably in or out of every optimal solution. Montanaro's quantum B&B: query complexity O(sqrt(T)*d) on backtracking tree of size T, depth d."),
  sectionRule(),

  // IV. ALGORITHM
  hdr("IV.  Algorithm"),
  sub("Phase 1 — LP Preprocessing & Core Reduction"),
  body("Solve LP relaxation. Apply reduced-cost fixing to partition into F_1 (fixed in), F_0 (fixed out), core C with |C| = m <= alpha*n."),
  sub("Phase 2 — Quantum Threshold Search"),
  body("Classical binary-search outer loop over thresholds tau. For each tau, invoke Montanaro's quantum detection oracle on the LP-pruned B&B tree over core C. Composed query complexity: O(sqrt(T_max)*m*log(m)*log(V_max))."),
  sub("Phase 3 — Classical Post-Processing"),
  body("Reconstruct global optimum from oracle output, accounting for F_1 and F_0 contributions."),
  sectionRule(),

  // V. THEORY
  hdr("V.  Theoretical Analysis"),
  body("Theorem 1 (Core Containment): For any optimal solution x*, reduced-cost fixing correctly identifies F_1 and F_0. The core C contains all items whose LP status is ambiguous."),
  body("Theorem 2 (Query Complexity): The composed quantum algorithm achieves O(sqrt(T_max)*m*log(m)*log(V_max)) queries under Montanaro's oracle model."),
  body("Necessity-of-Delta: The minimum-spacing hypothesis (delta-separation of item efficiencies) cannot be removed in general — exhibited by an explicit instance family with bounded LP gap but unbounded core size as delta -> 0."),
  sectionRule(),

  // VI. EXPERIMENTS
  hdr("VI.  Experimental Results"),
  sub("A.  Core Size by Instance Type"),
  body("Average core ratio alpha = m/n: Uncorrelated 0.32 (tight LP gap), Weakly correlated 0.76, Strongly correlated 0.95, Subset-sum 1.00 (very loose), Inverse strongly 0.81."),
  sub("B.  Spectral Validation"),
  body("889 of 1200 conditions completed (T_LP <= 2000): 489 completed marked (phase-zero validated), 400 completed unmarked (spectral-gap validated), 74 tree-cap marked, 163 immediately pruned, 74 seed-level empty-core. All 889 agree perfectly with the analytical detection criterion."),
  sub("C.  OR-Tools Benchmark"),
  body("69 of 90 instances fully solved by both solvers. 21 reached cutoffs (OR-Tools: 20s; our B&B: 1,000,000 nodes) — no timing comparison drawn for these rows."),
  sub("D.  IBM Hardware (ibm_fez, Heron r2)"),
  body("Core-3A: sim 0.9975, HW 0.8621, depth 62, 2Q gates 14. Core-4A: sim 0.9942, HW 0.6183, depth 481, 132. Core-5B: sim 0.9613, HW 0.0637, depth 9273, 3012. Core-6A: sim 0.9992, HW 0.0312, depth 50520, 16579. Hardware fidelity collapses for core size > 4."),
  sub("E.  T_LP Regression"),
  body("log(T_LP) ~ log(gap) + m per class. R^2: Uncorrelated 0.812, Weakly correlated 0.743, Strongly correlated 0.601, Subset sum 0.010, Inverse strongly 0.583. Query reduction relevant only in the LP-hard large-coefficient regime."),
  sectionRule(),

  // VII. DISCUSSION
  hdr("VII.  Discussion"),
  body("Limitations: query complexity is not wall-clock runtime; gate estimates for m > 4 are partial lower bounds; hardware results limited to n in {3,4,5,6}. The necessity-of-delta result closes one open question. Open question: for which instance classes does alpha remain small enough for practical quantum advantage?"),
  sectionRule(),

  // VIII. CONCLUSION
  hdr("VIII.  Conclusion"),
  body("We present a hybrid LP-pruned quantum branch-and-bound for the 0/1 knapsack problem that is provable, QRAQM-free, knapsack-specific, and instance-adaptive. Key results: core containment theorem; necessity-of-delta structural result; spectral validation on 889 simulated trees; reversible LP oracle synthesized and verified at m=4; OR-Tools benchmark (n up to 1000); IBM hardware characterization. No wall-clock speedup or hardware advantage is claimed. The central open question — whether T_LP is small enough for practical advantage — is left for future work."),
  sectionRule(),

  new Paragraph({
    alignment: AlignmentType.CENTER,
    ...sp(120, 0),
    children: [new TextRun({ text: "VNR Vignana Jyothi Institute of Engineering and Technology, Hyderabad, India", font: "Times New Roman", size: 18, italics: true })],
  }),
];

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Times New Roman", size: 20 } } },
    paragraphStyles: [{
      id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 24, bold: true, font: "Times New Roman", color: "1A1A6E" },
      paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 },
    }],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1080, bottom: 1440, left: 1080 },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "1A1A6E", space: 2 } },
          children: [new TextRun({ text: "LP-Pruned Quantum B&B for 0/1 Knapsack \u2014 VNR VJIET", font: "Times New Roman", size: 16, italics: true, color: "444444" })],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "Page ", font: "Times New Roman", size: 16 }),
            new TextRun({ children: [PageNumber.CURRENT], font: "Times New Roman", size: 16 }),
          ],
        })],
      }),
    },
    children,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("main.docx", buf);
  console.log("main.docx written (" + buf.length + " bytes)");
});
