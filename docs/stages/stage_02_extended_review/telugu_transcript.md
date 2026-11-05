# తెలుగు narration — Stage 2 extended evidence review

ఈ environment లో playable Telugu audio generate చేయలేదు. Speech-generation tool లేదు.
కింద ఉన్నది text-to-speech కోసం ఉపయోగించగల పూర్తి వివరణ.

1. ఈ భాగంలో మనం ఏం చేస్తున్నాం?
మన benchmark కి ఇంకొన్ని research papers ఆధారంగా నమ్మదగిన reference cases చేరుస్తున్నాం.
పాత data ని మార్చకుండా కొత్త version లో ప్రతి decision కి ఆధారం నమోదు చేస్తున్నాం.

2. ఇది ఎందుకు అవసరం?
Element recommendation అంటే రెండు elements ఒకేలా కనిపిస్తున్నాయని చెప్పడం మాత్రమే కాదు.
కొత్త element material లో సరైన స్థానంలో చేరిందా, ఏ phase లో ఉంది, ఎంత concentration వాడారో తెలుసుకోవాలి.
ఈ వివరాలు లేకుండా recommendation scientifically correct అని మార్కులు ఇవ్వలేం.

3. మనం ఏం implement చేశాం?
కొత్త evidence ledger, source-table checks, పాత 23 assertions కి follow-up requirements తయారు చేశాం.
ఒక experimental substitution reference చేరింది. మూడు అదనపు observations ని scoring బయట ఉంచాం.
పాత computational reference అలాగే ఉంది. Stage 3 మొదలుపెట్టలేదు.

4. ఏ methods వాడాం?
Local Python, JSON, SHA-256 hashes, pytest, matplotlib, PDF reading వాడాం.
కొత్త AI model train చేయలేదు. కొత్త DFT calculation కూడా నడపలేదు.
XRD అంటే X-ray diffraction: crystal లో atoms arrangement గురించి సమాచారం ఇచ్చే experiment.
XAS అంటే X-ray absorption spectroscopy: ఒక element చుట్టూ ఉన్న local environment ని పరిశీలించే పద్ధతి.

5. Site occupancy ఎలా అర్థం చేసుకోవాలి?
ఒక crystal site లో ఎంత భాగం Se ఉంది అనేదే occupancy. అదే రకం స్థానాలు cell లో ఎన్ని ఉన్నాయో multiplicity.
Outer site లో ఆరు positions ఉన్నాయి; Se occupancy 0.043. అందువల్ల modeled Se count 6 గుణించు 0.043, అంటే 0.258.
Inner site లో మూడు positions ఉన్నాయి; occupancy 0.915. Count 2.745.
మొత్తం 3.003 Se atoms ని తొమ్మిది chalcogen positions తో భాగిస్తే సుమారు 0.3337 వస్తుంది.
ఇది source model మీద చేసిన arithmetic check మాత్రమే; కొత్త chemical measurement కాదు.

6. ఏ ఫలితాలు వచ్చాయి?
ఇప్పుడు ఒక experimental substitution reference, ఒక computational substitution reference ఉన్నాయి.
పూర్తి context ఉన్న doping references ఇంకా సున్నా. మొత్తం software tests 143 pass అయ్యాయి.
ఇది పెద్ద scientific test benchmark పూర్తయిందని అర్థం కాదు.

7. Graphs అర్థం ఏమిటి?
మొదటి graph లో inner site మీద source-reported Se occupancy 91.5 percent, outer site మీద 4.3 percent చూపించాం.
Error bars paper లోని refinement uncertainty. అవి మన AI confidence కాదు.
రెండో graph లో ఎన్ని evidence records ready గా ఉన్నాయో చూపించాం. అది accuracy graph కాదు.
Se చక్కగా ఒకే site లో పూర్తిగా ఉంది అనడం తప్పు; కొంత mixing ని source report చేసింది.

8. ఏ edge cases పరీక్షించాం?
తప్పు units, infinite values, boolean values, ఖాళీ tables, duplicate sites, మొత్తం ఒకటి కాకపోయే occupancies,
మార్చిన source numbers, తప్పు multiplicity, లేని source passage, చెడిపోయిన hash పరీక్షించాం.
Unknown chemistry ని negative label చేయడం, unscored observation కి accuracy credit ఇవ్వడం కూడా reject అవుతుందా చూశాం.

9. ఏ సమస్యలు ఎదురయ్యాయి?
రెండు PDF requests కి నిజమైన PDF బదులు వేరే response వచ్చింది. వాటికి evidence credit ఇవ్వలేదు.
Sn-Ga2O3 paper లో site preference evidence దొరికింది; కానీ XAS crystal కి ఖచ్చితమైన concentration tie చేయలేకపోయాం.
Graph చూసి మనమే exact number కల్పించలేదు. Ba-Sr paper లో coordination, symmetry wording conflicts కనిపించాయి.

10. ఇంకా ఏం మిగిలింది?
మరిన్ని independent materials, site-specific doping cases, స్పష్టమైన phase-temperature details అవసరం.
పాత 23 broad assertions ఇంకా withheld గానే ఉన్నాయి. Researchers ద్వారా independent review కూడా మిగిలింది.
Band-gap preservation, energy stability, final recommendation accuracy ఇంకా పరీక్షించలేదు.

11. ఏ మేరకు విజయవంతమైంది?
Code సరిగ్గా పనిచేస్తోందని executed tests చూపించాయి. అదే cached evidence తో అదే release మళ్లీ build అవుతోంది.
కానీ రెండు development references తో అన్ని elements మీద system accurate అని చెప్పలేం.
Dopant atoms సంఖ్య, free carriers సంఖ్య ఒకటి కాదు. ఎక్కువ Sn ఉన్న amorphous film కూడా resistive గా ఉండొచ్చని source చూపించింది.
ఆ observation ని అన్ని Sn substitutions విఫలం అన్న general rule గా మార్చలేదు.

12. తర్వాతి stage తో సంబంధం ఏమిటి?
Similarity engines ని పరీక్షించడానికి సరైన answer references సిద్ధం చేస్తున్నాం.
ఇప్పుడు ఉన్న cases development కోసం మాత్రమే. Held-out test set అంటే development లో ఉపయోగించని independent పరీక్ష cases;
అవి ఇంకా సిద్ధం కాలేదు. ఒకే host family కి చెందిన samples ని వేర్వేరు independent పరీక్షలుగా లెక్కించకూడదు.
Research hold ని స్పష్టంగా ఉంచి, మీ review తర్వాతే stage మారుస్తాం.
