upstream celebritytodaynews {
    server 127.0.0.1:3010 fail_timeout=0;
}

upstream celebritytodaynews_api {
    server 127.0.0.1:8010 fail_timeout=0;
}

server {
    listen 80;
    server_name celebritytodaynews.com;

    location / {
        proxy_pass http://celebritytodaynews;
        proxy_redirect     off;

        proxy_cache_bypass  $http_cache_control;
        add_header X-Proxy-Cache $upstream_cache_status;
        proxy_set_header X-Real-IP $remote_addr;

        proxy_set_header   Host              $http_host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header        X-Forwarded-Proto https;
    }

    location ^~ /.well-known {
        allow all;
        auth_basic off;
        alias /home/celebs/.well-known/;
    }
}

server {
    listen 80;
    server_name www.celebritytodaynews.com;

    location / {
        proxy_pass http://celebritytodaynews;
        proxy_redirect     off;

        proxy_cache_bypass  $http_cache_control;
        add_header X-Proxy-Cache $upstream_cache_status;
        proxy_set_header X-Real-IP $remote_addr;

        proxy_set_header   Host              $http_host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header        X-Forwarded-Proto https;
    }

    location ^~ /.well-known {
        allow all;
        auth_basic off;
        alias /home/celebs/.well-known/;
    }
}

server {
    listen 80;
    server_name api.celebritytodaynews.com;

    location / {
        proxy_pass http://celebritytodaynews_api;
        proxy_redirect     off;

        proxy_cache_bypass  $http_cache_control;
        add_header X-Proxy-Cache $upstream_cache_status;
        proxy_set_header X-Real-IP $remote_addr;

        proxy_set_header   Host              $http_host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header        X-Forwarded-Proto https;
    }

    location ^~ /.well-known {
        allow all;
        auth_basic off;
        alias /home/celebs/api_server/.well-known/;
    }
}