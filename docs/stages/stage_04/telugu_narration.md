# Stage 4 — తెలుగు వివరణ

ఇది చదివి వినిపించడానికి లేదా text-to-speech కోసం సిద్ధం చేసిన script. ఈ environment లో actual playable audio తయారు చేయలేదు.

1. ఈ స్టేజ్‌లో మనం ఏం చేస్తున్నాం?
మన MATRA లో ముందే ఉన్న PN, Atom2Vec, Property అనే మూడు similarity methods ని ఒకే pipeline లో కలిపాం. ఒక element కి దగ్గరగా కనిపించే ఇతర elements ని ఒక జాబితాలో చూపిస్తున్నాం. ఇది పరిశోధన మొదలుపెట్టడానికి shortlist మాత్రమే.

2. ఈ స్టేజ్ ఎందుకు అవసరం?
ఒక్కో method chemistry లో ఒక్కో కోణాన్ని చూస్తుంది. PN periodic ordering ని చూస్తుంది. Atom2Vec compounds లో elements కలిసి కనిపించే patterns నేర్చుకున్న vector ని ఉపయోగిస్తుంది. Property method numerical elemental features ని పోలుస్తుంది. వాటి అభిప్రాయాలు ఎక్కడ కలుస్తున్నాయి, ఎక్కడ భిన్నంగా ఉన్నాయి అనేది ఇప్పుడు చూడగలం.

3. ఏం implement చేశాం?
Fusion engine, evaluation script, local web demo, source evidence notes, JSON మరియు CSV export చేశాం. మన laptop లోనే Python server నడుస్తుంది. Browser లో formula మరియు target ఇచ్చి candidates చూడవచ్చు. Formula లో target ఉందా అని మాత్రమే చూస్తున్నాం. ఆ material structure ని ఇంకా model అర్థం చేసుకోవడం లేదు.

4. ఏ algorithms ఉపయోగించాం?
Weighted score మరియు reciprocal rank fusion ఉపయోగించాం. మొదటి method scores ని కలుపుతుంది. రెండో method ranks ని కలుపుతుంది. Equal weights అంటే ప్రతి method కి మూడో వంతు ప్రాధాన్యత. ఇవి training ద్వారా నేర్చుకున్న best weights కావు.

5. అవి ఎలా పనిచేస్తాయి?
Cosine score minus one నుంచి plus one మధ్య ఉంటుంది. దానికి one కలిపి two తో divide చేస్తే zero నుంచి one మధ్యకి వస్తుంది. ఉదాహరణకు 0.8 score, 0.9 అవుతుంది. దాన్ని మూడో వంతు weight తో multiply చేస్తే contribution 0.3. ఇలా మూడు contributions కలిపితే combined score. ఇది success probability కాదు. RRF లో మంచి rank కి ఎక్కువ contribution ఇస్తాం. Sixty అనే fixed parameter ని ఉపయోగించాం.

6. ఫలితాలు ఏమిటి?
మనకు ప్రస్తుతం రెండు eligible development references మాత్రమే ఉన్నాయి. PN MRR 1.0. Atom2Vec, weighted fusion, RRF కి 0.75. Property కి సుమారు 0.208. Fusion రెండు known candidates ని Top-3 లో చూపించింది. మొదటి స్థానంలో మాత్రం ఒకటి మాత్రమే ఉంది. ఇవి కొత్త predictions కి accuracy percentages కావు.

7. ఈ సంఖ్యల అర్థం?
MRR అంటే known candidate rank కి reciprocal తీసుకుని average చేయడం. Ranks రెండు, ఒకటి అయితే reciprocals 0.5, 1. వాటి average 0.75. Ga నుంచి Al కి PN మొదటి rank ఇచ్చింది, fusion రెండో rank ఇచ్చింది. Te నుంచి Se కి Atom2Vec రెండో rank ఇచ్చింది, fusion మొదటి rank ఇచ్చింది. కాబట్టి fusion ప్రతి సందర్భంలో better అని చెప్పలేం. Property ని తీసేస్తే ఈ రెండు cases లో score మెరుగైంది. కానీ అదే రెండు examples చూసి weights మార్చి, అదే examples మీద best model అని చెప్పడం తప్పు.

8. ఏ edge cases పరీక్షించాం?
Invalid elements, unsupported elements, wrong input types, zero weights, negative లేదా infinite weights, wrong formula, target లేని formula, duplicate rankings, invalid model scores, zero లేదా excessive k, repeated execution, output mutation, HTTP errors, oversized requests, local export paths పరీక్షించాం. మొత్తం full test suite లో 386 tests pass అయ్యాయి. Test pass అంటే code requirements ప్రకారం పనిచేసిందని అర్థం. Chemistry correct అని దానితో నిరూపించలేం.

9. ఏ సమస్యలు వచ్చాయి?
మొదట local socket permissions వల్ల HTTP tests నడవలేదు. Permission వచ్చిన తర్వాత Windows లో unread request body వల్ల error response connection reset అయింది. Bounded body ని చదివి response ఇచ్చేలా మార్చాం. తర్వాత పూర్తి test suite pass అయింది. పాత failure logs కూడా ఉంచాం.

10. ఇంకా ఏమి మిగిలింది?
Crystal structures, actual substitution sites, energy మరియు stability, band-gap preservation, dilute doping ఇంకా implement చేయాలి. అన్ని 118 elements ని గుర్తించగలం. కానీ మూడు methods కి complete common data ఉన్నవి 79 మాత్రమే. మిగతా elements కి fabricated features ఇవ్వలేదు. Doping కి పూర్తి contextual benchmark లేదు.

11. Stage verification ఎలా చేశాం?
Unit tests, real local HTTP tests, deterministic ranking checks చేశాం. Browser లో Ga example, Te example, export, evaluation table చూశాం. Numerical calculations కి tests ఉన్నాయి. రెండు scoped references కి retrieval comparison ఉంది. Independent held-out test cases సున్నా. అందుకే general scientific validity ఇంకా నిర్ధారించలేదు. Actual measurements evaluation.json లో, test execution logs లో ఉన్నాయి.

12. తర్వాతి stage కి సంబంధం?
ఇప్పుడు వచ్చిన elemental shortlist ని తర్వాత actual host structure మరియు site context తో పరిశీలించాలి. ఒక element దగ్గరగా ఉందంటే ఏ material లోనైనా replace చేయవచ్చు అని కాదు. Site, concentration, charge balance, structure relaxation వంటి అంశాలు కీలకం. మీ review మరియు approval తర్వాత మాత్రమే తదుపరి stage ప్రారంభిస్తాం. ఈ review కోసం working partial demo మరియు honest comparison plots సిద్ధంగా ఉన్నాయి.
