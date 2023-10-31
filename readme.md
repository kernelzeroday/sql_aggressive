httpx | ./sqla.py "sqlmap -m" -o output.txt -i sqlmap_args.txt
cat output.txt | python format_findings.py

