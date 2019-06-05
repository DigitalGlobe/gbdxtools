osx:
	PYCURL_SSL_LIBRARY=openssl LDFLAGS="-L/usr/local/opt/openssl/lib" CPPFLAGS="-I/usr/local/opt/openssl/include" pip install --no-cache-dir pycurl
	pip install gbdxtools

init:
	git config core.hooksPath .githooks
	if [ "$$(uname)" = "Darwin" ]; then \
		PYCURL_SSL_LIBRARY=openssl LDFLAGS="-L/usr/local/opt/openssl/lib" CPPFLAGS="-I/usr/local/opt/openssl/include" pip install --no-cache-dir pycurl; \
	fi
	pip install -r requirements.txt