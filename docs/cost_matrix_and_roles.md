# Business Cost Matrix and User Roles

## 1. Cost Matrix Definition
Because this is a portfolio project of mine, I will be using documented, simulated assumptions for the business costs associated with my predictions. 

- **False Negative (FN):** The model predicts an employee is at *low risk* (e.g., < 50%), but they actually leave. 
  - *Cost Impact:* High. Replacing an employee includes recruitment, onboarding, and lost productivity. 
  - *Simulated Cost:* **$10,000** per missed employee.
- **False Positive (FP):** The model predicts an employee is at *high risk* (e.g., > 50%), but they actually stay.
  - *Cost Impact:* Low. The cost of an unnecessary intervention (e.g., a retention meeting or a small training budget).
  - *Simulated Cost:* **$500** per false alarm.

**Ratio:** The cost of a False Negative is **20x higher** than a False Positive. This means our final threshold selection will likely favor higher recall (catching more potential leavers) even at the expense of some false alarms.

## 2. User Roles and Access Control
The following matrix dictates who has access to the AI features within the Frappe HR interface:

| User Role        | Attrition Risk Panel | Skill Gap & Recommendations |
| :--------------- | :------------------- | :-------------------------- |
| **HR Admin**     | YES                  | YES                         |
| **HR Manager**   | YES                  | YES                         |
| **Employee**     | **NO**               | YES                         |
| **Regular User** | NO                   | NO                          |

**Security Rule:** Employees must never see the Attrition Risk panel for themselves or others. This is to prevent anxiety and potential discrimination. Employees *can* see their Skill Gap panel to encourage career development. Only the HR admin and manager will have access to the Attrition risk panel.