# Word Dictionary Microservice

This microservice is responsible for supplying other microservices with words from Wiktionary. Since the team behind Wiktionary does not have an easily-accessible API as of the creation of this project, we download a Wiktionary dump, parse it, store it in a database and finally make the parsed entries accessible with a REST API.