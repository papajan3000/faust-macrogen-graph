# faust-macrogen-graph
Creation of a graph which represents an absolute order of the creation date of the manuscripts based on the macrogenesis of the digital <b>Faust-Edition</b> (http://www.faustedition.net/). To learn more about the problems of an absolute manuscript order see: http://faustedition.net/intro_macrogenesis.

## 1. The issue of the manuscript macrogenesis
### 1.1. The research issue
The digital <b>Faustedition</b> delivers manuscripts of the novels <b>Faust</b> and <b>Faust II</b>. These manuscripts hold the problem that they are undated. It is furthermore possible that more than one inscription exists for a manuscript. The research tried and tries to date the making of the manuscripts but most of the dates cannot be clearly evidenced and some creation dates of the manuscripts contradict each other. It is the goal for the editors and authors of the <b>Faustedition</b> to obtain an absolute order of the manuscripts. 

### 1.2. The technical issue
To achieve this goal, the authors of the model for the <b>Faustedition</b> created a graph network which should ideally represent the manuscripts in a definite order. The contradictions of the research dates lead to appearance of <b>cycles</b> whereby a definite order is not possible. The removal of cycles within a graph is one of Karps 21 NP-complete problems (see: https://en.wikipedia.org/wiki/Karp%27s_21_NP-complete_problems) which means there is no efficient solution for the problem. The problem, which is called <b>Minimum Feedback Arc Set</b>-problem (MFAS), tries to induce a minimal <b>Feedback Arc Set</b> (FAS) and is a field of research within the computer science. There are some attempts who found a partial solution for the problem. An effiecent yet simple solution is given by Peter <b>Eades</b> (see: Eades, Peter / Lin, Xuemin / Smyth, W. F., "A Fast and Effective Heuristic for the Feedback Arc Set Problem," in: Information Processing Letters (1993), Vol. 47(6), pp. 319-323).

## 2. The challenge of this project
This project will deliver an implementation of Eades MFAS-algorithm which will be applied to the graph that represents the dating elements of the macrogenesis and is also created in this project. This project will follow the content of these following three questions:

1. How can we integrate the absolute datings? How does the FAS look like with and without absolute datings?
2. Can a more detailed analysis of the number of edges and the number of contradictions be helpful to decide which edges of which source should be removed?
3. Can erroneously removed edges be re-added without sacrificing performance? How can this be done and how many edges can be re-added?

The answers to this question and more detailed information about the approach of the creation of a reasonable and acylic graph will be explained in the jupyter notebook <b>"macrogenesismodel_nb</b>.

## 3. The tree structure layout of the project

├── data<br>
│   ├── longer_period_fas_dataframe.csv<br>
│   ├── minimize_rm_source_df(longer-period)<br>
│   ├── minimize_rm_source_df(shorter-period)<br>
│   ├── minimize_rm_source_df(vitt)<br>
│   ├── optimal_order_dict_lG(p=0).pkl<br>
│   ├── optimal_order_dict_sG(p=0).pkl<br>
│   ├── optimal_order_dict_vG(p=0).pkl<br>
│   ├── shorter_period_fas_dataframe.csv<br>
│   └── vitt_fas_dataframe.csv<br>
├── resources<br>
│   ├── macrogenesis-normalized<br>
│   │   ├── empty.xml<br>
│   │   ├── fischer-lamberg<br>
│   │   │   ├── III.xml<br>
│   │   │   └── II.xml<br>
│   │   ├── handschriftendatierung_iii.xml<br>
│   │   ├── handschriftendatierung_ii.xml<br>
│   │   ├── handschriftendatierung_iv.xml<br>
│   │   ├── handschriftendatierung_i.xml<br>
│   │   ├── handschriftendatierung_pre1800.xml<br>
│   │   ├── handschriftendatierung_uncertain.xml<br>
│   │   ├── handschriftendatierung_v.xml<br>
│   │   ├── macrogenesis.rnc<br>
│   │   ├── self<br>
│   │   │   ├── self_1.xml<br>
│   │   │   ├── self_2_III.xml<br>
│   │   │   ├── self_2_II.xml<br>
│   │   │   ├── self_2_IV.xml<br>
│   │   │   ├── self_2_I.xml<br>
│   │   │   ├── self_2_V.xml<br>
│   │   │   └── self_print.xml<br>
│   │   └── wa<br>
│   │       └── 15_2<br>
│   │           ├── III.xml<br>
│   │           ├── II.xml<br>
│   │           ├── IV.xml<br>
│   │           ├── I.xml<br>
│   │           └── V.xml<br>
│   ├── macrogenesis-normalized.zip<br>
│   └── vitt_macrogen.pdf<br>
└── src<br>
    ├── faust_macrogen_graph<br>
    │   ├── analyzeutils.py<br>
    │   ├── approachesutils.py<br>
    │   ├── comparisonutils.py<br>
    │   ├── eades_fas.py<br>
    │   ├── graphutils.py<br>
    │   ├── __init_.py<br>
    │   ├── parserutils.py<br>
├── macrogenesismodel_nb.ipynb<br>
├── README.md<br>
├── setup.cfg<br>
├── setup.py<br>


## 4. Short explanation of the most important files and folders
### 4.1. data

This folder stores saved pkl-, txt- and csv-files which are relevant for analyzes within the <b>"macrogenesismodel_nb"</b>-notebook but had to be saved because the calculation of the data inside these files took a long time.

### 4.2. resources

This folder stores the macrogensis data within the XML files and a pdf-file referenced in the src/faust_macrogen_graph/approachesutils.py file. For this project, only three XML elements of the macrogenesis are relevant for our purposes and the structure of these is shown below:

#### 4.2.1. date elements
<i>item release date between @notBefore and @notAfter</i>
```xml
<date notBefore="year-month-day" notAfter="year-month-day">
  <comment>...</comment>
  <source uri="faust....">...</source>
  <item uri="faust....">...</item>
</date>
```
#### 4.2.2. relation elements with @temppre-attribute
<i>item1 released before item2</i>
```xml
<relation name="temp-pre">
  <source uri="faust....">...</source>
  <comment>...</comment>
  <item uri="faust....">...</item>
  <item uri="faust....">...</item>
</relation>
```

#### 4.2.3. relation elements with @tempsyn-attribute
<i>item1 released about the same time as item2</i>
```xml
<relation name="temp-syn">
  <source uri="faust....">...</source>
  <comment>...</comment>
  <item uri="faust....">...</item>
  <item uri="faust....">...</item>
</relation>
```

### 4.3. src
<b>analyzeutils.py</b>: In this file are the functions stored which are mainly relevant for the analyzing of the macrogenesis sources like normalizing the publication years of the sources, minimizing the removal of the sources and finding optimal source orders for a minimal source removal.<br>
<b>approachesutils.py</b>: In this file are the functions stored which implements six different implementation approaches of the date-elements of the macrogenesis.<br>
<b>comparisonutils.py</b>: In this file are the functions stored which compare the approaches of the <i>approachesutils.py</i> and their features with eachother.<br>
<b>eades_fas.py</b>: This file implements the minimum feedback arc set algorithm by Peter <b>Eades</b> and a variation of this algorithm by Felix <b>Tintelnot</b>.<br>
<b>graphutils.py</b>: In this file are the functions stored which are relevant for the creation of the graphs of the three different XML elements (see 4.2) and the removing and re-adding of edges to graphs.<br>
<b>parserutils.py</b>: In this file are the functions stored which parses the XML files of the macrogenesis for the three different XML elements (see 4.2).


### 4.4. macrogenesismodel_nb.ipynb

In this notebook will the whole process of the analysis, consideration and implementation of an acyclic macrogenesis graph be explained and performed. 
Further information will be provided by the notebook itself.

