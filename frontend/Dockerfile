FROM node:15.0
 
WORKDIR /var/www/frontend
 
COPY package*.json ./
 
RUN npm install
 
COPY . .
 
EXPOSE 3000
 
CMD [ "npm", "start" ]