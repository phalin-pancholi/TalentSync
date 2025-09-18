# Development Dockerfile for React frontend
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install dependencies for development
RUN apk add --no-cache git

# Copy package files
COPY package.json yarn.lock ./

# Install all dependencies (including devDependencies)
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Start development server
CMD ["yarn", "start"]