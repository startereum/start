---
title: Product Specs - Objective, User Stories
release: Alpha
type: Meta
created: 2018-05-24
---

# Product Specs

## Introduction

*refer to FAQs, TWR Concept note for more information.*

In brief, Startereum project brings together a knowledge-oriented community to curate the human algorithmic rankings of new projects. The rankings generate signals for early stage funding. There are three aspects of the whole startereum project:

1. New Project Sign up
2. Members playing staking games
3. Paid access to generated ranked lists

This document will cover the product specs for **alpha release** and that is limited to item no. 2 in the above list i.e members playing staking games.

## Objective

In theory, we have a token-weighted algorithm that uses the wisdom of crowd to rank the projects. With the alpha release, we would like to create a proof of concept, identify weaknesses in the algorithm and tackle user experience challenges. 

The objectives of the alpha run are following:

- [ ]  Design 3 types of staking games to rank 25 projects (i.e 3 dimensions that a project can be compared against other projects)
- [ ]  Launch at Ethereum Testnet
- [ ]  Invite N members to the platform and airdrop tokens for initial plays
- [ ]  Host T total game plays
- [ ]  Compute token-weighted rankings and publish the result

## User personas

In alpha run, there is only one user persona - the player.

Here is how we describe the player:

- players are generally looking to acquire knowledge in crypto space
- players are well versed with startup ecosystem
- expertise of these players range from technical to strategy, innovation and leadership

In order to understand what a user can do on startereum platform, lets see the user stories in the next section.

## User stories

**Sign up, Login**

1. As a new user, I should be able to register using the sign up link. 
2. On the sign up website, if metamask plugin is detected, the user can proceed to sign up. If the metamask is not detected, then the user is asked to download the metmask chrome extension.
3. The sign up requires `email`, `ethererum address` (hard filled using metamask) and `password`

![sign up](https://user-images.githubusercontent.com/1164613/40267150-7cdfc3de-5b75-11e8-9254-ddb94d05ea80.png)

4. Subsequent logins will use metamask. (We might not need a password at all for logins as metamask can ensure if the public eth address belongs to the user)

![login](https://user-images.githubusercontent.com/1164613/40267152-830962d8-5b75-11e8-81a0-1990d7ca5f48.png)

**Token Airdrops**

There are few ways we can airdrop tokens. I will list down few alternatives and we can take a final decision at an appropriate time.

1. We will open the first wave of sign ups and the first 100 members will get an automatic airdrop in their wallet on successful sign up.
2. We will create a microsite for airdrops and send the signed up members a notification email. On notification, a member will have to click the link and register for airdrop using their metamask walllet.
3. We can also do a selective airdrop through human qualification on the first wave of successful registration. This would require us to take more information at registration such as area of expertise, qualification, organisation etc.

**Game center (Dashboard)**

Game center is the dashboard for players. This is the default home page on a successful login. 

As a player,

1. In the top section, I see if any game session is live or not.
2. If the game session is live, I can jump into the session by pressing `play` button.
3. In the rest of the dashboard, I can see all the previous games that I have participated in. I can also see the status of the game if they have finished or not. 
4. I can also see how much STR i have staked and what is the outcome/reward of the game.

![game center](https://user-images.githubusercontent.com/1164613/40267155-8ac2ecce-5b75-11e8-9e2a-7959040f250a.png)

**Play your first game**

The staking game is very simple both in it's logic and user experience. Once, the player clicks on the `play` button from game center, the player is redirected to game screen.

*The dimension such as team-dream, dream-machine, etc are represented by attributes. Attributes help making the comparison easier from comprehension and usability.*

![stake game](https://user-images.githubusercontent.com/1164613/40267159-900e240a-5b75-11e8-99ab-d7561854882c.png)

As a players,

1. I see the duel between dimensions of the two contesting projects.
2. I can only select one of the two projects and enter the staking amount. 
3. I can not stake more than the max. staking amount for that game.
4. Once, I make my selection and put in the minimum stake required to play the game, I can submit my vote.
5. I can also choose to skip the game if I wish to do so.
6. Either way, I am then taken to the next game in the session. 
7. Once the game is played, it cannot be revisited again.

**Finish the first batch of game**

A game session will consist of 10 games played in a streak. 

As a player,

1. I can either play or skip the game.
2. Once I finish the session streak, I am shown a completion screen.
3. The screen tells me how many games I played, skipped and how much tokens I staked.
4. Once the game session expires and ready with results, I get a notification in my email.

![session completion](https://user-images.githubusercontent.com/1164613/40267156-8b0cc1be-5b75-11e8-9f01-0f96d7180e38.png)

**Check your wallet balance**

We should have a minimal wallet functionality of `withdraw` and `deposit`. Both of the functionalities will allow players to import or export tokens to other compatible ERC20 wallets.

As a player,

1. I should be able to check my wallet balance
2. I should be able to see the transaction list for all the games I played where either tokens got debited or credited from my wallet balance.
3. I should have an option to withdraw or deposit tokens to my wallet.
4. In case of withdraw, I should be able to submit an ethereum address where the tokens should be sent to. I should be able to see the gas fee for the transaction cost. It's possible that we may levy a separate withdraw fee.
5. In case of deposit, I should be able to see my wallet public address that I can use to send the money from other wallets (personal or exchange).

![wallet](https://user-images.githubusercontent.com/1164613/40267160-9065be40-5b75-11e8-96ea-4ade17b065da.png)

**Analytics[WIP]**

Analytics are a crucial component of the game engine. It helps us figure how are the members playing the game. Remember the current game design is a zero sum game. Which means people win from people and people lose to people, and this requires us to look at different parameters to measure the game health - repeatability and predictability.

With repeatability, we would like to know if players are coming back for new games. Is it because they are hope to earn more? Are the earnings improving linearly or non-linearly?

With predictability, we would like to know if players are becoming good over a time improving their earnings and human algorithms (in this case ranking). Other way to ask the same metric is to figure how many players must participate in the games to get a trusted algorithm.


**Integrations[WIP]**

* Customer support.
* Email notifications.
* Infrastructure monitoring and alerting.