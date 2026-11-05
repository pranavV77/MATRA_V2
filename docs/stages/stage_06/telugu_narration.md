# Stage 6 — తెలుగు narration script

ఈ environment లో playable Telugu audio తయారు చేసే tool అందుబాటులో లేదు. ఇది పూర్తి narration script మాత్రమే; actual audio file తయారు చేశామని చెప్పడం లేదు.

## 1. ఈ స్టేజ్‌లో మనం ఏం చేస్తున్నాం?

Stage 5 లో ఒక crystal లో ఒక atom స్థానంలో మరో element పెట్టి trial structure తయారు చేశాం. కానీ చుట్టూ ఉన్న atoms ని కదపలేదు. ఇప్పుడు ఆ geometry కి pretrained MACE model ద్వారా energy మరియు forces predict చేస్తున్నాం. కావాలంటే atoms కొద్దిగా కదిలేలా చేసి relaxation చేస్తున్నాం. ఇది measured experimental result కాదు; neural potential ఇచ్చే prediction.

## 2. ఈ stage ఎందుకు అవసరం?

Replacement atom పెట్టినప్పుడు neighbors మీద forces రావచ్చు. పాత arrangement లోనే ఉంచితే అది strained configuration కావచ్చు. ఒక బంతిని ఒంపులు ఉన్న నేల మీద పెట్టినట్టు ఊహించండి. Energy అంటే ఆ landscape లో height లాంటిది. Force అంటే ఏ దిశలో కదలాలనే సూచన. Relaxation దగ్గరలో ఉన్న valley వైపు వెళ్తుంది. ఆ valley నిజమైన material కి సరిపోతుందా, అన్నిటికంటే stable గా ఉందా అనేది ఇంకా వేరే ప్రశ్న.

## 3. మనం ఏం implement చేశాం?

Project లోనే `.venv_energy` అనే isolated environment సృష్టించాం. Existing `.venv` లో Torch లేదా ASE install చేయలేదు. MACE CPU backend, request validation, output checks, relaxation, convergence reporting, JSON/CIF exports మరియు local UI connection implement చేశాం. Browser లో Structure lab కింద నాలుగో section లో ఒక candidate ని energy assessment కోసం ఎంచుకోవచ్చు.

## 4. ఏ model మరియు technologies ఉపయోగించాం?

MACE-MP-0b2-small pretrained potential, mace-torch 0.3.14, Torch 2.6 CPU, ASE, pymatgen మరియు numpy ఉపయోగించాం. Training మనం చేయలేదు. Model developers ముందే materials calculations నుంచి నేర్చుకున్న weights ని ఉపయోగిస్తున్నాం. GPU లేదా cloud ఉపయోగించలేదు. Official Hugging Face repository నుంచి exact revision download చేసి published SHA-256 తో file verify చేశాం. Actual checkpoint లో 89 elements ఉన్నాయి; మన fusion pool లో ఉన్న 79 elements అన్నీ అందులో ఉన్నాయి. Coverage ఉందంటే వాటన్నింటిపై accuracy నిరూపించామని మాత్రం కాదు.

## 5. ఇవి ఎలా పనిచేస్తాయి?

Model కి lattice, atomic identities మరియు positions ఇస్తాం. అది total energy మరియు ప్రతి atom మీద force vector ఇస్తుంది. Total energy unit eV. Energy per atom కోసం total ని atoms సంఖ్యతో divide చేస్తాం. Force unit eV per angstrom. Angstrom అంటే పది యొక్క minus ten power metre.

Force అనేది energy position derivative కి negative. Numerical check కోసం atom ని చాలా చిన్న దూరం రెండు directions లో కదిపి energies calculate చేశాం. వాటి difference తో force estimate చేశాం. Model force తో అది close గా ఉంది. కానీ రెండు values కూడా అదే model నుంచి వచ్చినవి. అందుకే దీన్ని DFT accuracy అని చెప్పలేం.

Relaxation కి FIRE optimizer ఉపయోగించాం. Lattice fixed గా ఉంటుంది; atoms మాత్రమే కదులుతాయి. ప్రతి step లో maximum displacement 0.1 angstrom. Default గా largest atomic force 0.05 eV per angstrom కన్నా తక్కువ లేదా సమానంగా వచ్చే వరకు, గరిష్ఠంగా 100 steps ప్రయత్నిస్తాం. Budget అయిపోయినా condition meet కాకపోతే not converged అని report చేస్తాం.

Stage 5 లో formal oxidation annotations partial గా ఉండొచ్చు. అవి JSON లో nonzero bookkeeping charge గా కనిపించాయి. అది నిజంగా charged electronic calculation చేయమని user ఇచ్చిన request కాదు. అందుకే source metadata ని అలాగే ఉంచి, energy model కోసం neutral atomic geometry ని explicitly తయారు చేస్తున్నాం. Charged defects లేదా donor activation calculate చేస్తున్నామని చెప్పడం లేదు.

## 6. మనకు ఏ ఫలితాలు వచ్చాయి?

మూడు selected trials evaluate చేశాం. SrTiO3 లో Ti స్థానంలో Zr ఉన్న forty-atom trial 17 steps లో converge అయింది. Maximum force సుమారు 3.65 నుంచి 0.033 eV per angstrom కి తగ్గింది. అదే trial composition కి energy సుమారు 0.8566 eV తగ్గింది.

GaN లో Ga నుంచి Al trial ఏడు steps లో, ZnS లో Zn నుంచి Cd trial ఇరవై రెండు steps లో declared threshold meet అయ్యాయి. ఈ మూడు demonstrations converge అయ్యాయి. కానీ అవి మూడు experimentally successful substitutions అని అర్థం కాదు. GaN మరియు ZnS examples లో target replacement fifty percent; వాటిని dilute doping examples అనకూడదు.

## 7. Numbers మరియు graphs అర్థం ఏమిటి?

Graph లో energy curve ప్రతి case కి తన starting value నుంచి zero గా మొదలవుతుంది. కిందకి వెళ్తే ఆ same composition లో predicted energy తగ్గిందని అర్థం. Different compositions curves ని చూసి ఎవరు ఎక్కువ stable అని rank చేయకూడదు.

Force plot లో dashed line 0.05 threshold. Final force దాని కింద ఉంటే model-local convergence condition meet అయింది. Force ప్రతి step లో తప్పనిసరిగా తగ్గదు; కొన్నిసార్లు పెరిగి మళ్లీ తగ్గొచ్చు. అందుకే actual trajectory save చేశాం.

Fresh five-atom CPU prediction median సుమారు 61 milliseconds. P95 సుమారు 66 milliseconds. Cache ని reset చేసి fresh inference measure చేశాం. Recorded isolated process peak memory సుమారు 695 MiB. Browser మరియు మొత్తం laptop memory ఇందులో లేవు. Forty-atom live HTTP request కి model startup మరియు 17-step relaxation కలిపి సుమారు 17 seconds పట్టింది. ఇవి వేర్వేరు workloads; వాటిని ఒకే speed number గా చెప్పకూడదు.

## 8. ఏ edge cases పరీక్షించాం?

Regular suite లో 510 tests pass అయ్యాయి; అందులో 32 కొత్త Stage 6 tests. Isolated energy suite లో 24 tests pass అయ్యాయి. Actual checkpoint prediction, repeated fresh inference, atom order మార్పు, rigid translation, rotation, supercell scaling, finite-difference force, convergence మరియు nonconvergence పరీక్షించాం.

Missing లేదా tampered model, project బయట model path, unsupported element, forty atoms limit, explicit charged input, NaN energy/forces, wrong force shape/type, wrong site, invalid options, different-composition comparison, busy worker, timeout మరియు failed subprocess కూడా పరీక్షించాం. Test cases లో కొన్నింటికి intentionally synthetic malformed values ఇచ్చాం. వాటిని scientific benchmark data గా చూపించడం లేదు.

## 9. ఏ సమస్యలు ఎదురయ్యాయి?

Original GitHub small model download కి connection reset errors వచ్చాయి. Official repository లో అందుబాటులో ఉన్న 0b2 small revision ని తీసుకుని exact checksum verify చేశాం. అది original 0a model కి identical అని లేదా automatically better అని చెప్పలేదు.

Current MACE release కి newer Python కావాలి. Existing Python 3.10 కోసం approved pinned 0.3.14 isolated stack install చేసి actual tests run చేశాం. Partial formal charge interpretation issue ని source bookkeeping మరియు neutral energy input విడిగా record చేయడం ద్వారా సరిచేశాం.

మొదటి timing run లో ASE unchanged geometry కి cached result ఉపయోగించింది. అందుకే అది fresh model timing కాదు అని గుర్తించి, cache reset చేసేలా మార్చి run_002 లో మళ్లీ measure చేశాం. పాత logs/results delete చేయలేదు. Browser screenshot file save కి permission error వచ్చింది; screenshot saved అని claim చేయలేదు. Actual UI results మాత్రం browser లో చూశాం.

## 10. ఇంకా ఏమి మిగిలింది?

Independent DFT numerical energy references ప్రస్తుతం admitted cases సున్నా. అందుకే energy MAE, RMSE, prediction accuracy report చేయలేదు. Formation energy కి compatible elemental references కావాలి. Energy above hull కోసం relevant competing phases కూడా కావాలి. అవి లేకుండా stable label ఇవ్వడం scientifically సరైంది కాదు.

Band gap preservation, charged defects, dilute doping activation, phonon stability మరియు finite-temperature synthesis feasibility ఇంకా assess చేయలేదు. Fixed-cell relaxation మాత్రమే చేశాం; cell dimensions/shape adjust చేయలేదు. More diverse materials మరియు clean-machine/GPU/Mac checks కూడా pending.

## 11. ఏది verified అని ఎలా నిర్ణయించాం?

Software functionality కి executed tests ఉన్నాయి. Numerical consistency కి actual energy/force calculations మరియు symmetry/gradient checks ఉన్నాయి. Reproducibility కోసం source structure hash, checkpoint hash, environment lock, parameters, raw timings మరియు trajectories ఉన్నాయి. API నుంచి వచ్చిన nonconverged one-step example కూడా CIF గా save చేసి checksum మరియు round-trip verify చేశాం.

ఇవి model యొక్క chemistry accuracy ని independently establish చేయవు. Successful execution, optimizer convergence, DFT accuracy మరియు thermodynamic stability అన్నీ వేర్వేరు validation categories అని report లో స్పష్టంగా ఉంచాం.

## 12. తర్వాత ఏం చేయాలి?

ఇప్పుడు working energy and relaxation engineering milestone ఉంది. కానీ complete scientific Stage 6 ఇంకా finish కాలేదు. Compatible independent energy references మరియు phase-reference data curate చేయడం recommended next work. Stage 7 band-gap module కి automatic గా వెళ్లడం లేదు. ఈ results మరియు limitations మీరు review చేసి informed approval ఇచ్చిన తర్వాతే scope లేదా next stage గురించి నిర్ణయిస్తాం.

Demo లో Structure lab → SrTiO3 → repeats two/two/two → analyze → Ti site eight → generate → Zr select → positional relaxation enable → predict అనే flow చూపించండి. Final force మరియు convergence చూపించి, “ఇది model prediction; stability కోసం independent reference assessment ఇంకా అవసరం” అని చెప్పండి.
