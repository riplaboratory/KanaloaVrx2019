# Docker Hub
## Commonly used commands
Docker is a tool that allows companies to create, distribute and run applications all inside a container. Containers are essentially virtual machines that use less resources for the application that they run. The advantage of a container is that they are universal. The developer does not need to worry about compatibility issues with the the customer’s computer.

This tutorial assumes you have Docker installed on Ubuntu 18.04.
If you do not, you can install Docker from this link https://docs.docker.com/install/linux/docker-ce/ubuntu/

## There are two main vocabulary words to understand, Images and Containers. 
### An Image 
An image is what you download from the docker website. It is the base program that you will then build off of. Depending on which Image you download it has specific attributes to it. These attributes can be changed if you create a container from the image but cannot be changed directly. 

### A Container
A container is an instance of the downloaded image. This container inherits all the properties of the image and can be edited to have different applications or files held within it. This container is independent of the image and any other containers created from your base image.

More about containers: in order for people to be able to access your container from the docker website you will need to commit your container and push it to docker. Until then your container is only available from your local machine. If you delete your container before committing it all progress on that container will be lost.  

### To download an image from the internet
	1. Go to docker hub and search for ubuntu
	2. Copy the pull command from the image repository
	3. Past into the terminal
Example: docker pull ubuntu:latest

we use the tag "latest" to identify the version of the image we wish to pull. This allows us to have the same name for an image but different build states to go back to if need be. For example I could have an image called "my_image" and have three different build states my_image:v1.0   my_image:v2.0   my_image:latest

I find it useful to set your latest build with the tag latest because if someone is pulling your image and they do not specify a version, docker will automatically assign the "latest" tag to the image.

### To look at your images
#### In the terminal type out:
	docker images

### To create a new intractable, running docker container from an image
(--name allows you to set a name for your container making it ease to distinguish between different containers of the same image)
docker run --name my_container <USERNAME>/<IMAGE_REPOSITORY_NAME>:<TAG>

### Editing a container
You must enter the container to edit it, make sure the container is running. To enter an existing docker container in bash:
docker exec -it <container name> bash 

### To exit a container but keep it running
CTRL + P + Q

### To exit and close a container you are currently in type
exit
Adding files to container (you will need to move to the location of your file then) in terminal write: 
docker cp <file_name> <container ID>:/home/developer/vrx_ws/src/vrx


### To check running containers:
docker ps

### To check running and non running containers:
docker ps -a

### To start a container:
docker start <Container ID>

### To stop a container:
docker stop <Container ID>

### How to push a container to Docker Hub:
docker commit <Container ID> <username/repository_name:tag>
Ex: docker commit my_container jordandalessandro/vrx-challenge:v4_2019

	### Then run:
	docker login
	You will need to login with your username and password in the terminal

	### After login in we need to push our container to the repository
	docker push jordandalessandro/vrx-challenge:v4_2019


### Removing a container
WARNING! Removing a container will get rid of all progress you have made in that container.
If you want to save your progress, look at HOW TO COMMIT A CONTAINER
If you want to remove containers that you are not using anymore make sure the image is not running with docker ps if the comtainer is not listed this means it is not running
docker rm <Container ID>


### Removing an image
To remove image (any containers associated with this image must be removed first)
docker rmi <Image ID>

Good resource: https://ligerlearn.com/how-to-edit-files-within-docker-containers/
	       https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04

