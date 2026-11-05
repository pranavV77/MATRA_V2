# Stage 1 — తెలుగు వివరణ

## Audio స్థితి

ఈ స్టేజ్‌కు playable Telugu audio తయారు కాలేదు. అందుబాటులో ఉన్న audio-generation tool లేదు. స్థానిక Windows speech engineలో Microsoft Zira Desktop అనే English en-US voice మాత్రమే కనిపించింది; Telugu voice లేదు. English voiceతో తెలుగు చదివించి దాన్ని సహజమైన Telugu audio అని చెప్పడం సరైంది కాదు. అందుకే కింద పూర్తి narration script ఇస్తున్నాం. ఆన్‌లైన్ text-to-speech సేవకు ఈ script పంపలేదు. తర్వాత మీరు అనుమతిస్తే తగిన Telugu speech విధానాన్ని విడిగా నిర్ణయించవచ్చు.

## 1. ఈ స్టేజ్‌లో మనం ఏం చేశాం?

మన MATRA ప్రాజెక్టులో కొత్త recommendation algorithm రాయడానికి ముందు, ఇప్పటికే ఉన్న పని నిజంగా ఎలా పనిచేస్తుందో పరీక్షించాం. దీన్నే baseline audit అంటాం. Baseline అంటే తర్వాత చేసే మార్పులను పోల్చడానికి ఉపయోగించే ప్రస్తుత స్థితి. ఒక ఇంటికి మరో అంతస్తు కట్టే ముందు పునాది ఎలా ఉందో చూసినట్టు, మనం data, environment, tests, similarity engines, benchmark results అన్నింటినీ పరిశీలించాం.

అన్ని కొత్త audit files మన C driveలోని Final Project directoryలోనే ఉన్నాయి. అసలు source code, dataset, పాత results మార్చలేదు. ఇప్పటికే ఉన్న presentation files కూడా అలాగే ఉంచాం.

## 2. ఇది ఎందుకు అవసరం?

ఒక script error లేకుండా నడిచిందంటే దాని chemistry సరైందని కాదు. అలాగే ఒక reportలో మంచి percentage ఉందంటే అది మళ్లీ సాధించగలమని కూడా అనుకోకూడదు. అందుకే మూడు ప్రశ్నలు వేరు చేశాం. Code పనిచేస్తుందా? అదే inputsతో అదే output మళ్లీ వస్తుందా? ఆ outputకు సరైన scientific evidence ఉందా? మొదటి రెండు విషయాల్లో ఈ స్టేజ్ స్పష్టమైన ఆధారాలు ఇచ్చింది. మూడో విషయంలో ఇంకా సరిచేయాల్సిన విషయాలు కనిపించాయి.

## 3. ఏం implement చేశాం?

Production recommendation algorithms మార్చకుండా మూడు audit tools జోడించాం. మొదటి tool environment వివరాలు, dataset hashes, పాత tests, benchmark reproduction, edge cases, fresh rebuildingని పరిశీలిస్తుంది. రెండో tool కొన్ని అదనపు సమస్యలను స్పష్టంగా పరీక్షిస్తుంది. మూడో tool actual results ఆధారంగా reports, graphs, manually open చేయగల HTML summary తయారు చేస్తుంది.

Hash అంటే file contentsకు ఒక digital fingerprint లాంటిది. మనం SHA-256 ఉపయోగించాం. అసలు 47 filesకు మొదట hash తీసుకుని, చివర మళ్లీ పోల్చాం. Audit మొదటి భాగం పూర్తయ్యాక ఆ files మారలేదని నిర్ధారించాం; చివరి verificationలో కూడా మళ్లీ పరీక్షిస్తాం. Hash సరిపోవడం file మారలేదని చెబుతుంది. అందులోని scientific value నిజమని మాత్రం చెప్పదు.

## 4. ఏ technologies ఉపయోగించాం?

ఇప్పటికే ఉన్న Python 3.10.11 virtual environment ఉపయోగించాం. Virtual environment అంటే ఈ projectకు ప్రత్యేకంగా ఉన్న Python packages సముదాయం. కొత్త environment అవసరం లేదు. NumPy numerical calculationsకు, pandas tables చదవడానికి, SciPy Atom2Vec decompositionకు, pytest tests నడపడానికి, matplotlib graphsకు ఉపయోగించాం. pathlibతో Windows pathsను నిర్వహించాం. subprocess ద్వారా existing scriptsను విడిగా నడిపి exit code, runtime, output logs భద్రపరిచాం.

Gitలో system executableతో status error వచ్చింది. కానీ bundled Gitతో status సరిగ్గా వచ్చింది. Repository configurationని మార్చాల్సిన అవసరం లేకుండా పనిచేసే executableను ఉపయోగించాం. ముందే ఉన్న local changeను తొలగించలేదు.

## 5. మన similarity methods ఎలా పనిచేస్తాయి?

PN methodలో elementsకు chemical ordering numbers ఉంటాయి. ఇవి atomic numbers కావు. Gaకు PN 83, Alకు 82. Difference 1. Similarity formula ఒకటి భాగించాలి, ఒకటి కలిపిన differenceతో. అందువల్ల ఒకటి భాగించాలి రెండుతో, అంటే 0.5 వస్తుంది. ఈ number chemical orderingలో దగ్గరతనాన్ని సూచిస్తుంది. ఏ host materialలోనైనా Al పనిచేస్తుందని ఇది ఒంటరిగా నిరూపించదు.

Atom2Vecలో known compound formulas నుంచి elements ఏ compositional environmentsలో కనిపిస్తున్నాయో matrix తయారు చేస్తాం. SVD అంటే singular value decomposition. పెద్ద sparse matrixలో ఉన్న ముఖ్యమైన patternsను కొన్ని dimensionsలో ఉంచే mathematical method. మన cacheలో 79 elementsకు 20-dimensional vectors ఉన్నాయి. రెండు vectors మధ్య cosine similarityతో దగ్గరతనం చూస్తాం. ఈ versionలో atomic coordinates ఉండవు కాబట్టి ఇది actual crystal siteని అర్థం చేసుకోదు.

Property methodలో 14 elemental features ఉన్నాయి. Electronegativity, radii, density లాంటి values అన్నీ వేర్వేరు scalesలో ఉంటాయి. Standardizationలో ప్రతి feature నుంచి mean తీసేసి standard deviationతో భాగిస్తాం. ఉదాహరణకు radius 130, mean 100, standard deviation 20 అయితే standardized value 1.5. తర్వాత vector direction ఆధారంగా cosine similarity చూస్తాం. Element densityని compound densityగా అనుకోకూడదు. ఈ features band gap preservationకు direct proof కావు.

## 6. Actual results ఏమిటి?

పాత 26 automated tests అన్నీ pass అయ్యాయి. Existing benchmarkను అసలు results overwrite కాకుండా projectలోని isolated workspaceలో నడిపాం. Rankings, scores, overlap values, summary metrics అన్నీ పాత fileతో సమానంగా వచ్చాయి. Timestamp వేరుగా రావడం సహజం.

PN Hit@1 63.64 శాతం, Atom2Vec Hit@1 కూడా 63.64 శాతం, Property Hit@1 36.36 శాతం వచ్చాయి. మొత్తం 11 primary casesలో PN, Atom2Vec రెండింటికీ ఏడు casesలో మొదటి candidate documented positive. Propertyకి నాలుగు casesలో అలాగే వచ్చింది.

మూడింటికీ Hit@10 100 శాతం వచ్చింది. దీని అర్థం ప్రతి caseలో కనీసం ఒక documented positive మొదటి పది suggestionsలో ఉందని మాత్రమే. పది suggestions అన్నీ సరైనవని కాదు. అన్ని possible materialsకు మన system 100 శాతం accurate అని అసలు కాదు.

Recall@10లో PN 96.97 శాతం, Atom2Vec 100 శాతం, Property 78.79 శాతం వచ్చాయి. ఇవి ప్రతి caseలో ఉన్న documented optionsలో ఎంత భాగం తిరిగి దొరికిందో చెప్పే average values. Benchmark చిన్నది. పదకొండు cases ఉన్నా target elements తొమ్మిదే. ఇది కొత్త unseen benchmark కాదు; legacy development benchmark.

## 7. Reproducibilityని ఎలా పరీక్షించాం?

Cache load చేసి output మళ్లీ రావడం మాత్రమే కాకుండా, raw dataset నుంచి Atom2Vecను మళ్లీ train చేశాం. Fresh training తర్వాత pairwise similaritiesలో గరిష్ఠ difference zero వచ్చింది. Supported 79 targets అన్నింటికీ Top-10 lists కూడా సమానంగా వచ్చాయి. ఇది ప్రస్తుత local software environmentలో reproducibilityకి బలమైన evidence.

Element master tableను source libraries నుంచి మళ్లీ build చేశాం. అందులోని values మాత్రమే కాకుండా Parquet file checksum కూడా అసలు fileతో సమానంగా వచ్చింది. కానీ వేరే operating system, వేరే library versionsలో కూడా ఇదే byte-level result వస్తుందని ఇప్పుడే చెప్పలేం.

## 8. ఏ edge cases పరీక్షించాం?

ఖాళీ element పేరు, తప్పు symbol, lowercase, extra spaces, formulaని element స్థానంలో ఇవ్వడం, None, number, list, dictionary ఇచ్చి చూశాం. Candidate count zero, one, చాలా పెద్ద number, negative, decimal, string, boolean values కూడా పరీక్షించాం.

Missing dataset, corrupt file, duplicate rows, missing feature, NaN, infinity, negative density, nonnumeric feature, invalid embedding cache, shape mismatch, zero vector వంటి casesను అసలు data మార్చకుండా చిన్న fixture filesతో పరీక్షించాం. Fixture అంటే ఒక సమస్యను కావాలనే చూపించడానికి తయారు చేసిన ప్రత్యేక test input.

మొదటి auditలో 73 probesలో 61 pass, 12 fail అయ్యాయి. ఇవి project-wide accuracy percentages కాదు. ఇవి కొన్ని technical expectations నెరవేరాయా లేదా అన్న checks మాత్రమే. అదనపు checksలో duplicate candidate actualగా రెండుసార్లు రావడం, zero vector cacheని reject చేయకపోవడం కూడా నిర్ధారించాం. ప్రతీ executed caseకు reportలో actual observation ఉంది. Execute చేయని testsను passగా చూపించలేదు.

## 9. ఏ సమస్యలు బయటపడ్డాయి?

Negative kకి error ఇవ్వకుండా Python slicing వల్ల పెద్ద list వచ్చింది. Trueకి ఒక candidate వచ్చింది, ఎందుకంటే Pythonలో booleanను integerలా ఉపయోగించవచ్చు. అందుకే input typesని స్పష్టంగా validate చేయాలి.

Duplicate Al row ఉన్నప్పుడు recommendationలో Al రెండుసార్లు వచ్చింది. Infinite feature, NaN embedding ఉన్నప్పుడు finite similarity బదులుగా NaN score రావచ్చు. Dimension 10 అడిగినా cacheలో ఉన్న dimension 20నే load చేస్తోంది. ఇవి తర్వాత engine-hardening stageలో address చేయాల్సిన actual defects.

Scientific documentationలో polarizability units తప్పుగా ఉన్నాయి. Installed Mendeleev library ప్రకారం అవి atomic units. Reportలో Angstrom cubed అని ఉంది. PN metadata range 103 వరకు అని చెబుతుంది, కానీ actual tableలో 117 వరకు values ఉన్నాయి. 103తో divide చేసిన normalized PN ఒకటి కంటే ఎక్కువ కావచ్చు. ప్రస్తుతం ranking engines ఈ normalized PN fieldని ఉపయోగించడం లేదు; అందువల్ల ఈ తప్పును ప్రస్తుత rankings మారిపోయాయని అర్థం చేసుకోకూడదు.

ఒక doping referenceలో ఇచ్చిన DOI SrTiO3 doping paperకు కాకుండా glass structure గురించి ఉన్న articleకు వెళ్తోంది. అందువల్ల ఆ citationని evidenceగా అంగీకరించలేం. Dopant తప్పు అని దీని అర్థం కాదు; citation తప్పు అని మాత్రమే నిర్ధారించాం. మిగతా literature claims అన్నింటినీ పూర్తిగా verify చేశామని చెప్పలేదు.

## 10. ఇంకా ఏమి మిగిలింది?

Dataset metadata, units, imputation justification, benchmark primary evidenceను తరువాతి dataset stageలో సరిచేయాలి. Input validation, duplicate handling, nonfinite data rejection, cache validationను engine stageలో బలపరచాలి. Site-aware validation, energy model, band-gap assessment, actual dilute defect physics ఇంకా implement కాలేదు.

అన్ని 118 element symbolsతో requests పంపి coverage చూసాం. PN 94 targetsను accept చేసింది. Property 88, Atom2Vec 79 targetsను accept చేశాయి. ఇది supported input coverage మాత్రమే. ఆ elementsకి అన్ని combinationsలో scientifically correct substitutions వస్తాయని కాదు. Noble gasesను PN targetగా accept చేసినా candidatesలో noble gases ఉండవు; ఇది policy consistency కోసం review చేయాలి.

## 11. ఈ స్టేజ్ పూర్తయిందని ఎలా నిర్ణయిస్తాం?

Audit పనులు చేశాం, logs ఉన్నాయి, original tests pass అయ్యాయి, legacy benchmark reproduce అయింది, fresh datasets, embeddings regenerate అయ్యాయి, సమస్యలకు executed evidence ఉంది. అందువల్ల baseline audit పని పూర్తయిందని చెప్పవచ్చు. కానీ project clean scientific pass అయిందని లేదా robust product సిద్ధమైందని చెప్పలేం. Stage completion reportలో ఈ తేడా స్పష్టంగా ఉంటుంది. Known defects ఉన్నందున next stageకి వెళ్లే ముందు మీ informed approval అవసరం.

## 12. తర్వాతి stageతో సంబంధం ఏమిటి?

తర్వాతి approved stage dataset correctness, provenance, coverage handling. ఈ auditలో వచ్చిన unit, metadata, citation findings ఆ stageకి inputs. మనం ముందుగా dataకి సరైన అర్థం ఇవ్వాలి. తర్వాత enginesని harden చేయాలి. ఆ తర్వాతే fusion వల్ల నిజంగా improvement ఉందా అని న్యాయంగా పరీక్షించగలం. ప్రతి stage తర్వాత actual resultsని వివరించి మీ approval తీసుకున్న తర్వాతే ముందుకు వెళ్తాం.
