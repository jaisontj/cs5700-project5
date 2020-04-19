project:
	cp dnsserver.py dnsserver
	chmod +x dnsserver
	cp httpserver.py httpserver
	chmod +x httpserver

clean:
	rm httpserver
	rm dnsserver

