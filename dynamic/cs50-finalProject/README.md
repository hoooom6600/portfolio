
# CS50 Tic-Tac-Toe

#### Video Demo:  [https://youtu.be/NdwSuFU0H_s](https://youtu.be/NdwSuFU0H_s)

#### Description:

Hello world! My name is EJ.

As the project title. It's a tic-tac-toe game. Named it "CS50" just to specify it's the final project for CS50 course.
There are two versions in this project, the normal one and the advanced one.


You can also play the game on this URL and no need to download any files, it's my page too!
[https://mikaa7144.pythonanywhere.com/](https://mikaa7144.pythonanywhere.com/)

## Normal Version

it plays just like a traditional tic-tac-toe game.

## Advanced Version

The climax is the advanced version, before you occupy the block, you have to play the paper-scissors-stone first. Only the winner can take a block, and it can always be the same person to take a block as long as he wins.

## Record System

Both the normal and the advanced versions have a record system, it will show up while the game is over. It's optional to submit your current round result. And here you can view the latest 10 records from anyone’s result in the world who has submitted the record.


The records table in the normal and the advanced are different.

## Light Switch

Just click the button at the right-top buttons to switch light mode. This system will remember the light mode you chose the last time you visited the website, and when you visit here next time, it will display the corresponding mode for you.

The attribute comes from Bootstrap usage.


The switch logic is done with JavaScript addEventListener and puts the related HTML attribute to &lt;html&gt;. The custom remember function is achieved by localStorage.setItem and localStorage.getItem in built-in syntax in JavaScript.

## How The Project Works?

### Overall

Most of the functions are achieved by JavaScript and the visual design by Bootstrap and FontAwesome.

The record system is accomplished with Flask.


What's more!! The game site is also available on mobile. In other words, it is a RWD (Responsive Web Design) supported website.

### How to Determine Who Go First and The Computer Thinking?

In the normal version, the first player is determined by generating a random integer. To make a proof, please refresh the page and observe who is in the first turn in the normal version. The thinking function is done by **asynchronous** in JavaScript, and the computer taking his block also is done by generating a random integer.

## Final Project Reflection

To me, manipulating a database is not hard in Flask with CS50 module. The most difficult part for me is "waiting for the user and computer to take the actions", like imitating the computer choosing a block, and monitoring if the user or the computer finishes his turn.


These are finished by **async/await and Promise** in JavaScript. They are truly a whole new coding knowledge (so as the whole new coding world😂) to me, and I took a lot of time to do the research and asked Bing Copilot to clarify the concepts.

And finally, the ideas of how to wait for the actions are provided by Bing Copilot. If there's no assistance, I would never know Promise can be **resolved (a JavaScript built-in function)** in other functions, it doesn't always need to be placed in the Promise when the Promise is defined.
