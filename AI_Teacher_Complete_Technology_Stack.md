|          | AI  | TEACHER    |     | OF    | THE              | FUTURE |           |
| -------- | --- | ---------- | --- | ----- | ---------------- | ------ | --------- |
| Complete |     | Technology |     | Stack | & Infrastructure |        | Blueprint |
Forthe10-moduleAdaptiveCognitiveAITeacher
| 1. Executive | Summary |     |     |     |     |     |     |
| ------------ | ------- | --- | --- | --- | --- | --- | --- |
ThisdocumentdefinestherecommendedtechnologystackforimplementingthecompleteAITeacherproject.The
stackisintentionallypracticalforahackathon:onemainwebfrontend,onePythonAIbackend,PostgreSQLfor
structuredlearnerdata,pgvectorforRAG,Redisfortemporarystate/jobs,AImodelprovidersbehindanabstraction
layer,andexternalvoice/avatar/videoservices.
TheassessmentpermitsLLMs,GenerativeAI,MLmodels,RAGsystems,vectordatabases,Speech-to-Text,Text-
to-Speech,AIAvatartechnologies,computervision,generativemedia,web/mobiletechnologies,cloudservices
andopen-sourceframeworks.Italsorequiresdisclosureofsignificantthird-partyAPIs,models,librariesand
services.
| 2. Recommended |     | Final | Stack                     | — Quick | View |          |     |
| -------------- | --- | ----- | ------------------------- | ------- | ---- | -------- | --- |
| Layer          |     |       | RecommendedTechnology     |         |      | Status   |     |
| Frontend       |     |       | Next.js+React+TypeScript+ |         |      | Required |     |
TailwindCSS
| Backend      |     |     | Python+FastAPI+Pydantic |     |     | Required                  |     |
| ------------ | --- | --- | ----------------------- | --- | --- | ------------------------- | --- |
| Database     |     |     | PostgreSQL              |     |     | Required                  |     |
| VectorSearch |     |     | pgvector                |     |     | RequiredforrecommendedRAG |     |
design
| Cache/Jobs     |     |     | Redis+backgroundworker   |     |     | Stronglyrecommended       |     |
| -------------- | --- | --- | ------------------------ | --- | --- | ------------------------- | --- |
| PDFProcessing  |     |     | PyMuPDF                  |     |     | RequiredforPDFpath        |     |
| DOCXProcessing |     |     | python-docx              |     |     | RequiredifDOCXsupported   |     |
| PPTXProcessing |     |     | python-pptx              |     |     | RequiredifPPTXsupported   |     |
| OCR            |     |     | TesseractorcloudOCR      |     |     | Neededforscanneddocuments |     |
| RAG            |     |     | Embeddings+hybridsearch+ |     |     | Required                  |     |
reranking
| LLM |     |     | OneormoreLLMAPIsbehinda |     |     | Required |     |
| --- | --- | --- | ----------------------- | --- | --- | -------- | --- |
ModelProviderinterface
CognitiveEngine CustomPython+PostgreSQL Requiredforstrongsolution
implementation
TeachingHarness CustomPythonstatemachine+ Requiredforrobustsolution
policyengine+Pydanticvalidation
| Visuals |     |     | SVG+LaTeX+Matplotlib+ |     |     | Stronglyrecommended |     |
| ------- | --- | --- | --------------------- | --- | --- | ------------------- | --- |
Mermaid+imagegeneration
| STT |     |     | Speech-to-TextAPI |     |     | OptionalforMVP/usefulforfull |     |
| --- | --- | --- | ----------------- | --- | --- | ---------------------------- | --- |
interaction
| TTS      |     |     | MultilingualText-to-SpeechAPI |     |     | Requiredforstrongvideodemo |     |
| -------- | --- | --- | ----------------------------- | --- | --- | -------------------------- | --- |
| Avatar   |     |     | AIavatar/videoAPI             |     |     | Required                   |     |
| Video    |     |     | FFmpeg+objectstorage          |     |     | Stronglyrecommended        |     |
| Realtime |     |     | WebSockets                    |     |     | Recommended                |     |
Storage S3-compatibleobjectstorage Requiredforproduction-likedesign
| Charts  |     |     | Recharts |     |     | Recommended |     |
| ------- | --- | --- | -------- | --- | --- | ----------- | --- |
| Testing |     |     | Pytest   |     |     | Required    |     |

| Deployment    |     | Docker+clouddeployment | Requiredforfinaldemo |
| ------------- | --- | ---------------------- | -------------------- |
| Observability |     | Structuredlogs+        | Recommended          |
OpenTelemetry/LLMtracing
| VersionControl  |          | Git+GitHub | Required |
| --------------- | -------- | ---------- | -------- |
| 3. Architecture | Overview |            |          |
STUDENT
|
v
Next.js/ReactFrontend
|
REST/WebSocket
|
v
FastAPIBackend
|
+--------------------+--------------------+
| |                   | |               | |           |     |
| ------------------- | --------------- | ----------- | --- |
| v                   | v               | v           |     |
| RAGEngine           | CognitiveEngine | AIGateway   |     |
| |                   | |               | |           |     |
| v                   | v               | v           |     |
| PostgreSQL+pgvector | LearnerModel    | ModelRouter |     |
| |                   | |               | |           |     |
+--------------------+--------------------+
|
v
TEACHINGHARNESS
State+Policy+Tools
|
+-----------------+------------------+
| |            | | |     |              |     |
| ------------ | ------- | ------------ | --- |
| v            | v v     |              |     |
| VisualEngine | TTS/STT | Avatar/Video |     |
| |            | | |     |              |     |
+-----------------+------------------+
|
v
LessonInteraction
|
v
Assessment+Adaptation
|
v
LearningAnalytics
|
+---->LearnerMemory

4. Frontend Technology Stack
4.1 Next.js
UseNext.jsasthemainwebapplicationframework.
 Studentonboarding/profile.
 Documentupload.
 Topicinput.
 Lessonconfiguration.
 AIteacherlessonplayer.
 Interactivequestioninterface.
 Assessmentscreen.
 Learningreport.
 Progressdashboard.
4.2 React
UseReactcomponentsfortheinteractiveteachingexperience.
4.3 TypeScript
UseTypeScripttokeepfrontendstateandAPIcontractsstronglytyped.
4.4 Tailwind CSS
UseTailwindforrapidhackathonUIdevelopment.
4.5 Recommended UI additions
 Rechartsforlearninganalytics.
 LucideIconsforUIicons.
 FramerMotionforsubtlelesson/playertransitions.
5. Backend Technology Stack
5.1 Python
PythonshouldbetheprimaryAI/RAG/backendlanguagebecausethedocument,retrieval,evaluationandAI
ecosystemisstrongesthere.
5.2 FastAPI
UseFastAPIasthemainbackendAPIlayer.
POST/documents/upload
POST/documents/{id}/process
POST/rag/search
POST/lessons/plan
POST/lessons/{id}/question
POST/lessons/{id}/answer
POST/lessons/{id}/replan
POST/video/segment
POST/lessons/{id}/assessment
GET /students/{id}/progress

5.3 Pydantic
UsePydantictovalidatemodeloutputsandinternalAPIcontracts.ThisisparticularlyimportantforHarness
Engineering.
classTeachingDecision(BaseModel):
action:Literal[
"TEACH",
"QUESTION",
"REEXPLAIN",
"PRACTICE",
"ADVANCE"
]
concept:str
difficulty:str
confidence:float
6. Database Technology
6.1 PostgreSQL
UsePostgreSQLasthesystem-of-recorddatabase.
Table Purpose
users Studentprofile/preferences
documents Uploadeddocumentmetadata
document_chunks RAGchunksandmetadata
concepts Conceptcatalogue/prerequisites
lessons Lesson/sessionmetadata
lesson_segments Teachingsegments/mediareferences
questions Questionsanddifficulty
answers Studentanswers/evaluations
concept_mastery Per-studentmastery
misconceptions Detectedconceptualerrors
learning_history Pastlessons/results
recommendations Revision/next-topicrecommendations
ai_traces AI/harnessobservability
7. Vector Database / RAG Technology
7.1 pgvector
Forthehackathon,PostgreSQL+pgvectoristhesimplestrecommendedchoice.Itavoidsintroducingasecond
databasewhilesupportingsemanticsimilaritysearch.
7.2 RAG Pipeline
PDF/DOCX/PPTX
|
v
Parser/OCR
|
v

Structureextraction
|
v
Semanticchunking
|
v
Embeddings
|
+------>PostgreSQL+pgvector
|
+------>Keywordindex
|
v
Hybridretrieval
|
v
Reranker
|
v
Evidencepack
|
v
LLM
7.3 Retrieval technologies
 Embeddingmodel:chooseahigh-qualitymultilingualembeddingmodelsuitableforyourlanguages.
 Keywordsearch:PostgreSQLfull-textsearchorequivalent.
 Reranking:cross-encoderorproviderreranker.
 Metadatafiltering:document,chapter,section,page,conceptanddifficulty.
 Evidencereferences:preservedocument/page/sectioninformationforgroundedanswers.
8. Document Processing Stack
Input Technology Purpose
PDF PyMuPDF Extracttext,pagesandmetadata.
DOCX python-docx Extract
paragraphs/headings/tables.
PPTX python-pptx Extractslidetextandstructure.
ScannedPDF/image TesseractorcloudOCR Convertimagetexttosearchable
text.
Imagesindocuments OCR+imageprocessing Recovertextwhererequired.
Theassessmentrequiressupportforbooks,textbooks,PDFdocuments,lecturenotes,DOC/DOCX,PPT/PPTX,
researchpapersandcoursematerial,sotheingestionlayershouldbedesignedaroundmultipledocumenttypes
ratherthanPDFonly.
9. LLM / AI Model Stack
UseanAIGatewaysothatapplicationlogicdoesnotdependdirectlyononeprovider.
AIGATEWAY
|
+----------------+----------------+

| | |
v v v
Planner Teacher Evaluator
| | |
ModelA ModelB ModelC
9.1 AI tasks
Task AIRequirement
Requestunderstanding Structuredextraction
Lessonplanning Reasoning
Explanation Generation
Questiongeneration Generation+difficultycontrol
Answerevaluation Reasoning/evaluation
Misconceptiondetection Reasoning/evaluation
Adaptiveaction Reasoning+policy
Translation Multilingualgeneration
Visualplanning Multimodal/reasoning
Learningreport Structuredsummarization
10. Cognitive Architecture Technology
TheCognitiveArchitectureisprimarilyapplicationlogicbuiltusingPython,PostgreSQLandstructuredAIoutputs.It
shouldmaintainexplicitstateratherthanrelyingonlyonconversationhistory.
CognitiveEngine
|
+--LearnerProfile
+--ConceptMastery
+--Confidence
+--Misconceptions
+--SessionMemory
+--Long-TermMemory
+--LearningHistory
+--ConceptPrerequisites
{
"student_id":"S001",
"concept_mastery":{
"voltage":0.85,
"current":0.72,
"resistance":0.32
},
"weak_concepts":["resistance"],
"misconceptions":[
{
"concept":"resistance",
"belief":"higherresistanceincreasescurrent",
"confidence":0.91
}
]
}

11. Harness Engineering Technology
HarnessEngineeringdoesnotrequireaspecialproduct.BuildadeterministiccontrollayeraroundtheLLM.
11.1 Recommended technologies
 Python
 FastAPI
 Pydantic
 PostgreSQL
 Redis
 Backgroundworkers
 Structuredlogging/tracing
11.2 Harness responsibilities
 Statemachine.
 Teachingpolicies.
 Toolregistry.
 Structuredoutputvalidation.
 Retry/fallbacklogic.
 Evidencerequirements.
 Permission/transitionchecks.
 Observability.
START
->UNDERSTAND
->PLAN
->TEACH
->QUESTION
->EVALUATE
|
+-->PASS->ADVANCE
|
+-->STRUGGLE->REEXPLAIN
->NEWEXAMPLE
->NEWQUESTION
->EVALUATE
->ASSESSMENT
->REPORT
->END
12. Redis and Background Jobs
Redisisrecommendedfortemporarysessionstate,cachingandjobcoordination.Videogenerationshouldbe
asynchronous.
Student
->FastAPI
->createmediajob
->Redis/jobqueue
->worker
->TTS
->Avatar

->FFmpeg
->ObjectStorage
->frontendpolls/WebSocketforstatus
Possibleworkerchoices:Celery,RQ,oralightweightcustomworker.Forahackathon,keeptheworker
architecturesimple.
13. Visual Intelligence Stack
Usedeterministicrenderingfortechnicalvisualswhereveraccuracymatters,andgenerativeimagemodelswhere
illustrationisappropriate.
VisualNeed RecommendedTechnology
Equations LaTeXrendering
Graphs Matplotlib
Flowcharts Mermaid/SVG
Technicaldiagrams SVG/programmaticdrawing
Code Monaco/CodeMirror
Generalillustrations Imagegenerationmodel/API
Presentationoverlays HTML/CSS/SVG
Visualflow:
Concept
->Subjectdetection
->Visualstrategy
->Visualspecification
->deterministicrendererorimagegeneration
->lessonsegment
14. Voice Stack
14.1 Student Speech
Microphone->Speech-to-Text->Studenttext->Evaluation/Teacher
14.2 Teacher Speech
Teachingscript->Text-to-Speech->Audio->Avatar/video
Forafirstdemo,typedanswersareacceptableasafallback;voiceinputcanbeaddedoncetheadaptiveloopis
stable.
15. Avatar and Video Stack
UseanexternalAIavatar/videoserviceratherthanbuildingafacialanimationsystemduringthehackathon.
Lessonscript
+
Visualplan
|
v
TTS
|

v
Avatar/videogeneration
|
v
Captions
|
v
FFmpeg/mediaprocessing
|
v
Objectstorage
|
v
Lessonplayer
Generateshortsegmentsratherthanonelargelessonvideo.Thisisessentialforadaptationbecausethesystem
needstoevaluatethestudentbeforedecidingwhatcontentcomesnext.
16. FFmpeg
 Combineaudio/videosegments.
 Convertmediaformats.
 Normalizeaudio.
 Add/preparecaptions.
 Assemblelessonsegments.
17. Object Storage
UseS3-compatibleobjectstorageforuploadeddocumentsandgeneratedmedia.
Data Storage
UploadedPDF/DOCX/PPTX Objectstorage
Parsedchunks PostgreSQL
Embeddings pgvector
Generatedaudio Objectstorage
Generatedvideo Objectstorage
Thumbnails/assets Objectstorage
PossibleprovidersincludeAWSS3,CloudflareR2orSupabaseStorage.Pickonebasedonteamfamiliarity.
18. Real-Time Communication
UseWebSocketsforapolishedinteractiveexperience.
Backendevents:
lesson_started
segment_ready
question_ready
student_answer_received
evaluation_ready
adaptation_selected

next_segment_ready
assessment_complete
Iftimeislimited,RESTpollingcanbeusedinitiallyandWebSocketsaddedlater.
19. Authentication
Forahackathon,useasimplesecureauthenticationsolution.OptionsincludeamanagedauthproviderorFastAPI
JWTauthentication.Thekeyrequirementisthatlearnerhistoryisassociatedwithastablestudentaccount/session.
| 20. Observability | and Harness | Tracing |
| ----------------- | ----------- | ------- |
RecordeveryimportantAI/harnessdecision.
session_id
student_id
current_state
current_concept
retrieval_query
retrieved_chunk_ids
model_selected
prompt_version
evaluation_score
misconception_detected
policy_decision
next_action
latency_ms
media_job_status
error/fallback
UsestructuredJSONlogsfirst.Iftimepermits,addOpenTelemetryandanLLMtracingplatformforavisible
engineeringtrace.
21. Testing Stack
UsePytestforbackend/unit/integrationtests.
| Area      |     | Test                                          |
| --------- | --- | --------------------------------------------- |
| RAG       |     | Questionretrievesthecorrectchapter/section.   |
| Grounding |     | Answerissupportedbyevidence.                  |
| Planner   |     | Requesteddurationproducesanappropriatelysized |
plan.
| Harness    |     | Illegalstatetransitionsarerejected.        |
| ---------- | --- | ------------------------------------------ |
| Evaluation |     | Knowncorrect/incorrectanswersareclassified |
correctly.
| Misconception |     | Knownmisconceptionpatternstriggertheintended |
| ------------- | --- | -------------------------------------------- |
intervention.
| Adaptation   |     | Repeatedfailurechangesteachingstrategy.       |
| ------------ | --- | --------------------------------------------- |
| Persistence  |     | Masteryfromlesson1isvisibleinlesson2.         |
| Multilingual |     | Languageswitchpreservesconcept/lessonstate.   |
| Media        |     | Video/audiogenerationfailuretriggersfallback. |

| 22. Deployment | Stack |     |     |     |
| -------------- | ----- | --- | --- | --- |
INTERNET
|
+----------+----------+
| |
v v
| Next.jsApp | FastAPIBackend |     |     |     |
| ---------- | -------------- | --- | --- | --- |
|
+---------------+---------------+
| | |
v v v
| PostgreSQL | Redis ObjectStorage |     |     |     |
| ---------- | ------------------- | --- | --- | --- |
|
pgvector
|
AIGateway
|
+---------+---------+
| | |     | |      |     |     |     |
| ------- | ------ | --- | --- | --- |
| LLM TTS | Avatar |     |     |     |
UseDockerforreproducibility.AsimpleclouddeploymentispreferabletoacomplexKubernetessetupforthe
hackathon.
| 23. Recommended | Deployment |                         | Choices |                        |
| --------------- | ---------- | ----------------------- | ------- | ---------------------- |
| Component       |            | PossibleChoice          |         | Recommendation         |
| Frontend        |            | Vercelorequivalent      |         | Simpledeployment       |
| Backend         |            | Railway/Render/AWS/GCP/ |         | Choosefamiliarprovider |
Azure
| Database |     | ManagedPostgreSQL     |     | Recommended            |
| -------- | --- | --------------------- | --- | ---------------------- |
| Redis    |     | ManagedRedis          |     | Recommendedifavailable |
| Storage  |     | S3/R2/SupabaseStorage |     | Chooseone              |
Mediaworker Samecloudorseparateworker Separateifvideoloadishigh
| CI/CD        |                | GitHubActions |                              | Recommended |
| ------------ | -------------- | ------------- | ---------------------------- | ----------- |
| 24. Required | vs Recommended |               | vs Advanced                  |             |
| Category     |                |               | Technology/Feature           |             |
| Required     |                |               | LLM/GenerativeAI             |             |
| Required     |                |               | RAG+vectorsearch             |             |
| Required     |                |               | Documentprocessing           |             |
| Required     |                |               | Lessonplanner                |             |
| Required     |                |               | Learnerpersonalization       |             |
| Required     |                |               | Interactivequestions         |             |
| Required     |                |               | Answerevaluation             |             |
| Required     |                |               | Adaptiveteaching             |             |
| Required     |                |               | Multilingualcapability       |             |
| Required     |                |               | Voice                        |             |
| Required     |                |               | AIavatar                     |             |
| Required     |                |               | Video-basedteaching          |             |
| Required     |                |               | Workingapplication/prototype |             |

StronglyRecommended PostgreSQL
StronglyRecommended pgvector
StronglyRecommended Redis/backgroundjobs
StronglyRecommended Pydanticstructuredoutputs
StronglyRecommended FFmpeg
StronglyRecommended Objectstorage
StronglyRecommended Observability
Advanced Long-termmemory
Advanced Multipleteacherpersonalities
Advanced Emotion-awareinteraction
Advanced Studyplanner
Advanced Exam/revisionmode
Advanced Flashcards
Advanced Conceptmaps
Advanced Codingdemonstrations
Advanced Personalizedhomework
Advanced Offline/localmodels
25. What the Team Should NOT Over-Engineer
 Donotbuild20microservices.
 DonotintroduceKubernetesunlesstheteamalreadyusesit.
 DonotmaintainmultipledatabaseswhenPostgreSQL+pgvectorissufficient.
 Donotbuildacustomavatarmodel.
 Donotbuildcustomspeechsynthesis.
 DonottrainanewLLM.
 Donotbuildcustomcomputervisionunlessitisessentialtoaspecificdemo.
 Donotgenerateasinglelongvideobeforestudentevaluation.
 Donotrelyonasinglegiantpromptastheentireagentarchitecture.
26. Final Recommended Stack to Lock In
FRONTEND
Next.js
React
TypeScript
TailwindCSS
Recharts
WebSocket
BACKEND
Python
FastAPI
Pydantic
DATABASE
PostgreSQL
pgvector
RAG
PyMuPDF
python-docx

python-pptx
OCR
Embeddings
HybridSearch
Reranker
COGNITIVE
CustomLearnerModel
MasteryModel
MisconceptionModel
ConceptGraph
Session+Long-TermMemory
HARNESS
CustomStateMachine
PolicyEngine
ToolRegistry
StructuredOutputValidation
Redis
BackgroundWorker
Observability
AI
LLMAPI(s)
ModelRouter
AIEvaluator
PromptRegistry
VISUAL
SVG
LaTeX
Matplotlib
Mermaid
ImageGeneration
VOICE/VIDEO
Speech-to-Text
Text-to-Speech
AIAvatarAPI
FFmpeg
ObjectStorage
DEVOPS
Git
GitHub
Docker
CI/CD
CloudDeployment

27. Module-to-Technology Mapping
Module PrimaryStack
1.Student&Input Next.js,React,TypeScript,FastAPI,Pydantic
2.DocumentProcessing+RAG Python,PyMuPDF,python-docx,python-pptx,OCR,
embeddings,pgvector
3.LearnerCognitiveModel Python,PostgreSQL,Pydantic,Redis
4.AILessonPlanner LLM,Pydantic,PostgreSQL
5.TeachingHarness Python,FastAPI,Pydantic,Redis,PostgreSQL
6.AIModelIntelligence AIGateway,LLMAPIs,provideradapters
7.Assessment+Misconception LLMevaluator,Python,PostgreSQL
8.VisualIntelligence LLMplanner,SVG,LaTeX,Matplotlib,Mermaid,image
generation
9.Voice+Avatar+Video STT,TTS,avatarAPI,FFmpeg,objectstorage
10.Analytics+Recommendation PostgreSQL,Python,LLM,Recharts
28. Development Order
1. SetupNext.js+FastAPI+PostgreSQL.
2. Implementdocumentuploadandprocessing.
3. ImplementRAGretrievalandgrounding.
4. Implementlearnercognitivestate.
5. Implementlessonplanner.
6. Implementteachingharness/statemachine.
7. Implementquestiongenerationandanswerevaluation.
8. Implementmisconceptiondetectionandadaptivere-explanation.
9. Implementfinalassessmentandlearningreport.
10. Integratevisualgeneration.
11. IntegrateTTSandavatar/video.
12. Addmultilingualsupport.
13. AddRedis/backgroundmediajobs.
14. Addobservabilityandtests.
15. Deployandrehearsethefulldemo.
29. Final Architecture Principle
ThemostimportantdesignprincipleistoseparateprobabilisticAIfromdeterministicapplicationcontrol.
PROBABILISTIC
LLM/Vision/TTS/Avatar
|
v
STRUCTUREDOUTPUT
|
v
VALIDATOR
|
v
TEACHINGPOLICY
|
v
STATEMACHINE

|
v
TOOLACTION
|
v
COGNITIVEUPDATE
Thisallowsthesystemtoremainadaptivewhilebeingpredictable,testableanddemonstrable.
30. Hackathon Decision: Minimum Stack
Ifyourteamhaslimitedtime,lockthefollowingandavoidaddingtechnologiesuntilthecoreloopworks:
Next.js
TypeScript
Tailwind
Python
FastAPI
Pydantic
PostgreSQL
pgvector
Redis
PyMuPDF
LLMAPI
Embeddingmodel
Reranker
CustomCognitiveEngine
CustomTeachingHarness
Matplotlib/SVG/LaTeX
TTS
AIAvatarAPI
FFmpeg
S3-compatiblestorage
GitHub
Docker
31. Source Alignment
ThistechnologyplanisbasedontheuploadedRound2TechnicalAssessmentfortheAIInnovationHackathon
2026.TheassessmentspecificallypermitstheAI/RAG/multimediatechnologycategorieslistedaboveandrequires
theteamtodisclosesignificantthird-partyAPIs,models,librariesandservices.Therecommendedstackisan
implementationchoiceforsatisfyingthoserequirementsefficiently;itisnotpresentedasamandatoryvendorlist
fromtheassessment.
ENDOFTECHNOLOGYSTACKBLUEPRINT