#sql_aggressive

```
httpx | ./sqla.py "sqlmap -m" -o output.txt -i sqlmap_args.txt
cat output.txt | python format_findings.py


cat output.txt | python format_findings.py  > found.txt ; cat output.txt | python process_higher_levels.py --found found.txt | python sqla_tamper_tantrum.py "sqlmap -m" -o output.txt -i sqlmap_args_level2.txt -t tampers.txt

httpx | python sqla_tamper_tantrum.py "sqlmap -m" -o output.txt -i sqlmap_args.txt -t tampers.txt


python fancy_surface.py --attack_surface attack_surface.txt --found found.txt --color
```
