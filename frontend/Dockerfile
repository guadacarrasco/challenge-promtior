FROM node:18-alpine

# Nos ubicamos en la carpeta de trabajo del contenedor
WORKDIR /app

# Copiamos los archivos de dependencias
COPY package*.json ./

# Instalamos las dependencias
RUN npm install

# Copiamos todo el código del frontend
COPY . .

# Compilamos la aplicación de Next.js para producción
RUN npm run build

# Exponemos el puerto
EXPOSE 3000

# Iniciamos el servidor en modo producción
CMD ["npx", "next", "start", "-H", "0.0.0.0"]