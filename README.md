# faust-macrogen-graph
Creation of a graph which represents an absolute order of the creation date of the manuscripts based on the macrogenesis of the digital <b>Faust-Edition</b> (http://www.faustedition.net/).  
To learn more about the problems of an absolute manuscript order see: http://faustedition.net/intro_macrogenesis

## 1. The issue of manuscript macrogenesis
### 1.1 The ... issue
The digital <b>Faustedition</b> delivers manuscript of the novels <b>Faust</b> and <b>Faust II</b>. These manuscript hold the problem that they are undated. It is furthermore possible that more than one inscriptions exist for a manuscript. The research tried and tries to date the making of the manuscripts but most of the dates cannot be clearly evidenced and some creation dates of the manuscripts contradict each other. It is the goal for the editors and authors of the <b>Faustedition</b> to obtain an absolute order of the manuscripts. 

### 1.2 The technical issue
To achieve this goal, the makers of the program model for the <b>Faustedition</b> created a graph network which should ideally represent the manuscript in a definite order. The contradictions of the research dates lead to appearance of <b>cycles</b> whereby a definite order is not possible. The removal of cycles within a graph is one of Karps 21 NP-complete problems (see: https://en.wikipedia.org/wiki/Karp%27s_21_NP-complete_problems) which means there is no efficient solution for the problem. The problem, which is called <b>Minimum Feedback Arc Set</b> (MFAS) and tries to induce a minimal <b>Feedback Arc Set</b> (FAS), is a field of research within the computer science and there are some attempts who found a partial solution for the problem. 
EADES, BAHAREV

## 2. The challenge of this project 

## ?. xml file structure
### ?.1 date
<i>item release date between @notBefore and @notAfter</i>
```xml
<date notBefore="year-month-day" notAfter="year-month-day">
  <comment>...</comment>
  <source uri="faust....">...</source>
  <item uri="faust....">...</item>
</date>
```
### ?.2 relation temp-pre
<i>item1 released before item2</i>
```xml
<relation name="temp-pre">
  <source uri="faust....">...</source>
  <comment>...</comment>
  <item uri="faust....">...</item>
  <item uri="faust....">...</item>
</relation>
```

### ?.3 relation temp-syn
<i>item1 released about the same time as item2</i>
```xml
<relation name="temp-syn">
  <source uri="faust....">...</source>
  <comment>...</comment>
  <item uri="faust....">...</item>
  <item uri="faust....">...</item>
</relation>
```
