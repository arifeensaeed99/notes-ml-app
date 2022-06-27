mkdir -p ~/.streamlit/
echo "[theme]
primaryColor='#ff5353'
backgroundColor='#f9f4e6'
secondaryBackgroundColor='#f7e14b'
textColor='#000000'
font='serif'
[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml