# Web Proxy
A simple web proxy written in Python3.

## Features

1. Act as a proxy agains the website: *http://comp3310.ddns.net/*
2. Rewrite absolute URL links that originally pointed to the website to now point to the proxy, so all subsequent requests also go via the proxy.
3. Modifies the text content, by replacing every instance of the word “the” in the body text with the word “eht” in bold.
4. Print out the logs in the command line.

## Coding Environment

The code is written in Python3 and tested on the Windows 10 OS system using Google Chrome browser. The HTMLs are parsed using library "BeautifulSoup4". To install beautiful soup, please use the below command: "**sudo pip install beautifulsoup4**".
  
## Running Instructions

Open terminal and type in the command "**python(or python 3) web_proxy.py [optional port number]**". You can input the port number of your choice, by default the port number is 2022. 

Open a browser and type "**localhost:2022**" and the browser will take you to the *comp3310.ddns.net* website. If you choose another port number, change the port number in the URL accordingly. 
