FROM node:14
EXPOSE 3000
WORKDIR usr/app
COPY package*.json ./
RUN npm i
COPY . .
CMD ["node", "index.js"]
