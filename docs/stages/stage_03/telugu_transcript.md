# తెలుగు narration — Stage 3 similarity engine hardening

Playable Telugu audio తయారు చేయలేదు. ఈ environment లో speech-generation tool అందుబాటులో లేదు.
ఇది text-to-speech కోసం ఉపయోగించగల పూర్తి narration script.

## 1. ఈ స్టేజ్‌లో మనం ఏం చేస్తున్నాం?
మన దగ్గర PN, Property, Atom2Vec అనే మూడు similarity engines ఉన్నాయి.
ఈ stage లో వాటి algorithm ని కలపడం లేదు. వాటికి తప్పు inputs వచ్చినప్పుడు సరైన error ఇవ్వడం,
చెడ్డ data లేదా cache తో recommendations ఇవ్వకుండా ఆపడం చేస్తున్నాం.

## 2. ఇది ఎందుకు అవసరం?
Calculator తప్పు input తీసుకుని సాధారణ answer చూపిస్తే మనం దాన్ని నమ్మే ప్రమాదం ఉంది.
మునుపు k=-1 ఇచ్చినా results వచ్చేవి, duplicate rows వల్ల repeated candidates వచ్చేవి,
NaN vectors కూడా cache నుంచి లోడ్ అయ్యేవి. ఇవి scientific accuracy సమస్యకు ముందున్న software సమస్యలు.

## 3. మనం ఏం implement చేశాం?
Common input validation, element support status, duplicate checks, feature validity checks,
embedding shape మరియు norm checks చేశాం. కొత్త cache లో dimension, seed, corpus hash metadata రాస్తున్నాం.
పాత working engines copies, rankings, scores ని ముందుగానే preserve చేశాం.

## 4. ఏ algorithms మరియు technologies వాడాం?
Python, numpy, pandas, scipy sparse SVD, pymatgen, pytest, matplotlib ఉపయోగించాం.
పాత మూడు algorithms అలాగే ఉన్నాయి. కొత్త dependency install చేయలేదు. Cloud లేదా GPU అవసరం రాలేదు.

## 5. మూడు engines ఎలా పనిచేస్తాయి?
PN లో periodic-number distance తక్కువైతే similarity ఎక్కువ. Formula ఒకటి భాగించు ఒకటి plus distance.
Distance రెండు అయితే score ఒకటి భాగించు మూడు, అంటే సుమారు 0.333.
Property engine లో 14 features ని standardize చేస్తాం. Mean తీసేసి standard deviation తో భాగిస్తాం.
తరువాత vectors మధ్య cosine similarity చూస్తాం. Vectors ఒకే direction లో ఉంటే score ఒకటికి దగ్గరగా ఉంటుంది.
Zero vector కి direction ఉండదు; అందుకే దానికి మౌనంగా zero score ఇవ్వకుండా error ఇస్తాం.
Atom2Vec లో compounds లో elements ఏ environments తో కలిసి కనిపిస్తున్నాయో count matrix తయారు చేస్తాం.
SVD దానిలోని ప్రధాన patterns ని చిన్న vectors లో ఉంచుతుంది. ఈ vectors మీద cosine similarity వాడతాం.
ఇవేవీ band gap లేదా stability ని నేరుగా లెక్కించవు.

## 6. Actual results ఏంటి?
చివరి పూర్తి test suite లో 320 tests pass అయ్యాయి. పాత 15 failing behaviours కి targeted regression tests pass అయ్యాయి.
మూడు engines కలిపి supported targets మీద 261 Top-10 outputs compare చేశాం; ఒక్కటి కూడా మారలేదు.
22,821 ordered pair scores compare చేశాం. తేడా సుమారు ఏడు గుణించు పది power minus పదహారు కంటే తక్కువ.
అది floating-point rounding స్థాయి. కొత్త పూర్తి corpus training కూడా పాత Atom2Vec rankings ని reproduce చేసింది.

## 7. Numbers మరియు graphs అర్థం ఏమిటి?
Score graph లో points diagonal మీద ఉండటం పాత score, కొత్త score ఒకేలా ఉన్నాయని చెబుతుంది.
అది experimental material property prediction సరైందని చెప్పదు. 15 regression checks pass అవడం software bugs సరిచేశామని చెబుతుంది.
Latency graph ఈ local run లో query కి పట్టిన milliseconds చూపిస్తుంది. Median సాధారణ measured time;
p95 అంటే 95 percent calls దానికంటే తక్కువ సమయంలో పూర్తయ్యాయి. ఒక్క run వల్ల general speedup claim చేయడం లేదు.

## 8. ఏ edge cases పరీక్షించాం?
ఖాళీ లేదా invalid element, formula బదులు symbol ఇవ్వడం, negative k, boolean k, duplicate records,
missing files, NaN, infinity, negative density, తప్పు electron counts, zero vectors, wrong cache dimensions పరీక్షించాం.
Wrong seed, changed corpus, damaged JSON, pickle అవసరమయ్యే cache, solver failure, permission failure,
మరో process file create చేసిన పరిస్థితి, వేరే working directory నుంచి execution కూడా పరీక్షించాం.
python -O లో కూడా validation ఆగిపోకుండా పని చేస్తుందని చూశాం.

## 9. ఏ సమస్యలు ఎదురయ్యాయి?
మొదటి కొత్త tests లో Windows hard-link operation కి permission denied వచ్చింది.
Windows లో existing destination ని overwrite చేయని rename పద్ధతి వాడి సమస్య సరిచేశాం.
మొదటి failed test logs తొలగించలేదు. కొత్త training సమయంలో pymatgen He electronegativity warning ఇచ్చింది;
ఆ warning log లో ఉంది. మనం He feature ని కల్పించలేదు; embeddings finite గా ఉన్నాయని checks నిర్ధారించాయి.

## 10. ఇంకా ఏం మిగిలింది?
118 elements ని recognize చేస్తాం కానీ ప్రతి engine కి అన్నింటి data లేదు. PN query support 94,
Property 88, Atom2Vec 79 మాత్రమే. Missing representation కి స్పష్టమైన unsupported error ఇస్తాం.
పాత cache లో training metadata లేదు; compatibility mode లో అది స్పష్టంగా చెబుతాం.
Strict metadata mode పాత cache ని reject చేస్తుంది; కొత్త verified experiment cache మాత్రం అందుబాటులో ఉంది.
Native Stage 2 feature release ని default గా మార్చలేదు. Mac లేదా clean machine reproduction ఇంకా పరీక్షించలేదు.

## 11. ఈ stage పూర్తి అయిందని ఎలా నిర్ధారించాం?
Executed tests, పాత behaviour comparison, pair-score invariants, కొత్త training మరియు reload,
file preservation hashes ఆధారంగా software లక్ష్యం పూర్తయిందని చెబుతున్నాం.
Scientific substitution validity మాత్రం వేరే విషయం. Benchmark ఇంకా incomplete; doping activation,
band-gap preservation, energy stability గురించి ఈ stage కొత్త claim చేయదు.

## 12. తర్వాతి stage తో సంబంధం ఏమిటి?
Stage 4 లో ఈ మూడు signals ని ఎలా కలపాలి అనేది చూస్తాం. అంతకుముందు ప్రతి signal reliable software గా పని చేయాలి.
ఇప్పుడు వాటి input, output, support limits స్పష్టంగా ఉన్నాయి. Next stage లో weights లేదా evaluation నిర్ణయాలు
విడిగా explain చేయాలి. మీ approval లేకుండా Stage 4 మొదలుపెట్టలేదు.
