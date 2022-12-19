FROM nginx:1.23.2
COPY nginx.conf /etc/nginx/nginx.conf
COPY app.nginx.conf /etc/nginx/sites-available/app.nginx.conf
COPY uwsgi_params /etc/nginx/uwsgi_params

RUN mkdir /etc/nginx/sites-enabled
RUN ln -s /etc/nginx/sites-available/app.nginx.conf /etc/nginx/sites-enabled/
# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log
CMD ["nginx", "-g", "daemon off;"]