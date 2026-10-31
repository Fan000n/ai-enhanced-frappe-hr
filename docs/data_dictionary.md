# Data Dictionary and Feature Mapping

This document maps the features used in the ML model to the IBM HR Analytics dataset and the Frappe HR DocTypes.

| IBM Dataset Column | Frappe HR Equivalent     | DocType             | Data Type | Description                                        |
| :----------------- | :----------------------- | :------------------ | :-------- | :------------------------------------------------- |
| `Attrition`        | `status` (Resigned/Left) | Employee Separation | Target    | The label we are predicting (1 = Left, 0 = Stayed) |
| `Age`              | `date_of_birth`          | Employee            | Integer   | Calculated age at prediction time                  |
| `Department`       | `department`             | Employee            | Link      | Department the employee belongs to                 |
| `JobRole`          | `designation`            | Employee            | Link      | Job title/designation                              |
| `MonthlyIncome`    | `ctc` / Salary Slip      | Salary Structure    | Float     | Current compensation                               |
| `YearsAtCompany`   | `date_of_joining`        | Employee            | Date      | Calculated as (Today - Joining Date)               |
| `OverTime`         | `attendance` / `checkin` | Attendance          | Boolean   | Derived from average daily hours worked            |
