server {
listen 80;
server_name 3.144.24.182;
location / {
proxy_pass http://127.0.0.1:8000/;
}
}
