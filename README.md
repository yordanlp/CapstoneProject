
# PixelLift: A Web Application for AI-Driven Image Manipulation using GANs

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [System Architecture](#system-architecture)
4. [Installation on localhost](#installation-on-localhost)
5. [Database Schema](#database-schema)
6. [Application Views](#application-views)
7. [Authors](#authors)
---

## Introduction

This project is the capstone for our Master's in Computer Science at [Harbour.Space University](https://harbour.space/). It's a web application designed to offer a user-friendly interface for interacting with Generative Adversarial Networks (GANs) models. The application allows users to perform various image processing and transformation tasks using these advanced machine learning models.

The primary goal is to make GANs accessible and easy to use, even for those who may not have a technical background in machine learning or computer science. This project showcases the skills and knowledge we've gained throughout our time at the university.

Stay tuned for more details on features, system architecture, and how to get started with the project.

---


## Features

This web application offers a range of features to interact with GANs models:

### Image Transformations
- **Projection**: Map your image into the latent space of the model.
- **PCA**: Perform Principal Component Analysis on the latent space to modify your image.
- **Superresolution**: Enhance the resolution of your images.

### User Interface
- **Gallery View**: Browse through a gallery of generated and transformed images.
- **Transformation View**: Apply various transformations to your images and see the results in real-time.
- **Saved Images View**: Save your favorite images and transformations for later.

### User Management
- **User Registration**: Sign up to create your own account.
- **User Login**: Securely log in to your account to access saved images and settings.

### Real-time Updates
- **Websockets**: Receive real-time updates on the status of your image transformations.

Feel free to explore these features and more as you interact with the application.

---


## System Architecture

The architecture of this web application is designed to provide a seamless and efficient user experience while interacting with various GAN models.

### Frontend
- **Language**: TypeScript
- **Framework**: Angular
- **Tools**: HTML, CSS, and various Angular libraries and components

### Backend
- **Language**: Python
- **Framework**: Flask
- **Database**: PostgreSQL with SQLAlchemy for ORM
- **Message Queue**: Redis
- **Asynchronous Communication**: WebSockets

### Worker and Model APIs
- **Language**: Python
- **Containerization**: Docker
- **Version Control**: Git

### Models and Communication with Backend
The application employs a microservices architecture where each model is isolated in its own Docker container. This includes the worker and Redis for message queuing. The backend communicates with these models via a Redis message queue. The worker listens to this queue, processes incoming messages, triggers the corresponding model, and then publishes the response back to another Redis queue that the backend subscribes to. 

This architecture was chosen for its scalability potential. Although currently running on a single machine due to resource constraints, it can easily be scaled up by adding more instances of the models and the worker, potentially across multiple servers.

To optimize the development process, we've separated the models and their environments into different Docker containers. This allows us to make code changes without having to rebuild the entire environment, saving considerable time.


![image](https://github.com/yordanlp/CapstoneProject/assets/56166215/10d391b6-1885-4c8f-8652-3eb0ec2fcab5)



---


## Installation on localhost

This section provides step-by-step instructions on how to set up the application on your local machine.

 ### Models & Redis
 #### Prerequisites  
 - [Docker](https://www.docker.com/)
 - [Nvidia Container Support](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/1.6.0/install-guide.html)

 #### Step  1: Go to the Jobs folder
 ```
 cd ./Jobs
 ```
 #### Step  2: Build the images
 ```
build_images.sh
 ```

 #### Step  3: Run the containers with docker-compose
 ```
docker-compose up
 ```

---

 ### Backend
 #### Prerequisites  
 - Python 3.x
 - pip 
 - posgressql
 
 #### Step 1: Go to the folder of the BackendApp
 ```
 cd ./BackendApp
 ```

 #### Step  2: Create a virtual environment
 ```
python3 -m venv env
 ```
 
 #### Step  3: Activate the virtual environment
 ```
source ./env/bin/activate
 ```

 #### Step  4: Install the dependencies
 ```
pip install -r requirements.txt
 ```

 #### Step  5: Configure the environment variables
 ```
create a .env file and fill it with these values

DEBUG=False
SECRET_KEY=your_secret_key

#ORM
SQLALCHEMY_DATABASE_URI=postgresql://user:password@localhost:5432/pixel-lift-db
SQLALCHEMY_TRACK_MODIFICATIONS=False

#JWT
JWT_SECRET_KEY=your_secret_key

#IMAGES FOLDER
IMAGES_FOLDER={ProjectDirectory}/Jobs/Shared/images
PCA_FOLDER={ProjectDirectory}/Jobs/Shared/pca
UPSCALED_IMAGES_FOLDER={ProjectDirectory}/Jobs/Shared/upscaled

#REDIS
REDIS_HOST=localhost
REDIS_PORT=6379`
 ```

 #### Step  5: Create the database
 ```
 create database pixel-lift-db
 create user {user} with encrypted password {password}
 grant all privileges on database pixel-lift-db to {user}
 ```

 #### Step  6: Apply the migrations
 ```
flask db upgrade 
```

 #### Step  7: Run the application
 ```
./env/Scripts/python.exe run.py
 ```
---

 ### Frontend  
 #### Prerequisites  
 - [Node.js](https://nodejs.org/es)
 - [Angular CLI](https://angular.io/)
 
 #### Step  1: Go to the folder of the FrontendApp, install the dependencies and run the application.
 ```
 cd ./FrontendApp
 npm install
 npm start --configuration=development
 ```

#### Step  2: Go to [http://localhost:4200](http://localhost:4200)

---


## Database Schema

This section describes the database schema and the relationships between tables.

### Tables

1. **User Table**
    - `id`: Integer, Primary Key
    - `user_name`: String, Unique
    - `email`: String, Unique
    - `password`: String

2. **Image Table**
    - `id`: Integer, Primary Key
    - `name`: String
    - `user_id`: Integer, Foreign Key (`users.id`)
    - `mime_type`: String
    - `model`: String
    - `status_process`: String

3. **SavedImage Table**
    - `id`: Integer, Primary Key
    - `name`: String
    - `user_id`: Integer, Foreign Key (`users.id`)
    - `parent_image_id`: Integer, Foreign Key (`images.id`)
    - `status_superresolution`: String

### Relationships

- One-to-Many relationship between `User` and `Image`.
- One-to-Many relationship between `User` and `SavedImage`.
- One-to-Many relationship between `Image` and `SavedImage`.

![image](https://github.com/yordanlp/CapstoneProject/assets/56166215/e64ffca0-8f8a-42ec-9eb7-afacfa2fa45f)

---

## Application Views

![image](https://github.com/yordanlp/CapstoneProject/assets/56166215/4c0490f8-73c8-4950-be6f-6bc225d2d838)

![image](https://github.com/yordanlp/CapstoneProject/assets/56166215/b0654848-f1ca-42d3-bf53-6021dc69c316)

![image](https://github.com/yordanlp/CapstoneProject/assets/56166215/0287bf5b-b851-4205-9fe4-8c64ae4af540)

![image](https://github.com/yordanlp/CapstoneProject/assets/56166215/27a997ed-29a5-4a0d-a6df-eb0f52e83852)

![image](https://github.com/yordanlp/CapstoneProject/assets/56166215/cfb638df-c731-4aee-9fff-a3b78c1035cf)


## Authors

- [@yordanlp](https://www.github.com/yordanlp)
- [@ernestico98](https://www.github.com/Ernestico98)

