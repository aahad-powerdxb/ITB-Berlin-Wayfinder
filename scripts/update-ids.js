import fs from 'fs';
import path from 'path';

// Define the path to the JSON file relative to the project root
const jsonFilePath = path.join(process.cwd(), 'src', 'data', 'basicDatas.json');

try {
  // Read and parse the JSON file
  const fileContent = fs.readFileSync(jsonFilePath, 'utf8');
  const data = JSON.parse(fileContent);

  // Transform the data according to the specified rules
  const updatedData = data.map(item => {
    const boothStr = item.booth.toString();
    const numberMatch = boothStr.match(/\d+/); // Find the first sequence of digits

    let newId;

    if (numberMatch) {
      // If a number is found (e.g., from "17" or "7 & D"), parse and use it.
      newId = parseInt(numberMatch[0], 10);
    } else {
      // If no number is found (e.g., "E" or "C"), use the original string.
      newId = boothStr;
    }

    // Return a new object with the original properties and the updated id
    return {
      ...item,
      id: newId
    };
  });

  // Write the updated and formatted data back to the file
  fs.writeFileSync(jsonFilePath, JSON.stringify(updatedData, null, 2), 'utf8');

  console.log('✅ Successfully updated IDs in basicDatas.json based on booth values.');

} catch (error) {
  console.error('❌ An error occurred while updating the JSON file:', error);
}
