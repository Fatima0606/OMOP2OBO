
## Clinical Data

**Dependencies:**  
- [Observational Medical Outcomes Partnership](https://www.ohdsi.org/data-standardization/the-common-data-model/) formatted data  
- [Accessing Google Service Account Json](https://stackoverflow.com/questions/46287267/how-can-i-get-the-file-service-account-json-for-google-translate-api)  

***

**Purpose:** This repository stores tab-delimited `.csv` files of clinical data that have been manually added by a user or that have been downloaded from a [Google Cloud Storage](https://cloud.google.com/storage) bucket. The algorithm utilized in this repository assumes that a separate file will be provided for each clinical domain (i.e conditions, drugs, or measurements) and that each file will contain at minimum, the following columns for each clinical domain:  
 
<br>

 _CONDITIONS (OMOP `condition_occurrence`)_  
   - **[`Condition_Occurrence Wiki Page`](https://github.com/callahantiff/OMOP2OBO/wiki/Conditions)**  
  - **[`Condition_Occurrence SQl Query`](https://gist.github.com/callahantiff/7b84c1bc063ad162bf5bdf5e578d402f/raw/2c002478192ba376b608bbcb638ce5960a4338a7/OMOPConcepts_ConditionOccurrence.sql)** 
 
CONCEPT_ID | CONCEPT_SOURCE_CODE | CONCEPT_LABEL | CONCEPT_VOCAB | CONCEPT_VOCAB_VERSION | CONCEPT_SYNONYM | ANCESTOR_CONCEPT_ID | ANCESTOR_SOURCE_CODE | ANCESTOR_LABEL | ANCESTOR_VOCAB | ANCESTOR_VOCAB_VERSION
-- | -- | -- | -- | -- | -- | -- | -- | -- | -- | --
4331309 | snomed_22653005 | Myocarditis due to infectious   agent | SNOMED | SnomedCT Release 20180131 | Myocarditis due to infectious agent \| Infective myocarditis \| Myocarditis due to infectious agent (disorder) | 4027384 \| 4027255 \| 4178818 | snomed_128139000 \| snomed_128599005 \| snomed_251052000 | Arthropod-borne disease \| Inflammatory disorder of mediastinum \| Finding by site | MedDRA \| SNOMED | MedDRA version 19.1 \| SnomedCT Release 20180131
37018594 | snomed_80251000119104 | Complement level below reference range | SNOMED | SnomedCT Release 20180131 | Complement level below reference   range \| Complement level below reference range (finding) | 36402192 \| 36313966 \| 36303153 | meddra_10061253 \| snomed_404684003 \| meddra_10027428 | Evaluation finding \| Metabolic   disorders NEC \| Measurement finding below reference range | MedDRA \| SNOMED | MedDRA version 19.1 \| SnomedCT Release 20180131
442264 | snomed_68172002 | Disorder of tendon | SNOMED | SnomedCT Release 20180131 | Disorder of tendon (disorder) \| Disorder of tendon \| Tendon disorder | 36503288 \| 36516772 \| 36303153 | meddra_10022891 \| meddra_10061253 \| snomed_123946008 | Connective tissue disorder \| Musculoskeletal finding \| Disorder of body system | MedDRA \| SNOMED | MedDRA version 19.1 \| SnomedCT Release 20180131

<br>

_MEDICATIONS (OMOP `drug_exposure`)_   
  - **[`Drug Exposure Wiki Page`](https://github.com/callahantiff/OMOP2OBO/wiki/Medications)**  
  - **[`Drug Exposure SQl Query`](https://gist.github.com/callahantiff/7b84c1bc063ad162bf5bdf5e578d402f/raw/2c002478192ba376b608bbcb638ce5960a4338a7/OMOPConcepts_DrugExposure.sql)**  

CONCEPT_ID | CONCEPT_SOURCE_CODE | CONCEPT_LABEL | CONCEPT_VOCAB | CONCEPT_VOCAB_VERSION | CONCEPT_SYNONYM | ANCESTOR_CONCEPT_ID | ANCESTOR_SOURCE_CODE | ANCESTOR_LABEL | ANCESTOR_VOCAB | ANCESTOR_VOCAB_VERSION | INGREDIENT_CONCEPT_ID | INGREDIENT_SOURCE_CODE | INGREDIENT_LABEL | INGREDIENT_VOCAB | INGREDIENT_VOCAB_VERSION | INGREDIENT_SYNONYM | INGRED_ANCESTOR_CONCEPT_ID | INGRED_ANCESTOR_SOURCE_CODE | INGRED_ANCESTOR_LABEL | INGRED_ANCESTOR_VOCAB | INGRED_ANCESTOR_VOCAB_VERSION
-- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | --
19010970 | rxnorm_11251 | Vitamin B Complex | RxNorm | RxNorm Full 20180507 | Vitamin B Complex | 19010970 | rxnorm_11251 | Vitamin B Complex | RxNorm | RxNorm | 19010970 | rxnorm_11251 | Vitamin B Complex | RxNorm | RxNorm Full 20180507 | Vitamin B Complex | 19010970 | rxnorm_11251 | Vitamin B Complex | RxNorm | RxNorm Full 20180507
19136097 | rxnorm_100213 | Bifidobacterium Infantis | RxNorm | RxNorm Full 20180507 | Bifidobacterium Infantis | 19136097 | rxnorm_100213 | Bifidobacterium Infantis | RxNorm | RxNorm | 19136097 | rxnorm_100213 | Bifidobacterium Infantis | RxNorm | RxNorm Full 20180507 | Bifidobacterium Infantis | 19136097 | rxnorm_100213 | Bifidobacterium Infantis | RxNorm | RxNorm Full 20180507
1401440 | rxnorm_198644 | Garlic preparation 100 MG Oral Tablet | RxNorm | RxNorm Full 20180507 | Garlic preparation 100 MG Oral Tablet | 40047801 \| 1401500 \| 36222902 \| 36217214 \| 1401440 \| 36222903 \| 1401437 \| 36217216 | rxnorm_198644 \| rxnorm_1163938 \| rxnorm_1163937 \| rxnorm_265647 \| rxnorm_375084 \| rxnorm_331973 \| rxnorm_1151133 \| rxnorm_1151131 | Garlic preparation 100 MG \| Pill \| Oral Product \| Garlic preparation 100 MG Oral Tablet \| Garlic preparation Oral Tablet \| Garlic preparation Pill \| Garlic preparation Oral Product \| Garlic preparation | RxNorm | RxNorm | 1401437 | rxnorm_265647 | Garlic preparation | RxNorm | RxNorm Full 20180507 | Garlic preparation | 40047801 \| 36222902 \| 1401500 \| 36217214 \| 1401440 \| 1401437 \| 36222903 \| 36217216 | rxnorm_1163937 \| rxnorm_198644 \| vrxnorm_265647 \| rxnorm_1163938 \| rxnorm_375084 \| rxnorm_331973 \| rxnorm_1151131 \| rxnorm_1151133 | Garlic preparation 100 MG \| Oral Product \| Pill \| Garlic preparation Oral Tablet \| Garlic preparation Oral Product \| Garlic preparation 100 MG Oral Tablet \| Garlic preparation \| Garlic preparation Pill | RxNorm | RxNorm Full 20180507

<br>

_MEASUREMENTS (OMOP `measurements`)_  
  - **[`Measurement Wiki Page`](https://github.com/callahantiff/OMOP2OBO/wiki/Laboratory-Tests)**  
  - **[`Measurement SQl Query`](https://gist.github.com/callahantiff/7b84c1bc063ad162bf5bdf5e578d402f/raw/2c002478192ba376b608bbcb638ce5960a4338a7/OMOPConcepts_Measurements.sql)**  

CONCEPT_ID | CONCEPT_SOURCE_CODE | CONCEPT_LABEL | CONCEPT_VOCAB | CONCEPT_VOCAB_VERSION | CONCEPT_SYNONYM | ANCESTOR_CONCEPT_ID | ANCESTOR_SOURCE_CODE | ANCESTOR_LABEL | ANCESTOR_VOCAB | ANCESTOR_VOCAB_VERSION | SCALE | RESULT_TYPE
-- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | --
40771573 | loinc_69052-9 | Flow cytometry specialist review of results | LOINC | LOINC 2.64 | Flow cytometry specialist review of results \| Flow cytometry specialist review \| Dynamic; Impression; Impression/interpretation of study; Impressions; Interp; Interpretation; Misc; Miscellaneous; Narrative; Other; Point in time; Random; Report; To be specified in another part of the message; Unspecified | 36208195 \| 36206173 \| 40771573 \| 45876017 | loinc_LP248770-2 \| loinc_69052-9 \| loinc_LP29693-6 \| MISC | Laboratory Categories \| Miscellaneous \| Lab terms not yet categorized \| Flow cytometry specialist review of results | LOINC | LOINC 2.64 | NAR | Normal/Low/High
3050001 | loinc_46252-3 | Acylcarnitine pattern [Interpretation] in Serum or Plasma | LOINC | LOINC 2.64 | Acylcarnitine pattern SerPl-Imp \| Acyl carnitine; Acylcarni; Chemistry; Impression; Impression/interpretation of study; Impressions; Interp; Interpretation; Nominal; Pl; Plasma; Plsm; Point in time; Random; SerP; SerPl; SerPlas; Serum; Serum or plasma; SR \| Acylcarnitine pattern [Interpretation] in Serum or Plasma | 3047123 \| 40785853 \| 40789215 \| 21496441 \| 40792372 \| 36206173 \| 36208195 \| 45876002 \| 40772935 \| 3050001 \| 45876249 \| 40783186 \| 45876033 \| 40794997 \| 40785803 \| 40796128 | loinc_43433-2 \| loinc_LP15318-6 \| loinc_CHEM \| loinc_LP31388-9 \| loinc_LP29693-6 \| loinc_PANEL.CHEM \| loinc_LP71614-9 \| loinc_LP248770-2 \| loinc_LP14482-1 \| loinc_LP32744-2 \| loinc_LP15705-4 \| loinc_46252-3 \| loinc_LP30844-2 \| loinc_PANEL \| loinc_LP14483-9 \| loinc_LP40271-6 | Acylcarnitine panel - Serum or Plasma \| Chemistry \| Order set \| Chemistry, challenge \| Acylcarnitine pattern \| Bld-Ser-Plas \| Carnitine \|   Urinalysis \| Acylcarnitine \| Lipids \| Acylcarnitine pattern [Interpretation] in Serum or Plasma \| Acylcarnitine pattern \| Carnitine esters \| Laboratory Categories \| Chemistry order set \| Lab terms not yet categorized | LOINC | LOINC 2.64 | NOM | Normal/Low/High

***  


### Downloading Clinical Data from Google Cloud Storage  
The repo comes with functionality to help users download data from a Google Cloud Storage bucket. In order to utilize this functionality, you need to obtain the following:  
- [x] The name of the Google Cloud Storage Bucket  
- [x] The path to the location of the data within the Google Cloud Storage bucket (e.g. `OMOP2OBO_ClinicalData`). Note that this path should point to a directory where this data is stored rather 
- [x] Service account information for the bucket where the data is stored, specifically, a service account connected to the account needs to be downloaded as a `json` file and should contain the following information (information below is fake; be sure to keep your information private, but place it somewhere in the project that is reachable by the code). For help obtaining this document see [this](https://stackoverflow.com/questions/46287267/how-can-i-get-the-file-service-account-json-for-google-translate-api) post:  

  ```python
  {
  "type": "service_account",
  "project_id": "sandbox-awesome",
  "private_key_id": "999999999999999999",
  "private_key": "-----BEGIN PRIVATE KEY-----\n123456789abcdefghhijklmnopqrstuvwxyz123456789\n-----END PRIVATE KEY-----\n",
  "client_email": "xxxxxxxx.iam.gserviceaccount.com",
  "client_id": "999",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x999/xxxxxxxx.iam.gserviceaccount.com"
   }
  ```
 
 <br>

Once the required information described above has been obtianed, run the following script from the terminal:  
   
```bash
python3 google_cloud_storage_downloader.py 
``` 
   
<br>

You will then be prompted for the information shown below specific content provided as an example):  
- The data to download from Google Cloud Storage (GCS) is stored in a bucket called `sandbox-awesome.appspot.com`  
- The data to download is stored in a directory called `clinical_data` and that directory is located within the `sandbox-awesome.appspot.com` bucket   
- Service account information for this account is stored locally at `resources/programming/google_api/sandbox-tc-43a70953c062.json`
  
```bash
The name of the GCS bucket: sandbox-awesome.appspot.com
The name of the GCS bucket directory to download data from: clinical_data
The filepath to service_account.json file: resources/programming/google_api/sandbox-awesome-99999999.json
 ```
 
_NOTE_. All data is ddownloadedd locally to `resources/clinical_data`