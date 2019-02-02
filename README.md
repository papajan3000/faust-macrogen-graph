# faust-macrogen-graph
Creation of a graph which represents an absolute order of the creation date of the manuscripts based on the macrogenesis of the digital Faust-Edition (http://www.faustedition.net/)

## 1. xml file structure
### 1.1 date
```xml
<date notBefore="year-month-day" notAfter="year-month-day">
  <comment>...</comment>
  <source uri="faust....">...</source>
  <item uri="faust....">...</item>
</date>
```
