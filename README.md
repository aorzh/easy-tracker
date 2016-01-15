# easy-tracker
Track your time from command line.

###usage: 
$etrc [-h] [--category CATEGORY] [--task TASK] [--days DAYS] [init]

###positional arguments:
  init                  Can be init, start, stop, report

###optional arguments:
  -h, --help            show this help message and exit
  --category CATEGORY, -c CATEGORY
                        Category like JIRA or Work or Private etc.
  --task TASK, -t TASK  Task short description
  --days DAYS, -d DAYS  How many days (optional for reports)
  
###For getting reports:
Run 
$etrc report --category="Optional category" --task="Optional task" --days="Optionals days"
