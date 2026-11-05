# తెలుగు వివరణ — Stage 2 primary-source verification

Playable Telugu audio ఈ environment లో తయారు చేయలేదు. Telugu speech-generation సౌకర్యం
అందుబాటులో లేదు. కింద ఉన్నది text-to-speech కోసం ఉపయోగించగల పూర్తి narration script.

## 1. ఈ భాగంలో మనం ఏం చేస్తున్నాం?
మన MATRA కోసం ఉపయోగించే reference cases నిజంగా ఏ పరిశోధన ఆధారంగా ఉన్నాయో చూస్తున్నాం.
Reference case అంటే మన సిస్టమ్ ఇచ్చే సలహాను పోల్చి చూడటానికి ఉపయోగించే ఆధారంతో కూడిన ఉదాహరణ.
ఒక paper పేరు ఉండటం సరిపోదు. మనం చెప్పే విషయం ఆ paper లో నిజంగా ఉందా అనేది చూడాలి.

## 2. ఇది ఎందుకు అవసరం?
తప్పు answer key తో పరీక్ష దిద్దితే మంచి సమాధానానికి కూడా తప్పు మార్కులు రావచ్చు.
అలాగే benchmark తప్పుగా ఉంటే model accuracy కూడా నమ్మదగినది కాదు.
అందుకే ముందుగా evidence ని సరిచూస్తున్నాం. సమాచారం దొరకలేదంటే ఆ chemistry తప్పు అని కాదు.

## 3. ఏం implement చేశాం?
పాత files మార్చకుండా కొత్త evidence ledger తయారు చేశాం. ఇందులో source link, paper file hash,
ఏ passage ఆధారమో line numbers, material, phase, site, concentration వివరాలు ఉన్నాయి.
Hash అంటే file మారిందా అని గుర్తించడానికి ఉపయోగించే digital fingerprint లాంటిది.

## 4. ఏ technologies వాడాం?
Local Python, pathlib, JSON, SHA-256, pytest, matplotlib ఉపయోగించాం.
PDF text తో పాటు ముఖ్యమైన figures ని కూడా చూశాం. కొత్త neural network train చేయలేదు.
DFT అంటే electron ప్రవర్తనను quantum-mechanics ఆధారంగా లెక్కించే పద్ధతి.
ఈసారి మనం DFT నడపలేదు; పరిశోధకులు చేసిన calculation ని reference గా నమోదు చేశాం.

## 5. Evidence check ఎలా పనిచేస్తుంది?
మొదట file hash సరిపోతుందా చూస్తాం. తరువాత చెప్పిన passage నిజంగా text లో ఉందా చూస్తాం.
Host అంటే అసలు material. Phase అంటే దాని crystal arrangement. Site అంటే crystal లో atom కూర్చునే స్థానం.
Concentration అంటే ఎంత భాగాన్ని కొత్త element తో మార్చామో చెప్పే పరిమాణం.
ఈ నాలుగు విషయాలు నిర్ధారణ కాకపోతే full contextual scoring లో case చేరదు.
Software check interpretation ని తానే నిజం చేయలేదు; మన scientific review కూడా అవసరం.

## 6. ఏ ఫలితాలు వచ్చాయి?
పద్నాలుగు source leads screen చేశాం. వాటిలో మూడు sources నుంచి మూడు ప్రత్యేక claims ని వివరంగా పరిశీలించాం.
ఒక computational substitution case కి అవసరమైన context దొరికింది.
రెండు experimental doping records కి పూర్తి context లేకపోవడంతో quantitative scoring లో పెట్టలేదు.
చివరి test run లో మొత్తం 105 tests pass అయ్యాయి. ఇవి software tests మాత్రమే.

## 7. ఈ సంఖ్యల అర్థం ఏమిటి?
Ga-Al case లో x=0.5 అంటే మొత్తం Al మరియు Ga cation స్థానాల్లో సగం Al అన్నమాట.
అది dilute doping కాదు. Re-MoS2 paper లో Mo స్థానంలో Re కనిపించింది; కొన్ని Re atoms
surface మీద adatoms గా కూడా కనిపించాయి. అందువల్ల ప్రతి Re atom substitutional అని చెప్పలేం.
Nb-SrTiO3 paper లో wt% అంటే బరువు శాతం. దాన్ని atomic percentage గా నేరుగా మార్చకూడదు.
మూడు claims లో ఒకటి ready అంటే MATRA accuracy 33 percent అని అర్థం కాదు.

## 8. ఏ edge cases పరీక్షించాం?
ఖాళీ inputs, duplicate IDs, తప్పు element పేరు, negative concentration, NaN, boolean value,
తప్పు units, లేని source file, మారిన checksum, project బయటకు వెళ్లే path, లేని passage,
metadata మాత్రమే ఉన్న source ని evidence గా చూపించడం వంటి పరిస్థితులు పరీక్షించాం.
Browser challenge page ని paper గా తీసుకోకుండా కూడా పరీక్షించాం.

## 9. ఏ సమస్యలు వచ్చాయి?
కొన్ని websites పూర్తి paper ఇవ్వలేదు. ఒక initial DOI తప్పుగా ఉంది; article header ఆధారంగా
సరైన DOI నమోదు చేసి పాత retrieval history అలాగే ఉంచాం. మొదటి test command లో లేని folder
ఇచ్చాం; దాన్ని సరిచేసి పూర్తి tests నడిపాం. ఆ failed attempt log కూడా అలాగే ఉంచాం.

## 10. ఇంకా ఏం మిగిలింది?
పాత 23 broad assertions ఇంకా scoring కి అంగీకరించలేదు. కొత్త narrow case వల్ల పాత పెద్ద
concentration range మొత్తం నిజమైపోదు. మరిన్ని primary passages, phase-specific details,
వేరే hosts, independent expert review అవసరం. Band gap లేదా stability preservation పరీక్షించలేదు.

## 11. ఏ మేరకు విజయవంతమైంది?
Evidence validation software పని చేస్తోందని, ఈ local release మళ్లీ అదే విధంగా build అవుతుందని
పరీక్షించాం. కానీ complete scientific benchmark సిద్ధమైందని చెప్పడం లేదు.
Graph లో కనిపించేవి evidence readiness counts మాత్రమే; material success rates కావు.

## 12. తర్వాతి stage తో సంబంధం ఏమిటి?
Similarity engines ని పరీక్షించేటప్పుడు trustworthy reference cases అవసరం.
ఇప్పటి evidence seed ఆ దిశగా చిన్న ముందడుగు. Stage 3 మొదలుపెట్టలేదు.
Research hold ని స్పష్టంగా ఉంచి, మిగిలిన evidence గురించి నిర్ణయం తీసుకున్న తర్వాతే ముందుకు వెళ్తాం.
