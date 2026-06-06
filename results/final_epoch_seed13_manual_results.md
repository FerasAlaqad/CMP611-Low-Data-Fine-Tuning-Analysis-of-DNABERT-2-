# Final Epoch-Based Results - Seed 13

These values were manually preserved from the Colab console output after the runtime disconnected before the zip download completed.

| Task | Ratio (%) | Seed | F1-macro | AUROC | AUPRC |
|---|---:|---:|---:|---:|---:|
| core_promoter | 0.05 | 13 | 0.391696 | 0.463438 | 0.477495 |
| core_promoter | 0.10 | 13 | 0.482502 | 0.555684 | 0.545704 |
| core_promoter | 1.00 | 13 | 0.676635 | 0.811098 | 0.828274 |
| core_promoter | 10.00 | 13 | 0.801351 | 0.877410 | 0.879398 |
| core_promoter | 100.00 | 13 | 0.820204 | 0.871411 | 0.825020 |
| nontata_promoter | 0.05 | 13 | 0.557477 | 0.602789 | 0.639379 |
| nontata_promoter | 0.10 | 13 | 0.503886 | 0.787018 | 0.837381 |
| nontata_promoter | 1.00 | 13 | 0.775203 | 0.820748 | 0.882611 |
| nontata_promoter | 10.00 | 13 | 0.813987 | 0.898601 | 0.932727 |
| nontata_promoter | 100.00 | 13 | 0.894504 | 0.950110 | 0.966698 |
| promoter | 0.05 | 13 | 0.475100 | 0.586574 | 0.581162 |
| promoter | 0.10 | 13 | 0.586212 | 0.640563 | 0.640447 |
| promoter | 1.00 | 13 | 0.890594 | 0.943899 | 0.932633 |
| promoter | 10.00 | 13 | 0.905061 | 0.964324 | 0.954816 |
| promoter | 100.00 | 13 | 0.920062 | 0.970103 | 0.960436 |
| splice | 0.05 | 13 | 0.276599 | 0.453054 | 0.308650 |
| splice | 0.10 | 13 | 0.241855 | 0.477438 | 0.319221 |
| splice | 1.00 | 13 | 0.240889 | 0.518125 | 0.347676 |
| splice | 10.00 | 13 | 0.745049 | 0.884410 | 0.798558 |
| splice | 100.00 | 13 | 0.889974 | 0.965854 | 0.938140 |

## Short Interpretation

- Promoter detection improves sharply from 0.1% to 1%, reaching high performance even with only 1% training data.
- Core promoter detection is harder than promoter detection at tiny ratios, but becomes strong at 10% and 100%.
- Splice site prediction is the most data-hungry task: very weak at 0.05%, 0.1%, and 1%, but strong at 10% and 100%.
- Non-TATA promoter detection shows useful learning from 1% onward and reaches its best result at 100%.
