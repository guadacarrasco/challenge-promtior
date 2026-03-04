To complete this challenge, I first developed the solution locally. My goal was to create a high-quality experience with low latency and a smooth UI before moving to production. Originally, I thought the challenge required a specific local model, so I started with LLaMA2 using Ollama. However, because this model has 7 billion parameters, it was very slow, taking about 80 to 90 seconds to respond. After contacting the team, I learned I could use any model, so I began looking for faster alternatives.


While testing smaller local models improved the speed slightly, I encountered a major problem when deploying to Railway. The free tier has limited memory, and running local LLMs requires more than 1GB of RAM, which caused the app to crash. To solve both the latency and the memory issues, I decided to switch to the OpenAI API. This was a great decision because the response time dropped from 80 seconds to less than 2 seconds, and the project became much lighter and more stable.


This change also allowed me to simplify the project. Initially, I built a complex streaming logic in the frontend so the user wouldn't think the app was frozen while waiting. Since OpenAI is almost instant, I refactored the React code to make it cleaner and easier to maintain.

Additionally, I faced an issue with the Dockerfile. I was using a python-slim image, which forced PyTorch to compile from source, taking over an hour to build. I decided to switch to a full Python image. Even though the image is larger, it saved me a lot of development time because it uses pre-compiled binaries. Finally, I deployed the project on Railway using two separate services: one for the frontend and one for the backend.

Initially, the vector store was empty every time the app started. I had to manually run a command to upload the information, which was very inefficient for a real project. To solve this, I updated the code so the app now checks the database automatically when it turns on. If the database is empty, it starts the ingestion process by itself. 


At first, I was only scraping the company's homepage, but details like the founding date (May 2023) were missing from that page. I fixed this by adding more sources, including the "Services" and "Use Cases" pages, and also the technical test PDF. 

I also had to restrict the chatbot so it only answers questions related to Promtior and the data sources I provided. Originally, the model could answer any general knowledge question, which was a problem because users could use our API for other purposes. This would increase our OpenAI costs unnecessarily. To fix this, I added instructions to the prompt, ensuring the chatbot stays on topic and avoids spending money on queries that are not related to the project.

If I had more time, I would implement protection against DOS attacks. My plan is to track the user’s IP address and limit the number of questions they can ask per day, in order to prevent irresponsible use or automated bots from sending thousands of requests to the OpenAI API. 