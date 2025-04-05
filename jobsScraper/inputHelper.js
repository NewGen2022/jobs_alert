// only for testing purposes - to get query string from the console
import readline from 'readline';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

const askQuestion = (query) =>
    new Promise((resolve) => {
        rl.question(query, (answer) => {
            resolve(answer);
        });
    });

export { rl, askQuestion };
