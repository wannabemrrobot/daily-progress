### Docker - Building Custom Docker Images

Learning how to build your own docker images (well not from scratch though) using existing base image.

Learning how to write `Dockerfile`, a configuration file used to drive the build process of custom images.

#### Outcomes: 
- Learning simple commands/instructions in Dockerfile
  - FROM
  - RUN
  - CMD
- Build Command
  - docker build
- Docker Build behind the scenes
- Docker rebuilding with cache
- Tagging an image
  - docker build -t mydockerID/reponame:version [dockerbuild-context]
- Manually creating image, with changes in a container
  - docker commit -c 'CMD ["command-to-run-on-container-start"]' containerID

#### Reference:
- Yet to be uploaded [my notes on Github]()