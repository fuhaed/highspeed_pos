const { execSync } = require('child_process');

console.log('Installing dependencies...');
execSync('yarn install', { stdio: 'inherit' });

console.log('Building the application...');
execSync('node esbuild --production --apps highspeed_pos --run-build-command', { stdio: 'inherit' }); 