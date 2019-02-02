# faust-macrogen-graph
Creation of a graph which represents an absolute order of the creation date of the manuscripts based on the macrogenesis of the digital Faust-Edition (http://www.faustedition.net/).  
To learn more about the problems of an absolute manuscript order see: http://faustedition.net/intro_macrogenesis

## 1. xml file structure
### 1.1 date
<i>item release date between @notBefore and @notAfter</i>
```xml
<date notBefore="year-month-day" notAfter="year-month-day">
  <comment>...</comment>
  <source uri="faust....">...</source>
  <item uri="faust....">...</item>
</date>
```
### 1.2 relation temp-pre
<i>item1 released before item2</i>
```xml
<relation name="temp-pre">
  <source uri="faust....">...</source>
  <comment>...</comment>
  <item uri="faust....">...</item>
  <item uri="faust....">...</item>
</relation>
```

### 1.3 relation temp-syn
<i>item1 released about the same time as item2</i>
```xml
<relation name="temp-syn">
  <source uri="faust....">...</source>
  <comment>...</comment>
  <item uri="faust....">...</item>
  <item uri="faust....">...</item>
</relation>
```
