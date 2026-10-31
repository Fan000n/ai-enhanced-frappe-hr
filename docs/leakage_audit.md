# Leakage Audit

The purpose of this audit is to ensure the model does not use data that would only be known **after** the prediction is made. The prediction is meant to be made at time `T` (e.g., end of month) to predict attrition in the future window (e.g., next 6 months).

| Candidate Feature          | Available at Prediction Time? | Keep?  | Reason / Decision                                                                                             |
| :------------------------- | :---------------------------- | :----- | :------------------------------------------------------------------------------------------------------------ |
| `date_of_joining` (Tenure) | Yes                           | Yes    | Historical fact, always known.                                                                                |
| `department`               | Yes                           | Yes    | Current state, always known.                                                                                  |
| `MonthlyIncome`            | Yes                           | Yes    | Current salary is known.                                                                                      |
| `Attrition` (Target)       | N/A                           | N/A    | This is the label we are predicting.                                                                          |
| `TerminationDate`          | No                            | **No** | **Direct Leakage.** We cannot use the exact date someone quits if we are trying to predict if they will quit. |
| `ExitInterviewReason`      | No                            | **No** | **Post-Exit Data.** This is recorded only after the employee leaves. Using it would be cheating.              |
| `LastPromotionDate`        | Yes                           | Yes    | If promotion happened in the past, it is valid history.                                                       |