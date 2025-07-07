FROM golang:1.24.4-alpine AS builder

# Create and change to the app directory.
WORKDIR /app

# Retrieve application dependencies.
# This allows the container build to reuse cached dependencies.
# Expecting to copy go.mod and go.sum to the build context.
COPY go.* ./
RUN go mod download

# Copy local code to the container image.
COPY . ./

# Build the binary.
RUN CGO_ENABLED=0 GOOS=linux go build -o /smarthome-backend

# Use a slimier image for the final build.
FROM alpine:latest

# Copy the binary to the production image.
COPY --from=builder /smarthome-backend /smarthome-backend

# Expose the port that the application listens on.
EXPOSE 8085

# Run the web service on container startup.
CMD ["/smarthome-backend"]
