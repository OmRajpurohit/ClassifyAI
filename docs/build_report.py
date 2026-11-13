from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'ClassifyAI_AG_News_Classifier_Report.docx'
doc = Document()
sec = doc.sections[0]
sec.top_margin = Inches(.72); sec.bottom_margin = Inches(.72); sec.left_margin = Inches(.82); sec.right_margin = Inches(.82)
sec.header_distance = Inches(.35); sec.footer_distance = Inches(.35)
styles=doc.styles
styles['Normal'].font.name='Calibri'; styles['Normal'].font.size=Pt(10.3); styles['Normal'].font.color.rgb=RGBColor(45,55,72)
styles['Normal'].paragraph_format.space_after=Pt(6); styles['Normal'].paragraph_format.line_spacing=1.12
for name,size,color in [('Title',32,'12304A'),('Heading 1',21,'12304A'),('Heading 2',14,'087E83'),('Heading 3',11,'31566F')]:
 s=styles[name]; s.font.name='Calibri'; s.font.size=Pt(size); s.font.bold=True; s.font.color.rgb=RGBColor.from_string(color); s.paragraph_format.space_before=Pt(12); s.paragraph_format.space_after=Pt(6)
if 'Caption Custom' not in styles:
 s=styles.add_style('Caption Custom', WD_STYLE_TYPE.PARAGRAPH); s.font.name='Calibri'; s.font.italic=True; s.font.size=Pt(8); s.font.color.rgb=RGBColor(90,105,120)

def shade(cell, fill):
 tcPr=cell._tc.get_or_add_tcPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),fill); tcPr.append(shd)
def cell_text(cell,text,bold=False,color='2D3748',size=8.5):
 cell.text=''; p=cell.paragraphs[0]; p.paragraph_format.space_after=Pt(2); r=p.add_run(str(text)); r.bold=bold; r.font.size=Pt(size); r.font.color.rgb=RGBColor.from_string(color); cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
def table(headers,rows,widths=None):
 t=doc.add_table(rows=1, cols=len(headers)); t.style='Light Shading Accent 1'; t.alignment=WD_TABLE_ALIGNMENT.CENTER
 for i,h in enumerate(headers): cell_text(t.rows[0].cells[i],h,True,'FFFFFF',8.5); shade(t.rows[0].cells[i],'12304A')
 for ri,row in enumerate(rows):
  cells=t.add_row().cells
  for i,val in enumerate(row): cell_text(cells[i],val,False,'2D3748',8.1); shade(cells[i],'F0F6F8' if ri%2==0 else 'FFFFFF')
 if widths:
  for row in t.rows:
   for i,w in enumerate(widths): row.cells[i].width=Inches(w)
 doc.add_paragraph().paragraph_format.space_after=Pt(0)
 return t
def para(text='',boldlead=None,italic=False):
 p=doc.add_paragraph()
 if boldlead and text.startswith(boldlead): p.add_run(boldlead).bold=True; p.add_run(text[len(boldlead):])
 else: p.add_run(text).italic=italic
 return p
def bullets(items):
 for item in items:
  p=doc.add_paragraph(style='List Bullet'); p.paragraph_format.space_after=Pt(3); p.add_run(item)
def numbered(items):
 for item in items:
  p=doc.add_paragraph(style='List Number'); p.paragraph_format.space_after=Pt(3); p.add_run(item)
def heading(title,level=1): doc.add_heading(title,level=level)
def page(): doc.add_page_break()
def chapter(num,title,subtitle):
 page(); p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(100)
 r=p.add_run(f'CHAPTER {num}'); r.bold=True; r.font.size=Pt(12); r.font.color.rgb=RGBColor(8,126,131)
 p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(10); r=p.add_run(title); r.bold=True; r.font.size=Pt(28); r.font.color.rgb=RGBColor(18,48,74)
 p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=p.add_run(subtitle); r.italic=True; r.font.size=Pt(12); r.font.color.rgb=RGBColor(90,105,120)
 page()
def figure(file,caption,width=6.3):
 p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(str(ROOT/file),width=Inches(width))
 p=doc.add_paragraph(style='Caption Custom'); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run(caption)
def box(text):
 t=doc.add_table(rows=1,cols=1); c=t.cell(0,0); shade(c,'E8F5F5'); cell_text(c,text,False,'164E63',9)
 doc.add_paragraph().paragraph_format.space_after=Pt(1)
def field(run,instr):
 fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),instr); run._r.addnext(fld)

# Header and page numbering
for s in doc.sections:
 h=s.header.paragraphs[0]; h.alignment=WD_ALIGN_PARAGRAPH.RIGHT; rr=h.add_run('CLASSIFYAI  |  AG NEWS CLASSIFICATION STUDY'); rr.font.size=Pt(8); rr.font.color.rgb=RGBColor(100,115,130)
 f=s.footer.paragraphs[0]; f.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=f.add_run('Continuous Assessment 2  •  INT234  •  '); r.font.size=Pt(8); r.font.color.rgb=RGBColor(100,115,130); field(r,'PAGE')

# COVER
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(80); r=p.add_run('CONTINUOUS ASSESSMENT 2'); r.bold=True; r.font.size=Pt(16); r.font.color.rgb=RGBColor(8,126,131)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(24); r=p.add_run('CLASSIFYAI'); r.bold=True; r.font.size=Pt(38); r.font.color.rgb=RGBColor(18,48,74)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=p.add_run('AUTOMATED CLASSIFIER SELECTION\nAND AG NEWS TEXT CLASSIFICATION'); r.bold=True; r.font.size=Pt(19); r.font.color.rgb=RGBColor(35,76,98)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(14); r=p.add_run('A comparative study of Logistic Regression, Support Vector Machines, Random Forest and K-Nearest Neighbors'); r.italic=True; r.font.size=Pt(11)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(36); r=p.add_run('Lovely Professional University\nPunjab, India'); r.bold=True; r.font.size=Pt(14)
table(['SUBMISSION DETAILS',''],[
 ['Course Code','INT234'],['Student Name','Rajpurohit Omsingh'],['Registration Number','12410233'],['Submitted To','Professor Mrinali Rana'],['LinkedIn','www.linkedin.com/in/omsingh-rajpurohit']],[2.1,4.2])
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(20); r=p.add_run('Academic Project Report  |  2026'); r.font.size=Pt(10); r.font.color.rgb=RGBColor(90,105,120)

page(); heading('Student Declaration',1)
para('I, Rajpurohit Omsingh, declare that this report titled “ClassifyAI: Automated Classifier Selection and AG News Text Classification” has been prepared for Continuous Assessment 2 in course INT234. The report describes the ClassifyAI project and a reproducible, held-out comparison on the supplied AG News training file. Results are reported with their experimental scope and limitations.')
para('Student: Rajpurohit Omsingh     Registration No.: 12410233')
para('Signature: ______________________________     Date: __________________')
heading('Acknowledgement',1)
para('I express my gratitude to Professor Mrinali Rana for academic guidance and to Lovely Professional University for the opportunity to undertake this work. I also acknowledge the open-source Python and scikit-learn communities whose tools support the implementation and evaluation of machine-learning workflows.')
heading('Abstract',1)
para('This report studies ClassifyAI, a web-based machine-learning orchestration project that profiles uploaded tabular data, prepares leakage-controlled pipelines, benchmarks registered classifiers, ranks them by cross-validation performance and evaluates a selected model on a held-out test split. The report gives particular attention to Logistic Regression, Support Vector Machines (SVM), Random Forest and K-Nearest Neighbors (KNN), including their mechanics, assumptions, strengths, limitations and preprocessing requirements. It explains stratified train-test splitting, cross-validation and classification performance measures.')
para('The supplied archive contains 120,000 rows of the AG News training data, with three columns: Class Index, Title and Description. The four topic classes are exactly balanced at 30,000 examples each. Since AG News is text, the comparison uses title-plus-description TF-IDF features. On a seeded stratified 80/20 split, Logistic Regression reached 92.15% accuracy and 92.14% weighted F1; a linear SVM reached 92.20% and 92.18%; a Random Forest trained on a 20,000-row subsample reached 84.20%; and cosine-distance KNN trained on the same subsample reached 88.08%, with substantially slower prediction. Thus linear SVM is the measured accuracy leader in this run, while Logistic Regression is a near-tied, efficient and interpretable alternative. The report distinguishes this text-specific experiment from the project’s existing tabular-oriented dashboard and concludes with the author’s development of an agent that automatically profiles datasets, benchmarks candidate classifiers and recommends a suitable model.')
heading('Keywords',2); para('AG News; text classification; TF-IDF; Logistic Regression; linear SVM; Random Forest; K-Nearest Neighbors; train-test split; cross-validation; ClassifyAI; automated model selection.')

page(); heading('Contents',1)
contents=[('Executive Summary','4'),('1. Introduction','5'),('2. Project Overview and System Architecture','8'),('3. Dataset: AG News','12'),('4. Experimental Methodology','16'),('5. Classifier Algorithms','20'),('6. Train-Test Split and Validation','28'),('7. Performance Measures','32'),('8. Results and Comparative Analysis','37'),('9. ClassifyAI Dashboard Demonstration','42'),('10. The Automated Classifier Selection Agent','46'),('11. Limitations, Risks and Future Work','49'),('12. Conclusion','52'),('References','54'),('Appendices','56')]
table(['SECTION','PAGE (APPROX.)'],contents,[4.8,1.4])
para('Note: page references are approximate and depend on the word processor and installed fonts. The report is designed as a long-form academic submission; update the table of contents in Word after opening if pagination changes.')
heading('List of Figures',2)
bullets(['Figure 1. ClassifyAI dataset overview and sample preview','Figure 2. Experiment configuration and model selection controls','Figure 3. Classifier leaderboard in the dashboard demonstration','Figure 4. Cross-validation comparison visualisation','Figure 5. Prediction playground interface','Figure 6. Feature-importance interpretability note','Figure 7. Confusion matrix for the measured AG News split'])
heading('List of Tables',2)
bullets(['Dataset structure and label distribution','Comparison experiment configuration','Classifier design comparison','Held-out classifier results','Confusion matrix for the linear SVM','Project modules and future text-agent extension'])

page(); heading('Executive Summary',1)
para('ClassifyAI is a full-stack academic project for automating the early stages of supervised classification. A user uploads a CSV, chooses a target, selects models and evaluation settings, and runs an orchestration agent. The backend profiles the dataset, constructs preprocessing pipelines, evaluates algorithms by stratified cross-validation, applies deterministic ranking rules and tests the selected pipeline on a held-out set. The React dashboard presents the workflow through dataset summaries, a leaderboard, comparisons, diagnostics and an inference playground.')
para('This report focuses on four widely used classifiers. Logistic Regression is a regularised linear probabilistic classifier. SVMs select a maximum-margin decision boundary; a linear SVM is particularly effective for sparse text. Random Forest averages many randomized decision trees and is robust on many tabular tasks, but sparse word-vector spaces challenge its split-based representation. KNN assigns the majority class among nearby examples; in high-dimensional text spaces, distance computations at prediction time are expensive.')
box('Dataset identity and scope: the uploaded archive is the 120,000-row AG News training CSV, not the full 127,600-example train-plus-test release. This analysis uses only the supplied file.')
para('The label counts are exactly balanced: World, Sports, Business and Sci/Tech each have 30,000 rows. The uploaded table has zero missing values and zero exact duplicate rows. Its fields are one integer class label, a short news headline and a longer article description. Together, the text fields are the predictors; Class Index is the target. Raw category ids 1–4 are mapped to readable topic names for explanation.')
para('The controlled comparison uses a fixed random seed, an 80/20 stratified split, and word-level TF-IDF unigram/bigram features. Logistic Regression and linear SVM are fitted on all 96,000 training rows. To keep runtime practical, Random Forest and KNN use a reproducible stratified 20,000-row subsample from the training partition and are evaluated on the same 24,000-row test set. This difference in training-set size means their scores are informative but not a perfectly equal-resource comparison. The results are one held-out run, not cross-validated estimates or a hyperparameter search.')
table(['Model / training protocol','Accuracy','Weighted precision','Weighted recall','Weighted F1','Test prediction time'],[
 ['Linear SVM; 96,000 train','92.20%','92.19%','92.20%','92.18%','0.021 s'],
 ['Logistic Regression; 96,000 train','92.15%','92.14%','92.15%','92.14%','0.026 s'],
 ['KNN cosine; 20,000 train sample','88.08%','88.05%','88.08%','88.06%','29.519 s'],
 ['Random Forest; 20,000 train sample','84.20%','84.20%','84.20%','84.11%','0.133 s']], [2.3,.7,1, .8,.8,1.1])
para('The linear SVM ranks first on accuracy and weighted F1 by only about 0.06 percentage points over Logistic Regression. Given that narrow margin and the absence of repeated validation, this should be described as the best observed model for this split, not a proven universal winner. Both linear methods substantially outperform the reduced-sample Random Forest and KNN runs and predict rapidly. ClassifyAI’s key contribution is an agent that makes this evaluation process repeatable and explainable; support for text vectorization is a clear next development step.')

chapter('1','Introduction','Problem context, aims and report boundaries')
heading('1.1 Background',2)
para('Classification assigns an input to one category from a finite set. It underpins spam filtering, document routing, image recognition, fraud screening and topic tagging. A practical classifier is not only an estimator: performance depends on data quality, representation, preprocessing, validation design, metric choice and deployment constraints. A model-selection workflow therefore needs to compare candidates under a controlled protocol and communicate why one is preferred.')
para('The project addressed in this report, ClassifyAI, makes that workflow visible. It combines a Python FastAPI service and scikit-learn models with a React dashboard. The system aims to reduce manual setup by identifying column types, handling missing values, applying transformations inside pipelines and comparing candidate algorithms. In a conventional tabular task, this approach can make an experiment easier to reproduce and audit.')
para('The supplied dataset introduces an important change in data modality. AG News examples are documents, not rows of ordinary numeric measurements. A document must be transformed into a feature representation such as TF-IDF before classical classifiers can use it. This report therefore describes both the project as implemented and a separate text-specific benchmark on the submitted archive.')
heading('1.2 Problem statement',2)
para('Given a labelled news headline and description, predict one of four broad topic categories. The study also asks how four classifier families compare on this dataset and which should be selected when predictive quality, runtime and model characteristics are considered together. A second, system-level objective is to explain how an automated agent can profile an unfamiliar dataset, benchmark models and recommend a classifier with an auditable rationale.')
heading('1.3 Objectives',2)
numbered(['Describe the source file, columns, target labels and data quality.','Explain Logistic Regression, SVM, Random Forest and KNN in practical and mathematical terms.','Explain stratified train-test splitting, cross-validation and prevention of data leakage.','Define accuracy, precision, recall, F1, balanced accuracy, ROC-AUC, confusion matrices and timing measures.','Run and document a reproducible held-out comparison on the supplied AG News file.','Present the ClassifyAI dashboard screenshots as a demonstration of the implemented interface.','Describe the author-developed classifier-selection agent and identify responsible next steps for text support.'])
heading('1.4 Research questions',2)
bullets(['What is the shape, label distribution and quality profile of the supplied AG News sample?','How do the four classifiers differ in decision rule, assumptions, computation and interpretability?','Which candidate performed best under the reported split and feature representation?','How should the project agent select and justify a classifier for an uploaded dataset?'])
heading('1.5 Scope and interpretation',2)
para('The measured classifier comparison is an independent, script-based text experiment. It does not claim that the screenshots depict AG News model results. The supplied screenshots show ClassifyAI’s web dashboard operating in a tabular classification demonstration, including a separate sample schema with fields such as Age, EstimatedSalary, Gender and Purchased. Those values and visible scores are interface examples only and are not used as AG News evidence.')
para('The archive contains only the supplied training CSV. No official AG News test file was provided, so the study creates its own stratified 20% held-out test partition. Because the tree and KNN fits required a smaller training subsample to keep computation feasible, the results are not a perfectly equal-resource benchmark. The report records this limitation alongside each relevant result.')
heading('1.6 Report organisation',2)
para('Chapters 2–3 describe the software and dataset; Chapters 4–7 explain experimental design, classifiers, splitting and metrics; Chapter 8 presents measured results; Chapter 9 documents the visual interface; Chapter 10 describes the agent; Chapter 11 records limitations and future work; and Chapter 12 summarises the findings.')
heading('1.7 Project significance',2)
para('Classifier selection is often taught as a sequence of isolated model-fitting exercises. In applied work, users also need to make choices about data typing, missingness, validation design, preprocessing, metrics and operational trade-offs. ClassifyAI’s educational value is that it brings these choices into one workflow and makes the intermediate evidence visible. The leaderboard and audit trail turn an estimator comparison into a repeatable experiment that can be discussed, questioned and improved.')
para('The AG News case study adds a second lesson: automatic model selection must account for the type of input. A tabular transformation that is reasonable for a small number of categories can be inappropriate for raw documents. The agent must recognize the representation problem before it chooses a classifier. This observation connects the algorithm comparison to a practical engineering roadmap rather than treating the reported score as a standalone endpoint.')

chapter('2','Project Overview and System Architecture','How the software components work together')
heading('2.1 System summary',2)
para('ClassifyAI is a browser-based machine-learning workbench. A user uploads a CSV through the frontend; the API parses it and returns a profile, candidate target columns and preview rows. The user selects a target, algorithms, a primary score, number of cross-validation folds and test proportion. The agent then runs the requested experiment and returns ranked models, a winner, test diagnostics and an execution log.')
heading('2.2 Frontend',2)
para('The React dashboard provides upload controls and a staged analysis view. The interface contains a dataset overview, target analysis, experiment configuration, live execution logs, a classifier leaderboard, performance charts, a held-out confusion matrix, feature-importance display and interactive prediction form. The screenshots supplied with the task document this experience. They are arranged in the dashboard chapter and captioned as software demonstrations.')
heading('2.3 Backend services',2)
table(['Module','Responsibility'],[
 ['FastAPI routes','Health/algorithm discovery, CSV preview, target analysis, experiment run, results retrieval and prediction endpoints.'],
 ['Data analyzer','Row/column counts, dtypes, missing values, duplicates, target candidates and class distribution.'],
 ['Preprocessing','Separates target, encodes class labels, imputes numeric/categorical features, optionally scales numeric data and one-hot encodes categories.'],
 ['Classifier registry','Maps stable algorithm identifiers to estimator factories and metadata.'],
 ['Model evaluator','Runs stratified K-fold validation and computes fold-level classification metrics and timing.'],
 ['Model ranker','Sorts successful candidates using the selected score, variability, secondary metrics and training duration.'],
 ['Model trainer','Fits the selected pipeline and measures performance on the isolated held-out test split.'],
 ['Classifier agent','Coordinates validation, profiling, splitting, model evaluation, ranking, final fitting and audit logs.']], [1.5,5.0])
heading('2.4 Data flow',2)
numbered(['Upload CSV bytes and validate the file.','Infer basic column types and display a profile.','Select a target and inspect class counts.','Separate features from target; encode labels.','Create an outer stratified training/test partition.','Cross-validate each candidate using only the training partition.','Rank candidates by the selected primary metric and deterministic tie-breakers.','Fit the selected pipeline on all training data.','Evaluate once on the untouched test data and expose prediction capability.'])
heading('2.5 Methodological strengths in the codebase',2)
bullets(['The scikit-learn Pipeline keeps imputation, scaling and encoding inside each training fold, limiting leakage.','A fixed random seed makes the split and stochastic estimators repeatable.','Stratified splitting preserves class proportions in classification partitions.','Individual estimator failures are recorded rather than stopping all comparisons.','Ranking uses a primary metric, fold variability and tie-break metrics.','The held-out set is reserved for final evaluation after model selection.'])
heading('2.6 Architectural boundary for AG News',2)
para('The current preprocessing service identifies numeric and categorical columns and applies median/mode imputation, standard scaling and one-hot encoding. An article description is a high-cardinality text string: treating each unique document as a categorical level is not a useful semantic representation, and one-hot encoding it would be impractical. AG News therefore needs a text transformer such as TfidfVectorizer or a hashing/embedding representation, combined with sparse-compatible classifiers. Supporting text requires a modality-aware pipeline, not merely changing the selected target column.')
box('Implementation distinction: the dashboard establishes the autonomous selection workflow for tabular data. The AG News results in this report were generated with a dedicated TF-IDF experiment; they should not be represented as a completed AG News run inside the existing dashboard.')
heading('2.7 API and experiment lifecycle',2)
para('The API exposes health and algorithm discovery routes, CSV preview, target analysis, experiment execution, result retrieval and prediction with a fitted winner. Uploaded datasets and experiment objects are held in process memory, which is appropriate for a local academic demonstration but not a durable multi-user deployment. Restarting the backend clears those registries. A production version would need authenticated sessions, artifact persistence, storage quotas and explicit deletion/retention policy.')
para('Each experiment response includes a unique identifier, configuration, dataset profile, target profile, ranked model list, failed model records, winning model detail, class mapping and agent logs. Separating these outputs makes the workflow inspectable: the dashboard can display the same structured result while the backend owns experiment logic and the frontend focuses on interaction and visual communication.')
heading('2.8 Design principle: preprocessing and estimator as one object',2)
para('A preprocessing pipeline should travel with its classifier. If a user saves only the estimator and later applies a different scaler, category vocabulary or text vectorizer, inference will not match training. The project already builds a scikit-learn Pipeline for tabular transformations and the estimator. A text extension should preserve this pattern by placing the vectorizer and classifier into a single fitted pipeline and serializing the whole object as one versioned artifact.')

chapter('3','Dataset: AG News','Structure, labels and data preparation')
heading('3.1 Source file and dimensions',2)
para('The submitted archive is train.csv.zip, containing one member named train.csv. Reading that member yields 120,000 records and three columns. This is the commonly distributed AG News training partition. It is not a single complete train-plus-test release: the widely used full release includes a separate 7,600-row test set, which was not supplied here.')
table(['Field','Observed type','Role','Description'],[
 ['Class Index','Integer','Target','Topic identifier, values 1, 2, 3 or 4.'],
 ['Title','Text/object','Predictor','Short news headline.'],
 ['Description','Text/object','Predictor','News summary/article description.']], [1.3,1.1,1.0,3.3])
heading('3.2 Topic labels',2)
table(['Class Index','Readable category','Rows','Share'],[
 ['1','World','30,000','25%'],['2','Sports','30,000','25%'],['3','Business','30,000','25%'],['4','Sci/Tech','30,000','25%']], [1.2,2.0,1.3,1.2])
para('The sample is exactly balanced. A naïve majority-class predictor therefore achieves 25% accuracy. Balance reduces the need for class-weighted or resampling strategies for this benchmark and makes accuracy easier to interpret than it would be on a strongly skewed target. Macro-F1 remains useful because it checks that performance is not concentrated in only a subset of topics.')
heading('3.3 Data quality checks',2)
table(['Diagnostic','Observed result','Interpretation'],[
 ['Total rows','120,000','Large enough for a meaningful train/test experiment.'],['Columns','3','One target and two text inputs.'],['Missing values','0','No missing-value imputation is required for this file.'],['Exact duplicate rows','0','No exact duplicate records detected.'],['Rows per class','30,000 each','Four balanced classes.'],['Description length','Median 188 characters; mean about 193 characters','Compact documents; lengths vary and are right-skewed.']], [1.6,1.7,2.8])
para('The length summary is computed on the Description field as supplied, before text vectorization. It is a basic character-count diagnostic, not a token-count or language-quality assessment. The data contain no explicit source or timestamp feature in the three-column schema, so temporal or publisher-stratified generalisation cannot be measured from this CSV alone.')
heading('3.4 Data preview',2)
table(['Class','Headline example','Description excerpt'],[
 ['World (3)','Wall St. Bears Claw Back Into the Black (Reuters)','Reuters — Short-sellers, Wall Street’s dwindling band of ultra-cynics, are seeing green again.'],
 ['World (3)','Carlyle Looks Toward Commercial Aerospace','Private investment firm Carlyle Group … has quietly placed its bets on another part of the market.'],
 ['World (3)','Oil and Economy Cloud Stocks’ Outlook','Soaring crude prices plus worries about the economy … are expected to hang over the stock market.']], [1.0,2.2,3.3])
para('These first examples illustrate that the target is topic-level and the prose includes publisher names and news-specific terms. A proper model must learn useful lexical associations while generalising beyond memorised names and phrases.')
heading('3.5 Target encoding and feature assembly',2)
para('For the benchmark, Class Index values are converted from the supplied 1–4 coding to zero-based integer labels for estimator compatibility, and a readable mapping to World, Sports, Business and Sci/Tech is retained for interpretation. The text input is assembled as Title followed by Description separated by a space. Combining both fields allows a headline to provide a concise topical signal while the description supplies additional context.')
heading('3.6 Text-specific data preparation',2)
para('TF-IDF converts each document into a sparse vector. Word unigrams represent individual terms and bigrams represent adjacent two-word sequences. Inverse document frequency downweights terms appearing in many documents. The benchmark uses sublinear term-frequency scaling, a minimum document frequency of three, and a maximum vocabulary of 50,000 terms in the resource-bounded run. The fitted vocabulary and IDF weights are learned from training text only and then applied unchanged to the test text.')
heading('3.7 Dataset caveats',2)
bullets(['The provided archive’s row count is 120,000; some published descriptions refer to 120,000 training rows plus an additional test partition.','Class balance is not evidence that all semantic subtopics are equally represented.','Publisher or named-entity cues can inflate random-split scores if they appear in both partitions.','No test set from the original benchmark release was supplied, so these results cannot be compared directly with published leaderboard scores without matching preprocessing and split.','The report uses text preprocessing that is separate from the project’s present tabular ColumnTransformer.'])
heading('3.8 Why headline and description are combined',2)
para('The headline is compact and often contains the central event, team or company. The description adds context, entities and relations that may not appear in the title. Combining them increases available evidence but also increases document length and vocabulary. A useful follow-up ablation would evaluate title-only, description-only and title-plus-description under the same split. This would reveal whether the additional body text improves accuracy enough to justify its processing and storage cost.')
heading('3.9 Basic exploratory checks beyond row counts',2)
para('A responsible first pass also checks whether labels are valid, whether text fields are empty, whether records are duplicated, whether character encodings parse correctly and whether train and test splits share suspiciously similar documents. In this archive, the direct audit found complete values and no exact row duplicates. Near-duplicates were not exhaustively detected. Reposted or lightly edited stories could therefore still appear on both sides of a random split. A future audit could compare normalized text hashes or near-duplicate similarity, but any deduplication rule should be defined before final evaluation.')

chapter('4','Experimental Methodology','Reproducibility and fair-comparison principles')
heading('4.1 Experimental question',2)
para('The experiment compares four classical classifier families on the same four-class AG News problem using a common text representation. The primary descriptive endpoint is weighted F1, supported by accuracy, weighted precision and recall, macro-F1, per-class confusion counts and measured runtime. Since class counts are equal, weighted and macro averaging are numerically almost identical in aggregate here; both are still recorded to aid interpretation.')
heading('4.2 Split and random seed',2)
para('An 80/20 stratified holdout is generated with random_state=42. This allocates 96,000 records to the training partition and 24,000 to test. Stratification maintains approximately 25% representation per topic on each side. The test partition is not used to fit the vectorizer or train estimators. Each model is evaluated on the same test rows, enabling paired comparison at the example level.')
heading('4.3 Feature representation',2)
table(['Setting','Value used'],[
 ['Text fields','Title + Description'],['Vectorizer','Word-level TF-IDF'],['N-gram range','Unigrams and bigrams (1, 2)'],['Minimum document frequency','3'],['Maximum vocabulary','50,000 terms in resource-bounded run'],['Term frequency','Sublinear TF enabled'],['Matrix type','Sparse CSR, float32'],['Seed','42']], [2.5,3.7])
para('The generated training matrix for the capped run contained approximately 96,000 rows, 50,000 columns and 4.48 million non-zero values. Sparse storage matters: most documents contain only a small fraction of the entire vocabulary. Keeping the matrix sparse avoids allocating memory for all zero entries.')
heading('4.4 Model settings and compute protocol',2)
table(['Classifier','Key estimator configuration','Training rows'],[
 ['Logistic Regression','C=4; lbfgs; max_iter=120; seed=42','96,000'],
 ['Linear SVM','LinearSVC; C=1.0; seed=42','96,000'],
 ['Random Forest','40 trees; sqrt features; parallel jobs; seed=42','20,000 stratified sample'],
 ['KNN','k=5; distance weights; cosine distance; brute search','20,000 stratified sample']], [1.4,3.2,1.7])
para('The baseline ClassifyAI SVM implementation is an RBF SVC with probability=True. This benchmark instead uses LinearSVC because AG News becomes a large sparse matrix and linear decision boundaries are well suited to high-dimensional text. The RBF model’s kernel calculations and probability calibration would incur substantial cost at 96,000 rows. The report therefore compares the SVM family using the practical linear variant and does not claim to measure the repository’s configured RBF SVC.')
para('Random Forest and KNN were fitted on the same 20,000-row subsample drawn from the training partition with seed 42, while all models used the full 24,000-row test set. This resource limit makes their training protocols different. It is a transparent practical comparison, not a strictly equal training-volume bake-off. No parameter search or repeated random seeds were performed.')
heading('4.5 Metrics and timing',2)
para('Accuracy, weighted precision, weighted recall, weighted F1 and macro-F1 were computed from predictions on the held-out set. The confusion matrix was retained for each estimator. Fit and predict wall-clock times were measured using the local Python process and this environment. Timing measurements are approximate, machine-dependent and include estimator operations on the already vectorized matrices; the separate vectorization step took approximately 21.6 seconds for the capped-vocabulary run.')
heading('4.6 Reproducibility record',2)
table(['Item','Value'],[
 ['Input','train.csv.zip → train.csv'],['Observed shape','120,000 × 3'],['Split','80% training / 20% test, stratified'],['Random seed','42'],['Vectorizer','TF-IDF, word 1–2 grams, min_df=3, max_features=50,000, sublinear TF'],['Primary ranking lens','Weighted F1, with accuracy and efficiency considered'],['Protocol note','Linear models use full training partition; RF/KNN use 20,000-row training subsample'],['Validation caveat','One holdout run; no repeated folds or confidence intervals']], [2.0,4.4])
heading('4.7 Computational rationale for model variants',2)
para('The experiment distinguishes a scalable model family from one specific implementation. Kernel SVC constructs relationships among training examples; the number of pairwise interactions can become burdensome at tens of thousands of rows, especially when probability estimation is enabled. LinearSVC instead learns a hyperplane directly in the sparse feature space. It therefore gives a practical SVM comparison for this dataset without implying that every SVM variant has the same cost or score.')
para('KNN avoids iterative optimization but shifts much of its work to each prediction. For every query vector it must compare against the reference vectors, then rank distances. Even efficient sparse operations can accumulate into long batch inference times. Random Forest performs repeated split searches over candidate features. A 50,000-term word vocabulary creates a different challenge than a compact set of numeric columns, so reducing the sample size was necessary to finish the local run in a practical time.')
heading('4.8 Fair comparison checklist',2)
bullets(['Use the same source rows, target labels and held-out cases.','Use a representation that each method can consume correctly.','Fit preprocessing only on training folds.','Record algorithm variant and important hyperparameters.','Keep training sample sizes equal where feasible; if not, disclose the deviation.','Compare quality and runtime using clearly defined units and batch sizes.','Repeat folds or seeds before making a strong superiority claim.','Separate validation metrics used for model selection from final test metrics.'])

chapter('5','Classifier Algorithms','How the four model families produce predictions')
heading('5.1 Logistic Regression',2)
heading('5.1.1 Core idea',3)
para('Despite its name, Logistic Regression is a classification algorithm. It forms a linear score from the input features and transforms that score into probabilities. For binary classification, the sigmoid maps a real-valued score to the interval [0,1]: p(y=1|x)=1/(1+exp(-(wᵀx+b))). For multiple classes, the softmax function produces a probability for each category. The predicted category is usually the class with the largest probability.')
para('For a four-class text problem with TF-IDF vector x, the model learns a coefficient vector for each class. A positive coefficient increases the corresponding class score when that token is present; a negative coefficient decreases it. The model is linear in the feature representation. It does not directly understand word order or meaning unless those properties are represented by features such as bigrams.')
heading('5.1.2 Regularisation and fitting',3)
para('The implementation uses L2 regularisation by default. Regularisation penalises very large weights, reducing sensitivity to rare or noisy features. The inverse-strength parameter C controls the trade-off: smaller C means stronger regularisation, while larger C allows a closer fit to training data. Model parameters are estimated by optimising a convex log-loss objective, usually with an iterative numerical solver such as lbfgs.')
heading('5.1.3 Strengths and limitations',3)
bullets(['Fast and memory-efficient for sparse high-dimensional text.','Probabilistic outputs support confidence display and probability-based metrics.','Coefficients can be inspected to identify class-associated terms.','Linear boundary may miss complex interactions without feature engineering.','Correlated word and phrase features can distribute weight across alternatives.','Probability calibration and confidence quality should be checked when decisions depend on thresholds.'])
heading('5.1.4 Why scale matters',3)
para('On numeric tabular inputs, feature scaling often improves optimisation and makes regularisation act more evenly across features. TF-IDF values are already bounded and normalised by the vectorizer in common configurations, so the text pipeline does not apply a second standard scaler. A sparse-compatible estimator and transformation are needed to preserve memory efficiency.')
heading('5.2 Support Vector Machine',2)
heading('5.2.1 Maximum-margin principle',3)
para('An SVM selects a decision boundary that separates classes while maximising the margin to the closest training examples. Those closest examples are the support vectors. A wider margin often generalises well. The penalty parameter C controls the balance between a wide margin and training errors: high C penalises errors strongly, while lower C allows more violations in exchange for a softer margin.')
para('For linear classification, the decision function is a weighted sum wᵀx+b. Multiclass SVM implementations combine class-wise decision functions, commonly using one-vs-rest or one-vs-one strategies. LinearSVC is a scalable linear implementation that optimises a hinge-style loss and typically does not provide calibrated probabilities by default.')
heading('5.2.2 Kernel SVM',3)
para('A kernel function compares examples as if they were mapped into a richer feature space without explicitly materialising every mapped coordinate. The RBF kernel K(x,z)=exp(-γ||x-z||²) yields nonlinear boundaries. The gamma parameter controls how local each example’s influence is. Kernel SVMs can be effective on small or medium datasets but kernel computation and memory scale poorly as the number of training instances grows.')
heading('5.2.3 Linear SVM for news text',3)
para('TF-IDF vectors have many dimensions and relatively few nonzero values per document. Topic categories can often be separated by weighted lexical evidence, making a linear maximum-margin classifier a strong baseline. The measured experiment uses LinearSVC for this reason. The project’s registered SVC uses an RBF kernel and probability=True; that exact configuration was not used in the AG News benchmark.')
heading('5.2.4 Strengths and limitations',3)
bullets(['Strong accuracy on high-dimensional sparse text classification.','Margin-based objective can generalise well when the signal is approximately linear.','Linear prediction is efficient after fitting.','RBF SVC can model nonlinear boundaries but is computationally expensive at large N.','LinearSVC decision scores are not probabilities without a calibration step.','A linear coefficient model is less directly human-readable than a small tree, though top class-weighted terms can be inspected.'])
heading('5.3 Random Forest',2)
heading('5.3.1 Tree building',3)
para('A decision tree recursively divides feature space using tests chosen to make child nodes more class-pure. Classification trees commonly use Gini impurity or entropy. A single deep tree can fit intricate patterns but has high variance and may overfit. Random Forest reduces variance by fitting many trees on bootstrap samples and aggregating their votes.')
heading('5.3.2 Bagging and random subspaces',3)
numbered(['Draw a bootstrap sample of training examples for each tree.','At each split, consider only a random subset of the available features.','Grow each tree using a criterion such as Gini impurity.','Combine tree predictions through majority vote or averaged class probabilities.'])
para('Bootstrap aggregation makes the trees less correlated; random feature selection further reduces their dependence. Averaging many diverse trees typically stabilises the prediction relative to a single tree. The repository configuration uses 100 trees, Gini criterion, unconstrained depth and parallel fitting. The bounded AG News run uses 40 trees over a 20,000-row subsample.')
heading('5.3.3 Strengths and limitations',3)
bullets(['Strong general-purpose model for mixed-type tabular data and nonlinear feature interactions.','Usually needs no standardisation.','Captures threshold interactions without explicit feature engineering.','Ensembles are larger and less interpretable than a single tree.','Impurity feature importance can favour high-cardinality or correlated predictors.','Sparse text with tens of thousands of mostly zero word features is a poor computational and inductive-bias match for conventional tree splits.'])
heading('5.3.4 Relevance to AG News',3)
para('A Random Forest can learn word-presence thresholds and interactions, but the feature space is extremely wide and sparse. Many trees must search among many mostly absent terms; an ensemble of such local splits may need far more data or tuning than a linear text classifier. The observed lower accuracy is consistent with this mismatch, although the reduced training sample is an additional confounding factor.')
heading('5.4 K-Nearest Neighbors',2)
heading('5.4.1 Instance-based prediction',3)
para('KNN stores training examples rather than fitting a compact global decision function. For a new vector, it computes distances to stored examples, selects the nearest k, and predicts the majority label. With distance weighting, close neighbours contribute more than farther ones. The value of k trades sensitivity against smoothing: small k can be noisy; large k can blur class boundaries.')
heading('5.4.2 Distance metrics and sparse documents',3)
para('Euclidean distance is sensitive to vector magnitude and scale. Cosine distance, 1 minus cosine similarity, focuses on the angle between vectors and is common for normalized text representations. In this experiment, KNN uses k=5, cosine distance and distance weighting. For a test document, the model compares it with each training vector, so prediction work grows with training-set size and feature dimensions.')
heading('5.4.3 Strengths and limitations',3)
bullets(['Simple, intuitive and able to form nonlinear local boundaries.','Little estimator fitting is needed; training is mainly storage.','Prediction can be very slow because many distances must be computed.','Memory requirements grow with the stored dataset.','Results depend on k, distance function, representation and neighbourhood density.','The curse of dimensionality makes neighbourhoods less informative as dimensions increase.'])
para('The AG News KNN run achieved useful performance, but prediction on 24,000 examples took about 29.5 seconds using the 20,000-row training sample. This is orders of magnitude slower than the linear models in the same run. Approximate nearest-neighbour indexes, dimensionality reduction, or a much smaller reference set could improve speed, but would alter the protocol.')
heading('5.5 Side-by-side algorithm summary',2)
table(['Property','Logistic Regression','Linear SVM','Random Forest','KNN'],[
 ['Learning style','Parametric linear','Maximum-margin linear','Bagged tree ensemble','Instance-based / lazy'],
 ['Boundary','Linear in TF-IDF','Linear in TF-IDF','Piecewise nonlinear','Local nonlinear'],
 ['Text suitability','Very strong baseline','Very strong baseline','Often weaker on sparse words','Can work, prediction costly'],
 ['Scaling','Usually helpful; TF-IDF normalised','Usually helpful; TF-IDF normalised','Not required','Critical / distance choice'],
 ['Probability output','Yes','Not by default','Yes','Yes, neighbour vote'],
 ['Interpretability','Class coefficients','Linear weights / margins','Impurity importance','Neighbour examples'],
 ['Main cost','Iterative fit','Fit efficient; prediction fast','Many tree fits','Distance search at inference']], [1.3,1.35,1.35,1.35,1.35])
heading('5.6 Bias, variance and representation fit',2)
para('The four methods express different assumptions. Logistic Regression and linear SVM have a global linear decision boundary in the transformed space; this can be a good bias-variance compromise when many terms contribute modest evidence. Random Forest can represent nonlinear interactions but may have higher variance and high search cost in an extremely wide sparse space. KNN creates flexible local boundaries, but its notion of “nearby” must remain meaningful as dimensionality grows. These inductive biases help explain why a simpler linear decision surface can win on text.')
heading('5.7 Practical hyperparameter effects',2)
table(['Method','Parameter','Practical effect'],[
 ['Logistic Regression','C','Controls regularization strength; smaller values shrink coefficients more.'],
 ['Logistic Regression','max_iter / solver','Affects convergence reliability and fitting time.'],
 ['SVM','C','Trades a wider margin against training errors.'],
 ['RBF SVM','gamma','Sets the locality of each training example’s influence.'],
 ['Random Forest','n_estimators','More trees can stabilize predictions but increase fit and inference cost.'],
 ['Random Forest','max_depth / min_samples_leaf','Restrains tree complexity and can reduce overfitting.'],
 ['KNN','n_neighbors','Small k is local and noisy; larger k smooths more.'],
 ['KNN','metric / weights','Changes neighbourhood geometry and how votes are counted.']], [1.4,1.6,3.5])
para('Hyperparameters should be tuned inside a validation process, not chosen based on test performance. A compact search can be more useful than a large blind grid: for example, test a few values of C and n-gram range for linear models, a small k/metric set for KNN, and a modest range of tree counts/depths for Random Forest. The search budget itself should be recorded because a more extensively tuned candidate otherwise receives an unfair advantage.')

chapter('6','Train-Test Split and Validation','Estimating performance without contaminating the test set')
heading('6.1 Why partition the data?',2)
para('A model can memorise patterns in the data on which it is trained. Measuring performance on those same examples gives an optimistic estimate of how it will perform on unseen articles. A train-test split holds examples aside before fitting so the final score approximates generalisation to new, similarly distributed cases.')
heading('6.2 Stratified 80/20 holdout',2)
para('For N=120,000, an 80/20 partition gives 96,000 training examples and 24,000 test examples. Stratification samples each class in approximately the same proportion as the full set. Because AG News is exactly balanced, the training and test partitions each retain close to 25% of each topic. A fixed seed makes the membership reproducible.')
table(['Partition','Rows','Use','Model fitting allowed?'],[
 ['Training','96,000','Fit vocabulary/IDF and classifier parameters','Yes'],['Test','24,000','Final estimate after the model is selected','No, until final evaluation']], [1.2,1.0,3.0,1.3])
heading('6.3 Cross-validation',2)
para('K-fold cross-validation divides the training partition into K folds. The model is trained K times, each time on K−1 folds and validated on the remaining fold. Mean score summarizes average performance; standard deviation describes variation across folds. Stratified K-fold maintains class proportions in every fold. The project agent uses this method on the outer training portion to rank candidates and reserves the outer test set for one final evaluation.')
para('Cross-validation costs more than one holdout because each candidate is fitted repeatedly. It is particularly useful when data are limited or when model rankings may depend on one split. For a large text dataset, the compute cost must be balanced against the value of more stable estimates. Repeated or nested cross-validation would provide a stronger comparison but was not performed for the reported results.')
heading('6.4 Leakage and how to prevent it',2)
para('Data leakage occurs when information unavailable at prediction time influences training or model selection. Examples include fitting a scaler on all rows before splitting, selecting vocabulary terms using the test set, using target-derived features, or repeatedly tuning against the final holdout. Leakage makes evaluation scores too optimistic.')
numbered(['Create the train/test partition before learning transformations.','Fit TF-IDF vocabulary and inverse document frequencies only on training text.','Transform validation/test text using the already fitted vectorizer.','Fit any imputers, scalers or encoders inside each cross-validation training fold.','Use CV to select settings and models; evaluate on the test set only after decisions are fixed.','Do not use test results for repeated tuning. If test-guided revisions occur, create a new final test set or use nested validation.'])
heading('6.5 Split choice and representativeness',2)
para('A random stratified split assumes training and future examples are exchangeable. If the intended deployment setting predicts future news, a chronological split may be more realistic. If publishers or story series dominate, group-based splitting can test transfer to unseen publishers or events. Those alternatives need reliable timestamps or group identifiers, which are not present in the supplied three-column file.')
heading('6.6 What this experiment estimates',2)
para('The score estimates performance on held-out examples drawn from the supplied training CSV under a random, stratified split and a common TF-IDF representation. It is not an official benchmark test score, a future-time evaluation, or a guarantee of performance on contemporary news. The model selection result is also based on one split and is subject to sampling variation.')
heading('6.7 Worked split arithmetic',2)
para('The supplied dataset has 30,000 records per topic. With an 80/20 stratified partition, the expected split is 24,000 training and 6,000 test rows per topic. Summing the four classes gives 96,000 training rows and 24,000 test rows. Stratification does not mean the algorithm is shown test text during fitting; it only controls the label composition as records are assigned to each side.')
heading('6.8 Cross-validation in the ClassifyAI agent',2)
para('The agent first removes the outer test set. It then runs StratifiedKFold on the remaining training features and labels. Every candidate receives the same fold indices, making model scores more directly comparable. A fresh clone of the full preprocessing-and-estimator pipeline is fitted for every fold. Fold-level metrics are aggregated into means and standard deviations. After ranking, the winning pipeline is fitted once more on the entire outer training partition and evaluated on the sequestered test partition.')
para('If one class has fewer examples than the requested number of folds, the evaluator reduces the fold count to a valid value. This prevents folds with no representation of a class, although very small minority counts still produce noisy estimates. The agent records this adjustment in its notes so the user can see that the requested setting changed.')

chapter('7','Performance Measures','Reading classification results beyond a single number')
heading('7.1 Confusion matrix',2)
para('A confusion matrix counts true labels by predicted labels. For multiclass classification, rows conventionally denote actual classes and columns predicted classes, though software and dashboards should label axes clearly. Diagonal values are correct predictions; off-diagonal values reveal the specific categories the classifier confuses. The order of class labels must be recorded to interpret the matrix.')
heading('7.2 Accuracy',2)
para('Accuracy = correct predictions / all predictions = (sum of diagonal counts) / N. It is intuitive and appropriate when classes have similar importance and are reasonably balanced. On this balanced four-class data, chance-level majority prediction is 25%. On imbalanced data, a model can achieve high accuracy while ignoring a rare but important class.')
heading('7.3 Precision',2)
para('For one class, precision = TP/(TP+FP): among examples predicted as that class, how many truly belong? A low value indicates false-positive assignments. In multiclass one-vs-rest evaluation, precision is computed per class and then averaged. Weighted precision weights each class by its true support; macro precision gives each class equal weight.')
heading('7.4 Recall',2)
para('Recall = TP/(TP+FN): among examples truly in a class, what fraction did the model recover? Low recall means many examples of that topic are assigned elsewhere. Recall matters when missing a category is more costly than reviewing a false positive.')
heading('7.5 F1 score',2)
para('F1 = 2 × (precision × recall)/(precision + recall). It is the harmonic mean of precision and recall, so a low value in either reduces the score. For multiclass tasks, macro-F1 averages class-wise F1 equally, while weighted-F1 weights by class support. Weighted-F1 can hide a poor minority class on imbalanced datasets; macro-F1 is more sensitive to equal treatment across classes.')
heading('7.6 Balanced accuracy',2)
para('Balanced accuracy is the average recall over classes. It counters class-frequency dominance by weighting each class equally. For a balanced dataset, it will usually be close to ordinary accuracy; for an imbalanced dataset it can reveal whether a classifier simply favours the largest class.')
heading('7.7 ROC-AUC',2)
para('ROC-AUC measures how well a score ranks positive examples above negatives across thresholds. In multiclass classification it can be computed using one-vs-rest comparisons and macro or weighted averaging. It requires decision scores or probabilities, not only hard labels. It may be unavailable for a particular estimator API or when a validation fold lacks a class. In the current project evaluator, ROC-AUC is computed only when predict_proba is available; a linear SVM without calibration therefore has no ROC-AUC in the measured benchmark.')
heading('7.8 Weighted versus macro averages in AG News',2)
para('Each AG News category has equal support in the full supplied file, and stratification preserves that balance in the split. Weighted averages therefore give nearly the same influence to each class as macro averages, so the two F1 values are numerically the same to the displayed precision in this run. This will not generally hold for other datasets.')
heading('7.9 Training time and inference latency',2)
para('Training time describes the time required to fit the estimator under a stated representation and sample size. Inference time describes the time required to predict a batch. They are hardware-, software-, and batch-dependent. KNN’s lazy-learning nature makes it attractive during fitting but expensive at prediction. A production choice should consider throughput and latency targets, memory, retraining frequency and probability requirements in addition to accuracy.')
heading('7.10 Metric choice as a decision',2)
para('The primary metric should reflect the cost of errors and the dataset’s balance. For this balanced topic classification task, accuracy and weighted F1 are understandable summary measures, while macro-F1 and the confusion matrix check category-specific consistency. In medical screening or fraud detection, recall or precision may take precedence. There is no single universally best metric independent of the application.')
heading('7.11 Worked interpretation of the AG News confusion matrix',2)
para('The Linear SVM confusion matrix has 24,000 entries in total. The diagonal sums to 22,128 correct classifications (5,446 + 5,899 + 5,354 + 5,429). Dividing 22,128 by 24,000 gives 0.922, or 92.20% accuracy. Each row totals 6,000 actual examples. For the Sports row, 5,899 divided by 6,000 gives 98.32% recall. For Business, 5,354 divided by 6,000 gives 89.23% recall. These row-level calculations explain why aggregate accuracy should be supplemented by class diagnostics.')
para('Precision for a predicted class uses a column total instead. For example, the World column has 5,446 true World examples plus false positives from the other three actual classes. The ratio of true World predictions to all predictions in the World column is World precision. Thus a confusion matrix can be used to calculate both precision and recall, while also showing the direction of misclassification.')
heading('7.12 Interpreting a near tie',2)
para('Two results that differ by a few hundredths of a percentage point may rank differently while being practically indistinguishable. A ranking table is useful for sorting, but it does not by itself establish that the first model is reliably better. Repeated folds, paired predictions, confidence intervals and operational needs should inform the choice. In this report, the linear SVM is listed first because it has the highest observed point estimate; Logistic Regression remains a credible co-finalist.')

chapter('8','Results and Comparative Analysis','Measured outcomes on the submitted AG News file')
heading('8.1 Main results',2)
para('All predictions were evaluated on the same 24,000 held-out rows. The reported times exclude the shared text-vectorization step. Logistic Regression and LinearSVC use all 96,000 training rows; Random Forest and KNN use the same 20,000-row training subsample. Scores are proportions converted to percentages.')
table(['Rank by accuracy','Classifier / protocol','Accuracy','Precision (weighted)','Recall (weighted)','F1 (weighted)','F1 (macro)','Fit seconds','Predict seconds'],[
 ['1','Linear SVM; full train','92.20%','92.19%','92.20%','92.18%','92.18%','10.09','0.021'],
 ['2','Logistic Regression; full train','92.15%','92.14%','92.15%','92.14%','92.14%','12.90','0.026'],
 ['3','KNN cosine; 20k sample','88.08%','88.05%','88.08%','88.06%','88.06%','0.014','29.519'],
 ['4','Random Forest; 20k sample','84.20%','84.20%','84.20%','84.11%','84.11%','3.59','0.133']], [0.8,1.55,.65,.9,.8,.75,.7,.65,.75])
para('The Linear SVM has the top observed accuracy and weighted F1. Its advantage over Logistic Regression is only 0.00046 in accuracy (0.046 percentage points) and about 0.00043 in weighted F1. Given a single split, no uncertainty interval and no repeated cross-validation, that is a narrow descriptive lead rather than strong statistical evidence of superiority. The two linear models should be treated as near-tied candidates.')
heading('8.2 Confusion matrix: Linear SVM',2)
para('Rows are actual classes; columns are predicted classes. Index order is World, Sports, Business, Sci/Tech. Each actual class has 6,000 test examples.')
table(['Actual \\ Predicted','World','Sports','Business','Sci/Tech','Recall'],[
 ['World','5,446','169','219','166','90.77%'],['Sports','55','5,899','20','26','98.32%'],['Business','167','49','5,354','430','89.23%'],['Sci/Tech','164','45','362','5,429','90.48%']], [1.7,1.0,1.0,1.0,1.0,1.0])
para('Sports is the easiest class in this split, with 98.32% recall. Business and Sci/Tech are more often confused with one another: 430 Business examples were predicted Sci/Tech, and 362 Sci/Tech examples were predicted Business. This is understandable because technology companies, markets and products can appear across both categories. World articles also show some overlap with Business topics.')
heading('8.3 Per-class perspective',2)
table(['Class','Test examples','Correct (Linear SVM)','Recall','Largest confusion'],[
 ['World','6,000','5,446','90.77%','219 → Business'],['Sports','6,000','5,899','98.32%','55 → World'],['Business','6,000','5,354','89.23%','430 → Sci/Tech'],['Sci/Tech','6,000','5,429','90.48%','362 → Business']], [1.4,1.1,1.4,1.0,1.7])
heading('8.4 Runtime interpretation',2)
para('Linear SVM fit in about 10.1 seconds and predicted the entire test set in roughly 0.021 seconds. Logistic Regression fit in about 12.9 seconds and predicted in 0.026 seconds. KNN fit took only milliseconds because it primarily stores examples, but predicting 24,000 test documents took approximately 29.5 seconds. Random Forest’s 40 trees fit in about 3.6 seconds on 20,000 examples and predicted in 0.133 seconds. These timings were measured on one local environment and should not be generalized as hardware-independent performance.')
heading('8.5 Which algorithm is best, and why?',2)
para('For the measured split, Linear SVM is the best observed classifier if “best” means highest held-out accuracy and weighted F1 among these four fitted candidates. It suits sparse, high-dimensional TF-IDF features, and its prediction latency is very low. It is also a close contest: Logistic Regression is essentially tied, gives native class probabilities and offers a familiar coefficient-based interpretation. If probability outputs or ease of explanation are more important than the tiny measured score difference, Logistic Regression may be the more useful deployment choice.')
para('KNN outperformed the reduced-sample Random Forest in accuracy but its full-test prediction cost is substantial. Random Forest had the lowest score in this resource-bounded comparison, but this should be interpreted cautiously because it received only a fraction of the linear models’ training examples and was limited to 40 trees. The score does not prove that every Random Forest configuration would be inferior.')
heading('8.6 Comparison validity and uncertainty',2)
bullets(['Same held-out test rows and same text representation for all methods.','Different effective training sizes: 96,000 for the linear models and 20,000 for tree/KNN.','One seed and one holdout; no standard errors or significance test.','No hyperparameter search; the outcome is configuration-dependent.','The RBF SVC in the application was not evaluated; LinearSVC was used for scale suitability.','The official AG News test partition was not included in the provided archive.'])
heading('8.7 Recommended stronger follow-up experiment',2)
numbered(['Fix a common training budget or run all models on the same sampled training subset.','Use a validation split or stratified CV to tune C, vocabulary size, n-grams, KNN k/metric and Random Forest depth/tree count.','Report mean and standard deviation across identical stratified folds.','Select the final model using CV only, then evaluate once on a sealed holdout.','If possible, evaluate on the official AG News test file and disclose the split source.','Use paired bootstrap intervals or a suitable paired comparison to quantify uncertainty.'])
heading('8.8 Error patterns and practical meaning',2)
para('The largest confusion flows occur between Business and Sci/Tech. Such category overlap is not necessarily a software defect: an article about a technology company’s earnings, product launch or market valuation can plausibly contain signals associated with both topics. The fixed labels force a single answer even when the semantics overlap. In a real editorial workflow, confidence thresholds or a multi-label taxonomy might be more useful than a forced single-class choice for borderline stories.')
para('Sports recall is notably stronger in this split. Sports stories often contain distinctive names, event vocabulary and competition language. This explanation is plausible but should be treated as an interpretation rather than a causal finding. A deeper analysis would inspect misclassified examples, identify recurring terms and test whether the pattern persists across folds or a temporal split.')

chapter('9','ClassifyAI Dashboard Demonstration','Screenshots of the implemented web application')
para('The following figures are the dashboard screenshots supplied for this report. They document the user interface and the project’s tabular-classification demonstration. They are not screenshots of the AG News experiment. One screenshot displays a Social_Network_Ads-style table with fields including User ID, Gender, Age, EstimatedSalary and Purchased; its visible scores and predictions belong to that separate demonstration context.')
heading('9.1 Dataset profiling and preview',2)
figure('dashboard-overview.png','Figure 1. Dashboard dataset overview, profiling counters, candidate targets and sample rows. The visible tabular dataset is a demonstration input, not AG News.',6.3)
para('The overview component surfaces row and column counts, numeric and categorical feature counts, missing-value and duplicate checks, candidate target columns and a small preview. For a text-capable version, this view should add text-length distributions, vocabulary indicators and fields recognized as free text.')
heading('9.2 Experiment setup',2)
figure('dashboard-configuration.png','Figure 2. Experiment configuration controls: candidate algorithms, primary metric, stratified CV folds, held-out proportion and run action.',6.3)
para('The experiment panel lets a user choose a model set, a primary ranking metric, cross-validation folds and the test fraction. These controls map directly to core evaluation design decisions and make them visible before execution.')
heading('9.3 Leaderboard',2)
figure('dashboard-leaderboard.png','Figure 3. Classifier leaderboard and score comparison chart in the submitted dashboard demonstration. Displayed scores refer to the shown tabular demo, not AG News.',6.3)
para('The leaderboard communicates rank, algorithm name, primary score, supporting metrics and timing. The project ranker sorts by the configured primary metric, then uses score variability, balanced accuracy, weighted F1 and training time as tie-breakers. A narrow margin can be flagged as ambiguous.')
heading('9.4 Cross-validation comparison and diagnostics',2)
figure('dashboard-comparison.png','Figure 4. Cross-validation metric comparison and the held-out test confusion-matrix/feature-importance panels in the dashboard.',6.3)
para('The chart supports side-by-side comparison rather than relying on a single number. Confusion matrices show which class pairs are being mixed. Feature importance is model-dependent: trees expose impurity reductions, and linear models expose coefficients; neither should automatically be read as causal explanation.')
heading('9.5 Prediction playground',2)
figure('dashboard-playground.png','Figure 5. Interactive model playground for entering feature values and obtaining a prediction from the fitted demonstration pipeline.',6.3)
para('An inference playground is useful for demonstrating the end-to-end fitted pipeline. For document classification, the natural text analogue would accept a headline and article body, apply the saved TF-IDF transform and show the predicted topic plus a calibrated confidence or decision score where available.')
heading('9.6 Interpretability and execution notes',2)
figure('dashboard-failure-note.png','Figure 6. Dashboard interpretability note and failure-status presentation. This screenshot is included as a UI example, not a result from the AG News benchmark.',5.9)
para('A responsible dashboard distinguishes unavailable outputs from zero values, explains when a model has no intrinsic feature importance and gives readable reasons for model failures. The interface screenshot demonstrates a caveat message about non-linear models and feature attributions.')
heading('9.7 Relation of screenshots to report findings',2)
box('Evidence boundary: the images establish that the dashboard has profiling, configuration, ranking, comparison, diagnostics and inference UI. They do not establish AG News model scores. All AG News metrics in Chapter 8 come from the described held-out TF-IDF experiment.')
heading('9.8 Suggested AG News dashboard run',2)
numbered(['Upload a CSV containing Class Index, Title and Description.','Select Class Index as the target and confirm the four labels map to their topic names.','Mark Title and Description as text fields and choose concatenation or separate-field vectorization.','Select a stratified 20% holdout and a small number of stratified validation folds.','Choose Logistic Regression and Linear SVM as the initial scalable candidates; optionally add resource-limited RF and KNN.','Set weighted F1 as the primary metric and inspect macro-F1, accuracy, class recalls, confusion matrix and timing.','Review the audit log and representation metadata before accepting the recommendation.'])
para('A dashboard implementation should not silently reinterpret a document field as a categorical variable. The upload/profile stage ought to identify it as text, explain what representation will be built, and preserve the fitted text transformation as part of the winning model artifact.')

chapter('10','The Automated Classifier Selection Agent','Agent workflow, reasoning and authorship')
heading('10.1 What was developed',2)
para('I developed ClassifyAI as an agent that automatically finds a suitable classifier for a dataset by inspecting the target and feature structure, preparing candidate pipelines, evaluating selected algorithms, ranking successful candidates and explaining the result. The agent coordinates the existing model-selection workflow rather than relying on a manually hard-coded winner.')
heading('10.2 Agent workflow',2)
table(['Stage','Agent action','Decision or output'],[
 ['1. Validate','Check target, metric, fold count, test proportion and requested algorithm ids.','Reject invalid configuration early.'],
 ['2. Profile','Compute schema, missingness, duplicates, cardinality and target distribution.','Summarise dataset suitability and balance.'],
 ['3. Prepare','Separate X/y, encode classes, infer numeric/categorical columns.','Build preprocessing specifications.'],
 ['4. Partition','Create seeded stratified outer holdout.','Keep the test split isolated.'],
 ['5. Benchmark','Fit each candidate pipeline within stratified folds.','Metrics, variability, timing and error status.'],
 ['6. Rank','Sort by selected primary score with deterministic tie-breaks.','Champion, runner-up and ambiguity flag.'],
 ['7. Finalise','Fit the winner on the full training partition.','Held-out metrics, confusion matrix, attribution.'],
 ['8. Explain','Record timestamped audit events.','Human-readable decisions and failure notes.']], [1.0,3.0,2.4])
heading('10.3 What makes it agent-like',2)
para('A fixed benchmark script can execute estimators but does not necessarily adapt to a dataset or explain what happened. ClassifyAI has agent-like orchestration because it validates user settings, profiles target structure, adapts the evaluation fold count to class availability, selects scaling based on estimator metadata, isolates individual model failures, ranks completed candidates, checks whether the winner is meaningfully ahead of the runner-up and returns an audit trail. It is a transparent, rule-based machine-learning agent rather than a generative conversational agent.')
heading('10.4 Automatic does not mean universally optimal',2)
para('The system can recommend the best candidate among the algorithms and settings it actually evaluates, under a chosen metric and data split. It cannot guarantee the global optimum over all possible model families, feature representations, parameter settings or deployment costs. The result depends on the candidate set, preprocessing, validation protocol, primary score and available compute. A responsible explanation states those conditions.')
heading('10.5 Current modality coverage',2)
para('The implemented preprocessing assumes tabular numeric and categorical features. The AG News results show an additional text pipeline is needed before the dashboard agent can automatically select among text classifiers. The current benchmark in this report is evidence for the approach and an extension target, not proof that the existing upload flow already handles AG News end to end.')
heading('10.6 Proposed text-aware agent extension',2)
numbered(['Identify long free-text columns using dtype, cardinality and sample content.','Allow users to select one or more text fields and define how to combine them.','Create sparse TF-IDF or hashing pipelines inside cross-validation folds.','Register sparse-compatible candidates such as Logistic Regression, LinearSVC, Complement Naive Bayes and SGDClassifier.','Use a compute-aware policy to avoid RBF SVC or brute-force KNN on very large sparse sets unless explicitly requested.','Benchmark through stratified CV, expose macro/weighted metrics and rank under user-selected quality and latency priorities.','Persist the fitted vectorizer and model together for prediction.','Display text-specific diagnostics such as vocabulary size, top class-weighted terms and misclassified examples with privacy-conscious handling.'])
heading('10.7 How the agent chooses a winner',2)
para('The winner is conditional on the primary metric. ClassifyAI first excludes failed candidates and candidates without that metric. It sorts successful candidates by the selected score in the preferred direction. Lower score standard deviation is the first tie-breaker, followed by balanced accuracy, weighted F1 and training time. The dashboard can then show the runner-up, absolute margin and an ambiguity notice when the top models are close relative to observed fold variation.')
para('This deterministic ordering improves repeatability: identical metrics and inputs yield the same order. Determinism is not a substitute for statistical validity, however. The ambiguity flag is a heuristic based on score variation and should be presented as a caution, not a formal hypothesis test. A future version could add paired fold-level comparisons and confidence intervals.')
heading('10.8 Human oversight and user control',2)
para('Users should remain able to select the target, primary metric, candidate models and split settings. The agent’s recommendation is most useful when it is accompanied by the evidence and assumptions behind it. Domain owners can then decide whether an apparent improvement matters, whether an error type is unacceptable, or whether latency and model size should outweigh a small score gain.')

chapter('11','Limitations, Risks and Future Work','How to strengthen the study and product')
heading('11.1 Experimental limitations',2)
bullets(['The four models were compared on one seeded holdout rather than repeated cross-validation.','Training volume differs for the linear models versus Random Forest and KNN, limiting strict fairness.','Only one small set of hyperparameters was assessed for each candidate.','The full official AG News test file was not supplied.','The linear SVM variant differs from the project’s registered RBF SVC.','Timings are local-environment measurements, exclude shared vectorization and are not portable.','A random split may not measure performance on future news or unseen publishers.'])
heading('11.2 Data and construct validity',2)
para('The sample is balanced and tidy, but its label definitions and curation may not reflect the distribution or semantics of a real newsroom taxonomy. Headlines can contain strong cues; publisher names and named entities may leak topical signals across a random split. The absence of source and time fields prevents group or temporal analysis. Future work should assess these effects with appropriate metadata and alternate splits.')
heading('11.3 Software limitations',2)
bullets(['Dataset and experiment stores are in-memory and reset when the backend restarts.','The upload route is CSV-focused; document files and text-specific preprocessing are not implemented in the current pipeline.','Dense one-hot encoding may not scale to high-cardinality text fields.','Some probability-based metrics are unavailable for estimators that do not expose predict_proba.','The ranker’s ambiguity heuristic is a practical notice based on fold standard deviations, not a formal significance test.','Feature importance displays must be interpreted cautiously and consistently with each model’s definition.'])
heading('11.4 Responsible reporting',2)
para('An automated selector should state what was tested, what was excluded, what objective was optimized, and how stable the result appears. It should avoid presenting small score differences as definitive. It should preserve class labels and split provenance, report metric limitations and expose model failures. Where errors have unequal impacts, users must choose metrics that encode the task’s priorities.')
heading('11.5 Future roadmap',2)
table(['Priority','Enhancement','Expected benefit'],[
 ['1','Add modality detection and sparse text pipelines.','Make AG News and other text CSVs first-class inputs.'],
 ['2','Add StratifiedKFold result summaries for every finalist.','More stable candidate ranking and score variability.'],
 ['3','Add resource-aware model settings and timeouts.','Predictable execution on large datasets.'],
 ['4','Add nested or repeated validation option.','Less optimistic tuning and better uncertainty estimates.'],
 ['5','Persist experiment configuration, fitted artifacts and provenance.','Reproducibility across service restarts.'],
 ['6','Add calibration and probability-quality diagnostics.','More trustworthy confidence outputs.'],
 ['7','Support temporal/group splitting where metadata permits.','More realistic deployment estimates.'],
 ['8','Add error analysis and per-class dashboard views.','Actionable insight into failure patterns.']], [0.75,3.1,2.55])
heading('11.6 Suggested evaluation policy for future releases',2)
para('A release-ready benchmark should define a versioned dataset snapshot, target semantics, split protocol, preprocessing graph, model configurations, primary and secondary metrics, runtime environment and random seed. Hyperparameter selection should use validation folds and the final test set should be consulted once. The dashboard could export this configuration as a machine-readable experiment card so another user can reproduce the ranking and understand what the selector did.')
para('For text, the experiment card should additionally list selected text columns, tokenizer/vectorizer settings, vocabulary size, sparse matrix dimensions and the method used to handle unknown terms. For each classifier, it should report whether probabilities are calibrated or only decision scores are available. These details help prevent an attractive score from obscuring important differences in workflow or prediction output.')

chapter('12','Conclusion','Findings and project contribution')
para('This report examined the ClassifyAI classifier-selection project and compared four model families on the supplied AG News training CSV. The archive contains 120,000 rows, three fields, four balanced classes, no missing values and no exact duplicate rows. News headlines and descriptions form the text features; Class Index is the topic target.')
para('On a seeded stratified 80/20 split with word-level TF-IDF, Linear SVM produced the highest observed score: 92.20% accuracy and 92.18% weighted F1. Logistic Regression was almost tied at 92.15% accuracy and 92.14% weighted F1. KNN using cosine distance reached 88.08% accuracy but required about 29.5 seconds to predict the test batch. Random Forest reached 84.20% in a compute-bounded run using a 20,000-row subsample. Because one split was used and training sizes differ, the SVM result is a provisional winner for this experiment, not a universal conclusion.')
para('Linear classifiers fit this dataset’s high-dimensional sparse text representation well. Linear SVM offers a very small observed quality lead and fast prediction; Logistic Regression remains an attractive probability-producing and interpretable alternative. Model choice should reflect the primary metric, need for probabilities, latency constraints and validation uncertainty.')
para('The screenshots document a functioning dashboard for tabular CSV profiling, experiment configuration, classifier comparison, diagnostics and interactive inference. The current preprocessing pipeline is tabular-oriented, so AG News requires a text-specific vectorizer and sparse-compatible model workflow before these benchmark results can be run directly through the dashboard. That is a concrete extension for the agent.')
para('I developed an agent that automatically profiles a classification dataset, evaluates a candidate set of classifiers, ranks them under a selected performance measure and explains the recommendation. Its purpose is to make model selection more systematic and reviewable. The report’s findings also show why a reliable agent must account for data modality, compute cost, metric selection and the uncertainty of close comparisons.')

page(); heading('References',1)
refs=[
 '1. ClassifyAI project source code and documentation. Backend modules: classifier_agent.py, preprocessing.py, model_evaluator.py, model_ranker.py, model_trainer.py, data_analyzer.py and algorithm factories. Repository snapshot supplied with this assessment.',
 '2. Zhang, X., Zhao, J. and LeCun, Y. (2015). Character-level Convolutional Networks for Text Classification. Advances in Neural Information Processing Systems 28. AG News corpus description and benchmark context.',
 '3. scikit-learn developers. User Guide: Text feature extraction, linear models, support vector machines, ensemble methods, nearest neighbors, model selection and classification metrics. https://scikit-learn.org/stable/user_guide.html',
 '4. scikit-learn developers. TfidfVectorizer API reference. https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html',
 '5. scikit-learn developers. train_test_split API reference. https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html',
 '6. scikit-learn developers. StratifiedKFold API reference. https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html',
 '7. scikit-learn developers. Classification metrics API reference. https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics',
 '8. Submitted file: train.csv.zip, containing train.csv. Dataset audit and held-out benchmark carried out for this report; accessed 31 October 2026.',
 '9. Submitted dashboard screenshots captured on 31 October 2026. Included as visual evidence of the ClassifyAI interface; not used as evidence for AG News benchmark metrics.'
]
for item in refs: para(item)
heading('Appendix A. Reproduction outline',1)
para('The reported procedure can be reproduced in Python with pandas, scikit-learn and a sparse TF-IDF vectorizer. The high-level steps are: read train.csv from the zip archive; map Class Index labels; combine Title and Description; split with train_test_split(test_size=0.20, stratify=y, random_state=42); fit the vectorizer on training text only; transform the held-out text; fit each estimator using the configuration and training sample size listed in Chapter 4; compute the metrics in Chapter 7; and record timing with a monotonic high-resolution clock.')
heading('Appendix B. Metric formulas',1)
table(['Measure','Formula / definition'],[
 ['Accuracy','(TP + TN) / (TP + TN + FP + FN), binary form; multiclass correct / total.'],
 ['Precision','TP / (TP + FP).'],['Recall','TP / (TP + FN).'],['F1','2 × Precision × Recall / (Precision + Recall).'],
 ['Macro average','Unweighted mean of per-class scores.'],['Weighted average','Mean of per-class scores weighted by class support.'],
 ['Balanced accuracy','Mean recall across classes.'],['Cosine distance','1 − (x · z)/(||x|| ||z||).']], [1.6,4.8])
heading('Appendix C. ClassifyAI source map',1)
table(['File','Role in this report'],[
 ['backend/app/agents/classifier_agent.py','End-to-end experiment orchestration and audit trail.'],
 ['backend/app/services/preprocessing.py','Tabular type handling, imputation, scaling and one-hot pipelines.'],
 ['backend/app/services/model_evaluator.py','Cross-validation, metric computation and timing.'],
 ['backend/app/services/model_ranker.py','Deterministic ranking, tie-breakers and ambiguity warning.'],
 ['backend/app/services/model_trainer.py','Stratified holdout and winner evaluation.'],
 ['backend/app/services/data_analyzer.py','Dataset and target profiles.'],
 ['backend/app/algorithms/logistic_regression.py','Logistic Regression factory and model metadata.'],
 ['backend/app/algorithms/svm.py','RBF-kernel SVC factory used by the tabular agent.'],
 ['backend/app/algorithms/random_forest.py','Random Forest factory.'],
 ['backend/app/algorithms/knn.py','KNN factory.']], [3.3,3.1])

doc.core_properties.title='ClassifyAI: Automated Classifier Selection and AG News Text Classification'
doc.core_properties.subject='Continuous Assessment 2, INT234'
doc.core_properties.author='Rajpurohit Omsingh'
doc.core_properties.keywords='AG News, ClassifyAI, Logistic Regression, SVM, Random Forest, KNN'
doc.save(OUT)
print(OUT)
