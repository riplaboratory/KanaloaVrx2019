# Docker Hub

Docker is a tool that allows companies to create, distribute and run applications all inside a container. Containers are  virtual environments that use less resources to run their application than virtual machines.

This tutorial assumes you have Docker installed on Ubuntu 18.04, an account on Docker Hub and a basic understanding of terminal commands.

If you do not, you can install Docker from this link: https://docs.docker.com/install/linux/docker-ce/ubuntu/

You can create a profile here: https://hub.docker.com/

## There are two main vocabulary words to understand, Images and Containers. 
### An Image 
An image is what you download from the docker website. It is the base program that you will then build off of. Depending on which Image you download it has specific attributes to it. These attributes can be changed if you create a container from the image but cannot be changed directly. 

### A Container
A container is an instance of the downloaded image. This container inherits all the properties of the image and can be edited to have different applications or files held within it. This container is independent of the image and any other containers created from your base image.

More about containers: in order for people to be able to access your container you will need to commit your container and push it to the docker website. Until then your container is only available from your local machine. ***If you delete your container before committing it all progress on that container will be lost.***



### To download an image from the internet
	1. Go to docker hub and search for ubuntu
	2. Copy the pull command from the image repository
	3. Past into the terminal
	Example: docker pull ubuntu:latest
![Image of docker hub's official ubuntu image](https://github.com/JordanDalessandro/Images/blob/master/Docker_Tutorial/DockerHub_ubuntu.png)

We use the ***tag*** `latest` to identify the version of the image we wish to pull. Tags allow us to have different build states of a single image. For example I could have an image called "my_image" and have three different build states my_image:v1.0   my_image:v2.0   my_image:latest

I find it useful to have a build with the tag latest because if someone is pulling your image and they do not specify a version, docker will automatically assign the "latest" tag to the image.

### To look at your images
##### In the terminal type out:
	docker images
##### If you get an authorization error prepend this and all other docker commands with sudo:
	sudo docker images

### To create a new interactable, running docker container from an image
	docker run -it --name my_container <USERNAME>/<IMAGE_REPOSITORY_NAME>:<TAG>
	
For example:

![Image of above command in terminal](https://github.com/JordanDalessandro/Images/blob/master/Docker_Tutorial/docker_images.png)

You will now be inside the docker container. This is how you can tell;

![Image of container identification](https://github.com/JordanDalessandro/Images/blob/master/Docker_Tutorial/container_indicator.png)

***--name***
Allows you to set a custom name for your container. If this isn't set docker will randomize a name you can use. But custom names make it ease to distinguish between multiple containers of the same image.

***-i***
Creates a stdin stream. This allows us to input commands and files into our container. You can think of this as a command that makes an "interactable" shell within the container you will create. This is how we will edit documents within the terminal. 

***-t*** 
Allows for your host machine to open a terminal like environment for your container.

### Editing a container
Now that we are in our ubuntu container it works just like any other ubuntu OS. But the image we pulled from hardly has anything installed. Lets install the text editor Nano:

	apt update
	apt install nano
We do not need to prepend these commands with sudo because we are operating as the root user.
We can now use the nano application to edit files.

### Exiting a container
There are two ways to exit a container

#### To exit a container but keep it running

	CTRL + P + Q
	
	exit
	
### To enter a container
You must enter the container to edit it. To enter an existing docker container in bash:

#### check running containers only:

	docker ps
	
If it is not running you can check all containers with this command:

	docker ps -a

In order to start your container:

	docker start <Container ID>
	
![ContainerID and name](https://github.com/JordanDalessandro/Images/blob/master/Docker_Tutorial/ContainerID_and_name.png)

Each container has an ID and name associated with it. For our Ubuntu container its ID is `266c7fc7c467` and we named it `my_container`.

In our case we would use:

	docker start my_container
	
or 

	docker start 266c7fc7c467

Then we would enter the container:

	docker exec -it my_container bash 
	
or 

	docker exec -it 266c7fc7c467 bash

The "bash" command tells docker to put us into a bash shell of the container. This is the same place we were when we created the container from our image and like before the `-it` command gives us an interactive terminal window to work with.

## Copying files to your container:
This might be easier with one terminal tab opened to your local host and another tab in the container.

When adding files to container you will need to move to the location of your file in the terminal on the host machine.

For example: 

![Desired location to copy](https://github.com/JordanDalessandro/Images/blob/master/Docker_Tutorial/cp_file_path.png)

I will be copying the folder _Team_Kanaloa_ into my_container.

Once at the desired location in terminal write: 

	docker cp <file_name> <container ID>:[container path]

This will copy the file from you local machine to the container.

To find the desired location within your container you can use the _pwd_ command to print the path you are in. copy this path:

![container directory](https://github.com/JordanDalessandro/Images/blob/master/Docker_Tutorial/container_cp_location.png)

My final command is:
	
	docker cp Team_Kanaloa my_container:/home
	
I am copying the folder _Team_Kanaloa_ to the _my_container_ container and it will be copied to my _/home_ directory.

Within your docker containner at the home directory you can check that the file is there by typing.
	
	ls

### How to push a container to Docker Hub:
Exit your container. We want to exit and stop the container before uploading it to our repository

#### To stop running your container use:

	docker stop <Container ID>

docker commit <Container ID> <username/repository_name:tag>
Ex: 
	
	docker commit my_container jordandalessandro/ubuntu:latest

Replace jordandalessandro with your username.
Then run:
	
	docker login

You will need to login with your username and password in the terminal.

After logging in we need to push our container to the repository:
	
	docker push jordandalessandro/ubuntu:latest

Once docker has pushed your container to its website you can view it by logging in and going to your repository section.
![Docker Hub Repository](https://github.com/JordanDalessandro/Images/blob/master/Docker_Tutorial/DockerHub_Repository.png)

### Removing a container
***WARNING! Removing a container will get rid of all progress you have made in that container.
If you want to save your progress, look at HOW TO COMMIT A CONTAINER***

If you want to remove containers that you are not using anymore make sure the container is not running using the command  _docker ps_ if the container is not listed this means it is not running. You can use the container's ID or the name you gave it in the beggining.

	docker rm my_container

### Removing an image
To remove image (any containers associated with this image must be stopped and removed first)

	docker rmi <Image ID>


Good resource: 
	More info on editing files: https://ligerlearn.com/how-to-edit-files-within-docker-containers/
	How to install docker: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04
	Commands and their meanings: https://docs.docker.com/engine/reference/commandline/exec/
	A good explanation of the -it command: https://stackoverflow.com/questions/30137135/confused-about-docker-t-option-to-allocate-a-pseudo-tty

