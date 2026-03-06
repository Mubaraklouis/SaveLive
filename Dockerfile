FROM node:20-alpine

WORKDIR /app

RUN apk add --update --no-cache python3 py3-pip

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

COPY translator_dependencies.txt ./
RUN pip install --no-cache-dir --break-system-packages -r translator_dependencies.txt

# Copy application source
COPY . .

EXPOSE 3000

CMD ["npm", "start"]
