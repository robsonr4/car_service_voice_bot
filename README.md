# Car Service Voice Bot

## Overview

This is a voice bot secretary for Lexus, & toyota car service. It was made for my NLP classes at my University, as well as, for my parents business which I may implement in the future. The voice bot is in Polish language since the car service is in Poland.

### Reasoning behind the project

Primary purpose of the project is to save time on calls that could be resolved by a bot or afterwards by my parents. Many times, especially potential clients, make calls to the car service that are time wasting, inappropriate, or could be resolved a lot faster with simple massage. Hence, the project is not simply a university assignment, but has a real justification and is made as if it was used at the car company.

### Tech stack, & libraries

* Django server;
* Twilio api;
* OpenAI api.

### Features

* Receives calls through Twilio Api;
* Conversation tree has 2 main branches;
  * Signing up for a car inspection;
  * Leaving a message for someone at the car service, like questions or ask for a callback for particular issue, other service than car inspection.
* Production cost efficienct features, like:
  * Blocking client's requests other than the ones listed at the beggining of the conversation;
  * Ending calls after the client stops responding;
  * Ending calls if the bot cannot understand the purpose of the call after 3 tries.
* Saving inputs in DB, like message content or informations for car inspection register;
* Prevention of user erros, like wrong car brand or wrong car brand's model;
* Ability to change client's information, if the voice transcriber gets it wrong;
* Ability to delete all saved informations if the client changed own mind.

### What could be improved in the future?

* Improving voice transcription, since the api gets it wrong sometimes;
* Better instructions, being dyslexic doesn't help :) ;
* Performance of server overall, so that the registering of inputs & the flow of the conversation is faster.

### What I learned?

* Integration of Twilio Call api;
* OpenAI api and integration with conversation flow;
* Prompt engineering for better reliability;
* NGROK hosting;
* Testing, since for the first half of the project I was myself testing the bot, and then resolved to testing;

### Conversation diagram

I couldn't export with good resoultion so here is the [link](https://miro.com/app/board/uXjVM9GD-ug=/) to miro diagram.

### Demo


