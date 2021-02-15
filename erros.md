# Correções a serem feitas:
- ADH1_RAT(Adh1) e REVERSE;
- Isoformas;
- Score < 60.000


## Isoformas
Excluir isoformas de um mesmo spot, deixando com maior score;
### Spot 1
Gene Symbol | Protein | Score
------------|---------|--------
Gstm1	| Glutathione S-transferase Mu 1 | 831.7065
Gstm2	| Glutathione S-transferase Mu 2 | 473.9019
Gstm4	| Glutathione S-transferase Mu 4 | 326.3851
Gstm7	| Glutathione S-transferase Mu 7 | 491.9276

Deixar somente como <b>Glutathione S-transferase</b> com maior score.

Gene Symbol | Protein | Score
------------|---------|--------
Gstm1	| Glutathione S-transferase | 831.7065

## Proteína REVERSE e ADH1
Essas proteínas não precisam ser lidas no arquivo .csv, podem ser excluídas.

## Score < 60.000
Se um spot tiver mais que uma proteína, então devem ser excluídas as proteínas com score < 60.000. Mas se um spot só tiver uma proteína e ela tiver score < 60.000, não deve ser excluída essa proteína.
