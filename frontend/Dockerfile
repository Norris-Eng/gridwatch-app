# Stage 1: Use the official Nginx image
FROM nginx:alpine

# Stage 2: Copy the custom Nginx config to replace the default one
COPY default.conf /etc/nginx/conf.d/default.conf

# Stage 3: Copy the HTML file to the web root
COPY index.html /usr/share/nginx/html/index.html

# Stage 4: Expose port 80
EXPOSE 80