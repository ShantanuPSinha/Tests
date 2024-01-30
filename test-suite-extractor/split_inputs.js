const fs = require('fs');
const readline = require('readline');

function splitInputsByRegex(filePath, outputFilePath) {
    const readStream = fs.createReadStream(filePath, 'utf-8');
    const writeStream = fs.createWriteStream(outputFilePath);
    const rl = readline.createInterface({ input: readStream });
    let isFirstEntry = true;
    const positiveInputsCounts = [];
    const negativeInputsCounts = [];

    rl.on('line', line => {
        if (line) {
            let entry;
            let regex;
            try {
                entry = JSON.parse(line);
                regex = new RegExp(entry.regex);
            } catch (e) {
                console.error('Error parsing JSON or creating regex');
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

            positiveInputsCounts.push(positiveInputs.length);
            negativeInputsCounts.push(negativeInputs.length);

            const result = {
                regex: entry.regex,
                positive_inputs: positiveInputs,
                negative_inputs: negativeInputs,
                file_path: entry.file_path
            };

            if (!isFirstEntry) {
                writeStream.write('\n');
            }
            writeStream.write(JSON.stringify(result));
            isFirstEntry = false;
        }
    });

    rl.on('close', function () {
        writeStream.end();

        if (positiveInputsCounts.length > 0) {
            const medianPositive = median(positiveInputsCounts);
            const medianNegative = median(negativeInputsCounts);
            console.log(`\nMedian Number of Positive Inputs: ${medianPositive}`);
            console.log(`Median Number of Negative Inputs: ${medianNegative}`);
        }
    });

    writeStream.on('finish', function () {
        console.log('Finished writing to', outputFilePath);
    });
}

function median(arr) {
    const sorted = [...arr].sort((a, b) => a - b);
    const middle = Math.floor(sorted.length / 2);
    if (sorted.length % 2 === 0) {
        return (sorted[middle - 1] + sorted[middle]) / 2;
    } else {
        return sorted[middle];
    }
}

const args = process.argv.slice(2);

if (!args[0]) {
    console.error('Input file path is required');
    console.error('Usage: node split_inputs.js <input_file_path> [output_file_path]');
    process.exit(1);
}

splitInputsByRegex(args[0], args[1] || 'output_file.ndjson');
