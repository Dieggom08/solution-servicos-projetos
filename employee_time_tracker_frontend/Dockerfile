# Use an official Node.js runtime as a parent image
# Use a version compatible with the Next.js app (Node 20 was used in sandbox)
FROM node:20-slim

# Set the working directory in the container
WORKDIR /app

# Install pnpm globally (as used by create_nextjs_app template)
RUN npm install -g pnpm

# Copy package.json and pnpm-lock.yaml first to leverage Docker cache
COPY package.json pnpm-lock.yaml* ./

# Install dependencies using pnpm
RUN pnpm install --frozen-lockfile

# Copy the rest of the application code
COPY . .

# Build the Next.js application for production
RUN pnpm run build

# Expose the port the app runs on (default for Next.js is 3000)
# Cloud Run will automatically use the PORT environment variable
EXPOSE 3000

# Define the command to start the application
# Use the PORT environment variable provided by Cloud Run
CMD ["pnpm", "start", "--port", "$PORT"]

