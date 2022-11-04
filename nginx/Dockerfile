FROM nginx:1.21.6 as base

RUN rm /etc/nginx/conf.d/default.conf

# copy all files, including static files
COPY . .

###########
# DEV IMAGE
###########
FROM base as dev
COPY nginx.dev.conf /etc/nginx/conf.d

############
# MAIN IMAGE
############
FROM base as main
COPY nginx.conf /etc/nginx/conf.d