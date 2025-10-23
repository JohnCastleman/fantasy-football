# Tool Usage Log

## 2025-10-08 — Test runner: Dump ROS K and ROS DST tab-delimited lists

- Date: 2025-10-08
- Test settings (intent): DUMP, rankingType=ROS, positions=[K, DST]
- Command used (from project root):

```powershell
clear; $env:NODE_PATH = "C:\Users\johnc\AppData\Roaming\npm\node_modules"; node ".\code\client\tests\index.js"
```

- Outputs: Copied the terminal tab-delimited output into a temp scratchpad file for tab char manipulation, copied the updated content for use elsewhere and then discarded the temp file after use.

---

(Keep this file as a short-lived session log or commit to the repository if you want persistent history.)

---

## 2025-10-09 — Test runner: Dump WEEKLY K and WEEKLY DST tab-delimited lists (TSV)

- Date: 2025-10-09
- Test settings (intent): DUMP, rankingType=WEEKLY, positions=[K, DST]
- Command used (from project root):

```powershell
clear; $env:NODE_PATH = "C:\Users\johnc\AppData\Roaming\npm\node_modules"; node ".\code\client\tests\index.js" > ".\code\client\tests\output\tmp_runner_output.txt"
```

- Outputs: Captured stdout to `code/client/tests/output/tmp_runner_output.txt`; created `code/client/tests/output/tmp_runner_output_tabs.txt` where columns are explicitly separated by tab characters for spreadsheet copy/paste (TSV). Both temp files were removed after verification and user confirmed success.

---
