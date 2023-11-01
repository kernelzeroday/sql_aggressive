cat ../attack_surface.txt | cut -f2 -d: | httpx|katana | python sqla2.py "sqlmap -m" -o output.txt -i sqlmap_args_katana.txt
