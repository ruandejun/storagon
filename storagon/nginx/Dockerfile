FROM node:15.0 as build
 
WORKDIR /var/www/frontend
 
COPY ./frontend/package*.json ./
 
RUN npm install

COPY ./frontend/ ./
 
RUN npm run build


FROM nginx:alpine
RUN apk add --update curl && \
    rm -rf /var/cache/apk/*
RUN mkdir -p /var/www/storagon/media && \
    mkdir -p /var/www/storagon/django_static && \
    mkdir -p /var/www/conf/ && \
    mkdir -p /var/log/nginx/
WORKDIR /var/www/storagon/frontend
COPY storagon/nginx/nginx.conf /var/www/conf/nginx.conf
COPY storagon/nginx/htpasswd.txt /var/www/conf/htpasswd.txt
COPY storagon/nginx/mime.types /var/www/conf/mime.types
COPY storagon/nginx/uwsgi_params /var/www/conf/uwsgi_params
COPY static /var/www/storagon/django_static

COPY --from=build /var/www/frontend/build /var/www/html

EXPOSE 80 443
CMD ["nginx", "-c", "/var/www/conf/nginx.conf"]
# CMD ["nginx", "-g", "daemon off;"]
