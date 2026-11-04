# Stage 2 — Data correctness, provenance, coverage: తెలుగు narration

## Audio స్థితి

ఈ స్టేజ్‌కు playable Telugu audio తయారు కాలేదు. అందుబాటులో ఉన్న Windows voice English Zira మాత్రమే; తగిన Telugu synthesis tool అందుబాటులో లేదు. External speech service ఉపయోగించలేదు. కింద పూర్తి narration script ఉంది. ఇది audio file కాదు.

## 1. ఈ stageలో మనం ఏం చేస్తున్నాం?

మన recommendation system ఏ data ఆధారంగా నిర్ణయాలు తీసుకుంటుందో ఆ dataకి స్పష్టమైన అర్థం ఇవ్వడం ఈ stage పని. Stage 1లో code run అవుతుందని, పాత results మళ్లీ వస్తాయని నిర్ధారించాం. కానీ dataలో కొన్ని units, descriptions, references సరిగా లేవని తెలిసింది. ఇప్పుడు ఆ సమస్యలను versioned data releaseతో address చేశాం. Versioned అంటే పాత files అలాగే ఉంచి, కొత్త సరిచేసిన releaseని వేరుగా భద్రపరచడం.

## 2. ఇది ఎందుకు అవసరం?

ఒక value 50 అని ఉండటం సరిపోదు. అది ఏ property? Unit ఏది? Libraryలో ఎక్కడి నుంచి వచ్చింది? అది measured valueనా, calculated valueనా, estimateనా? ఏ temperature, ఏ phaseకి సంబంధించినది? ఇవన్నీ తెలియాలి. లేకపోతే reportలో సరైన-looking numbers ఉన్నా తప్పుగా అర్థం చేసుకోవచ్చు.

అందుకే provenance అనే concept ఉపయోగించాం. Provenance అంటే ఒక data valueకి సంబంధించిన మూలం, అది ఎలా వచ్చింది అనే చరిత్ర. ఉదాహరణకు Ga polarizability value 50 అయితే, అది Mendeleev libraryలోని dipole_polarizability field నుంచి వచ్చింది, unit bohr cubed అని ఇప్పుడు స్పష్టంగా ఉంటుంది. దాన్ని మనం Angstrom cubedగా చూపించడం లేదు.

## 3. ఏం implement చేశాం?

కొత్త data preparation module, validation module, source capture script, tests, reports జోడించాం. Original data files, old benchmark, three existing similarity engines మార్చలేదు. కొత్త native tableలో 94 elements, 14 physical features ఉన్నాయి. ప్రతి feature cellకి provenance ఉంది. 94ని 14తో గుణిస్తే 1,316. అన్ని 1,316 cellsకి source record పెట్టాం.

Native table అంటే library నుంచి తెలిసిన values లేదా స్పష్టంగా వివరించిన derived values ఉన్న table. మన project ఊహించి పూరించిన values ఇందులో లేవు. Missing valuesకి missing status ఉంది; zero పెట్టలేదు.

## 4. ఏ algorithms, technologies ఉపయోగించాం?

Python, pathlib, pandas, NumPy, PyArrow, pytest ఉపయోగించాం. Dataను Parquetగా భద్రపరిచాం. ఇది tableని compactగా, data typesతో నిల్వచేసే format. Source records, review ledgerని JSON, JSON Linesలో పెట్టాం. JSON Linesలో ప్రతి line ఒక స్వతంత్ర record. అందువల్ల పెద్ద provenance fileలో ఒక్క element-feature recordని కూడా సులభంగా inspect చేయవచ్చు.

DOI metadata కోసం Crossref, DataCite registriesని query చేశాం. DOI అంటే publication లేదా datasetకి ఇచ్చే persistent identifier. DOI resolve అయితే ఆ identifier ఏ titleకి చెందిందో తెలుస్తుంది. కానీ DOI resolve అవ్వడం వల్ల మన chemical claim నిజమైపోదు. ఆ paperలో నిజంగా ఏం చేశారో కూడా చదవాలి.

## 5. Missing values, estimates ఎలా handle చేశాం?

కొత్త native tableలో తొమ్మిది missing cells ఉన్నాయి. He, Ne, Arకి Pauling electronegativity మూడు. Kr, Xe, At, Rn, Frకి atomic radius ఐదు. Frకి thermal conductivity ఒకటి. మొత్తం తొమ్మిది. ఇది తొమ్మిది తప్పులు అని కాదు. తెలియని valueని తెలియనిదిగా ఉంచడం scientific honesty.

Fr thermal conductivityకి పాత codeలో 15 అని పెట్టారు. ఆ numberకి reproducible derivation లేదు. కాబట్టి కొత్త tableలో దాన్ని నిజమైన valueగా కొనసాగించలేదు. Original fileలో మాత్రం మార్చలేదు, ఎందుకంటే baselineని preserve చేయాలి.

Radius missing ఉన్న ఐదు elementsకి regression estimatesని వేరే fileలో ఇచ్చాం. Regression అంటే known examples ఆధారంగా ఒక mathematical relation fit చేయడం. Covalent radius x, atomic radius y అయితే y = a*x + b అనే line fit చేశాం. Source radii ఉన్న 89 elements మాత్రమే trainingకి ఉపయోగించాం. Benchmark substitution labels ఉపయోగించలేదు.

## 6. Regression results అర్థం ఏమిటి?

మన fitted slope సుమారు 0.8002, intercept 28.5861 pm. Covalent radius 150 pm అనే purely numerical example తీసుకుంటే estimate సుమారు 0.8002*150 + 28.5861 = 148.61 pm. ఇది formula ఎలా పనిచేస్తుందో చూపించే example మాత్రమే; కొత్త experimental element value కాదు.

Actual fitలో R-squared సుమారు 0.773 వచ్చింది. R-squared అంటే training dataలో ఉన్న variationలో fitted relation ఎంత భాగాన్ని వివరించిందో చెప్పే measure. ఇది 77.3 శాతం predictions correct అని అర్థం కాదు. పాత reportలో 0.963 అని ఉంది; అది ఈ executed fitతో సరిపోలలేదు. అందుకే actual resultనే report చేశాం.

Leave-one-element-out validationలో ఒక్కో known elementని fit నుంచి తీసేసి, మిగతావాటితో ఆ element radius predict చేశాం. అలా వచ్చిన absolute errors average సుమారు 13.29 pm. ఇది fitలో చూసిన elementsకే prediction చేయడం కంటే కఠినమైన check. అయినా missing, unstable elementsకి కూడా error ఖచ్చితంగా ఇంతే ఉంటుందని చెప్పలేం. Estimates native tableలో కలపలేదు.

## 7. Units, phase descriptionsలో ఏం మార్చాం?

PN source libraryలో పూర్తి range ఒకటి నుంచి 118. అందుకే కొత్త normalized field PNని 118తో divide చేస్తుంది. Ga PN 83 అయితే normalized value 83/118. పాత metadataలో 103తో divide చేయడం వల్ల కొన్ని values ఒకటి కంటే ఎక్కువ వచ్చాయి. Legacy engines raw PNనే ఉపయోగిస్తున్నాయి కాబట్టి వాటి outputని ఈ stageలో మార్చలేదు.

Densityని uniformly STP density అని చెప్పడం మానేశాం. Source metadataలో near-room-temperature values, gas conventions, కొన్ని theoretical estimates ఉన్నాయి. At, Fr density sourceలోనే estimates అని గుర్తించాం. అవి project imputationతో వేరే విషయం. Libraryలో value ఉంది కాబట్టి experimental measurement అని అనుకోలేదు.

పాత molar_volume column atomic weightని densityతో divide చేసి వచ్చింది. Hydrogen gasకి కూడా అదే ratio. అందువల్ల అన్ని elementsకి condensed-solid molar volume అని పిలవడం తప్పు. కొత్త field పేరు atomic_molar_volume_cm3_mol_atoms. దాని derived formula, source conditions రెండూ metadataలో ఉన్నాయి.

## 8. Benchmark auditలో ఏం తెలిసింది?

అన్ని 16 cases, మొత్తం 23 candidate assertionsని preserve చేశాం. వాటిలో 18 substitution entries, ఐదు doping entries. Six casesలో recorded identifiers వేరే chemistry లేదా వేరే material గురించి ఉన్న recordsకి వెళ్తున్నాయని గుర్తించాం. Five casesలో query చేసిన registryలో identifier resolve కాలేదు. Four casesలో topicకి సంబంధం కనిపించినా పూర్తి conditions నిర్ధారించలేదు. One caseకి review source ఉంది; direct experimental passage ఇంకా extract చేయలేదు.

404 వచ్చింది అంటే ఆ chemistry అసాధ్యం అని కాదు. Identifier typo ఉండవచ్చు, registry వేరుగా ఉండవచ్చు, correct source ఇంకా దొరకకపోవచ్చు. అలాగే title match అయితే full concentration range, Wyckoff site, phase retention అన్నీ prove అయిపోయినట్టు కాదు.

అందుకే strict contextual benchmarkలో ప్రస్తుతం zero eligible claims ఉన్నాయి. దీన్ని అన్ని substitutions తప్పు అని అర్థం చేసుకోకూడదు. మనం పెట్టుకున్న పూర్తి evidence gateని ఇంకా ఏ claim దాటలేదని మాత్రమే. Unknownని negativeగా మార్చలేదు. కొత్త scientifically validated accuracy score తయారు చేయలేదు. పాత scores legacy reproduction కోసం అలాగే ఉన్నాయి.

## 9. All-element coverage ఎలా చూపించాం?

అన్ని 118 elementsకి registry entries ఉన్నాయి. కానీ physical feature table 94 elementsకే ఉంది. మిగతా 24 elementsకి features invent చేయలేదు. Registryలో recognized, source PN available, native features available, legacy engine support, scientific validation వంటి విషయాలు వేరుగా ఉంటాయి.

ఇది ఒక person పేరు directoryలో ఉండటం, వారి పూర్తి qualification verified అవ్వడం వేర్వేరు అన్నట్టు. Element పేరు గుర్తించడం వల్ల దాని అన్ని combinationsకి recommendation scientifically valid అని చెప్పలేం.

## 10. ఏ edge cases పరీక్షించాం?

Empty table, duplicate elements, missing columns, negative density, infinity, unexpected NaN, strings బదులుగా numbers కావాల్సిన చోట strings, invalid atomic numbers, invalid symbols, wrong PN range, wrong normalization, fractional electron counts, wrong feature counts పరీక్షించాం. Provenanceలో duplicate record, missing record, wrong unit, wrong value, source లేకపోవడం కూడా reject అవుతాయో చూశాం.

Unknown benchmark claimకి accuracy credit ఇవ్వడానికి ప్రయత్నిస్తే reject అవుతుందో పరీక్షించాం. Required site, concentration, evidence class, source passage లేకుండా admission చేయలేమని పరీక్షించాం. Duplicate cases, substitution/doping mix-up కూడా పరీక్షించాం. Existing releaseని overwrite చేయకుండా refusal, project బయట output pathని reject చేయడం, same snapshotతో repeat build reproducibility కూడా పరీక్షించాం.

Final suiteలో మొత్తం 73 tests pass అయ్యాయి. వీటిలో 26 original tests, 47 కొత్త Stage 2 tests. ఇది data contracts, implementation safeguards పని చేస్తున్నాయని evidence. అన్ని chemical cases నిజమని మాత్రం ఈ tests చెప్పవు.

## 11. సమస్యలు, limitations, ఇంకా మిగిలిన పని

Source lookupలో unrelated DOI records రావడం పెద్ద research finding. Correct primary sources, exact supporting passages, concentration/site conditions ఇంకా curate చేయాలి. ఈ పని పూర్తికాకుండా new benchmark accuracy claim చేయలేం. Pipeline software passes, scientific benchmark holdలో ఉంది అని వేరుగా report చేశాం.

ఈ stageలో legacy enginesలో ఉన్న negative k, boolean k, invalid cache problemsని మార్చలేదు. అవి Stage 3 scope. కొత్త dataలో genuine missing values ఉన్నందున Stage 3లో missing-data policyని explicitly నిర్ణయించాలి. అన్ని valuesని zeroగా పూరించడం సరైన పరిష్కారం కాదు.

Live DOI API ఎప్పుడూ అదే response ఇస్తుందని guarantee లేదు. అందుకే ఈ queriesలో వచ్చిన raw responsesని local filesగా నిల్వచేశాం. Rebuild సమయంలో network మళ్లీ అవసరం లేకుండా captured snapshotతో పనిచేస్తాం. Package dependency checkలో broken requirements కనిపించలేదు; అయినా clean machine installation test జరగలేదు.

## 12. Stage complete అన్న మాటకు అర్థం, తర్వాతి సంబంధం

ఈ stageలో data engineering, explicit units, provenance, coverage registry, evidence gate implement చేసి test చేశాం. Original files preserve చేశామో final verificationలో పరీక్షిస్తాం. కానీ benchmark evidence fully verified అయిందని చెప్పడం లేదు. Reportలో software verification, scientific verification వేరు.

తర్వాతి engine stageకి వెళ్లడానికి ముందు ఈ limitations మీకు స్పష్టంగా చెప్పాలి. Scientific benchmark inactiveగా ఉండగానే engineering work కొనసాగించాలా, లేక ముందుగా source curationని ఈ stageలోనే కొనసాగించాలా అన్న నిర్ణయం మీ approvalతోనే తీసుకుంటాం. ఎలాంటి మార్గమైనా unverified positivesకి accuracy credit ఇవ్వం. అదే research-grade MATRAకి అవసరమైన నిజాయితీ.
