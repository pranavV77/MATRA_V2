import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = pptx.Presentation('Mid review PPT Template.pptx')
    
    # Define primary brand / academic colors matching template
    DARK_BLUE = RGBColor(16, 44, 87)       # #102C57
    MED_BLUE = RGBColor(37, 77, 142)       # #254D8E
    ACCENT_GOLD = RGBColor(218, 165, 32)   # #DAA520
    CHARCOAL = RGBColor(33, 37, 41)        # #212529
    WHITE = RGBColor(255, 255, 255)
    LIGHT_GRAY = RGBColor(245, 247, 250)
    BORDER_GRAY = RGBColor(200, 205, 215)
    GREEN = RGBColor(34, 139, 34)
    MAROON = RGBColor(140, 29, 64)         # Amrita Maroon
    
    # Helper to set text frame margins
    def zero_margins(tf):
        tf.margin_left = Inches(0.05)
        tf.margin_right = Inches(0.05)
        tf.margin_top = Inches(0.05)
        tf.margin_bottom = Inches(0.05)

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------
    slide1 = prs.slides[0]
    for shape in slide1.shapes:
        if shape.name == "TextBox 1": # Project title
            tf = shape.text_frame
            tf.word_wrap = True
            tf.clear()
            p = tf.paragraphs[0]
            p.text = "Explainable AI-Based Element Recommendation Framework for Functional Materials Using Unsupervised Representation Learning (MATRA)"
            p.font.name = "Segoe UI"
            p.font.size = Pt(22)
            p.font.bold = True
            p.font.color.rgb = DARK_BLUE
            shape.top = Inches(2.3)
            shape.height = Inches(1.8)
            shape.width = Inches(6.8)
            
        elif shape.name == "TextBox 7": # Header review text
            tf = shape.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            p.text = "S7 PROJECT MID REVIEW"
            p.font.name = "Arial Narrow"
            p.font.size = Pt(28)
            p.font.bold = True
            p.font.color.rgb = MAROON
            
        elif shape.name == "TextBox 9": # Guide info
            tf = shape.text_frame
            tf.clear()
            p1 = tf.paragraphs[0]
            p1.text = "Guided by:"
            p1.font.name = "Times New Roman"
            p1.font.size = Pt(14)
            p1.font.bold = True
            p1.font.color.rgb = CHARCOAL
            
            p2 = tf.add_paragraph()
            p2.text = "Ms. Remya V S"
            p2.font.name = "Times New Roman"
            p2.font.size = Pt(15)
            p2.font.bold = True
            p2.font.color.rgb = DARK_BLUE
            
            p3 = tf.add_paragraph()
            p3.text = "Assistant Professor, Dept. of CSE\nAmrita School of Computing, Amritapuri"
            p3.font.name = "Times New Roman"
            p3.font.size = Pt(12)
            p3.font.color.rgb = CHARCOAL
            shape.top = Inches(4.3)
            shape.height = Inches(1.1)

        elif shape.name == "TextBox 3": # Team info
            tf = shape.text_frame
            tf.clear()
            p_head = tf.paragraphs[0]
            p_head.text = "Project Team (D19):"
            p_head.font.name = "Times New Roman"
            p_head.font.size = Pt(14)
            p_head.font.bold = True
            p_head.font.color.rgb = CHARCOAL
            
            members = [
                "V Govardhan Pranav Suraj (AM.SC.U4CSE23366)",
                "T Ruthvik Rao (AM.SC.U4CSE23364)"
            ]
            for m in members:
                p = tf.add_paragraph()
                p.text = m
                p.font.name = "Times New Roman"
                p.font.size = Pt(13)
                p.font.bold = True
                p.font.color.rgb = DARK_BLUE
            
            p_course = tf.add_paragraph()
            p_course.text = "Course: 23CSE498 – Project Phase II (2026–2027)"
            p_course.font.name = "Times New Roman"
            p_course.font.size = Pt(11)
            p_course.font.italic = True
            p_course.font.color.rgb = CHARCOAL
            shape.top = Inches(5.5)
            shape.height = Inches(1.4)

    # -------------------------------------------------------------
    # SLIDE 2: Outline
    # -------------------------------------------------------------
    slide2 = prs.slides[1]
    for shape in slide2.shapes:
        if shape.name == "TextBox 5":
            shape.text_frame.text = "MATRA: Explainable AI-Based Element Recommendation Framework"
            shape.text_frame.paragraphs[0].font.size = Pt(11)
            shape.text_frame.paragraphs[0].font.color.rgb = CHARCOAL
        elif shape.name == "Content Placeholder 1":
            tf = shape.text_frame
            tf.clear()
            sections = [
                ("1. Introduction", "Functional materials discovery & the combinatorial substitution bottleneck"),
                ("2. Problem Definition", "Motivation, core problem statement & primary project objectives"),
                ("3. Literature Review Summary", "Critical review of state-of-the-art representations, GNNs & explainability"),
                ("4. Research Gap", "Key deficiencies in existing ML frameworks & MATRA's novel formulation"),
                ("5. Methodology", "Multi-signal representations, universal GNN screening & database validation"),
                ("6. Design / Architecture", "Four-tier decoupled system architecture & operational pipeline workflow"),
                ("7. Algorithms & Formulations", "Mathematical similarity metrics, fusion equations & confidence scoring"),
                ("8. Result Analysis", "Quantitative benchmark performance (Hit@K, MRR) & β-Ga2O3 headline demo"),
                ("9. Project Timeline & Plan", "Completed foundational milestone vs. upcoming full-stack development"),
                ("10. References", "Key peer-reviewed literature in materials informatics and AI")
            ]
            for idx, (title, desc) in enumerate(sections):
                p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
                p.text = f"{title}: "
                p.font.name = "Segoe UI"
                p.font.size = Pt(13)
                p.font.bold = True
                p.font.color.rgb = DARK_BLUE
                p.space_after = Pt(4)
                
                run = p.add_run()
                run.text = desc
                run.font.name = "Segoe UI"
                run.font.size = Pt(12)
                run.font.bold = False
                run.font.color.rgb = CHARCOAL

    # -------------------------------------------------------------
    # SLIDE 3: Introduction
    # -------------------------------------------------------------
    slide3 = prs.slides[2]
    for shape in slide3.shapes:
        if shape.name == "Content Placeholder 1":
            tf = shape.text_frame
            tf.clear()
            points = [
                ("Functional Materials Demand:", "Advanced applications in power semiconductors (β-Ga2O3, GaN), batteries, thermoelectrics (Bi2Te3), and catalysts rely heavily on precise elemental substitution and chemical doping to tune bandgaps and conductivity."),
                ("The Combinatorial Space Bottleneck:", "Exploring chemical substitute space across the periodic table (>94 elements, multiple Wyckoff lattice sites) produces an intractable search space for empirical trial-and-error synthesis."),
                ("Computational Burden of Ab Initio DFT:", "Density Functional Theory (DFT) calculations are computationally prohibitive (~10^3–10^5 CPU-hours) for large-scale combinatorial screening."),
                ("Deficit in Current Materials AI:", "Existing machine learning models operate primarily as black boxes—outputting isolated scalar properties or unverified structures without transparent scientific justification or empirical validation."),
                ("MATRA Solution:", "An explainable AI decision-support framework that combines unsupervised representation learning, ultrafast DFT-free GNN formation-energy screening, and database precedent validation.")
            ]
            for idx, (lead, body) in enumerate(points):
                p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
                p.space_after = Pt(8)
                run_lead = p.add_run()
                run_lead.text = f"•  {lead} "
                run_lead.font.name = "Segoe UI"
                run_lead.font.size = Pt(13)
                run_lead.font.bold = True
                run_lead.font.color.rgb = DARK_BLUE
                
                run_body = p.add_run()
                run_body.text = body
                run_body.font.name = "Segoe UI"
                run_body.font.size = Pt(12.5)
                run_body.font.color.rgb = CHARCOAL

    # -------------------------------------------------------------
    # SLIDE 4: Problem Definition
    # -------------------------------------------------------------
    slide4 = prs.slides[3]
    for shape in slide4.shapes:
        if shape.name == "Content Placeholder 1":
            tf = shape.text_frame
            tf.clear()
            
            # Motivation
            p = tf.paragraphs[0]
            p.text = "1. Motivation"
            p.font.name = "Segoe UI"
            p.font.size = Pt(14)
            p.font.bold = True
            p.font.color.rgb = MAROON
            p.space_after = Pt(2)
            
            p_m = tf.add_paragraph()
            p_m.text = "Accelerating the discovery of replacement materials to eliminate toxic, scarce, or expensive elements (e.g., Co, In, Pb) requires rapid, physically reliable screening without incurring prohibitive experimental and supercomputing costs."
            p_m.font.name = "Segoe UI"
            p_m.font.size = Pt(12)
            p_m.font.color.rgb = CHARCOAL
            p_m.space_after = Pt(8)
            
            # Problem Statement
            p_ps = tf.add_paragraph()
            p_ps.text = "2. Problem Statement"
            p_ps.font.name = "Segoe UI"
            p_ps.font.size = Pt(14)
            p_ps.font.bold = True
            p_ps.font.color.rgb = MAROON
            p_ps.space_after = Pt(2)
            
            p_pst = tf.add_paragraph()
            p_pst.text = "Develop an explainable AI-based element recommendation framework that autonomously discovers chemically viable substitute elements for target host lattice sites, enforces thermodynamic plausibility via universal GNN potentials, validates precedent in materials databases, and produces human-interpretable scientific justifications."
            p_pst.font.name = "Segoe UI"
            p_pst.font.size = Pt(12)
            p_pst.font.color.rgb = CHARCOAL
            p_pst.space_after = Pt(8)
            
            # Objectives
            p_obj = tf.add_paragraph()
            p_obj.text = "3. Core Project Objectives"
            p_obj.font.name = "Segoe UI"
            p_obj.font.size = Pt(14)
            p_obj.font.bold = True
            p_obj.font.color.rgb = MAROON
            p_obj.space_after = Pt(2)
            
            objs = [
                ("Multi-Signal Unsupervised Learning:", "Formulate and fuse 3 orthogonal similarity signals (Villars PN, Atom2Vec SVD, 14-Property vectors)."),
                ("DFT-Free Energetic Gating:", "Deploy pretrained universal GNN potentials (M3GNet/MACE) for formation energy plausibility (dE < cutoff)."),
                ("Database Precedence Verification:", "Cross-reference candidate structures against Materials Project / OQMD via StructureMatcher."),
                ("Explainable AI Justification:", "Synthesize SHAP feature attributions and Gemini API into grounded natural-language justifications.")
            ]
            for l, b in objs:
                p_o = tf.add_paragraph()
                p_o.space_after = Pt(3)
                r1 = p_o.add_run()
                r1.text = f"•  {l} "
                r1.font.name = "Segoe UI"
                r1.font.size = Pt(11.5)
                r1.font.bold = True
                r1.font.color.rgb = DARK_BLUE
                
                r2 = p_o.add_run()
                r2.text = b
                r2.font.name = "Segoe UI"
                r2.font.size = Pt(11)
                r2.font.color.rgb = CHARCOAL

    # -------------------------------------------------------------
    # SLIDE 5: Literature Review Summary (TABLE)
    # -------------------------------------------------------------
    slide5 = prs.slides[4]
    # Remove placeholder text shape on slide 5 and add structured Table
    ph5 = None
    for shape in slide5.shapes:
        if shape.name == "Content Placeholder 1":
            ph5 = shape
            break
    if ph5:
        slide5.shapes._spTree.remove(ph5._element)
        
    # Create Literature Table
    rows, cols = 7, 5
    left = Inches(0.6)
    top = Inches(1.1)
    width = Inches(12.13)
    height = Inches(5.6)
    
    table_shape5 = slide5.shapes.add_table(rows, cols, left, top, width, height)
    table5 = table_shape5.table
    table5.columns[0].width = Inches(1.8) # Paper / Year
    table5.columns[1].width = Inches(3.1) # Key Contribution
    table5.columns[2].width = Inches(2.9) # Demerit / Limitation
    table5.columns[3].width = Inches(2.1) # Dataset Used
    table5.columns[4].width = Inches(2.23) # Evaluation Metrics
    
    headers5 = ["Paper & Year", "Key Contribution", "Demerit / Limitation", "Dataset Used", "Evaluation Metrics"]
    for c_idx, h in enumerate(headers5):
        cell = table5.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_BLUE
        tf = cell.text_frame
        tf.word_wrap = True
        zero_margins(tf)
        p = tf.paragraphs[0]
        p.text = h
        p.font.name = "Segoe UI"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        
    lit_data = [
        ("Oran et al.\n(2026, JCTC)", "PNcsp+: Periodic Number (PN) descriptor for crystal structure prediction; ensembled GNN ranking", "Substitution driven by 1D PN distance alone; lacks multi-property fusion & explainability", "OQMD (1.4M+),\nMPDS, CSPBench (180 systems)", "Space-group match (86.1%), Top-5 match (85.0%)"),
        ("Zhou et al.\n(2018, PNAS)", "Atom2Vec: Unsupervised atom vectors from co-occurrence statistics in chemical formulas via SVD", "Purely compositional; ignores crystal symmetry, coordination, energetics & explanations", "Materials Project\n(~60k inorganic formulas)", "Clustering accuracy, formation energy regression MAE"),
        ("Kusaba et al.\n(2021, Sci. Rep.)", "PTG: Reconstructs 2D periodic table from 39 physical features using GTM-LDLV generative mapping", "Representation/clustering tool only; capped at 54 elements; does not propose site substitutions", "XenonPy\n(39 elemental properties, 54 elements)", "GTM topographic error, property prediction R²"),
        ("Nguyen et al.\n(2021, arXiv)", "DeepOFM: Supervised MLP on Voronoi orbital field matrices to predict atom substitution likelihood", "Black-box likelihood score; requires full DFT to validate; no automated DB precedent check", "OQMD\n(~4.2k local chemical environments)", "Top-1/Top-3 hit rate, Jensen-Shannon divergence"),
        ("Wang et al.\n(2021, npj CM)", "CrabNet: Composition-based self-attention Transformer with element contribution attention weights", "Limited to property prediction; cannot propose Wyckoff site substitutions or explain failures", "28 benchmarks (MP, AFLOW, OQMD, Matbench)", "Regression MAE & R² across 28 materials datasets"),
        ("Ying et al.\n(2019, NeurIPS)", "GNNExplainer: Model-agnostic framework generating compact subgraph & node feature explanations", "Generic graph method; requires domain adaptation to chemical & crystallographic properties", "Synthetic graphs, MUTAG, Reddit", "Explanation accuracy, mutual information metric")
    ]
    for r_idx, row in enumerate(lit_data):
        for c_idx, val in enumerate(row):
            cell = table5.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = LIGHT_GRAY if r_idx % 2 == 0 else WHITE
            tf = cell.text_frame
            tf.word_wrap = True
            zero_margins(tf)
            p = tf.paragraphs[0]
            p.text = val
            p.font.name = "Segoe UI"
            p.font.size = Pt(9.5)
            p.font.color.rgb = CHARCOAL
            if c_idx == 0:
                p.font.bold = True

    # -------------------------------------------------------------
    # SLIDE 6: Research Gap
    # -------------------------------------------------------------
    slide6 = prs.slides[5]
    for shape in slide6.shapes:
        if shape.name == "Content Placeholder 1":
            tf = shape.text_frame
            tf.clear()
            
            p = tf.paragraphs[0]
            p.text = "1. Limitations of Current SOTA Approaches"
            p.font.name = "Segoe UI"
            p.font.size = Pt(13.5)
            p.font.bold = True
            p.font.color.rgb = MAROON
            p.space_after = Pt(2)
            
            sota_points = [
                ("1D Periodic Descriptors (PNcsp):", "Fast but constrained to 1D integer sequence; cannot capture continuous multi-property correlations."),
                ("Formula Embeddings (Atom2Vec):", "Captures empirical stoichiometry co-occurrence but remains blind to 3D crystal coordination & energetics."),
                ("Supervised Deep Learning (DeepOFM):", "Generates black-box probability distributions without natural-language chemical justifications.")
            ]
            for l, b in sota_points:
                p_s = tf.add_paragraph()
                p_s.space_after = Pt(2)
                r1 = p_s.add_run()
                r1.text = f"•  {l} "
                r1.font.name = "Segoe UI"
                r1.font.size = Pt(11.5)
                r1.font.bold = True
                r1.font.color.rgb = DARK_BLUE
                r2 = p_s.add_run()
                r2.text = b
                r2.font.name = "Segoe UI"
                r2.font.size = Pt(11)
                r2.font.color.rgb = CHARCOAL
                
            p_gap = tf.add_paragraph()
            p_gap.text = "2. Specific Research Gaps Targeted by MATRA"
            p_gap.font.name = "Segoe UI"
            p_gap.font.size = Pt(13.5)
            p_gap.font.bold = True
            p_gap.font.color.rgb = MAROON
            p_gap.space_before = Pt(6)
            p_gap.space_after = Pt(2)
            
            gaps = [
                ("Signal Isolation Deficit:", "No existing framework unifies 3 orthogonal representations (Mendeleev topology, formula co-occurrence, and physical property vectors) for candidate recommendation."),
                ("Absence of DFT-Free Energetic Gating:", "Current similarity tools lack integrated GNN interatomic potentials to filter thermodynamically implausible substitutions in real time."),
                ("Lack of Precedent Cross-Validation:", "Candidates are surfaced without automated verification against known crystal databases (Materials Project, OQMD)."),
                ("Explainability Void:", "No end-to-end framework synthesizes SHAP feature attributions and LLMs into grounded, human-readable scientific rationale.")
            ]
            for l, b in gaps:
                p_g = tf.add_paragraph()
                p_g.space_after = Pt(2)
                r1 = p_g.add_run()
                r1.text = f"•  {l} "
                r1.font.name = "Segoe UI"
                r1.font.size = Pt(11.5)
                r1.font.bold = True
                r1.font.color.rgb = DARK_BLUE
                r2 = p_g.add_run()
                r2.text = body = b
                r2.font.name = "Segoe UI"
                r2.font.size = Pt(11)
                r2.font.color.rgb = CHARCOAL

    # -------------------------------------------------------------
    # SLIDE 7: Methodology (TABLE)
    # -------------------------------------------------------------
    slide7 = prs.slides[6]
    ph7 = None
    for shape in slide7.shapes:
        if shape.name == "Content Placeholder 1":
            ph7 = shape
            break
    if ph7:
        slide7.shapes._spTree.remove(ph7._element)
        
    table_shape7 = slide7.shapes.add_table(11, 4, Inches(0.6), Inches(1.1), Inches(12.13), Inches(5.6))
    table7 = table_shape7.table
    table7.columns[0].width = Inches(2.2) # Pipeline Component
    table7.columns[1].width = Inches(3.2) # Method / Tool
    table7.columns[2].width = Inches(1.5) # Status
    table7.columns[3].width = Inches(5.23) # Scientific Purpose
    
    headers7 = ["Pipeline Component", "Methodology / Tool", "Milestone Status", "Scientific Purpose"]
    for c_idx, h in enumerate(headers7):
        cell = table7.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_BLUE
        tf = cell.text_frame
        zero_margins(tf)
        p = tf.paragraphs[0]
        p.text = h
        p.font.name = "Segoe UI"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        
    meth_data = [
        ("Master Elemental Table", "mendeleev 1.2.0 + pymatgen 2025.10.7", "COMPLETED", "Curated 14 audited physical properties for Z=1–94; transparent imputation."),
        ("Signal 1: PN Similarity", "Pierre Villars Mendeleev Number", "COMPLETED", "1D helical periodic table distance: S_pn = 1 / (1 + |PN(e_t) - PN(e_c)|)."),
        ("Signal 2: Atom2Vec", "Truncated SVD (d=20) on MP Corpus", "COMPLETED", "Unsupervised co-occurrence cosine similarity S_comp across 83,989 formulas."),
        ("Signal 3: Property Cosine", "14-Property Z-Score Standardization", "COMPLETED", "Continuous physicochemical property cosine similarity S_prop (88 elements)."),
        ("Substitution Benchmark", "11 Primary (18 GT) + 5 Secondary", "COMPLETED", "Curated crystallographic ground truth with Wyckoff site provenance."),
        ("Multi-Signal Fusion", "Weighted Linear Combination", "Planned Phase", "Fused candidate ranking: S = w1*S_pn + w2*S_comp + w3*S_prop (w1+w2+w3=1)."),
        ("Crystal Site Substitution", "pymatgen Structure Engine", "Planned Phase", "Wyckoff-preserving site replacement generating candidate crystal M'."),
        ("GNN Energetic Screening", "Pretrained M3GNet (matgl) / MACE", "Planned Phase", "DFT-free formation energy dE(M') scoring; thermodynamic plausibility filter."),
        ("Database Validation", "StructureMatcher + CrystalNN", "Planned Phase", "Precedent matching score D(M') against Materials Project & OQMD."),
        ("Explainability & UI", "SHAP + Gemini API + FastAPI + React", "Planned Phase", "Feature attributions, grounded natural-language explanations, interactive UI.")
    ]
    for r_idx, row in enumerate(meth_data):
        for c_idx, val in enumerate(row):
            cell = table7.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = LIGHT_GRAY if r_idx % 2 == 0 else WHITE
            tf = cell.text_frame
            zero_margins(tf)
            p = tf.paragraphs[0]
            p.text = val
            p.font.name = "Segoe UI"
            p.font.size = Pt(9.2)
            p.font.color.rgb = CHARCOAL
            if c_idx == 0:
                p.font.bold = True
            elif c_idx == 2:
                p.font.bold = True
                p.font.color.rgb = GREEN if val == "COMPLETED" else MAROON

    # -------------------------------------------------------------
    # SLIDE 8: Design / Architecture (Visual Multi-Tier Flow)
    # -------------------------------------------------------------
    slide8 = prs.slides[7]
    ph8 = None
    for shape in slide8.shapes:
        if shape.name == "Content Placeholder 1":
            ph8 = shape
            break
    if ph8:
        slide8.shapes._spTree.remove(ph8._element)
        
    # Draw Architecture Tier Boxes
    # Tier 1: Client & API
    tier1 = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.1), Inches(12.13), Inches(0.85))
    tier1.fill.solid()
    tier1.fill.fore_color.rgb = RGBColor(235, 243, 250)
    tier1.line.color.rgb = MED_BLUE
    tf1 = tier1.text_frame
    tf1.word_wrap = True
    zero_margins(tf1)
    p = tf1.paragraphs[0]
    p.text = "TIER 1: PRESENTATION & SERVICE LAYER"
    p.font.name = "Segoe UI"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = DARK_BLUE
    p_sub = tf1.add_paragraph()
    p_sub.text = "React + TypeScript + Tailwind CSS Frontend  ⟷  FastAPI REST API (POST /recommend, GET /candidates, GET /explanation)  ⟷  Redis + Celery Workers"
    p_sub.font.name = "Segoe UI"
    p_sub.font.size = Pt(10.5)
    p_sub.font.color.rgb = CHARCOAL

    # Core Pipeline Container
    core_box = slide8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(2.1), Inches(12.13), Inches(3.65))
    core_box.fill.solid()
    core_box.fill.fore_color.rgb = WHITE
    core_box.line.color.rgb = MAROON
    core_box.line.width = Pt(1.5)
    tf_c = core_box.text_frame
    zero_margins(tf_c)
    p_ct = tf_c.paragraphs[0]
    p_ct.text = "  CORE 4-PHASE RECOMMENDATION PIPELINE (MATRA ENGINE)"
    p_ct.font.name = "Segoe UI"
    p_ct.font.size = Pt(11)
    p_ct.font.bold = True
    p_ct.font.color.rgb = MAROON
    
    # 4 Phase Cards inside Core Box
    phase_data = [
        ("Phase 1: Multi-Signal Similarity", "[COMPLETED]", "• Signal 1: Villars PN S_pn\n• Signal 2: Atom2Vec SVD S_comp\n• Signal 3: 14-Property Cosine S_prop\n• Score Fusion: S = w1*S_pn+w2*S_comp+w3*S_prop", Inches(0.8), Inches(2.5), Inches(2.75)),
        ("Phase 2: GNN Energy Screening", "[PLANNED]", "• Wyckoff Site Substitution M'\n• M3GNet / MACE GNN Potential\n• Ultrafast Formation Energy dE(M')\n• Plausibility Gate: dE <= cutoff", Inches(3.8), Inches(2.5), Inches(2.75)),
        ("Phase 3: Database Validation", "[PLANNED]", "• Materials Project & OQMD Matching\n• StructureMatcher & CrystalNN\n• Precedent Match Score D(M')\n• Confidence: Conf = a*S + b*sig + g*D", Inches(6.8), Inches(2.5), Inches(2.75)),
        ("Phase 4: Explainable AI Layer", "[PLANNED]", "• SHAP Feature Attributions\n• Gemini API Scientific Synthesis\n• Grounded Natural-Language Justification\n• Confidence & Risk Warning Cards", Inches(9.8), Inches(2.5), Inches(2.75))
    ]
    for p_title, p_stat, p_body, p_left, p_top, p_w in phase_data:
        p_card = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, p_left, p_top, p_w, Inches(3.05))
        p_card.fill.solid()
        p_card.fill.fore_color.rgb = LIGHT_GRAY
        p_card.line.color.rgb = BORDER_GRAY
        tf_p = p_card.text_frame
        tf_p.word_wrap = True
        zero_margins(tf_p)
        
        p1 = tf_p.paragraphs[0]
        p1.text = p_title
        p1.font.name = "Segoe UI"
        p1.font.size = Pt(10.5)
        p1.font.bold = True
        p1.font.color.rgb = DARK_BLUE
        
        p_st = tf_p.add_paragraph()
        p_st.text = p_stat
        p_st.font.name = "Segoe UI"
        p_st.font.size = Pt(9.5)
        p_st.font.bold = True
        p_st.font.color.rgb = GREEN if "COMPLETED" in p_stat else MAROON
        p_st.space_after = Pt(4)
        
        p_b = tf_p.add_paragraph()
        p_b.text = p_body
        p_b.font.name = "Segoe UI"
        p_b.font.size = Pt(9.2)
        p_b.font.color.rgb = CHARCOAL

    # Tier 4: Storage
    tier4 = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(5.9), Inches(12.13), Inches(0.85))
    tier4.fill.solid()
    tier4.fill.fore_color.rgb = RGBColor(235, 243, 250)
    tier4.line.color.rgb = MED_BLUE
    tf4 = tier4.text_frame
    tf4.word_wrap = True
    zero_margins(tf4)
    p4 = tf4.paragraphs[0]
    p4.text = "TIER 4: PERSISTENCE & DATA STORAGE LAYER"
    p4.font.name = "Segoe UI"
    p4.font.size = Pt(11)
    p4.font.bold = True
    p4.font.color.rgb = DARK_BLUE
    p4_sub = tf4.add_paragraph()
    p4_sub.text = "PostgreSQL Relational DB (Materials, Substitutions, Conf Scores, Explanations)  ⟷  FAISS Vector Index  ⟷  elements_master.parquet (SHA256 Verified)"
    p4_sub.font.name = "Segoe UI"
    p4_sub.font.size = Pt(10)
    p4_sub.font.color.rgb = CHARCOAL

    # -------------------------------------------------------------
    # SLIDE 9: Algorithms (if any)
    # -------------------------------------------------------------
    slide9 = prs.slides[8]
    for shape in slide9.shapes:
        if shape.name == "Content Placeholder 1":
            tf = shape.text_frame
            tf.clear()
            
            p = tf.paragraphs[0]
            p.text = "1. Implemented Foundational Similarity Formulations (Completed Tasks 1 & 2)"
            p.font.name = "Segoe UI"
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = MAROON
            p.space_after = Pt(2)
            
            eqs = [
                ("Signal 1 (Villars PN Similarity):", "S_pn(e_t, e_c) = 1 / (1 + |PN(e_t) - PN(e_c)|)", "Maps 1D helical Mendeleev sequence distance into bounded [0, 1] similarity."),
                ("Signal 2 (Atom2Vec SVD Embedding):", "S_comp(e_t, e_c) = (f_t · f_c) / (||f_t|| ||f_c||),  where F = U_20 * D_20 in R^(79 x 20)", "Unsupervised SVD decomposition of row L2-normalized formula co-occurrence matrix."),
                ("Signal 3 (Physicochemical Property Cosine):", "S_prop(e_t, e_c) = (v_t · v_c) / (||v_t|| ||v_c||),  where v in R^14 (Z-score standardized)", "Cosine similarity over 14 continuous physical features (radii, electronegativity, polarizability).")
            ]
            for title, eq, desc in eqs:
                p_eq = tf.add_paragraph()
                p_eq.space_after = Pt(2)
                r1 = p_eq.add_run()
                r1.text = f"•  {title} "
                r1.font.name = "Segoe UI"
                r1.font.size = Pt(11)
                r1.font.bold = True
                r1.font.color.rgb = DARK_BLUE
                
                r2 = p_eq.add_run()
                r2.text = f"  {eq}  — {desc}"
                r2.font.name = "Segoe UI"
                r2.font.size = Pt(10.5)
                r2.font.color.rgb = CHARCOAL

            p_pipe = tf.add_paragraph()
            p_pipe.text = "2. Planned Integration & Confidence Scoring Pipeline (Next Milestone)"
            p_pipe.font.name = "Segoe UI"
            p_pipe.font.size = Pt(13)
            p_pipe.font.bold = True
            p_pipe.font.color.rgb = MAROON
            p_pipe.space_before = Pt(6)
            p_pipe.space_after = Pt(2)
            
            pipe_steps = [
                ("Similarity Fusion:", "S(e_t, e_c) = w1*S_pn + w2*S_comp + w3*S_prop,  with w1 + w2 + w3 = 1", "(Weights calibrated via Leave-One-Out Cross-Validation / UI sliders)."),
                ("GNN Energy Plausibility Gate:", "If dE(M') > energy_cutoff => Discard candidate and fetch next shortlisted element", "(Evaluated via M3GNet universal potential in <2s)."),
                ("Composite Confidence Scoring:", "Conf(M') = alpha*S(e_t, e_c) + beta*sigma(-dE(M')) + gamma*D(M')", "(Combines similarity, energetic stability, and database match precedent).")
            ]
            for title, eq, desc in pipe_steps:
                p_p = tf.add_paragraph()
                p_p.space_after = Pt(2)
                r1 = p_p.add_run()
                r1.text = f"•  {title} "
                r1.font.name = "Segoe UI"
                r1.font.size = Pt(11)
                r1.font.bold = True
                r1.font.color.rgb = DARK_BLUE
                
                r2 = p_p.add_run()
                r2.text = f"  {eq}  {desc}"
                r2.font.name = "Segoe UI"
                r2.font.size = Pt(10.5)
                r2.font.color.rgb = CHARCOAL

    # -------------------------------------------------------------
    # SLIDE 10: Result Analysis (Visual + Quantitative TABLE)
    # -------------------------------------------------------------
    slide10 = prs.slides[9]
    ph10 = None
    for shape in slide10.shapes:
        if shape.name == "Content Placeholder 1":
            ph10 = shape
            break
    if ph10:
        slide10.shapes._spTree.remove(ph10._element)
        
    # Table 1: Quantitative Benchmark Performance
    t_top10 = slide10.shapes.add_table(4, 8, Inches(0.6), Inches(1.1), Inches(12.13), Inches(2.2))
    table10 = t_top10.table
    table10.columns[0].width = Inches(2.5) # Method
    table10.columns[1].width = Inches(1.3) # Hit@1
    table10.columns[2].width = Inches(1.3) # Hit@3
    table10.columns[3].width = Inches(1.3) # Hit@5
    table10.columns[4].width = Inches(1.3) # Hit@10
    table10.columns[5].width = Inches(1.3) # MRR
    table10.columns[6].width = Inches(1.5) # Mean Best Rank
    table10.columns[7].width = Inches(1.63) # Mean Recall@10
    
    headers10 = ["Similarity Method", "Hit@1", "Hit@3", "Hit@5", "Hit@10", "MRR", "Mean Best Rank", "Mean Recall@10"]
    for c_idx, h in enumerate(headers10):
        cell = table10.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_BLUE
        tf = cell.text_frame
        zero_margins(tf)
        p = tf.paragraphs[0]
        p.text = h
        p.font.name = "Segoe UI"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        
    res_rows = [
        ("Pierre Villars PN (Signal 1)", "63.6%", "100.0%", "100.0%", "100.0%", "0.8182", "1.36", "97.0%"),
        ("Atom2Vec SVD (Signal 2)", "63.6%", "81.8%", "81.8%", "100.0%", "0.7516", "2.36", "100.0%"),
        ("Property Cosine (Signal 3)", "36.4%", "72.7%", "90.9%", "100.0%", "0.5394", "3.09", "78.8%")
    ]
    for r_idx, row in enumerate(res_rows):
        for c_idx, val in enumerate(row):
            cell = table10.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = LIGHT_GRAY if r_idx % 2 == 0 else WHITE
            tf = cell.text_frame
            zero_margins(tf)
            p = tf.paragraphs[0]
            p.text = val
            p.font.name = "Segoe UI"
            p.font.size = Pt(9.5)
            p.font.color.rgb = CHARCOAL
            if c_idx == 0:
                p.font.bold = True
            else:
                p.alignment = PP_ALIGN.CENTER

    # Headline Demonstration Box: beta-Ga2O3 -> Ga
    demo_box = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(3.45), Inches(12.13), Inches(3.35))
    demo_box.fill.solid()
    demo_box.fill.fore_color.rgb = WHITE
    demo_box.line.color.rgb = MED_BLUE
    demo_box.line.width = Pt(1.5)
    tf_d = demo_box.text_frame
    tf_d.word_wrap = True
    zero_margins(tf_d)
    
    pd_head = tf_d.paragraphs[0]
    pd_head.text = "Headline Case Study: β-Ga2O3 → Ga (Octahedral 4i Site Substitution)"
    pd_head.font.name = "Segoe UI"
    pd_head.font.size = Pt(11.5)
    pd_head.font.bold = True
    pd_head.font.color.rgb = DARK_BLUE
    pd_head.space_after = Pt(2)
    
    pd_sub = tf_d.add_paragraph()
    pd_sub.text = "• Verified Primary Ground Truth: [Al, In] (isostructural solid solutions)  |  • Secondary Dopant Context: [Si, Sn] (quarantined from GT accuracy)"
    pd_sub.font.name = "Segoe UI"
    pd_sub.font.size = Pt(10)
    pd_sub.font.color.rgb = MAROON
    pd_sub.font.bold = True
    pd_sub.space_after = Pt(4)
    
    ranks_text = [
        ("Villars PN Rankings:", "Rank 1: Al (0.5000) [GT],  Rank 2: In (0.5000) [GT],  Rank 3: B (0.3333),  Rank 4: Tl (0.3333),  Rank 8: Si (0.1667) [Dopant]"),
        ("Atom2Vec SVD Rankings:", "Rank 1: Al (0.8462) [GT],  Rank 2: In (0.7601) [GT],  Rank 3: Y (0.7573),  Rank 4: Bi (0.6505),  Rank 6: Sn (0.6046) [Dopant]"),
        ("Property Cosine Rankings:", "Rank 1: In (0.8771) [GT],  Rank 2: Sn (0.8389) [Dopant],  Rank 3: Ge (0.7352),  Rank 4: P (0.6226),  Rank 5: Tl (0.6177)")
    ]
    for r_title, r_list in ranks_text:
        p_r = tf_d.add_paragraph()
        p_r.space_after = Pt(2)
        run1 = p_r.add_run()
        run1.text = f"•  {r_title} "
        run1.font.name = "Segoe UI"
        run1.font.size = Pt(10)
        run1.font.bold = True
        run1.font.color.rgb = DARK_BLUE
        run2 = p_r.add_run()
        run2.text = r_list
        run2.font.name = "Segoe UI"
        run2.font.size = Pt(9.5)
        run2.font.color.rgb = CHARCOAL
        
    p_takeaway = tf_d.add_paragraph()
    p_takeaway.space_before = Pt(3)
    p_takeaway.text = "Key Scientific Insights: 100% Hit@10 across all 3 signals confirms high candidate recall. Low pairwise Jaccard overlap (19%–33%) proves representations capture orthogonal chemical features. DeepOFM baseline & fusion calibration slated for next phase."
    p_takeaway.font.name = "Segoe UI"
    p_takeaway.font.size = Pt(9.5)
    p_takeaway.font.italic = True
    p_takeaway.font.color.rgb = CHARCOAL

    # -------------------------------------------------------------
    # SLIDE 11: Project Time Line (Plan)
    # -------------------------------------------------------------
    slide11 = prs.slides[10]
    ph11 = None
    for shape in slide11.shapes:
        if shape.name == "Content Placeholder 1":
            ph11 = shape
            break
    if ph11:
        slide11.shapes._spTree.remove(ph11._element)
        
    # Table / Gantt structure for Timeline
    t_time = slide11.shapes.add_table(6, 4, Inches(0.6), Inches(1.1), Inches(12.13), Inches(5.6))
    table11 = t_time.table
    table11.columns[0].width = Inches(2.2) # Phase / Period
    table11.columns[1].width = Inches(4.5) # Core Deliverables
    table11.columns[2].width = Inches(1.6) # Status
    table11.columns[3].width = Inches(3.83) # Outcome / Verification
    
    headers11 = ["Phase & Timeline", "Key Deliverables / Milestones", "Status", "Verification Artifacts"]
    for c_idx, h in enumerate(headers11):
        cell = table11.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_BLUE
        tf = cell.text_frame
        zero_margins(tf)
        p = tf.paragraphs[0]
        p.text = h
        p.font.name = "Segoe UI"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        
    time_data = [
        ("Phase 1: Foundations\n(Months 1–2)", "• Literature survey & research gap identification\n• 14-property master dataset curation (Z=1–94)\n• 11-case crystallographic substitution benchmark", "COMPLETED", "• elements_master.parquet (SHA256)\n• benchmark_cases.json\n• 13 passing unit tests"),
        ("Phase 2: Similarity Layer\n(Months 2–3 | S7 Mid Review)", "• Independent PN, Atom2Vec SVD & Property engines\n• Full benchmark evaluation & Jaccard overlap\n• Headline case study demonstration (β-Ga2O3)", "COMPLETED\n(FROZEN)", "• task2_benchmark_evaluation.json\n• benchmark_metrics_summary.md\n• 26 passing automated pytest tests"),
        ("Phase 3: Energetic Gating\n(Months 4–5)", "• Multi-signal fusion calibration via LOOCV\n• Wyckoff site crystal substitution generator\n• Pretrained M3GNet / MACE formation energy screening", "UPCOMING\n(Next Sprint)", "• src/fusion/fusion_engine.py\n• src/gnn_scorer/m3gnet_scorer.py\n• Energy threshold ablation tests"),
        ("Phase 4: Validation & XAI\n(Months 5–6)", "• Materials Project / OQMD StructureMatcher\n• SHAP feature attributions on physical properties\n• Gemini API grounded natural-language justifications", "PLANNED", "• src/validation/db_matcher.py\n• src/explainability/gemini_explainer.py\n• DeepOFM baseline comparative report"),
        ("Phase 5: Full Application\n(Months 6–7 | Final Review)", "• FastAPI backend + Celery worker pool + Redis\n• PostgreSQL persistence + React / 3Dmol.js UI\n• Final dissertation, deployment & paper submission", "PLANNED", "• Docker Compose containerization\n• Interactive decision-support dashboard\n• Final B.Tech Dissertation")
    ]
    for r_idx, row in enumerate(time_data):
        for c_idx, val in enumerate(row):
            cell = table11.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = LIGHT_GRAY if r_idx % 2 == 0 else WHITE
            tf = cell.text_frame
            zero_margins(tf)
            p = tf.paragraphs[0]
            p.text = val
            p.font.name = "Segoe UI"
            p.font.size = Pt(9.5)
            p.font.color.rgb = CHARCOAL
            if c_idx == 0:
                p.font.bold = True
            elif c_idx == 2:
                p.font.bold = True
                p.font.color.rgb = GREEN if "COMPLETED" in val else MAROON

    # -------------------------------------------------------------
    # SLIDE 12: Reference
    # -------------------------------------------------------------
    slide12 = prs.slides[11]
    for shape in slide12.shapes:
        if shape.name == "Content Placeholder 1":
            tf = shape.text_frame
            tf.clear()
            refs = [
                ("[1] C. Oran, R. Caputo, P. Villars, and A. Tekin, “PNcsp+: A Periodic Number-Based Crystal Structure Prediction Method Enhanced by Machine Learning,” Journal of Chemical Theory and Computation, vol. 22, pp. 3761–3771, 2026."),
                ("[2] Q. Zhou, P. Tang, S. Liu, J. Pan, Q. Yan, and S.-C. Zhang, “Atom2Vec: Learning Atoms for Materials Discovery,” Proceedings of the National Academy of Sciences USA, vol. 115, no. 25, pp. 6411–6417, 2018."),
                ("[3] M. Kusaba, C. Liu, Y. Koyama, K. Terakura, and R. Yoshida, “Recreation of the Periodic Table with an Unsupervised Machine Learning Algorithm,” Scientific Reports, vol. 11, p. 4780, 2021."),
                ("[4] T.-C. Nguyen, V.-Q. Nguyen, V.-L. Ngo, Q.-K. Than, and T.-L. Pham, “Learning Hidden Chemistry with Deep Neural Networks,” arXiv preprint arXiv:2101.11902, 2021."),
                ("[5] A. Y.-T. Wang, S. K. Kauwe, R. J. Murdock, and T. D. Sparks, “Compositionally Restricted Attention-Based Network for Materials Property Predictions,” npj Computational Materials, vol. 7, p. 77, 2021."),
                ("[6] R. Ying, D. Bourgeois, J. You, M. Zitnik, and J. Leskovec, “GNNExplainer: Generating Explanations for Graph Neural Networks,” in Advances in Neural Information Processing Systems (NeurIPS), 2019."),
                ("[7] C. Oran, R. Caputo, P. Villars, H. B. Özcü, F. H. Canbaz, and A. Tekin, “Phase Prediction via Crystal Structure Similarity in the Periodic Number Representation,” Inorganic Chemistry, vol. 63, pp. 20521–20530, 2024."),
                ("[8] V. Tshitoyan et al., “Unsupervised Word Embeddings Capture Latent Knowledge from Materials Science Literature,” Nature, vol. 571, pp. 95–98, 2019.")
            ]
            for idx, r in enumerate(refs):
                p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
                p.text = r
                p.font.name = "Segoe UI"
                p.font.size = Pt(10)
                p.font.color.rgb = CHARCOAL
                p.space_after = Pt(4)

    # Save to MATRA_S7_Mid_Review_Presentation.pptx
    output_path = 'MATRA_S7_Mid_Review_Presentation.pptx'
    prs.save(output_path)
    print(f'Successfully built presentation and saved to {output_path}')

if __name__ == '__main__':
    build_presentation()
