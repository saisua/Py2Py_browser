import os

init_pages = os.getenv(
	"P2Py_BROWSER_INIT_URLS",
	"http://test_website.html.p2p"
	# "https://www.duckduckgo.com,"
	# "http://testvideo.webm.p2p,"
	# "http://cloud_country.weba.p2p,"
).split(',')

# TODO: allow offline only browsing
