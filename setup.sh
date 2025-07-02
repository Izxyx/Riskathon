mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
[theme]\n\
primaryColor = '#ffe400'\n\
backgroundColor = '#ffe400'\n\
secondaryBackgroundColor = '#a2a2a4'\n\
textColor = '#ffffff'\n\
" > ~/.streamlit/config.toml