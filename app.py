from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
S=Path(__file__).with_name("site")
if __name__=="__main__":
 if not (S/"data.json").exists():print("site/data.json missing: run train.py, then build_site_data.py")
 print("http://127.0.0.1:8000")
 ThreadingHTTPServer(("127.0.0.1",8000),partial(SimpleHTTPRequestHandler,directory=str(S))).serve_forever()
