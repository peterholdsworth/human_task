# human_task

An Airflow plugin which adds HumanTaskOperator and Human Task List page to the UI.

When a HumanTaskOperator task instance runs it adds a line to the Human Task table. 
Users may Claim a task, then either set it to Completed, Release it for someone else to Claim, or mark it as Failed.
