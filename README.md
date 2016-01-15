# easy-tracker
Track your time from command line.

usage: etrc [-h] [--category CATEGORY] [--task TASK] [--days DAYS] [init]

positional arguments:
  init                  Can be init, start, stop, report

optional arguments:
  -h, --help            show this help message and exit
  --category CATEGORY, -c CATEGORY
                        Category like JIRA or Work or Private etc.
  --task TASK, -t TASK  Task short description
  --days DAYS, -d DAYS  How many days (optional for reports)
  
  For getting reports like:
Id|Category       |Name                                                             |Spent hours    |
 1|Private        |Main issues on the light tacker                                  |0:08:29        |
 2|Private        |Main issues on the light tacker, Work on a reports               |0:04:30        |
 3|Private        |Add arguments tor report                                         |0:25:51        |
 4|Private        |Add arguments tor report                                         |0:23:29        |
 5|Private        |Prepare code for app                                             |0:05:32        |
 6|Testing        |Test args                                                        |1:35:21        |
*****************
Total: 2:43:12.020602 (hh:mm:ss)

Run etrc report --category="Optional category" --task="Optional task" --days="Optionals days"
