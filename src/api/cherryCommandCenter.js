const express = require('express');
const bodyParser = require('body-parser');
const cherryAPI = require('./cherryAPI');
const app = express();
const PORT = process.env.COMMAND_CENTER_PORT || 3000;

app.use(bodyParser.json());
app.use('/api/cherry', cherryAPI);

app.listen(PORT, () => {
  console.log(`Cherry Command Center running on port ${PORT}`);
});