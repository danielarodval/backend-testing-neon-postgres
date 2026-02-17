# Backend Testing with Neon Postgres

## Description

Testing the deployment of a Neon Postgres backend with FastAPI webhooks to log data from a local server via a Tailscale proxy. Containerized using Docker to package Postgres and Fast API.

## Demo

Add a GIF, image, or link to a live demo. Visuals grab attention.

## Deployment Process

- [Singular Neon Postgres Database](./neon-solo-test)
    - Iterated through the tutorial on the Neon documentation to test the creation and understand the various sub-component scripts and requirements needed to rollout a table and update items on the online version of Neon Postgres. 
    - In doing so there are a slew of limitations found based around resources and free subscription limitations.
        - As such in the next stage/iteration with integrating Fast API I will begin doing research tangentially on docker container instances for a local implementation of Neon Postgres rather than relying on the cloud based implementation.
- [Testing Neon Postgres with Fast API](./neon-fastapi-test)
    - Commenced with the creation of the database models still leveraging the cloud instance for testing, namely focused on FastAPI and Neon interoperability.
    
- [Drafting the Actual Deployment](./actual-use-case)
    - description

## Usage

Show how to run it or use it. Include example commands or screenshots.

## Features

List key features so users know what to expect.

## Built With

Mention the languages, frameworks, and tools you used.

## License

Let people know how they can use or reuse your code.

## Credits / Acknowledgments (optional)

- [Markdown Guidelines Help](https://medium.com/@fulton_shaun/readme-rules-structure-style-and-pro-tips-faea5eb5d252)
- 