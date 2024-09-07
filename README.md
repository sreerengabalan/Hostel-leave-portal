# Hostel Leave Application

This is a simple hostel leave application built using Python Flask and MongoDB. It allows students to apply for leave and check their application status, while administrators can manage leave requests by approving or rejecting them.

## Features

- **Student Portal:** Students can log in, submit leave requests, and monitor their approval status.
- **Admin Dashboard:** Administrators have access to all leave requests, with the ability to approve or reject them.
- **Secure Authentication:** Uses JWT (JSON Web Tokens) for secure user authentication.
- **Database:** MongoDB is used for efficient data management and scalability.

## Technologies Used

- Python Flask
- MongoDB
- Docker (for containerization)
- JWT for Authentication

## Usage

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2.Build and start the Docker containers:
   ```bash
   docker-compose up -d --build
   ```
3.Access the application:
  - Open a web browser and go to http://localhost:5000 to manage leave requests.

## Docker Image 

1.You can pull the Docker image from Docker Hub :
   ```bash
   docker pull 4run/hostel-leave-portal-app
   ```
