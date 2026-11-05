# Stage 5 — తెలుగు వివరణ script

ఈ environment లో actual playable Telugu audio generation అందుబాటులో లేదు. ఇది పూర్తి narration script. Audio file తయారు చేశామని చెప్పడం లేదు.

## 1. ఈ స్టేజ్‌లో మనం ఏం చేస్తున్నాం?

ఇంతకుముందు MATRA లో ఒక element పేరు ఇస్తే దానికి దగ్గరగా ఉన్న ఇతర elements జాబితా వచ్చేది. ఇప్పుడు ఒక actual crystal geometry తీసుకుని, దానిలో ఏ atom స్థానంలో replacement చేయాలో ఎంచుకుని, కొత్త trial structure తయారు చేస్తున్నాం. ఉదాహరణకు SrTiO3 లో Ti స్థానాన్ని Zr తో మార్చిన configuration ని CIF file గా చూడవచ్చు. ఇది ఒక candidate arrangement మాత్రమే. ఆ పదార్థం నిజంగా తయారవుతుందని ఇంకా చెప్పడం లేదు.

## 2. ఈ స్టేజ్ ఎందుకు అవసరం?

ఒకే element వేర్వేరు materials లో వేర్వేరు environments లో ఉంటుంది. ఒక building లో ఒకే రకమైన ఇటుకలు ఉన్నా, ఏ గోడలో ఉన్న ఇటుకను మారుస్తున్నామో ముఖ్యం కదా. Crystal లో కూడా atom ఏ site లో ఉంది, చుట్టూ ఎన్ని atoms ఉన్నాయి, ఎలాంటి symmetry ఉంది అనే సమాచారం అవసరం. Element similarity నుంచి material-specific పరిశోధనకి వెళ్లడానికి ఈ structure module పునాది.

## 3. మనం ఏం implement చేశాం?

CIF import, structure validation, symmetry analysis, site table, periodic neighbors, supercell creation, selected-site replacement, exact concentration calculation, supplied formal oxidation-state arithmetic, CIF మరియు JSON exports implement చేశాం. Browser లో Structure lab అనే tab ఉంది. Python command line నుంచి కూడా ఇదే pipeline వాడవచ్చు. అన్ని code, data, tests మరియు outputs C:\Final Project లోనే ఉన్నాయి.

## 4. ఏ algorithms లేదా technologies ఉపయోగించాం?

Python, numpy, pymatgen మరియు spglib ఉపయోగించాం. Pymatgen crystal lattice, coordinates మరియు structures ని నిర్వహిస్తుంది. Spglib symmetry operations ద్వారా equivalent sites ని గుర్తిస్తుంది. Stage 4 FusionEngine ఇచ్చే candidates ని అలాగే తీసుకుంటున్నాం. కొత్త site-specific success score ని ఊహించి జోడించలేదు. Local HTTP server ద్వారా browser interface పనిచేస్తుంది. ఈ stage కోసం GPU training, DFT లేదా cloud execution చేయలేదు.

## 5. అవి ఎలా పనిచేస్తాయి?

Crystal అంటే lattice మరియు atoms కలయిక. Lattice అనేది మూడు directions లో repeat అయ్యే vectors. Fractional coordinate 0.5 అంటే ఆ vector లో సగం దూరం. అది నేరుగా 0.5 angstrom అని కాదు. Cell బయట ఉన్న periodic images కూడా neighbors గా వస్తాయి. అందుకే ఒక atom మాత్రమే ఉన్న cubic cell లో కూడా ఆరు nearest periodic neighbors ఉండవచ్చు. ఆ case ని test చేశాం.

Symmetry orbit అంటే crystal rotations మరియు translations వల్ల ఒకదానికొకటి equivalent అయ్యే atom positions సమూహం. అలాంటి సమూహంలో ఒక్క atom ని మార్చే configurations symmetry-related కావచ్చు. కానీ అదే సమూహంలో రెండు atoms ని ఎన్ని విధాలుగా మార్చవచ్చో వేరే సమస్య. మనం అన్ని multi-site arrangements enumerate చేయడం లేదు.

Nearest shell కోసం ముందుగా nearest distance కనుక్కుంటాం. దానికి 1.15 రెట్ల దూరంలో ఉన్న periodic neighbors ని count చేస్తాం. Search radius ఎనిమిది angstrom. ఇది explicit geometric definition మాత్రమే; chemical bonds గుర్తించామని చెప్పలేం. Search సరిపోకపోతే completeness flag false అవుతుంది.

Supercell 2×2×2 అంటే input cell ని ఎనిమిది సార్లు repeat చేయడం. SrTiO3 base cell లో ఐదు atoms ఉంటే supercell లో నలభై ఉంటాయి. Site indices కూడా మారతాయి. అందుకే expanded structure ని analyze చేసిన తర్వాతే దానిలోని exact index ఎంచుకుంటాం.

Concentration కి denominator చాలా ముఖ్యం. ఎనిమిది Ti sites లో ఒకటి మార్చితే Ti sublattice లో 12.5 శాతం. మొత్తం నలభై atoms లో అదే ఒక్క atom అంటే 2.5 శాతం. ఈ రెండు numbers సరైనవే, కానీ వాటి అర్థాలు వేరు. Supercell పెద్దగా ఉందని isolated dilute dopant behavior established అయిందని అనుకోకూడదు.

Formal charge విషయంలో ఇచ్చిన assumptions మాత్రమే ఉపయోగిస్తాం. Ti4+ స్థానంలో Zr4+ ఉంటే delta సున్నా. Nb5+ ఉంటే delta plus one. ఇది electron carrier activation prediction కాదు. Candidate oxidation state ఇవ్వకపోతే unknown అని చూపిస్తాం. Basic UI లో candidate state ఇవ్వడం లేదు కాబట్టి charge unknown రావడం సరైన ప్రవర్తన. Python/API ద్వారా state స్పష్టంగా ఇవ్వవచ్చు.

## 6. ఎలాంటి ఫలితాలు వచ్చాయి?

మూడు hosts ని మూడు cell sizes లో పరిశీలించాం. తొమ్మిది requests నుంచి ఇరవై ఏడు trial structures తయారు చేశాం. అన్ని trials లో ఎంచుకున్న sites మాత్రమే మారాయి. Atom counts, lattice, coordinates మరియు fraction arithmetic checks pass అయ్యాయి. పూర్తి suite లో 478 tests pass అయ్యాయి. అందులో 386 పాత tests, 92 కొత్త Stage 5 tests ఉన్నాయి.

Ideal cubic SrTiO3 కి space group 221 వచ్చింది. Ideal GaN మరియు AFLOW ZnS కి 186 వచ్చింది. Ti nearest shell లో ఆరు oxygen neighbors వచ్చాయి. Ideal GaN మరియు ZnS లో tetrahedral four-neighbor geometry వచ్చింది. SrTiO3 లో oxygen nearest shell count రెండు: అది దగ్గరగా ఉన్న Ti neighbors count మాత్రమే, మొత్తం chemistry coordination కాదు.

## 7. ఆ ఫలితాల అర్థం ఏమిటి?

ఇప్పుడు మన pipeline elemental shortlist నుంచి explicit atomic configurations వరకు పనిచేస్తుందని చూపించగలం. ఇరవై ఏడు constructions correct గా ఉన్నాయంటే ఇరవై ఏడు chemically successful substitutions అని అర్థం కాదు. Coordinates మార్చకపోవడం వల్ల distance checks అలాగే ఉండటం సహజం. Atomic relaxation, energy, stability మరియు band gap ఇంకా calculate చేయలేదు.

Concentration plot లో cell పెరిగే కొద్దీ ఒక atom replacement fraction తగ్గుతుంది. Symmetry plot equivalent single-site choices ని ఎన్ని తగ్గించవచ్చో చూపిస్తుంది. ఎనిమిది equivalent Ti sites కి ఒక్క representative సరిపోతే 87.5 శాతం redundant choices తగ్గుతాయి. అది accuracy లేదా measured speedup కాదు. GaN మరియు ZnS curves overlap కావడానికి target site counts ఒకేలా ఉండటమే కారణం.

Recorded forty-atom, three-candidate warm query median సుమారు 56 milliseconds. P95 సుమారు 86 milliseconds. పది measurements మాత్రమే చేశాం. Browser, export, startup time ఇవి అందులో లేవు. Laptop load మారితే timing మారవచ్చు.

## 8. ఏ edge cases పరీక్షించాం?

Empty CIF, malformed text, oversized CIF, multiple data blocks, partial occupancy, duplicate periodic positions, overlapping atoms, NaN coordinates, invalid lattice, nonperiodic input, invalid symmetry tolerances, unavailable neighbors, wrong site index, wrong target element, unsupported candidates, duplicate candidates, invalid formal states, supercell limits, external file paths, repeated execution, mutable output isolation, unique exports, unique CIF labels, CLI errors మరియు real HTTP requests పరీక్షించాం. Executed test names మొత్తం edge_case_report.md లో ఉన్నాయి. చేయని test ని passed అని రాయలేదు.

## 9. ఏ సమస్యలు ఎదురయ్యాయి?

మొదటి test run లో ఒక పెద్ద input string మొత్తం pytest test name అయింది. Windows environment variable length limit వల్ల test setup error వచ్చింది. Short explicit test IDs ఇచ్చి సరిచేశాం. URL ని local file path గా పరిగణించి missing-file error రావడం కూడా కనిపించింది. ఇప్పుడు remote URL ని స్పష్టంగా reject చేస్తున్నాం.

AFLOW CIF లో asymmetric-unit label symmetry expansion తర్వాత repeat అయింది. Trial CIF exports కి unique labels ఇచ్చాం. Original source CIF మార్చలేదు. Source labels host analysis లో ఉన్నాయి. Warning ని error గా తీసుకుని export test చేశాం; అది pass అయింది. Initial run outputs అన్నీ ఉంచి corrected evaluation ని run_002 లో చేశాం.

Installed spglib నుంచి కొన్ని deprecation warnings వచ్చాయి. అవి nonfatal. వాటిని దాచలేదు, అవసరం లేకుండా packages upgrade చేయలేదు. Browser screenshot ని project folder లో save చేయడానికి permission error వచ్చింది. అందుకే screenshot saved అని claim చేయలేదు. Browser లో actual analysis, generation మరియు export మాత్రం చూసి నిర్ధారించాం. Scientific plots project folder లో ఉన్నాయి.

## 10. ఇంకా ఏమి మిగిలింది?

ప్రస్తుతం రెండు idealized examples మరియు ఒక sourced ZnS CIF మాత్రమే packaged గా ఉన్నాయి. పెద్ద sourced host collection, automatic formula-to-polymorph selection, experimental site-preference validation, arbitrary supercells మరియు multiple ordering arrangements ఇంకా మిగిలి ఉన్నాయి. More importantly energy, phase stability, band-gap preservation మరియు dilute doping activation ఇంకా pending. User CIF ఇచ్చినా దాని source నిజమా అని automatically ధృవీకరించలేం.

## 11. ఈ stage పూర్తయిందని ఎలా నిర్ధారించాం?

Functional checks కి 478 passing tests evidence. Deterministic repeated output, unchanged original host, source SHA-256, exact changed-site checks, CIF roundtrip మరియు real HTTP workflow evidence ఉన్నాయి. Geometric expectations ideal fixtures మరియు sourced topology తో match అయ్యాయి. Chemical substitution validity మాత్రం not verified అని report లో ప్రత్యేకంగా పేర్కొన్నాం. Source data, assumptions, units, requests, timings మరియు limitations అన్నీ recorded ఉన్నాయి. Previous results overwrite చేయలేదు.

## 12. తర్వాతి stage తో సంబంధం ఏమిటి?

ఇప్పుడు energy model కి ఇవ్వడానికి explicit ordered trial structures సిద్ధంగా ఉన్నాయి. తర్వాతి Stage 6 లో energy మరియు stability assessment కోసం model support, reference conventions మరియు limitations ని నిర్ణయించాలి. Structure ఉందని వెంటనే energy valid అవదు; model ఆ chemistry కి సరిపోతుందా అన్నది కూడా చూడాలి. ఈ Stage 5 report ని మీరు review చేసి approval ఇచ్చిన తర్వాతే ఆ పని మొదలుపెడతాం.
