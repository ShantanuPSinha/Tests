const fs = require('fs');
const readline = require('readline');

function splitInputsByRegex(filePath, outputFilePath) {
    const readStream = fs.createReadStream(filePath, 'utf-8');
    const writeStream = fs.createWriteStream(outputFilePath);
    const rl = readline.createInterface({ input: readStream });
    let isFirstEntry = true;
    let totalPositive = 0;
    let totalNegative = 0;
    let entryCount = 0;

    writeStream.write('[');

    rl.on('line', line => {
        if (line) {
            let entry;
            let regex;
            try {
                entry = JSON.parse(line);
                regex = new RegExp(entry.regex);
            } catch (e) {
                console.error('Error parsing JSON or creating regex:','\n', e.message, '\n');
                return;
            }

            const positiveInputs = [];
            const negativeInputs = [];

            entry.inputs.forEach(input => {
                if (regex.test(input)) {
                    positiveInputs.push(input);
                } else {
                    negativeInputs.push(input);
                }
            });

            totalPositive += positiveInputs.length;
            totalNegative += negativeInputs.length;
            entryCount++;

            const result = {
                regex: entry.regex,
                positive_inputs: positiveInputs,
                negative_inputs: negativeInputs,
                file_path: entry.file_path
            };

            if (!isFirstEntry) {
                writeStream.write(',\n');
            }
            writeStream.write(JSON.stringify(result));
            isFirstEntry = false;
        }
    });

    rl.on('close', function() {
        writeStream.write(']');
        writeStream.end();

        if (entryCount > 0) {
            const averagePositive = totalPositive / entryCount;
            const averageNegative = totalNegative / entryCount;
            console.log(`Average Number of Positive Inputs: ${averagePositive.toFixed(0)}`);
            console.log(`Average Number of Negative Inputs: ${averageNegative.toFixed(0)}`);
        }
    });

    writeStream.on('finish', function() {
        console.log('Finished writing to', outputFilePath);
    });
}



function calculateAverageInputs(outputFilePath) {
    fs.readFile(outputFilePath, 'utf8', (err, data) => {
        if (err) {
            console.error("Error reading file:", err);
            return;
        }

        let entries;
        try {
            entries = JSON.parse(data);
        } catch (e) {
            console.error("Error parsing JSON:", e);
            return;
        }

        let totalPositive = 0;
        let totalNegative = 0;

        entries.forEach(entry => {
            totalPositive += entry.positive_inputs.length;
            totalNegative += entry.negative_inputs.length;
        });

        const averagePositive = totalPositive / entries.length;
        const averageNegative = totalNegative / entries.length;

        console.log(`Average Number of Positive Inputs: ${averagePositive.toFixed(2)}`);
        console.log(`Average Number of Negative Inputs: ${averageNegative.toFixed(2)}`);
    });
}

const args = process.argv.slice(2);

if (!args[0]) {
    console.error('Input file path is required');
    console.error('Usage: node split_inputs.js <input_file_path> [output_file_path]');
    process.exit(1);
}

splitInputsByRegex(args[0], args[1] || 'output_file.json');